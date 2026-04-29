---
type: technical-specification
last_updated: 2026-04-28
status: APPROVED
project: Case 1 - Support Intelligence Agent
---

# CASO 1: Especificación Técnica - Agente Inteligente de Soporte
## Con OpenAI + Supabase + n8n (Railway)

## 1. PROBLEMA & SOLUCIÓN

**Problema Real**
```
- Empresa SaaS: 200 tickets/día
- Equipo soporte: 2.5 min/ticket triage manual
- 400-600 minutos/día = 8.3 horas/día desperdiciadas
- 40% de tasa de malclasificación
```

**Solución: Agente Inteligente**
```
Ticket ingresa → OpenAI analiza → Clasificación automática + Decisión
↓
¿Es FAQ conocida? → Respuesta automática + envía
¿Es técnico? → Asigna a especialista + notifica
¿Es crítico? → Escala a liderazgo
```

---

## 2. ARQUITECTURA TÉCNICA

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO COMPLETO                           │
└─────────────────────────────────────────────────────────────┘

INGESTA (n8n Webhook)
    ↓
    │ Ticket JSON: {id, subject, description, priority}
    ↓
ANÁLISIS (OpenAI)
    │ Modelo: gpt-4-mini
    │ Prompt: Clasificar + extraer contexto
    │ Output: {category, priority, is_faq, confidence}
    ↓
DECISIÓN (Lógica n8n)
    │ SI es_faq → Buscar en BD FAQ
    │ SI es_faq → Generar respuesta automática
    │ ELSE SI técnico → Asignar a dev_team
    │ ELSE SI crítico → Escalar a liderazgo
    │ ELSE → Respuesta humana normal
    ↓
PERSISTENCIA (Supabase PostgreSQL)
    │ Guardar: ticket completo + clasificación + respuesta
    │ Guardar: log de procesamiento (auditoría)
    ↓
ACCIÓN (n8n Send)
    │ Email al cliente
    │ Slack al equipo si requiere escalación
    │ Actualizar estado ticket
    ↓
OUTPUT
    │ Respuesta automática o asignación a especialista
    │ Métrica: <2 min tiempo-a-clasificar
