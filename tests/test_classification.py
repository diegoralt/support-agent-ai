#!/usr/bin/env python3
"""
Test script for OpenAI ticket classification prompt.
Tests the prompt against 10 sample tickets and validates accuracy.
"""

import json
import os
from datetime import datetime
from openai import OpenAI

# Initialize OpenAI client (uses OPENAI_API_KEY from .env)
client = OpenAI()

# Load test tickets
with open("test-tickets.json", "r", encoding="utf-8") as f:
    test_tickets = json.load(f)

# Expected classifications (ground truth for validation)
expected_results = {
    1: {"category": "Billing", "priority": "Low"},
    2: {"category": "Bug", "priority": "Critical"},
    3: {"category": "Feature Request", "priority": "Low"},
    4: {"category": "Billing", "priority": "High"},
    5: {"category": "Bug", "priority": "Critical"},
    6: {"category": "Billing", "priority": "Low"},
    7: {"category": "Bug", "priority": "Medium"},
    8: {"category": "Feature Request", "priority": "Low"},
    9: {"category": "Technical", "priority": "Critical"},
    10: {"category": "Billing", "priority": "Low"},
}

SYSTEM_PROMPT = """Eres un especialista en clasificación de tickets de soporte técnico para una plataforma SaaS.

Tu tarea es analizar cada ticket de cliente y:
1. Clasificarlo en una categoría
2. Asignar una prioridad
3. Identificar si puede responderse con una respuesta automática basada en FAQs

Categorías posibles:
- Billing: Preguntas sobre planes, facturación, pagos, cambios de suscripción
- Technical: Errores, bugs, problemas técnicos, problemas de acceso a funciones
- Feature Request: Solicitudes de nuevas características o mejoras
- Bug: Reportes específicos de fallos o comportamientos inesperados
- Other: Cualquier otro tipo de pregunta

Niveles de prioridad:
- Critical: Bloquea trabajo del cliente, error en producción, acceso completo denegado
- High: Impacta significativamente la experiencia pero hay workaround temporal
- Medium: Molestia o funcionalidad reducida pero no bloquea el trabajo principal
- Low: Preguntas, solicitudes, problemas menores

Responde SIEMPRE en JSON con esta estructura:
{
  "category": "...",
  "priority": "...",
  "summary": "Resumen conciso del problema",
  "can_auto_respond": true/false,
  "reasoning": "Explicación breve de la clasificación"
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
            temperature=0.3,  # Lower temperature for consistency
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except json.JSONDecodeError:
        print(f"⚠️  JSON decode error for ticket {ticket['id']}")
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
    print("🚀 Starting ticket classification test...")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total tickets: {len(test_tickets)}\n")

    results = []
    correct = 0
    total = len(test_tickets)

    for ticket in test_tickets:
        ticket_id = ticket["id"]
        print(f"[{ticket_id}/10] Classifying: {ticket['subject'][:50]}...", end="")

        result = classify_ticket(ticket)

        if result:
            is_correct = validate_classification(ticket_id, result, expected_results[ticket_id])
            status = "✅" if is_correct else "❌"
            if is_correct:
                correct += 1

            print(f" {status}")
            print(
                f"      → Category: {result.get('category')} (expected: {expected_results[ticket_id]['category']})"
            )
            print(
                f"      → Priority: {result.get('priority')} (expected: {expected_results[ticket_id]['priority']})"
            )

            results.append(
                {
                    "ticket_id": ticket_id,
                    "subject": ticket["subject"],
                    "result": result,
                    "expected": expected_results[ticket_id],
                    "correct": is_correct,
                }
            )
        else:
            print(" ⚠️")
            results.append(
                {"ticket_id": ticket_id, "subject": ticket["subject"], "result": None, "correct": False}
            )

    accuracy = (correct / total) * 100
    print(f"\n{'='*60}")
    print(f"📊 RESULTS")
    print(f"{'='*60}")
    print(f"✅ Correct: {correct}/{total}")
    print(f"📈 Accuracy: {accuracy:.1f}%")
    print(f"🎯 Target: 90%")
    print(f"{'='*60}\n")

    # Save detailed results
    report = {
        "timestamp": datetime.now().isoformat(),
        "model": os.getenv("OPENAI_MODEL", "gpt-4-mini"),
        "total_tickets": total,
        "correct": correct,
        "accuracy_percent": round(accuracy, 1),
        "results": results,
    }

    with open("classification-test-results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📁 Results saved to: classification-test-results.json")

    # Exit with success if accuracy >= 90%
    if accuracy >= 90:
        print(f"✅ SUCCESS: Accuracy meets 90% target!\n")
        return 0
    else:
        print(f"⚠️  WARNING: Accuracy below 90% target. Review misclassifications.\n")
        return 1


if __name__ == "__main__":
    exit(main())
