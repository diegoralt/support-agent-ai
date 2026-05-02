---
type: workflow-configuration
status: IN PROGRESS (design phase complete, implementation ready)
last_updated: 2026-05-02
version: 2.0-specification
---

# n8n Workflow Configuration Guide - v2.0

Complete guide for setting up the Support Agent workflow in n8n (Railway-hosted).

**Status**: Design specification validated. Ready for Phase 1-5 implementation.

## System Architecture: 3 Execution Flows

```
FLOW 1: FAQ Auto-Response
  Webhook → Classify → If(is_faq) → Search FAQ (HTTP+SQL) → Format → Email → Save

FLOW 2: Escalation (High/Critical)
  Webhook → Classify → If(priority High/Critical) → Save Escalated → Route to Flow 3

FLOW 3: Internal Alerting
  Escalated Ticket → Format Alert → Slack/Telegram → Log
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
**TRUE Branch**: → FAQ Search (Node 5)
**FALSE Branch**: → Route by Priority (Node 4b)

### 4b. Switch/IF (Route by Priority)
**Node**: Switch or IF
**Condition**: `{{ $json.priority }} in ['High', 'Critical']`
**TRUE Branch**: → Escalation Flow (Node 5a)
**FALSE Branch**: → Generic Response (Node 6)

### 5. FAQ Search via HTTP Request + Supabase REST API
**Node**: HTTP Request (NEW - replaces Supabase Execute Query)
**Method**: POST
**URL**: `https://[your-project].supabase.co/rest/v1/rpc/search_faqs`
**Auth**: Bearer Token (Supabase anon key)
**Body**:
```json
{
  "search_keyword": "{{ $json.faq_primary_keyword }}",
  "search_category": "{{ $json.category }}"
}
```

**SQL Function in Supabase** (create this first):
```sql
CREATE OR REPLACE FUNCTION search_faqs(
  search_keyword TEXT,
  search_category TEXT
)
RETURNS TABLE (
  id INT,
  title VARCHAR,
  full_content TEXT,
  category VARCHAR,
  is_active BOOLEAN,
  match_score INT
) AS $$
BEGIN
  RETURN QUERY
  SELECT f.id, f.title, f.full_content, f.category, f.is_active,
    CASE 
      WHEN f.title ILIKE '%' || search_keyword || '%' THEN 100
      WHEN f.full_content ILIKE '%' || search_keyword || '%' THEN 25
      ELSE 0
    END as match_score
  FROM faqs f
  WHERE f.is_active = TRUE
  AND (
    f.title ILIKE '%' || search_keyword || '%'
    OR f.full_content ILIKE '%' || search_keyword || '%'
  )
  ORDER BY match_score DESC
  LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

**Expected Output**:
```json
{
  "id": 1,
  "title": "¿Cómo cambio mi plan?",
  "full_content": "Para cambiar tu plan...",
  "category": "Billing",
  "match_score": 100
}
```

**Success Metric**: FAQ found with match_score >= 25

### 6. Code Node (Data Mapping for Prompt V2)
**Node**: Code (Node.js) - ONLY if FAQ found
**Input**: HTTP Request response from Node 5

```javascript
return {
  json: {
    faq_title: $json[0].title,
    faq_full_content: $json[0].full_content,
    original_subject: $('Webhook').json.subject,
    original_description: $('Webhook').json.description,
    faq_category: $json[0].category
  }
};
```

**Output**: JSON with FAQ data ready for Prompt V2

### 7. AI Agent (Format FAQ Response - Prompt V2)
**Node**: AI Agent (OpenAI)
**Model**: gpt-4-mini
**System Prompt**: Copy from `prompts/response_formatter.md`
**Chat Input**: `{{ $json }}`
**Condition**: Only if FAQ found (match_score >= 25)

**Expected Output**:
```json
{
  "success": true,
  "subject": "Re: Tu pregunta sobre cambio de plan",
  "body_content": "[plaintext max 250 words]"
}
```

### 6b. Generic Response (if no FAQ found)
**Node**: Code (Node.js) - If FAQ NOT found
**Template**:
```json
{
  "success": true,
  "subject": "Re: Tu ticket #{id}",
  "body_content": "Estamos analizando tu caso. Pronto te contactaremos con una respuesta completa. Gracias por tu paciencia."
}
```

### 8. Send Email (to Customer)
**Node**: Send Email (SMTP)
**To**: `{{ $('Webhook').json.customer_email }}`
**Subject**: `{{ $json.subject }}`
**Body**: HTML Template
**Condition**: Execute for Flow 1 (FAQ) + Medium/Low (generic)

**HTML Template**:
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { border-bottom: 2px solid #007bff; padding-bottom: 15px; }
    .content { white-space: pre-wrap; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>{{ $json.subject }}</h2>
    </div>
    <div class="content">{{ $json.body_content }}</div>
    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
      Ticket #{{ $('Create a row').json.id }}
    </div>
  </div>
</body>
</html>
```