```

---

## 3. STACK TÉCNICO

| Componente | Herramienta | Rol |
|-----------|-----------|-----------|
| **Análisis IA** | OpenAI (gpt-4-mini) | Clasificación, generación de respuestas |
| **Orquestación** | n8n (Railway) | Webhook→análisis→decisión→acción |
| **Base de Datos** | Supabase PostgreSQL | Tickets, FAQs, respuestas, logs |
| **Búsqueda Vectorial** | pgvector (Supabase) | Búsqueda FAQ por similitud |
| **Webhook Entry** | n8n Webhook | Recibir tickets |
| **Notificaciones** | n8n integrations | Slack/Email para escalaciones |

---

## 4. SCHEMA SUPABASE (PostgreSQL - Inglés)

### Tabla 1: `support_tickets`
```sql
CREATE TABLE support_tickets (
  id SERIAL PRIMARY KEY,
  external_ticket_id VARCHAR(50) UNIQUE,
  subject VARCHAR(255),
  description TEXT,
  status VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP,
  
  category VARCHAR(50),
  priority VARCHAR(20),
  is_faq BOOLEAN,
  confidence_score DECIMAL(3,2),
  matched_faq_id INT REFERENCES faqs(id),
  
  auto_response TEXT,
  is_auto_response BOOLEAN,
  response_sent_at TIMESTAMP,
  
  assigned_to VARCHAR(100),
  internal_notes TEXT,
  
  customer_id VARCHAR(100),
  customer_email VARCHAR(255),
  channel VARCHAR(20),
  
  llm_tokens_used INT,
  llm_model VARCHAR(50),
  
  INDEX idx_category (category),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
);
```

### Tabla 2: `faqs`
```sql
CREATE TABLE faqs (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255),
  short_description VARCHAR(500),
  full_content TEXT,
  category VARCHAR(50),
  
  embedding vector(1536),
  
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP,
  
  times_used INT DEFAULT 0,
  accuracy_rating DECIMAL(3,2),
  keywords VARCHAR(500),
  
  INDEX idx_category (category),
  INDEX idx_is_active (is_active)
);
```

### Tabla 3: `processing_logs`
```sql
CREATE TABLE processing_logs (
  id SERIAL PRIMARY KEY,
  ticket_id INT REFERENCES support_tickets(id),
  
  timestamp TIMESTAMP DEFAULT NOW(),
  step VARCHAR(100),
  status VARCHAR(50),
  
  openai_request JSONB,
  openai_response JSONB,
  openai_response_time_ms INT,
  
  error_message TEXT,
  metadata JSONB,
  
  INDEX idx_ticket_id (ticket_id),
  INDEX idx_timestamp (timestamp)
);
```

### Tabla 4: `auto_response_templates`
```sql
CREATE TABLE auto_response_templates (
  id SERIAL PRIMARY KEY,
  faq_id INT REFERENCES faqs(id),
  
  response_template TEXT,
  
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. PROMPTS OPENAI (Definición Exacta)

### Prompt 1: Clasificación
```
Role: Eres un agente experto en soporte de SaaS.

Task: Clasificar el siguiente ticket de soporte.

Input:
Subject: {subject}
Description: {description}
Customer History: {history_if_any}

Output MUST be valid JSON:
{
  "category": "Billing | Technical | Feature Request | Bug | Other",
  "priority": "Critical | High | Medium | Low",
  "is_faq": true/false,
  "faq_keywords": ["keyword1", "keyword2"],
  "confidence": 0.85,
  "summary": "Resumen breve del problema",
  "next_action": "auto_response | technical_escalation | leadership_escalation"
}

Guidelines:
- Critical: Servicio caído, pérdida datos, error billing
- High: Feature roto, bug bloqueador
- Medium: Comportamiento inesperado, mejora solicitada
- Low: Preguntas, documentación, feedback

Output ONLY valid JSON. No additional text.
```

### Prompt 2: Generación de Respuesta Automática (Si es FAQ)
```
Role: Agente de soporte amigable pero profesional.

Task: Generar respuesta automática basada en FAQ.

Input:
Customer Ticket: {ticket_description}
Relevant FAQ: {faq_content}
Customer Name: {customer_name}

Output: Email profesional, máximo 200 palabras.

Structure:
1. Saludo personalizado
2. Reconocer el problema
3. Solución paso a paso (desde FAQ)
4. Call-to-action
5. Cierre profesional

Tone: Empático, claro, sin jargón técnico innecesario.
```

---

## 6. N8N WORKFLOW (Railway) - Secuencia de Nodos

```
1. [WEBHOOK] Recibir ticket JSON
   Endpoint: https://[railway-n8n-url]/webhook/support-tickets
   Auth: Bearer token

2. [OPENAI] Clasificación
   - Construir prompt dinámico con ticket
   - Llamar gpt-4-mini
   - Parsear respuesta JSON

3. [SUPABASE] Guardar ticket crudo
   - INSERT en support_tickets
   - Set status: "classified"

4. [CONDITIONAL] Lógica de decisión
   SI is_faq → goto node 5
   ELSE SI technical → goto node 6
   ELSE SI critical → goto node 7
   ELSE → goto node 8

5. [OPENAI] Generar respuesta (Si es FAQ)
   - Buscar FAQ en Supabase
   - Crear prompt de respuesta
   - Generar respuesta automática

6. [SLACK] Notificación técnica
   - Enviar a #technical-support
   - Asignar a dev_team
   - @mencionar si crítico

7. [SLACK] Alerta de liderazgo
   - Enviar a #leadership-alerts
   - Marcar como crítico

8. [SUPABASE] Actualizar ticket con respuesta

9. [EMAIL] Enviar al cliente
   - Respuesta automática si se generó
   - "Estamos analizando" si escalado

10. [LOG] Guardar en processing_logs
    - Metadata completa de ejecución
    - Tiempos, tokens, errores
```

---

## 7. PLAN DE TESTING - Dataset de 50 Tickets

**Categoría Billing (15 tickets)**
- "¿Cómo cambio mi plan?" → FAQ Match
- "Me cobraron dos veces" → Billing High
- "¿Puedo pedir reembolso?" → Billing Medium

**Categoría Technical (20 tickets)**
- "API retorna 500 error" → Bug Critical
- "¿Cómo integro webhook?" → Feature/Doc
- "Feature X no funciona" → Bug High

**Feature Requests (10 tickets)**
- "Necesito exportar a CSV" → Feature Medium

**Otros (5 tickets)**
- Feedback, sugerencias

**Métricas de Éxito**
```
✅ Clasificación Accuracy: ≥90% (45/50 correctas)
✅ Tiempo promedio: <2 minutos/ticket
✅ Detección FAQ: ≥80% identificadas correctamente
✅ Respuestas automáticas: Coherentes y útiles (validación manual)
✅ Escalaciones: Sin falsos positivos/negativos
```

---

## 8. ENTREGABLES (Semana 1)

```
✅ Supabase: Proyecto creado + schema + datos de prueba
✅ n8n: Workflow completo en Railway, testeado
✅ OpenAI: Keys configuradas, prompts validados
✅ Repositorio GitHub con:
   - /workflows (exportación n8n)
   - /database (schema SQL)
   - /prompts (prompts OpenAI documentados)
   - /tests (dataset 50 tickets + resultados)
   - README.md con arquitectura + setup
   - Video demo: 3-5 min mostrando ticket→respuesta

✅ Métricas: 50 tickets procesados con resultados documentados
✅ LinkedIn: 4 posts (Mar/Mié/Jue/Vie)
```

---

## Development Timeline

Este proyecto se desarrolla en fases iterativas enfocadas en calidad y validación:

### Phase 1: Setup & Configuration
- Supabase project creation
- Database schema implementation
- OpenAI API configuration
- n8n workflow foundation

### Phase 2: Core Development
- OpenAI classification engine
- FAQ matching and retrieval
- Auto-response generation
- n8n workflow completion

### Phase 3: Testing & Validation
- 50 ticket dataset generation
- System-wide testing
- Accuracy validation (target: 90%+)
- Performance metrics measurement

### Phase 4: Documentation & Deployment
- Comprehensive README updates
- Architecture documentation
- Code cleanup and optimization
- Production-ready deployment

---

**Estado: ✅ APROBADO - Listo para implementación**

Creado: 2026-04-28
Última actualización: 2026-04-28
