---
type: workflow-configuration
status: IN PROGRESS (60% complete)
last_updated: 2026-05-02
---

# n8n Workflow Configuration Guide

Complete guide for setting up the Support Agent workflow in n8n (Railway-hosted).

## Workflow Overview

```
WEBHOOK → CLASSIFY → SAVE → ROUTE → SEARCH FAQ → MAP DATA → FORMAT → EMAIL → UPDATE
```

## Step-by-Step Setup

### 1. Webhook Trigger
**Node**: Webhook
**URL**: `https://[your-railway-app].up.railway.app/webhook/support-tickets`
**Method**: POST
**Expected Input**:
```json
{
  "subject": "string",
  "description": "string",
  "customer_email": "string",
  "customer_id": "string"
}
```

### 2. Classification (AI Agent - Prompt V1)
**Node**: AI Agent (OpenAI)
**Model**: gpt-4-mini
**System Prompt**: Copy from `prompts/classification.md`
**Chat Input**: `{{ $json }}`
**Output Mode**: Chat

**Validation**: Must return valid JSON with:
- category (one of 5)
- priority (one of 4)
- is_faq (boolean)
- confidence (0.0-1.0)

### 3. Create Row (Save Ticket)
**Node**: Supabase - Insert Row
**Table**: support_tickets
**Map Fields**:
- external_ticket_id: `{{ $json.id }}`
- subject: `{{ $json.subject }}`
- description: `{{ $json.description }}`
- customer_email: `{{ $json.customer_email }}`
- customer_id: `{{ $json.customer_id }}`
- status: "classified"

### 4. Switch/IF (Route by is_faq)
**Node**: Switch or IF
**Condition**: `{{ $json.is_faq }} == true AND {{ $json.confidence }} >= 0.80`
**TRUE Branch**: → FAQ Search
**FALSE Branch**: → Escalation (Slack/Manual)

### 5. Supabase Query (Search FAQ)
**Node**: Supabase - Execute Query
**Query**:
```sql
SELECT id, title, full_content, category, is_active
FROM faqs
WHERE is_active = TRUE
AND (
  keywords ILIKE '%' || $1 || '%'
  OR title ILIKE '%' || $1 || '%'
)
ORDER BY category = $2 DESC
LIMIT 1
```
**Params**:
- $1: `{{ $json.faq_keywords[0] }}`
- $2: `{{ $json.category }}`

### 6. Code Node (Data Mapping)
**Node**: Code (Node.js)

```javascript
return {
  json: {
    faq_full_content: $json.full_content,
    subject: $('Webhook').json.subject,
    description: $('Webhook').json.description,
    faq_category: $json.category
  }
};
```

**Output**: JSON with 4 fields ready for Prompt V2

### 7. AI Agent (Format Response - Prompt V2)
**Node**: AI Agent (OpenAI)
**Model**: gpt-4-mini
**System Prompt**: Copy from `prompts/response_formatter.md`
**Chat Input**: `{{ $json }}`

**Expected Output**:
```json
{
  "success": true,
  "subject": "Re: [something]",
  "body_content": "[plaintext max 250 words]"
}
```

### 8. Send Email
**Node**: Send Email (SMTP)
**To**: `{{ $('Webhook').json.customer_email }}`
**Subject**: `{{ $json.subject }}`
**Body**: HTML Template (see below)

**HTML Template**:
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { border-bottom: 2px solid #007bff; padding-bottom: 15px; margin-bottom: 20px; }
    .content { white-space: pre-wrap; }
    .footer { margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2 style="margin: 0; color: #007bff;">Respuesta a tu consulta</h2>
    </div>
    <div class="content">
{{ $json.body_content }}
    </div>
    <div class="footer">
      <p><strong>Ticket #{{ $('Create a row').json.id }}</strong></p>
      <p>Si necesitas ayuda adicional, no dudes en responder este email.</p>
      <p style="margin-top: 20px; color: #999;">
        <em>Este es un correo automático basado en nuestra base de conocimiento.</em>
      </p>
    </div>
  </div>
</body>
</html>
```

### 9. Update Row (Mark Processed)
**Node**: Supabase - Update Row
**Table**: support_tickets
**Record ID**: `{{ $('Create a row').json.id }}`
**Update Fields**:
- status: "auto_responded"
- auto_response: `{{ $json.body_content }}`
- is_auto_response: true
- processed_at: `{{ now().toISO() }}`
- matched_faq_id: `{{ $('Supabase Query').json[0].id }}`

### 10. Processing Logs (Audit Trail)
**Node**: Supabase - Insert Row
**Table**: processing_logs
**Map Fields**:
- ticket_id: `{{ $('Create a row').json.id }}`
- step: "auto_response_sent"
- status: "success"
- openai_response: `{{ $json }}`
- metadata: `{{ { tokens: $('AI Agent 2').json.usage.total_tokens, response_time: $json.created_at } }}`

## Error Handling

### If Classification Fails
→ Route to Manual Review (Slack notification)

### If FAQ Search Returns Empty
→ Escalate to Technical Support

### If Response Generation Fails
→ Send fallback message: "Estamos analizando tu caso. Pronto te contactaremos."

## Testing

1. **Test Webhook**: Send sample JSON via POST to webhook URL
2. **Test with Real FAQ**: Use FAQ ID 1 ("¿Cómo cambio mi plan?")
3. **Validate Output**: Check Supabase for created ticket
4. **Verify Email**: Check email sending node logs

## Current Status

- ✅ Nodes 1-6: Complete and tested
- 🔄 Node 7: Testing Prompt V2 output
- ⏳ Nodes 8-10: Pending configuration

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Classification returns invalid JSON | Check Prompt V1 in `prompts/classification.md` |
| FAQ not found | Verify keywords in FAQs table or check query |
| Email not sending | Verify SMTP credentials in n8n settings |
| Response too long | Prompt V2 enforces 250-word limit |

---

**Updated**: 2026-05-02
**Status**: Ready for testing phase
