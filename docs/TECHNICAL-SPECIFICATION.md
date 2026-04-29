---
type: technical-specification
last_updated: 2026-04-28
status: APPROVED
project: Case 1 - Support Intelligence Agent
---

# CASE 1: Technical Specification - Support Intelligence Agent
## With OpenAI + Supabase + n8n (Railway)

## 1. PROBLEM & SOLUTION

**Real Problem**
```
- SaaS Company: 200 tickets/day
- Support team: 2.5 min/ticket manual triage
- 400-600 minutes/day = 8.3 hours/day wasted
- 40% incorrect classifications
```

**Solution: Intelligent Agent**
```
Ticket ingesta → OpenAI analyzes → Automatic classification + Decision
↓
Is FAQ known? → Auto response + send
Is technical? → Assign to specialist + notify
Is critical? → Escalate to leadership
```

---

## 2. TECHNICAL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE FLOW                            │
└─────────────────────────────────────────────────────────────┘

INGESTION (n8n Webhook)
    ↓
    │ Ticket JSON: {id, subject, description, priority}
    ↓
ANALYSIS (OpenAI)
    │ Model: gpt-4-mini
    │ Prompt: Classify + extract context
    │ Output: {category, priority, is_faq, confidence}
    ↓
DECISION (n8n Logic)
    │ IF is_faq → Search FAQ database
    │ IF is_faq → Generate auto response
    │ ELSE IF technical → Assign to dev_team
    │ ELSE IF critical → Escalate to leadership
    │ ELSE → Normal human response
    ↓
PERSISTENCE (Supabase PostgreSQL)
    │ Save: complete ticket + classification + response
    │ Save: processing log (audit trail)
    ↓
ACTION (n8n Send)
    │ Email to customer
    │ Slack to team if escalation needed
    │ Update ticket status
    ↓
OUTPUT
    │ Auto response or specialist assignment
    │ Metric: <2 min time-to-classify
