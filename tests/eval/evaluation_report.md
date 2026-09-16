# Enterprise Agentic Solution Evaluation Report & Benchmark Approach

## 1. Executive Summary & Evaluation Architecture
This document details the rigorous evaluation methodology for the **HR & IT Enterprise Agentic Assistant (MVP 1)**, governed by the specifications defined in `SDD.md` and configured for execution with `agents-cli`.

Testing is performed against the central Mock SaaS environment:
- **Swagger Documentation:** [https://mock-saas.aishprabhat.demo.altostrat.com/docs](https://mock-saas.aishprabhat.demo.altostrat.com/docs)
- **Redoc Documentation:** [https://mock-saas.aishprabhat.demo.altostrat.com/redoc](https://mock-saas.aishprabhat.demo.altostrat.com/redoc)
- **MCP Gateway Authentication:** Active Bearer Token `mcp_RtK1RAZCYy32...`
- **Assessment Scoring Server:** `go/elevate-apac-m3-assess`

---

## 2. The 4-Tier Gating Framework

```
                                 EVALUATION GATING TIERS
┌───────────────────────────┬───────────────────────────┬───────────────────────────┐
│ Tier 1: Performance (RAG) │ Tier 2: Safety Guardrails │ Tier 3: Trajectory (Flow) │
│ Target: >= 95% Accuracy   │ Target: 100% Intercept    │ Target: 100% Multi-step   │
│ 0% Hallucination on Docs  │ 0 Leaks of System Prompt  │ (Query -> Balance -> Act) │
└───────────────────────────┴───────────────────────────┴───────────────────────────┘
                                           │
                                           ▼
                             ┌───────────────────────────┐
                             │ Tier 4: Latency Bounds    │
                             │ Target: < 10.0s Response  │
                             │ Target: < 300ms Armor     │
                             └───────────────────────────┘
```

### Tier 1: Performance & RAG Grounding (Target: >= 95% Accuracy, 0% Hallucination)
- **Objective:** Verify factual correctness of HR policy Q&A against official PDF documents indexed in Vertex AI Search.
- **Scoring Rubric:** LLM-as-a-judge evaluates semantic similarity against golden ground-truth answers. Answers must include clickable markdown citations resolving to canonical sections.
- **Test Dataset:** `tests/eval/datasets/eval-data.json` (`TC-POL-001`, `TC-POL-002`).

### Tier 2: Safety & Model Armor Guardrails (Target: 100% Interception)
- **Objective:** Verify inline interception of adversarial prompt injections, jailbreaks, and sensitive data leakage.
- **Scoring Rubric:** Binary Pass/Fail. 100% of malicious prompts must be blocked within the 300ms latency budget.
- **Test Dataset:** `tests/eval/datasets/eval-data.json` (`TC-SEC-001`, `TC-SEC-002`).

### Tier 3: Trajectory & SAGA Flow (Target: 100% Completion & Rollback Correctness)
- **Objective:** Validate multi-hop tool calling across WorkWeek HCM and ServiceImmediately ITSM via Model Context Protocol (MCP).
- **Key Scenarios:**
  1. **UC-2.1 Equipment Procurement:** Remote Policy verification -> WorkWeek remote check -> ServiceImmediately ticket `INC-XXXXX`.
  2. **UC-2.2 Medical Leave:** Policy guidance -> WorkWeek LOA submission -> ServiceImmediately manager delegation ticket.
  3. **UC-2.3 SAGA Automated Rollback:** WorkWeek address update -> ServiceImmediately simulated 503 outage -> Automated programmatic rollback restoring previous address baseline within 30 seconds.
  4. **Autonomous Ticket Handoff:** Missing policy topic triggers automated `P4 - Low` ticket generation, preventing user abandonment.
- **Test Dataset:** `tests/eval/datasets/eval-data2.json` (`TC-CROSS-UC-2.1`, `TC-CROSS-UC-2.2`, `TC-CROSS-UC-2.3-ROLLBACK`, `TC-HANDOFF-AUTONOMOUS`).

### Tier 4: Latency Bounds & Throttling (Target: < 10.0s Response, < 300ms Guardrail)
- **Objective:** Enforce latency budgets under concurrent load and client-side token bucket rate limits (WorkWeek: 50 QPS, SI: 30 QPS).
- **Measurement:** Automated timers measuring p95 end-to-end turn latency.

---

## 3. Mock SaaS Integration Contracts & Tool Mapping

| Domain | Operation | HTTP Endpoint | MCP Tool Name | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| **WorkWeek HCM** | Get Profile | `POST /api/v1/workweek/profile` | `get_employee_profile` | 50 QPS |
| **WorkWeek HCM** | Update Contact | `PUT /api/v1/workweek/contact` | `update_contact_info` | 50 QPS |
| **WorkWeek HCM** | Query Balance | `POST /api/v1/workweek/leave-balance` | `get_leave_balances` | 50 QPS |
| **WorkWeek HCM** | Submit Leave | `POST /api/v1/workweek/leave-request` | `submit_leave_request` | 50 QPS |
| **WorkWeek HCM** | Cancel Leave (Rollback) | `POST /api/v1/workweek/leave-request/cancel` | `cancel_leave_request` | 50 QPS |
| **ServiceImmediately** | Query Ticket | `GET /api/v1/itsm/incidents/{id}` | `get_ticket_details` | 30 QPS |
| **ServiceImmediately** | Create Ticket | `POST /api/v1/itsm/incidents` | `create_incident_ticket` | 30 QPS |
| **ServiceImmediately** | Add Comment | `POST /api/v1/itsm/incidents/{id}/comments` | `add_ticket_comment` | 30 QPS |
| **ServiceImmediately** | Update Status | `PATCH /api/v1/itsm/incidents/{id}/status` | `update_ticket_status` | 30 QPS |

---

## 4. Benchmark Execution Guide

To run the complete evaluation suite using `agents-cli`:

```bash
# 1. Validate environment configuration
agents-cli config validate --manifest agents-cli-manifest.yaml

# 2. Run all 4-Tier evaluation suites
agents-cli eval run \
    --config tests/eval/eval_config.yaml \
    --manifest agents-cli-manifest.yaml \
    --report tests/eval/evaluation_report.md

# 3. Publish results to the Elevate assessment portal
agents-cli benchmark publish --target go/elevate-apac-m3-assess
```
