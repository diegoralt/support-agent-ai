---
type: test-dataset
status: READY FOR TESTING
dataset_size: 20 FAQs from Supabase
last_updated: 2026-05-02
---

# Test Cases - Support Agent AI

Dataset and test cases for validating Prompt V1 (Classification) and Prompt V2 (Response Formatting).

## Test Dataset Source

All test cases use real FAQs from Supabase `faqs` table. 20 FAQs populated covering:
- **Billing** (6 FAQs): Plans, payments, refunds, subscriptions
- **Technical** (8 FAQs): API, webhooks, authentication, integration
- **Feature Request** (3 FAQs): Capabilities, limitations
- **Bug** (3 FAQs): Common errors, workarounds

## Test Plan

### Phase 1: Prompt V1 Validation (Classification)
**Goal**: Verify 86% accuracy on real tickets

**Metrics**:
- Accuracy: 43/50 tickets classified correctly
- Confidence: All scores 0.0-1.0
- JSON validity: 100%

**Validation**: Each test ticket should produce:
```json
{
  "category": "one of 5",
  "priority": "one of 4",
  "is_faq": true/false,
  "faq_keywords": ["array", "of", "keywords"],
  "confidence": 0.0-1.0,
  "next_action": "one of 3",
  "summary": "brief description",
  "reasoning": "explanation of classification"
}
```

### Phase 2: Prompt V2 Validation (Response Formatting)
**Goal**: Verify 9.1/10 quality on FAQ responses

**Metrics**:
- Quality: 9+/10 rating
- Word count: All < 250 words
- JSON validity: 100%
- Tone appropriateness: Manual review
- No hallucinations: All info from FAQ only

**Validation**: Each response should:
- Include customer name (N/A for now)
- Acknowledge problem from description
- Reference FAQ content only
- Stay under 250 words
- Include call-to-action

## Sample Test Cases

### Billing Category

**Test 1: FAQ ID 1 - "¿Cómo cambio mi plan?"**
- Input: "Necesito cambiar a Professional"
- Expected: category=Billing, priority=Medium, is_faq=true
- Expected Response: Clear steps + reassurance about immediate effect

**Test 2: FAQ ID 2 - "¿Cuál es la política de reembolsos?"**
- Input: "Me cobraron dos veces, quiero reembolso"
- Expected: category=Billing, priority=Critical, is_faq=true
- Expected Response: Professional, empathetic, references refund policy

**Test 3: FAQ ID 3 - "¿Por qué me cobraron dos veces?"**
- Input: "Aparecen dos cargos en mi tarjeta"
- Expected: category=Billing, priority=High, is_faq=true
- Expected Response: Explanation + resolution steps

### Technical Category

**Test 4: FAQ ID 6 - "¿Cómo integro webhooks?"**
- Input: "Necesito setup webhooks para mi app"
- Expected: category=Technical, priority=Medium, is_faq=true
- Expected Response: Step-by-step + documentation link

**Test 5: FAQ ID 9 - "¿La API soporta OAuth?"**
- Input: "Necesito OAuth 2.0 para mi mobile app"
- Expected: category=Technical, priority=Medium, is_faq=true
- Expected Response: Confirmation + implementation steps

**Test 6: FAQ ID 7 - "¿Cuáles son los límites de rate limit?"**
- Input: "¿Cuántas requests puedo hacer?"
- Expected: category=Technical, priority=Low, is_faq=true
- Expected Response: Clear limits + upgrade options

### Edge Cases

**Test 7: Vague Message (RESTRICCIÓN 1)**
- Input: "Error"
- Expected: category=Technical, priority=Medium, is_faq=false
- Reason: No context, can't classify as FAQ

**Test 8: Technical + Billing (RESTRICCIÓN 2)**
- Input: "Problema con integración y plan de facturación"
- Expected: category=Technical, priority=High, is_faq=false
- Reason: Technical is primary, but complex issue needs review

**Test 9: Frustration Escalation**
- Input: "Tercera vez que reporto este bug, esto es inaceptable"
- Expected: category=Bug, priority=Critical, is_faq=false
- Reason: Multiple reports + frustration indicators

**Test 10: Hidden Problem**
- Input: "Todo funciona bien pero me falta poder exportar a CSV"
- Expected: category=Feature Request, priority=Medium, is_faq=false
- Reason: Feature request despite positive tone

## Execution Instructions

### For Prompt V1 (Classification)

1. Get each test case subject + description
2. Send to Classification node
3. Verify output JSON structure
4. Check accuracy vs expected category/priority
5. Record confidence score
6. Tally correct/incorrect

**Success Criteria**: ≥ 86% accuracy (17+/20 correct)

### For Prompt V2 (Response Formatting)

1. Get FAQ from Supabase by ID
2. Create mapping: faq_full_content + subject + description
3. Send to Response Formatting node
4. Verify output JSON structure
5. Check response quality:
   - Under 250 words? ✓
   - Acknowledges problem? ✓
   - Only uses FAQ info? ✓
   - Appropriate tone? ✓
   - Call-to-action present? ✓

**Success Criteria**: ≥ 18/20 passing (90%+)

## Test Results Template

```
TEST CASE #[N]
──────────────
FAQ ID: [ID]
Category: [Category]
Input: [Ticket description]

EXPECTED:
- Category: [Expected category]
- Priority: [Expected priority]
- Is FAQ: [true/false]

ACTUAL:
- Category: [Actual result]
- Priority: [Actual result]
- Is FAQ: [Actual result]
- Confidence: [Score]

RESULT: [PASS/FAIL]
NOTES: [Any observations]

RESPONSE QUALITY (if applicable):
- Word Count: [N]/250
- Problem Acknowledged: [Yes/No]
- FAQ Info Only: [Yes/No]
- Tone Appropriate: [Yes/No]
- CTA Present: [Yes/No]
```

## Testing Schedule

- **Phase 1**: Prompt V1 validation (2 hours)
- **Phase 2**: Prompt V2 validation (2 hours)
- **Phase 3**: End-to-end workflow (1 hour)
- **Phase 4**: Final review + video demo (1 hour)

**Total**: ~6 hours of testing

---

**Dataset**: 20 FAQs from Supabase production
**Status**: Ready for execution
**Next**: Start Phase 1 testing with Prompt V1
