#!/usr/bin/env python3
"""
Comprehensive test script for ticket classification.
Tests against 50 tickets with edge cases, happy path, and adversarial cases.
Provides detailed analysis by category type.
"""

import json
import os
from datetime import datetime
from openai import OpenAI
from collections import defaultdict

# Initialize OpenAI client (uses OPENAI_API_KEY from .env)
client = OpenAI()

# Load comprehensive test tickets
with open("test-tickets-comprehensive.json", "r", encoding="utf-8") as f:
    test_tickets = json.load(f)

# Expected classifications (ground truth for validation)
expected_results = {ticket["id"]: {
    "category": ticket["expected_category"],
    "priority": ticket["expected_priority"]
} for ticket in test_tickets}

SYSTEM_PROMPT = """Eres un especialista en clasificación de tickets de soporte técnico para una plataforma SaaS.

Tu tarea es analizar cada ticket de cliente y:
1. Clasificarlo en una categoría
2. Asignar una prioridad
3. Identificar si puede responderse con una respuesta automática basada en FAQs

Categorías posibles:
- Billing: Preguntas sobre planes, facturación, pagos, cambios de suscripción, refunds
- Technical: Problemas de acceso, autenticación, conectividad, integración
- Feature Request: Solicitudes de nuevas características o mejoras
- Bug: Reportes específicos de fallos, comportamientos inesperados, errores de aplicación
- Other: Cualquier otro tipo de pregunta, spam, off-topic

Niveles de prioridad:
- Critical:
  * Usuario está completamente bloqueado (no puede trabajar)
  * Error en producción (error 500, timeout, API falla) + bloquea trabajo
  * Acceso denegado/autenticación fallida
  * Pérdida de datos confirmada o feature crítica destruida
  * Cliente furioso (repetición, amenazas de churn, demandas)
  * Frustración extrema + problema sin resolver
  * Problemas de facturación fraudulentos
  * Feature crítica rota + esperando 5+ días
- High:
  * Performance degradada (lentitud, timeouts ocasionales)
  * Datos inconsistentes o reportes incorrectos
  * Impacta significativamente la experiencia pero hay workaround
  * Cliente molesto (no furioso) pero problema persiste
  * Múltiples intentos fallidos del usuario (3+)
  * Afecta múltiples usuarios o features importantes
- Medium:
  * Molestia o funcionalidad reducida pero no bloquea trabajo
  * Mensajes vagos sin contexto crítico
  * Bugs menores que no afectan datos
  * Acceso fallido pero solución aparente (ej: reset password)
- Low:
  * Preguntas, solicitudes, problemas menores
  * General inquiries
  * Feature requests normales
  * UI cosmética

RESTRICCIÓN 1: MENSAJES TÉCNICOS VAGOS (sin contexto = NO escales)
Para mensajes que SOLO contienen una palabra técnica vaga (sin detalles adicionales):
- "Error" (palabra sola) → Technical/Medium (NO Other, NO Bug)
- "No funciona" (sin más) → Technical/Medium (NO Other)
- "Problema" (sin detalles) → Technical/Medium (NO Other)
- "No anda" (sin contexto) → Technical/Medium (NO Other)
- "Ayuda pls" (sin contexto técnico) → Technical/Medium (NO Other)
- "Doesn't work" (palabra sola) → Technical/Medium (NO Other)

IMPORTANTE: Esta restricción NO aplica si hay contexto específico o categoría clara:
- "Bug: Avatar no se actualiza" → ES específico, usar reglas normales (puede ser Bug/Medium o Bug/High)
- "Error 500 al guardar" → ES específico, usar reglas normales (Bug/Critical)
- Si ya está claro si es Bug/Billing/Feature Request → NO forzar a Technical

RESTRICCIÓN 2: PROBLEMAS TÉCNICOS CON MENCIÓN DE BILLING
Si el ticket menciona TANTO facturación/billing/plan COMO problemas técnicos (integración, acceso, migración, sincronización):
- El problema TÉCNICO es primario → Clasificar como Technical
- NO clasificar como Billing solo por mencionar facturación
- Palabras clave técnicas que prevalecen: "integración", "acceso", "migración", "sincronización", "conectividad"
- Ejemplos:
  * "Problema con integración y facturación" → Technical (problema técnico primario)
  * "Migración de datos y nuevo plan" → Technical (migración es técnica)
  * "Facturación y acceso - dos problemas" → Technical (acceso es técnico)

REGLA 1: FRUSTRATION ESCALATION (solo si hay CONTEXTO de problema serio)
Busca estas palabras/frases DE FRUSTRACIÓN + PROBLEMA SERIO:
- "tercera/segunda vez que reporto" + problema sin resolver → Critical
- "considerando cambiar de proveedor" + problema técnico/billing → Critical
- "inaceptable / insatisfecho" + problema recurrente → Critical
- "pérdida de dinero / estoy tirando dinero" + problema actual → Critical
- "esto es un fraude" (siempre) → Critical
- "exijo compensación" (siempre) → Critical
- Múltiples intentos fallidos (intenté 3+ veces) → High (al menos)
- "urgente" + problema que bloquea → Critical (pero no solo porque diga urgente)

REGLA 2: HIDDEN PROBLEMS (prioriza problemas graves escondidos)
- Si dice tono positivo ("gracias", "excelente", "me encanta") Y LUEGO menciona problema grave:
  * Pérdida de datos (archivos desaparecen, datos desaparecen) → CRITICAL
  * Acceso bloqueado → CRITICAL
  * Feature importante rota + esperando X días → CRITICAL (si X >= 3 días)
  * Error recurrente (múltiples veces) → HIGH
- Si el sujeto es casual pero el mensaje describe bloqueo o daño → CRITICAL
- Sincronización fallida + múltiples intentos = HIGH
- "Esperando X días" + problema que impacta trabajo → escala a HIGH mínimo

REGLA 3: CATEGORIZACIÓN CLARA
- Problema de entrada a cuenta (acceso, autenticación, login fallido) → Technical
- Problema de integración (conectividad, webhook fallido) → Technical
- API específica falla (endpoint timeout, error de API) → Bug
- Feature específica no funciona (botón, guardar, descargar) → Bug
- Lentitud/performance general → Technical
- Datos incorrectos o corruptos → Bug
- Refund/factura/plan → Billing
- Solicitud de feature → Feature Request
- Spam/off-topic → Other
- IMPORTANTE: Si hay duda, prefiere Bug sobre Technical para errores específicos

REGLA 4: MENSAJES VAGOS (sin contexto = NO escales)
- "No funciona" sin contexto → Medium (no sabemos si es crítico)
- "Ayuda pls" sin detalles → Medium (es vago)
- "Error" sin descripción → Medium (podría ser cualquier cosa)
- "Problema" sin contexto → Medium (demasiado vago)
- Solo escala si MENCIONA BLOQUEO o FRUSTRACIÓN clara

CASOS ESPECIALES:
- False alarms: "URGENTE" + pregunta simple = Low o Medium, NO Critical
- Logout no funciona = Medium (molestia pero no bloquea)
- UI desalineada en browser = Low o Medium (cosmético)
- Spam/Off-topic: Clasifica como "Other", priority Low

PARA EL JSON: Incluye también is_faq (igual a can_auto_respond), faq_keywords (palabras clave del ticket), confidence (0-1 seguridad), next_action (auto_response|technical_escalation|leadership_escalation|human_review)

Responde SIEMPRE en JSON con esta estructura:
{
  "category": "Billing|Technical|Feature Request|Bug|Other",
  "priority": "Critical|High|Medium|Low",
  "is_faq": true/false,
  "faq_keywords": ["keyword1", "keyword2"],
  "confidence": 0.75,
  "next_action": "auto_response|technical_escalation|leadership_escalation|human_review",
  "summary": "Resumen conciso del problema",
  "reasoning": "Explicación breve de la clasificación y cualquier factor de frustración detectado"
}"""


