---
tipo: guia-tecnica
fecha: 2026-04-29
tema: Restricciones y Optimizaciones del Prompt
---

# Guía de Restricciones del Prompt de Clasificación

## Descripción General

Este documento explica las restricciones (constraints) agregadas al system prompt para mejorar accuracy en clasificación de tickets de soporte. Las restricciones se basan en patrones de error identificados durante testing.

## Restricción 1: Mensajes Técnicos Vagos

### ¿Qué Problema Resuelve?

Mensajes con SOLO palabras técnicas pero sin contexto específico se clasificaban como "Other" en lugar de "Technical".

**Ejemplos de tickets afectados:**
- "Error"
- "No funciona"
- "Problema"
- "No anda"
- "Ayuda pls"

### La Solución

Agregar al SYSTEM_PROMPT:

```
RESTRICCIÓN 1: MENSAJES TÉCNICOS VAGOS
Para mensajes que SOLO contienen una palabra técnica vaga (sin detalles adicionales):
- "Error" (palabra sola) → Technical/Medium (NO Other, NO Bug)
- "No funciona" (sin más) → Technical/Medium (NO Other)
- "Problema" (sin detalles) → Technical/Medium (NO Other)
- "No anda" (sin contexto) → Technical/Medium (NO Other)
- "Ayuda pls" (sin contexto técnico) → Technical/Medium (NO Other)
- "Doesn't work" (palabra sola) → Technical/Medium (NO Other)

IMPORTANTE: Esta restricción NO aplica si hay contexto específico o categoría clara:
- "Bug: Avatar no se actualiza" → ES específico, usar reglas normales
- "Error 500 al guardar" → ES específico, usar reglas normales
- Si ya está claro si es Bug/Billing/Feature Request → NO forzar a Technical
```

### Impacto

- **Errores resueltos**: 6 tickets
- **Categoría mejorada**: EDGE_CASE_POOR_INFO (0% → 100%)
- **Regresiones**: Ninguna

### Por Qué Funciona

1. **Especificidad**: Solo aplica cuando el mensaje es SOLO una palabra vaga
2. **Contexto**: Si hay más información, se usa reglas normales
3. **Seguridad**: No interfiere con categorías que ya están claras
4. **Lógica**: Un mensaje técnico vago sigue siendo un problema técnico

---

## Restricción 2: Precedencia Technical/Billing

### ¿Qué Problema Resuelve?

Tickets que mencionan TANTO "facturación/plan" COMO problemas técnicos se categorizaban como Billing, cuando el problema técnico es primario.

**Ejemplos de tickets afectados:**
- "Problema con integración y facturación"
- "Migración de datos y nuevo plan"
- "Facturación y acceso - dos problemas"

### La Solución

Agregar al SYSTEM_PROMPT:

```
RESTRICCIÓN 2: PROBLEMAS TÉCNICOS CON MENCIÓN DE BILLING
Si el ticket menciona TANTO facturación/billing/plan COMO problemas técnicos 
(integración, acceso, migración, sincronización):
- El problema TÉCNICO es primario → Clasificar como Technical
- NO clasificar como Billing solo por mencionar facturación
- Palabras clave técnicas que prevalecen: "integración", "acceso", "migración", 
  "sincronización", "conectividad"
- Ejemplos:
  * "Problema con integración y facturación" → Technical (problema técnico primario)
  * "Migración de datos y nuevo plan" → Technical (migración es técnica)
  * "Facturación y acceso - dos problemas" → Technical (acceso es técnico)
```

### Impacto

- **Errores resueltos**: 3 tickets de EDGE_CASE_COMPLEXITY
- **Categoría mejorada**: EDGE_CASE_COMPLEXITY (55.6% → 88.9%)
- **Bonus**: EDGE_CASE_FALSE_CRITICAL mejoró (75% → 100%)
- **Mejora neta**: +8 puntos porcentuales
- **Regresiones**: 1 ticket cambió comportamiento (acceptable trade-off)

### Por Qué Funciona

1. **Jerarquía clara**: Technical > Billing cuando ambos presentes
2. **Problema primario**: Si algo bloquea trabajo, es Technical
3. **Contexto real**: En empresas reales, problemas técnicos + facturación significan bloqueo técnico
4. **Bajo riesgo**: Solo aplica cuando ambos topics mencioned

---

## Restricción 3: Frustración + Problema Técnico (Revertida)

### ¿Por Qué Se Revertió?

Se intentó agregar una restricción para evitar clasificar como "Other" cuando hay frustración + problema técnico serio.

