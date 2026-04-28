# 🤖 Support Agent AI - Intelligent Ticket Triage System

**Status**: 🔨 In Development (Week 1 of 4) | **Building in public** on [LinkedIn](https://www.linkedin.com/in/diego-reyes-altamirano/)

## 🎯 Overview

An intelligent support agent that automatically classifies, prioritizes, and responds to support tickets using Claude API, reducing manual triage time from 8+ hours/day to <1 hour/day.

## 📊 Problem Statement

```
Current State:
  • 200 tickets/day
  • 2.5 min per ticket × 200 = 8.3 hours/day of manual work
  • 40% misclassification rate
  • 30+ min average SLA response time

Target:
  • 90% automated (180 tickets)
  • 6 hours/day saved
  • 90%+ accuracy
  • 5 min average SLA
```

## ✨ Solution Architecture

```
┌─ WEBHOOK INGESTION ─────────────┐
│  New Support Ticket             │
└──────────────┬──────────────────┘
               ↓
┌─ AI ANALYSIS (Claude API) ──────┐
│  • Classify: Billing|Technical   │
│              |Feature|Bug|Other  │
│  • Priority: Critical|High|Med   │
│  • Detect if FAQ                 │
└──────────────┬──────────────────┘
               ↓
┌─ DECISION LOGIC ────────────────┐
│  IF FAQ → Auto-respond          │
│  IF Technical → Route to Dev    │
│  IF Critical → Escalate to Lead │
└──────────────┬──────────────────┘
               ↓
┌─ PERSISTENCE & NOTIFY ──────────┐
│  • Save in Supabase             │
│  • Log response                 │
│  • Trigger Slack/Email notif    │
└─────────────────────────────────┘
```

## 🔧 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| AI Engine | Claude API | Ticket analysis & classification |
| Workflow | n8n | Webhook → Claude → Decision → Action |
| Database | Supabase (PostgreSQL) | Ticket storage + FAQ base |
| Triggers | n8n Webhook | Receive incoming tickets |
| Notifications | Slack/Email (n8n) | Alert team on escalations |

## 📈 Expected Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Daily tickets | 200 | 200 | - |
| Manual work | 8.3h | <1h | **92% reduction** |
| Classification accuracy | 60% | 90% | **+30%** |
| Response SLA | 30 min | 5 min | **6x faster** |
| Automation rate | 0% | 90% | **90% automated** |

## 🚀 Development Timeline

- **Week 1** (Apr 28 - May 2): MVP dev + validation
- **Validation**: 50 test tickets, 90%+ accuracy
- **Video Demo**: Friday, May 2
- **Posts**: LinkedIn journey documented daily

## 📚 Project Structure

```
support-agent-ai/
├── README.md           (this file)
├── src/
│   ├── prompts/        (Claude prompts)
│   ├── workflows/      (n8n exports)
│   └── utils/          (helpers)
├── tests/
│   ├── test_tickets.csv
│   └── validation_results.md
├── docs/
│   ├── architecture.md
│   └── deployment.md
└── .gitignore
```

## 🔗 Resources

- **LinkedIn Journey**: https://www.linkedin.com/in/diego-reyes-altamirano/
- **Part of**: 4-week AI project challenge (May 2026)
- **Blog/Case Study**: [Link when available]

---

**Last Updated**: 2026-04-27  
**Author**: Diego Reyes (@diegoralt)  
**License**: MIT
