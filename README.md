# 🤖 Agente de Soporte AI - Sistema Inteligente de Triaje de Tickets

**Estado**: 🔨 En Desarrollo (Semana 1 de 4) | **Building in public** en [LinkedIn](https://www.linkedin.com/in/diego-reyes-altamirano/)

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

## 🚀 Timeline de Desarrollo

- **Semana 1** (28 abril - 2 mayo): Desarrollo MVP + validación
- **Validación**: 50 tickets de prueba, 90%+ de precisión
- **Video Demo**: Viernes, 2 de mayo
- **Posts**: Journey documentado diariamente en LinkedIn

## 📚 Estructura del Proyecto

```
support-agent-ai/
├── README.md                (este archivo)
├── docs/
│   ├── TECHNICAL-SPECIFICATION.md
│   ├── ARCHITECTURE.md
│   └── /database
├── /workflows               (exportaciones n8n)
├── /src
│   ├── /prompts            (prompts OpenAI)
│   ├── /orchestration      (scripts Python)
│   └── /utils              (helpers)
├── /tests
│   ├── test_tickets.json
│   └── validation_results.md
├── .env.example
├── .gitignore
└── LICENSE
```

## 🔗 Recursos

- **Journey en LinkedIn**: https://www.linkedin.com/in/diego-reyes-altamirano/
- **Parte de**: Desafío de proyecto IA de 4 semanas (Mayo 2026)
- **Blog/Case Study**: [Link cuando esté disponible]

---

**Última Actualización**: 2026-04-28  
**Autor**: Diego Reyes (@diegoralt)  
**Licencia**: MIT