```

---

## 3. TECH STACK

| Component | Tool | Role |
|-----------|------|------|
| **AI Analysis** | OpenAI (gpt-4-mini) | Classification, response generation |
| **Orchestration** | n8n (Railway) | Webhook→analysis→decision→action |
| **Database** | Supabase PostgreSQL | Tickets, FAQs, responses, logs |
| **Vector Search** | pgvector (Supabase) | FAQ similarity search |
| **Webhook Entry** | n8n Webhook | Receive tickets |
| **Notifications** | n8n integrations | Slack/Email for escalations |

---

## 4. SUPABASE SCHEMA (PostgreSQL - English)

### Table 1: `support_tickets`
```sql
CREATE TABLE support_tickets (
  id SERIAL PRIMARY KEY,
  external_ticket_id VARCHAR(50) UNIQUE,
  subject VARCHAR(255),
  description TEXT,
  status VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP,
  
  category VARCHAR(50),
  priority VARCHAR(20),
  is_faq BOOLEAN,
  confidence_score DECIMAL(3,2),
  matched_faq_id INT REFERENCES faqs(id),
  
  auto_response TEXT,
  is_auto_response BOOLEAN,
  response_sent_at TIMESTAMP,
  
  assigned_to VARCHAR(100),
  internal_notes TEXT,
  
  customer_id VARCHAR(100),
  customer_email VARCHAR(255),
  channel VARCHAR(20),
  
  llm_tokens_used INT,
  llm_model VARCHAR(50),
  
  INDEX idx_category (category),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
);
```

### Table 2: `faqs`
```sql
CREATE TABLE faqs (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255),
  short_description VARCHAR(500),
  full_content TEXT,
  category VARCHAR(50),
  
  embedding vector(1536),
  
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP,
  
  times_used INT DEFAULT 0,
  accuracy_rating DECIMAL(3,2),
  keywords VARCHAR(500),
  
  INDEX idx_category (category),
  INDEX idx_is_active (is_active)
);
```

### Table 3: `processing_logs`
```sql
CREATE TABLE processing_logs (
  id SERIAL PRIMARY KEY,
  ticket_id INT REFERENCES support_tickets(id),
  
  timestamp TIMESTAMP DEFAULT NOW(),
  step VARCHAR(100),
  status VARCHAR(50),
  
  openai_request JSONB,
  openai_response JSONB,
  openai_response_time_ms INT,
  
  error_message TEXT,
  metadata JSONB,
  
  INDEX idx_ticket_id (ticket_id),
  INDEX idx_timestamp (timestamp)
);
```

### Table 4: `auto_response_templates`
```sql
CREATE TABLE auto_response_templates (
  id SERIAL PRIMARY KEY,
  faq_id INT REFERENCES faqs(id),
  
  response_template TEXT,
  
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. OPENAI PROMPTS (Exact Definition)

### Prompt 1: Classification
```
Role: You are an expert support agent for a SaaS company.

Task: Classify the following support ticket.

Input:
Subject: {subject}
Description: {description}
Customer History: {history_if_any}

Output MUST be valid JSON:
{
  "category": "Billing | Technical | Feature Request | Bug | Other",
  "priority": "Critical | High | Medium | Low",
  "is_faq": true/false,
  "faq_keywords": ["keyword1", "keyword2"],
  "confidence": 0.85,
  "summary": "Brief problem summary",
  "next_action": "auto_response | technical_escalation | leadership_escalation"
}

Guidelines:
- Critical: Service down, data loss, billing error
- High: Feature broken, blocking bug
- Medium: Unexpected behavior, improvement request
- Low: Questions, documentation, feedback

Output ONLY valid JSON. No additional text.
```

### Prompt 2: Auto Response Generation (If FAQ)
```
Role: Professional, friendly support agent.

Task: Generate an auto response based on FAQ match.

Input:
Customer Ticket: {ticket_description}
Relevant FAQ: {faq_content}
Customer Name: {customer_name}

Output: Professional email, max 200 words.

Structure:
1. Personalized greeting
2. Acknowledge the problem
3. Step-by-step solution (from FAQ)
4. Call-to-action
5. Professional closing

Tone: Empathetic, clear, no unnecessary jargon.
```

---

## 6. N8N WORKFLOW (Railway) - Node Sequence

```
1. [WEBHOOK] Receive ticket JSON
   Endpoint: https://[railway-n8n-url]/webhook/support-tickets
   Auth: Bearer token

2. [OPENAI] Classification
   - Build dynamic prompt with ticket
   - Call gpt-4-mini
   - Parse JSON response

3. [SUPABASE] Save raw ticket
   - INSERT into support_tickets
   - Set status: "classified"

4. [CONDITIONAL] Decision Logic
   IF is_faq → goto node 5
   ELSE IF technical → goto node 6
   ELSE IF critical → goto node 7
   ELSE → goto node 8

5. [OPENAI] Generate Response (If FAQ)
   - Query FAQ from Supabase
   - Create response prompt
   - Generate auto response

6. [SLACK] Technical Notification
   - Send to #technical-support
   - Assign to dev_team
   - @mention if critical

7. [SLACK] Leadership Alert
   - Send to #leadership-alerts
   - Mark critical

8. [SUPABASE] Update ticket with response

9. [EMAIL] Send to customer
   - Auto response if generated
   - "We're analyzing" if escalated

10. [LOG] Save to processing_logs
    - Full execution metadata
    - Timing, tokens, errors
```

---

## 7. TEST PLAN - 50 Ticket Dataset

**Billing Category (15 tickets)**
- "How do I change my plan?" → FAQ Match
- "I was charged twice" → Billing High
- "Can I request a refund?" → Billing Medium

**Technical Category (20 tickets)**
- "API returns 500 error" → Bug Critical
- "How to integrate webhook?" → Feature/Doc
- "Feature X not working" → Bug High

**Feature Requests (10 tickets)**
- "Need CSV export" → Feature Medium

**Other (5 tickets)**
- Feedback, suggestions

**Success Metrics**
```
✅ Classification Accuracy: ≥90% (45/50 correct)
✅ Avg Processing Time: <2 minutes/ticket
✅ FAQ Detection: ≥80% identified correctly
✅ Auto Responses: Coherent and helpful (manual validation)
✅ Escalations: No false positives/negatives
```

---

## 8. DELIVERABLES (Week 1)

```
✅ Supabase: Project created + schema + test data
✅ n8n: Complete workflow on Railway, tested
✅ OpenAI: Keys configured, prompts validated
✅ GitHub repo with:
   - /workflows (n8n JSON export)
   - /database (SQL schema + migrations)
   - /prompts (OpenAI prompts documented)
   - /tests (50 ticket dataset + results)
   - README.md with architecture + setup
   - Video demo: 3-5 min showing ticket→response

✅ Metrics: 50 tickets processed with documented results
✅ LinkedIn: 4 posts (Mon/Tue/Wed/Fri)
```

---

## Week 1 Timeline

```
MONDAY April 28 (2h available)
- Setup Supabase (create project, schema)
- Setup OpenAI (keys, basic test)
- Post 1 LinkedIn (Problem Discovery)

TUESDAY April 29 (4h)
- Finalize OpenAI prompts
- First classification tests
- LinkedIn engagement
- Post 2 (Solution Architecture)

WEDNESDAY April 30 (4h)
- n8n workflow complete
- End-to-end test (webhook→OpenAI→Supabase)
- Post 3 (Live Development)

THURSDAY May 1 (4h)
- Generate 50 ticket dataset
- Process all through system
- Validate accuracy
- Post 4 (Building in Public)

FRIDAY May 2 (4h)
- Video demo (3-5 min)
- Professional README
- Git push final
- Document metrics
- Post 5 (Results)
```

---

**Status: ✅ APPROVED - Ready for implementation**

Created: 2026-04-28
