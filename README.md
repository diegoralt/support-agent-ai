# 🤖 Agente de Soporte AI - Sistema Inteligente de Triaje de Tickets

**Estado**: 🔨 En Desarrollo - Especificación v2.0 ✅ | **Building in Public** en [LinkedIn](https://www.linkedin.com/in/diego-reyes-altamirano/)

## 🎯 ¿Qué es este proyecto?

Un sistema inteligente de triaje de tickets de soporte que **automáticamente clasifica, responde y escala** tickets usando IA, demostrando arquitectura moderna con **3 flujos de ejecución claramente definidos**.

**Perfecto para**:
- 📚 Aprender cómo integrar IA en flujos de trabajo empresariales
- 🔧 Entender arquitectura de sistemas con n8n + Supabase + OpenAI
- 🚀 Fork y adaptar para tu propio proyecto de soporte
- 💼 Portfolio: Proyecto completo, documentado y reproducible

---

## 📊 El Problema

En empresas SaaS típicas:
```
Estado Actual (sin automatización):
  • 200 tickets/día
  • 2.5 minutos por ticket manual = 8.3 horas/día
  • 40-60% de malclasificación
  • Respuesta lenta (30+ minutos SLA)
  • Equipo quemado respondiendo lo mismo

Objetivo del Sistema:
  • ✅ Reducir trabajo manual de 8h → <1h por día
  • ✅ 90% de confiabilidad sistema completo
  • ✅ 85-90% de coincidencia FAQ automática
  • ✅ 86% precisión en clasificación (validado)
```

---

## ✨ Arquitectura: 3 Flujos Claros

El sistema está diseñado en **3 flujos de ejecución independientes**:

### **FLUJO 1️⃣: Respuesta Automática FAQ** 
```
Ticket entrante
    ↓
Clasificar con Prompt V1 (OpenAI)
    ├─ Categoría: Billing | Technical | Feature | Bug | Other
    ├─ Prioridad: Critical | High | Medium | Low
    └─ ¿Es FAQ?: true/false
    ↓
SI es FAQ + confianza >= 80%
    ↓
    Buscar en base FAQ (HTTP Request → Supabase REST API)
    ├─ Scoring: title (100pts) > full_content (25pts)
    └─ Match >= 25pts = FAQ encontrado
    ↓
    SI FAQ encontrado
        → Formatear respuesta (Prompt V2)
        → Enviar email al cliente
    ↓
    SI NO encontrado
        → Enviar respuesta genérica
        → Escalar a Flow 2
    ↓
    Guardar en Supabase: status="auto_responded"
```

**Métrica**: % de tickets con respuesta correcta (FAQ o genérica)

---

### **FLUJO 2️⃣: Escalación (High/Critical)**
```
Ticket clasificado con Prioridad = High o Critical
    ↓
    Guardar en Supabase: status="escalated"
    ↓
    [OPCIONAL] Enviar email al cliente: "Tu caso está siendo revisado"
    ↓
    Enrutar a Flujo 3 (alertar equipo interno)
```

**Política**: Sin respuesta automática para High/Critical → escalación inmediata

---

### **FLUJO 3️⃣: Alertamiento Interno (Slack + Telegram)**
```
Ticket escalado
    ↓
Formatear alerta con contexto:
    • ID del ticket
    • Email del cliente
    • Prioridad + Categoría
    • Resumen del problema (200 caracteres)
    ↓
Enviar alerta a equipo:
    ├─ PRIMARY: Slack → #support-alerts
    └─ FALLBACK: Telegram (si miembro no tiene Slack)
    ↓
Guardar en logs de auditoría
```

**Métrica**: % de alertas entregadas al equipo en <1 minuto

---

## 🔧 Stack Técnico

| Componente | Tecnología | Propósito |
|-----------|-----------|---------|
| **Clasificación IA** | OpenAI API (gpt-4-mini) | Analizar y clasificar tickets (86% accuracy) |
| **Orquestación** | n8n (Railway-hosted) | Flujo de trabajo: webhook → IA → decisión → acción |
| **Base de Datos** | Supabase (PostgreSQL) | Tickets, FAQs, logs de procesamiento |
| **Búsqueda FAQ** | HTTP Request + Supabase REST API | Búsqueda con scoring SQL personalizado |
| **Alertas Internas** | Slack (nativo n8n) + Telegram | Notificar al equipo en tiempo real |
| **Respuestas** | Email (SMTP) | Comunicación con clientes |

---

## 📈 Métricas de Éxito

### Global
```
Sistema Confiabilidad = 90%
  = (Respuestas correctas + Escalaciones correctas + Alertas entregadas) / Total tickets
```

### Por Flujo
| Flujo | Métrica | Target | Status |
|-------|---------|--------|--------|
| **Flow 1: FAQ** | % respuestas correctas | 85-90% | 🔄 Testing |
| **Flow 2: Escalación** | % tickets High/Critical escalados | 95%+ | 🔄 Testing |
| **Flow 3: Alertas** | % alertas entregadas <1min | 98%+ | 🔄 Testing |

### Clasificación (Validado)
```
Baseline (Prompt V1): 74% (37/50 tickets)
Con optimizaciones: 86% (43/50 tickets)
Mejora: +12 puntos porcentuales ✅
```

---

## 🚀 Roadmap: 5 Fases (10-11 horas total)

### **Phase 1: Búsqueda FAQ Optimizada** [2-3h] ← SIGUIENTE
- [ ] Crear función PostgreSQL `search_faqs()` en Supabase
- [ ] Configurar HTTP Request en n8n
- [ ] Tests con 10 tickets reales
- [ ] Medir accuracy % coincidencias

### **Phase 2: Refactor Flujo Escalación** [1-2h]
- [ ] Node 4b: Router por prioridad
- [ ] Node 5a: Guardar tickets escalados
- [ ] Preparar para Flow 3

### **Phase 3: Alertamiento Interno** [2-3h]
- [ ] Integración Slack nativa n8n
- [ ] Fallback Telegram vía API
- [ ] Formateo de alertas inteligente

### **Phase 4: Email Escalación** [1-2h] *Opcional - si tiempo permite*
- [ ] Template email para clientes
- [ ] Integración SMTP en n8n
- [ ] Notificación automática

### **Phase 5: Testing + Documentación** [2-3h]
- [ ] End-to-end tests todos los flujos
- [ ] Diagramas arquitectura
- [ ] Guía para forkear/adaptar

---

## 📁 Estructura del Proyecto

```
support-agent-ai/
├── README.md                              # Este archivo
├── docs/
│   ├── TECHNICAL_SPECIFICATION.md         # Especificación técnica v2.0
│   ├── N8N_WORKFLOW_GUIDE.md             # Guía detallada de configuración n8n
│   └── n8n_config.md                     # Quick reference nodos
├── prompts/
│   ├── classification.md                  # Prompt V1: Clasificación (86% accuracy)
│   └── response_formatter.md              # Prompt V2: Formatear respuestas
├── workflows/
│   └── n8n_config.md                     # Exportación configuración n8n
├── tests/
│   ├── test_classification.py             # Test 10 tickets
│   └── test_comprehensive_classification.py # Test 50 tickets
├── test-tickets.json                      # Dataset 10 tickets
├── test-tickets-comprehensive.json        # Dataset 50 tickets
├── .env.example                           # Template variables entorno
├── requirements.txt                       # Dependencias Python
├── LICENSE                                # MIT
└── OPTIMIZATION_SUMMARY.md                # Detalle mejoras prompt (74%→86%)
```

---

## 🚀 Cómo Usar (Forkeando este Repo)

### 1️⃣ Fork + Setup Local

```bash
# Clonar tu fork
git clone https://github.com/TU_USUARIO/support-agent-ai.git
cd support-agent-ai

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Configurar Credenciales

```bash
# Copiar template
cp .env.example .env

# Editar .env con tus valores:
```

```env
# OpenAI
OPENAI_API_KEY=sk-xxxxxxx
OPENAI_MODEL=gpt-4-mini

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJxxx
SUPABASE_SERVICE_ROLE_KEY=eyJxxx
```

⚠️ **IMPORTANTE**: Nunca commitear `.env` con secretos reales

### 3️⃣ Probar Clasificación Localmente

```bash
# Test simple (10 tickets)
python tests/test_classification.py

# Test completo (50 tickets)
python tests/test_comprehensive_classification.py

# Esperado: 80-86% accuracy
```

### 4️⃣ Integrar en n8n

Ver `docs/N8N_WORKFLOW_GUIDE.md` para guía paso-a-paso:
- Configurar Webhook n8n
- Setup OpenAI connection
- Supabase REST API setup
- Slack integration

---

## 🎓 Conceptos Clave Explicados

### ¿Por qué HTTP Request + Supabase REST API (no SQL directo)?
```
n8n Supabase node soporta: Insert, Update, Get, Delete (operaciones simples)
Nuestro caso: SQL custom con CASE/scoring (complejo)

Solución: HTTP Request → Supabase REST API
✅ Más flexible
✅ Soporta SQL personalizado
✅ Fácil de debuggear
✅ Escalable
```

### ¿Por qué 3 Flujos Separados?
```
Modelo empresarial real:
- FAQ (simple) ≠ Escalación (compleja)
- Medium tickets ≠ Critical tickets
- Respuesta automática ≠ Sin respuesta

3 Flujos = mejor control + más testeable + más mantenible
```

### Métrica 90%: ¿Qué significa?
```
90% = Sistema completo funciona correctamente
  (no es solo clasificación, incluye email + alertas + logs)

Medición:
  - Tickets procesados exitosamente / Total tickets
  - Rastrear por flujo para diagnosticar problemas
```

---

## 📚 Documentación Completa

| Documento | Propósito |
|-----------|-----------|
| **TECHNICAL_SPECIFICATION.md** | Arquitectura completa, decisiones, diagramas |
| **N8N_WORKFLOW_GUIDE.md** | Guía paso-a-paso configuración n8n |
| **OPTIMIZATION_SUMMARY.md** | Por qué accuracy mejoró de 74% → 86% |
| **prompts/classification.md** | Prompt V1 con explicación de reglas |
| **prompts/response_formatter.md** | Prompt V2 para formatear respuestas |

---

## 🔧 Customizar para tu Caso de Uso

### Cambiar categorías de tickets
Editar `prompts/classification.md`:
```
- Billing
- Technical
- Feature Request
- Bug
- Other
```

Reemplazar por tus categorías reales

### Agregar FAQs personalizadas
```sql
INSERT INTO faqs (title, full_content, category, is_active)
VALUES (
  '¿Cómo cambio mi plan?',
  'Respuesta completa...',
  'Billing',
  true
);
```

### Cambiar canal Slack
En n8n Node 6c:
```
Cambiar #support-alerts → tu canal
```

---

## 💡 Lecciones Aprendidas

### ¿Qué funcionó bien?
✅ Negative constraints (restricciones en prompts) vs few-shot learning
✅ Separar flujos = más testeable y debuggeable
✅ HTTP API vs SQL directo = más flexible

### ¿Qué mejorar en v3?
🔄 Vector search para FAQs más complejas
🔄 Sentiment analysis para escalación automática
🔄 Multi-idioma support

---

## 🔐 Seguridad

```bash
✅ Credenciales en .env (gitignored)
✅ Tokens OpenAI encriptados
✅ Supabase anon key + service role separadas
✅ Logs guardados (auditoría)
✅ Sin datos sensibles en GitHub
```

---

## 🤝 Cómo Contribuir

Este proyecto es educativo y completamente forkeable.

Para mejoras:
1. Fork el repo
2. Crea rama: `git checkout -b feature/mejora-tuya`
3. Commit: `git commit -m "feat: Agregar mejora"`
4. Push: `git push origin feature/mejora-tuya`
5. Abre Pull Request

---

## 📞 Preguntas/Problemas

- Documentación: Ver `/docs/`
- Problemas n8n: `docs/N8N_WORKFLOW_GUIDE.md`
- Problemas Prompts: `docs/OPTIMIZATION_SUMMARY.md`
- Issues técnicos: Abre GitHub Issue

---

## 📖 Referencias

- [OpenAI API Docs](https://platform.openai.com/docs)
- [n8n Documentation](https://docs.n8n.io/)
- [Supabase PostgreSQL Guide](https://supabase.com/docs/guides/database)
- [Building in Public](https://www.linkedin.com/in/diego-reyes-altamirano/)

---

## 📄 Licencia

MIT - Libre para usar, modificar, distribuir

---

**Última Actualización**: 2026-05-02  
**Versión**: 2.0 (Especificación de Diseño)  
**Autor**: Diego Reyes (@diegoralt)  
**Estado**: 🔨 En desarrollo - Ready para Phase 1 implementation
