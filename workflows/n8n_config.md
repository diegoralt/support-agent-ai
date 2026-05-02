---
type: workflow-reference
status: IN PROGRESS
last_updated: 2026-05-02
---

# n8n Workflow - Quick Reference

Fast lookup for node configuration and variable mapping.

## Node Configuration Checklist

### 1. Webhook
- [ ] URL configured: `/webhook/support-tickets`
- [ ] Method: POST
- [ ] No authentication required for testing

### 2. AI Agent (Classify)
- [ ] Model: gpt-4-mini
- [ ] System Prompt: `prompts/classification.md`
- [ ] Chat Input: `{{ $json }}`
- [ ] Output: Valid JSON

### 3. Create a Row
- [ ] Table: support_tickets
- [ ] Fields mapped correctly (see N8N_WORKFLOW_GUIDE.md)
- [ ] Status: "classified"

### 4. Switch/IF
- [ ] Condition: `$json.is_faq == true AND $json.confidence >= 0.80`
- [ ] TRUE path: FAQ Search
- [ ] FALSE path: Escalation/Manual

### 5. Supabase Query
- [ ] Keywords from classification
- [ ] Limit: 1
- [ ] Order by category match

### 6. Code Node ✅ ACTIVE
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

### 7. AI Agent (Format Response) 🔄 TESTING
- [ ] Model: gpt-4-mini
- [ ] System Prompt: `prompts/response_formatter.md`
- [ ] Chat Input: `{{ $json }}`
- [ ] Validate JSON output

### 8. Send Email ⏳ PENDING
- [ ] SMTP configured
- [ ] Template HTML ready
- [ ] Subject from Prompt V2

### 9. Update Row ⏳ PENDING
- [ ] Mark status: "auto_responded"
- [ ] Store response in DB
- [ ] Save FAQ match ID

### 10. Processing Logs ⏳ OPTIONAL
- [ ] Audit trail enabled
- [ ] Metadata captured

## Variable Quick Reference

| Variable | Source | Format |
|----------|--------|--------|
| `$json.subject` | Webhook | string |
| `$json.description` | Webhook | string |
| `$json.customer_email` | Webhook | string |
| `$json.category` | Node 2 (Classify) | string |
| `$json.is_faq` | Node 2 (Classify) | boolean |
| `$json.confidence` | Node 2 (Classify) | number (0-1) |
| `$json.full_content` | Node 5 (FAQ Search) | string |
| `$json.body_content` | Node 7 (Format) | string |

## Key Cross-Node References

```
Node 2 Output → Node 3 (Save)
Node 2 Output → Node 4 (Route)
Node 5 Output → Node 6 (Code Node maps faq_full_content)
Node 1 Data → Node 6 (Code Node gets subject, description)
Node 6 Output → Node 7 (Prompt V2 input)
Node 7 Output → Node 8 (Email body)
Node 3 Output → Node 9 (Ticket ID for update)
Node 5 Output → Node 9 (FAQ ID to store)
```

## Testing Sequence

1. **Test Node 2**: Classification with sample ticket
2. **Test Node 5**: FAQ search with keywords
3. **Test Node 6**: Code node output format
4. **Test Node 7**: Prompt V2 with Code node output
5. **Test Nodes 8-9**: Email sending + DB update

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Classification returns text instead of JSON | Check Prompt V1 - ensure "Output ONLY JSON" |
| Code node fails | Verify field names match exactly: `$json.full_content` (not `$json.faq_full_content`) |
| Prompt V2 response too long | Prompt enforces 250-word limit automatically |
| Email template not rendering | Check HTML syntax, use `{{ }}` for variables |
| FAQ not found | Check keywords field in faqs table or query logic |

## Node Status Summary

```
✅ Complete & Tested
  - Node 1: Webhook
  - Node 2: AI Agent (Classify)
  - Node 3: Create a Row
  - Node 4: Switch/IF

🔄 In Progress/Testing
  - Node 5: Supabase Query
  - Node 6: Code Node (Data Mapping)
  - Node 7: AI Agent (Format Response)

⏳ Pending Implementation
  - Node 8: Send Email
  - Node 9: Update Row
  - Node 10: Processing Logs (Optional)
```

---

**Workflow URL**: https://[your-railway-app].up.railway.app
**Status**: 60% Complete - Testing Phase
**Next**: Validate Prompt V2 output, then email integration