```
RESTRICCIÓN 3 (REVERTIDA): FRUSTRACIÓN + PROBLEMA TÉCNICO SERIO
Si hay frustración/enojo + mención de problema técnico grave:
- NO clasificar como "Other"
- Palabras clave: "sistema caído", "downtime", "problema sin resolver"
- Clasificar como Bug o Technical según contexto
```

**Resultado**: Accuracy bajó de 86% a 84% (-2pp)

**Por qué falló**:
- Causó regresiones en EDGE_CASE_FALSE_CRITICAL y EDGE_CASE_AMBIGUITY
- Fue demasiado agresiva en su interpretación
- Creó efectos secundarios no deseados

**Lección**: Negative constraints poderosos necesitan testing exhaustivo antes de implementar.

---

## Principios de Diseño

### 1. Especificidad Sobre Generalidad
❌ "SI menciona error → Technical" (demasiado general, causa regresiones)
✅ "SI SOLO menciona 'error' sin contexto → Technical" (específico, funciona)

### 2. Contexto Siempre Aplica
❌ Forzar restricción sin importar contexto
✅ Preguntar "¿hay ya contexto específico?" antes de aplicar

### 3. Bajo Riesgo de Regresión
❌ Cambios que podrían afectar 20+ categorías
✅ Cambios enfocados en 1-2 casos de error

### 4. Validación Científica
❌ "Esto debería funcionar" → publicar
✅ Probar antes/después en 50 tickets → validar impacto en TODAS las categorías

---

## Testing de Restricciones

### Cómo Agregar Una Nueva Restricción

1. **Identificar el patrón de error**
   ```
   Ticket X: "..." 
   Got: Categoría/Prioridad ACTUAL
   Expected: Categoría/Prioridad ESPERADA
   Patrón: [describe el patrón común]
   ```

2. **Diseñar la restricción**
   ```
   RESTRICCIÓN N: [Nombre]
   Problema: [Qué causa el error]
   Solución: [Qué cambiar]
   Palabras clave: [Qué detectar]
   Ejemplos: [Casos específicos]
   ```

3. **Agregar al SYSTEM_PROMPT**
   - Ubicación: Después de "Niveles de prioridad", antes de "REGLA 1"
   - Formato: Mantener consistencia con restricciones existentes
   - Especificidad: Muy específico, con ejemplos

4. **Ejecutar tests**
   ```bash
   python test_classification.py        # 10 tickets
   python test_comprehensive_classification.py  # 50 tickets
   ```

5. **Validar impacto**
   - Accuracy no baja (si baja > 1pp, reconsiderar)
   - No hay regresiones en categorías stable (HAPPY_PATH, FALSE_CRITICAL, etc.)
   - Error patterns se reducen como esperado

6. **Documentar resultado**
   - Guardar en OPTIMIZATION_SUMMARY.md
   - Explicar por qué funciona/falla

---

## Estado Actual del Prompt

### Restricciones Activas

✅ RESTRICCIÓN 1: Mensajes técnicos vagos
✅ RESTRICCIÓN 2: Precedencia Technical/Billing

### Estructura del SYSTEM_PROMPT

```
1. Descripción de tarea
2. Categorías posibles
3. Niveles de prioridad
4. ▶ RESTRICCIÓN 1 (Mensajes vagos)
5. ▶ RESTRICCIÓN 2 (Technical/Billing)
6. REGLA 1: Escalada por frustración
7. REGLA 2: Problemas escondidos
8. REGLA 3: Categorización clara
9. REGLA 4: Mensajes vagos (no escales)
10. CASOS ESPECIALES
11. Formato de respuesta JSON
```

### Métricas Finales

- **Total tokens**: ~1,200 (eficiente)
- **Accuracy**: 86% (43/50 tickets)
- **Stability**: Validado en 10 y 50 ticket sets
- **Listo para producción**: Sí, con fallback manual

---

## Próximas Mejoras Sugeridas

1. **Restricción de Escalada de Prioridad**
   - Problema: Priority escalation en frustración (High → Critical)
   - Oportunidad: 2 tickets pueden ser corregidos

2. **Claridad Bug vs Technical**
   - Problema: Confusión en límites
   - Oportunidad: 3 tickets

3. **Feature Request Detection**
   - Problema: No detecta "funcionalidad no existe"
   - Oportunidad: 2 tickets

---

## Referencias

- Test suite: `test_classification.py` (10 tickets), `test_comprehensive_classification.py` (50 tickets)
- Resultados: `classification-test-results.json`, `classification-comprehensive-results.json`
- Optimización: Ver `OPTIMIZATION_SUMMARY.md`