def classify_ticket(ticket):
    """Call OpenAI API to classify a single ticket."""
    user_message = f"""Analiza este ticket de soporte:

**Asunto**: {ticket['subject']}
**Mensaje**: {ticket['message']}

Clasifícalo según los criterios dados y responde en JSON."""

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except json.JSONDecodeError:
        return None
    except Exception as e:
        print(f"❌ Error classifying ticket {ticket['id']}: {e}")
        return None


def validate_classification(ticket_id, result, expected):
    """Check if classification matches expected result."""
    if not result:
        return False

    category_match = result.get("category") == expected["category"]
    priority_match = result.get("priority") == expected["priority"]

    return category_match and priority_match


def main():
    print("🚀 Starting comprehensive ticket classification test...")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total tickets: {len(test_tickets)}\n")

    results = []
    correct = 0
    total = len(test_tickets)

    # Track results by category type
    category_stats = defaultdict(lambda: {"correct": 0, "total": 0})

    for ticket in test_tickets:
        ticket_id = ticket["id"]
        category_type = ticket["category_type"]
        print(f"[{ticket_id:2d}/50] {category_type:25s} | {ticket['subject'][:40]:40s}", end="")

        result = classify_ticket(ticket)

        if result:
            is_correct = validate_classification(ticket_id, result, expected_results[ticket_id])
            status = "✅" if is_correct else "❌"
            if is_correct:
                correct += 1

            category_stats[category_type]["correct"] += (1 if is_correct else 0)
            category_stats[category_type]["total"] += 1

            print(f" {status}")

            results.append(
                {
                    "ticket_id": ticket_id,
                    "category_type": category_type,
                    "subject": ticket["subject"],
                    "result": result,
                    "expected": expected_results[ticket_id],
                    "correct": is_correct,
                }
            )
        else:
            print(" ⚠️")
            category_stats[category_type]["total"] += 1
            results.append(
                {
                    "ticket_id": ticket_id,
                    "category_type": category_type,
                    "subject": ticket["subject"],
                    "result": None,
                    "correct": False,
                }
            )

    accuracy = (correct / total) * 100

    # Print summary
    print(f"\n{'='*80}")
    print(f"📊 OVERALL RESULTS")
    print(f"{'='*80}")
    print(f"✅ Correct: {correct}/{total}")
    print(f"📈 Accuracy: {accuracy:.1f}%")
    print(f"🎯 Target: 90%")
    print(f"{'='*80}\n")

    # Print breakdown by category type
    print(f"{'='*80}")
    print(f"📋 BREAKDOWN BY CATEGORY TYPE")
    print(f"{'='*80}")

    for category_type in sorted(category_stats.keys()):
        stats = category_stats[category_type]
        cat_accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"{category_type:30s} | {stats['correct']:2d}/{stats['total']:2d} | {cat_accuracy:5.1f}%")

    print(f"{'='*80}\n")

    # Find patterns in errors
    errors = [r for r in results if not r["correct"] and r["result"]]
    if errors:
        print(f"{'='*80}")
        print(f"❌ ERROR ANALYSIS ({len(errors)} errors)")
        print(f"{'='*80}")

        for error in errors[:15]:  # Show first 15 errors
            print(f"\nTicket {error['ticket_id']}: {error['subject']}")
            print(f"  Category Type: {error['category_type']}")
            if error["result"]:
                print(f"  Got:      {error['result'].get('category')} / {error['result'].get('priority')}")
            print(f"  Expected: {error['expected']['category']} / {error['expected']['priority']}")

        if len(errors) > 15:
            print(f"\n... and {len(errors) - 15} more errors")

    # Save detailed results
    report = {
        "timestamp": datetime.now().isoformat(),
        "model": os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
        "total_tickets": total,
        "correct": correct,
        "accuracy_percent": round(accuracy, 1),
        "category_breakdown": {k: dict(v) for k, v in category_stats.items()},
        "results": results,
    }

    with open("classification-comprehensive-results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📁 Results saved to: classification-comprehensive-results.json")

    # Exit with success if accuracy >= 90%
    if accuracy >= 90:
        print(f"✅ SUCCESS: Accuracy meets 90% target!\n")
        return 0
    else:
        print(f"⚠️  WARNING: Accuracy below 90% target. {90 - accuracy:.1f}% improvement needed.\n")
        return 1


if __name__ == "__main__":
    exit(main())
