# 🤖 Agente de Soporte AI - Sistema Inteligente de Triaje de Tickets

**Estado**: 🔨 En Desarrollo | **Building in public** en [LinkedIn](https://www.linkedin.com/in/diego-reyes-altamirano/)

## 🎯 Resumen

Un agente de soporte inteligente que automáticamente clasifica, prioriza y responde tickets de soporte usando OpenAI API, reduciendo el tiempo manual de triaje de 8+ horas/día a <1 hora/día.

## 📊 Declaración del Problema

```
Estado Actual:
  • 200 tickets/día
  • 2.5 min por ticket × 200 = 8.3 horas/día de trabajo manual
  • 40% de tasa de malclasificación
  • 30+ min de tiempo de respuesta SLA promedio

Objetivo:
  • 90% automatizado (180 tickets)
  • 6 horas/día ahorradas
  • 90%+ de precisión
  • 5 min SLA promedio
```

## ✨ Arquitectura de la Solución

```
┌─ INGESTA POR WEBHOOK ───────────┐
│  Nuevo Ticket de Soporte        │
└──────────────┬──────────────────┘
               ↓
┌─ ANÁLISIS IA (OpenAI API) ──────┐
│  • Clasificar: Billing|Técnico   │
│               |Feature|Bug|Otro  │
│  • Prioridad: Crítica|Alta|Med   │
│  • Detectar si es FAQ            │
└──────────────┬──────────────────┘
               ↓
┌─ LÓGICA DE DECISIÓN ────────────┐
│  SI FAQ → Respuesta automática   │
│  SI Técnico → Asignar a Dev      │
│  SI Crítico → Escalar a Lead     │
└──────────────┬──────────────────┘
               ↓
┌─ PERSISTENCIA Y NOTIFICACIÓN ───┐
│  • Guardar en Supabase           │
│  • Registrar respuesta           │
│  • Trigger Slack/Email notif     │
└─────────────────────────────────┘
```

## 🔧 Stack Técnico

| Componente | Tecnología | Propósito |
|-----------|-----------|---------|
| Motor IA | OpenAI API | Análisis y clasificación de tickets |
| Flujo de Trabajo | n8n | Webhook → OpenAI → Decisión → Acción |
| Base de Datos | Supabase (PostgreSQL) | Almacenamiento de tickets + base FAQ |
| Triggers | n8n Webhook | Recibir tickets entrantes |
| Notificaciones | Slack/Email (n8n) | Alertar al equipo en escalaciones |

## 📈 Métricas Esperadas

| Métrica | Antes | Después | Mejora |
|--------|-------|---------|---------|
| Tickets diarios | 200 | 200 | - |
| Trabajo manual | 8.3h | <1h | **92% reducción** |
| Precisión clasificación | 60% | 90% | **+30%** |
| SLA de respuesta | 30 min | 5 min | **6x más rápido** |
| Tasa automatización | 0% | 90% | **90% automatizado** |

## 🚀 Fases de Desarrollo

1. **Setup & Configuration**: Supabase, OpenAI, n8n
2. **Core Development**: Motor de clasificación, matching FAQ, generación de respuestas
3. **Testing & Validation**: 50 ticket dataset, validación de accuracy
4. **Documentation & Deployment**: README, arquitectura, deployment

## 📊 Resultados Finales (Validación)

### Accuracy del Sistema
| Métrica | Resultado |
|---------|-----------|
| **Accuracy (50 tickets)** | **86%** (43/50 correctos) |
| **Accuracy (10 tickets)** | **80%** (8/10 correctos) |
| **Mejora vs Baseline** | +12 puntos porcentuales |
| **Estado** | ✅ Listo para producción |

### Desglose por Categoría de Prueba
| Categoría | Accuracy |
|-----------|----------|
| HAPPY_PATH | 90.9% (10/11) |
| EDGE_CASE_POOR_INFO | 100% (6/6) ✅ |
| EDGE_CASE_COMPLEXITY | 88.9% (8/9) |
| EDGE_CASE_FALSE_CRITICAL | 75% (3/4) |
| EDGE_CASE_FALSE_NEGATIVE | 100% (4/4) ✅ |
| EDGE_CASE_AMBIGUITY | 57.1% (4/7) |
| EDGE_CASE_FRUSTRATION | 57.1% (4/7) |

Ver `OPTIMIZATION_SUMMARY.md` para análisis completo.

## 📚 Estructura del Proyecto

```
support-agent-ai/
├── README.md                           (este archivo)
├── OPTIMIZATION_SUMMARY.md             (resultados finales)
├── PROMPT_GUIDE.md                     (guía de restricciones)
├── docs/
│   ├── TECHNICAL-SPECIFICATION.md
│   ├── ARCHITECTURE.md
│   └── /database
├── /workflows                          (exportaciones n8n)
├── /src
│   ├── /prompts                        (prompts OpenAI)
│   ├── /orchestration                  (scripts Python)
│   └── /utils                          (helpers)
├── test_classification.py              (test con 10 tickets)
├── test_comprehensive_classification.py (test con 50 tickets)
├── test-tickets.json                   (datos de prueba)
├── test-tickets-comprehensive.json     (datos complejos)
├── classification-test-results.json    (resultados 10 tickets)
├── classification-comprehensive-results.json (resultados 50 tickets)
├── .env.example                        (template de configuración)
├── .gitignore
└── LICENSE
```

## 🔬 Cómo Ejecutar Tests

### Setup Inicial
```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd support-agent-ai

# 2. Crear .env basado en .env.example
cp .env.example .env
# Editar .env con tus credenciales de OpenAI y Supabase

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar Test Simple (10 tickets)
```bash
python test_classification.py
```
**Esperado**: 8/10 correctos (80% accuracy)

### Ejecutar Test Comprehensivo (50 tickets)
```bash
python test_comprehensive_classification.py
```
**Esperado**: 43/50 correctos (86% accuracy)

### Ver Resultados
- Resultados guardados en archivos JSON automáticamente
- Análisis de errores incluido en output de terminal
- Métricas detalladas por categoría de prueba

## 📖 Documentación Importante

### Para Entender las Optimizaciones
- **`OPTIMIZATION_SUMMARY.md`**: Resumen de mejoras implementadas (74% → 86%)
- **`PROMPT_GUIDE.md`**: Explicación de restricciones y cómo funcionan

### Para Implementar en n8n
- **`docs/TECHNICAL-SPECIFICATION.md`**: Especificación técnica completa
- **`docs/ARCHITECTURE.md`**: Diagramas y flujos

## 🔐 Configuración Segura

### Variables de Entorno Requeridas
Copiar `.env.example` a `.env` y completar con tus credenciales:
```bash
# OpenAI
OPENAI_API_KEY=tu_api_key_aqui
OPENAI_MODEL=gpt-5.4-mini

# Supabase
SUPABASE_URL=tu_supabase_url
SUPABASE_ANON_KEY=tu_anon_key
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key

# n8n (opcional para local testing)
N8N_WEBHOOK_URL=tu_webhook_url
N8N_WEBHOOK_AUTH_TOKEN=tu_token
```

⚠️ **IMPORTANTE**: Nunca commitear `.env` a git. Solo `.env.example` sin credenciales.

## 🔗 Recursos

- **Journey en LinkedIn**: https://www.linkedin.com/in/diego-reyes-altamirano/
- **Parte de**: Desafío de proyecto IA de 4 semanas (Mayo 2026)
- **Blog/Case Study**: [Link cuando esté disponible]

---

**Última Actualización**: 2026-04-28  
**Autor**: Diego Reyes (@diegoralt)  
**Licencia**: MIT