### 9. Update Row (Mark Processed)
**Node**: Supabase - Update Row
**Table**: support_tickets
**Record ID**: `{{ $('Create a row').json.id }}`
**Update Fields** (Flow 1: FAQ auto-response):
- status: "auto_responded"
- auto_response: `{{ $json.body_content }}`
- is_auto_response: true
- processed_at: `{{ now().toISO() }}`
- matched_faq_id: `{{ $('FAQ Search').json[0].id }}`

**Update Fields** (Flow 2: Medium/Low generic):
- status: "waiting_team_review"
- auto_response: `{{ $json.body_content }}`
- is_auto_response: true
- processed_at: `{{ now().toISO() }}`

### 10. Processing Logs (Audit Trail)
**Node**: Supabase - Insert Row
**Table**: processing_logs
**Map Fields**:
- ticket_id: `{{ $('Create a row').json.id }}`
- step: "flow_1_complete" | "flow_2_escalation" | "flow_3_alert"
- status: "success"
- metadata: `{{ { faq_found: $('FAQ Search').json.length > 0, response_time: now() } }}`

---

## FLOW 2: Escalation (High/Critical) - Detailed Nodes

### 5a. Save Escalated Ticket
**Node**: Supabase - Update Row
**Update Fields**:
- status: "escalated"
- escalation_reason: `{{ $json.priority }} - {{ $json.category }}`
- processed_at: `{{ now().toISO() }}`

### 5b. Format Escalation Alert
**Node**: Code (Node.js)
```javascript
return {
  json: {
    ticket_id: $('Create a row').json.id,
    customer_email: $('Webhook').json.customer_email,
    priority: $json.priority,
    category: $json.category,
    summary: $('Webhook').json.subject,
    description: $('Webhook').json.description.substring(0, 200)
  }
};
```

### 5c. [OPTIONAL] Email Customer - Escalation
**Node**: Send Email (if <24h implementation time)
**To**: `{{ $('Webhook').json.customer_email }}`
**Subject**: "Tu ticket está siendo revisado"
**Template**: "Tu ticket ha sido escalado. Nuestro equipo lo revisa ahora."

---

## FLOW 3: Internal Alerting - Detailed Nodes

### 6c. Send to Slack
**Node**: Slack (native n8n node)
**Channel**: #support-alerts
**Message Format**:
```
🔴 CRITICAL/HIGH PRIORITY TICKET

Ticket ID: #{{ $json.ticket_id }}
Priority: {{ $json.priority }}
Category: {{ $json.category }}
Customer: {{ $json.customer_email }}
Issue: {{ $json.summary }}

{{ $json.description }}
```

### 6d. Send to Telegram [FALLBACK]
**Node**: HTTP Request (optional)
**Method**: POST
**URL**: Telegram Bot API endpoint
**Message**: Same as Slack (formatted for Telegram)

### 6e. Log Alert
**Node**: Supabase - Insert Row
**Table**: processing_logs
**Fields**:
- ticket_id: `{{ $json.ticket_id }}`
- step: "flow_3_alert_sent"
- status: "success"
- metadata: `{{ { channel: 'slack', timestamp: now() } }}`

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

## Implementation Status & Roadmap

### Phase 1: FAQ Search (Node 5) ← CURRENT
- **Status**: Design specification complete, ready for implementation
- **Deliverable**: HTTP Request + Supabase REST API (with SQL function)
- **Time**: 2-3 hours
- **Tasks**:
  - [ ] Create `search_faqs()` function in Supabase
  - [ ] Create HTTP Request node in n8n
  - [ ] Test with 10 sample tickets
  - [ ] Measure accuracy %

### Phase 2: Refactor Escalation Flow
- **Status**: Pending Phase 1 completion
- **Deliverable**: Nodes 4b, 5a (save escalated ticket)
- **Time**: 1-2 hours

### Phase 3: Internal Alerting (Slack + Telegram)
- **Status**: Pending Phase 2 completion
- **Deliverable**: Slack native node + Telegram fallback
- **Time**: 2-3 hours

### Phase 4: Customer Escalation Email [OPTIONAL - if <24h]
- **Status**: Pending Phase 3 completion
- **Deliverable**: Reuse Node 8 for escalation emails
- **Time**: 1-2 hours

### Phase 5: Testing & Documentation
- **Status**: Pending all phases
- **Deliverable**: README + Architecture diagrams + Success metrics
- **Time**: 2-3 hours

## Success Metrics

- **Overall System**: 90% reliability (all flows)
- **Flow 1 (FAQ)**: % FAQ responses correct + generic responses
- **Flow 2 (Escalation)**: % High/Critical tickets correctly escalated
- **Flow 3 (Alerting)**: % alerts sent to Slack/Telegram within <1 min

## Testing

### Phase 1 Testing (Node 5)
1. Test Supabase function: `SELECT search_faqs('API error', 'Bug')`
2. Test HTTP Request node in n8n
3. Validate with 10 sample tickets
4. Measure match_score accuracy

### End-to-End Testing
1. Send sample ticket via webhook
2. Verify all 3 flows execute
3. Check email received
4. Verify Slack alert
5. Confirm Supabase logs created

---

**Updated**: 2026-05-02
**Version**: 2.0 (Specification Design Phase)
**Status**: Ready for Phase 1 implementation
