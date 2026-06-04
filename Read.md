# Autonomous AI Research & Report Generation System
## Complete Implementation Documentation

> **Role**: Principal AI Architect · Senior Backend Engineer · AI Workflow Engineer · Enterprise System Designer  
> **Scope**: Local Development · Portfolio-Grade · Agentic AI System  
> **Stack**: Python · FastAPI · n8n · LangGraph · CrewAI · RAG · Multi-Agent Orchestration

### Project Goal

The **Autonomous AI Research & Report Generation System** is a local, multi-agent AI system that accepts a natural language research query and autonomously plans, researches, analyzes, and generates a structured professional report — without human intervention at each step.

The system will:
- Break down the query into sub-tasks
- Search the internet and/or local documents
- Extract and analyze relevant information
- Write, review, and refine a structured report
- Generate PDF output
- Trigger downstream automations via n8n

---
Agentic:      Query
                ↓
              Planner Agent → breaks into tasks
                ↓
              Research Agent → searches web/docs
                ↓
              Analyst Agent → evaluates findings
                ↓
              Writer Agent → drafts structured report
                ↓
              Reviewer Agent → critiques and refines
                ↓
              Final Report + PDF + n8n Trigger
```
### Phase 1 — Foundation (Day 1)
**Objective**: Working API + n8n connection  
**Output**: POST `/research` endpoint triggers n8n webhook  
**What works**: API receives a query, sends it to n8n, n8n logs it

### Phase 2 — Research Pipeline (Day 2)
**Objective**: Real research + report generation  
**Output**: Markdown report saved to disk  
**What works**: API runs a web search, extracts content, generates a markdown report

[User Query]
     │
     ▼
[FastAPI] ──────────────────────────────────────────────────────┐
     │                                                           │
     ▼                                                           │
[LangGraph StateGraph]                                          │
  ├── Planner Node                                              │
  ├── Research Node ──── [Web Search Tool]                      │
  ├── RAG Node ─────────── [Vector DB / Chroma]                 │
  ├── Analysis Node                                             │
  └── Report Node ──── [CrewAI Crew]                           │
       ├── Planner Agent                                        │
       ├── Research Agent                                       │
       ├── Writer Agent                                         │
       └── Reviewer Agent                                       │
                 │                                              │
                 ▼                                              │
         [Final Report MD/PDF]                                  │
                 │                                              │
                 ▼                                              │
         [n8n Webhook] ◄──────────────────────────────────────┘
           ├── Save to disk
           ├── Send email notification
           └── Trigger downstream automation
```
## 5. Phase-Wise Development Plan
 
### Phase 1 — Foundation (Day 1)
**Objective**: Working API + n8n connection  
**Output**: POST `/research` endpoint triggers n8n webhook  
**What works**: API receives a query, sends it to n8n, n8n logs it
 
### Phase 2 — Research Pipeline (Day 2)
**Objective**: Real research + report generation  
**Output**: Markdown report saved to disk  
**What works**: API runs a web search, extracts content, generates a markdown report
 
### Phase 3 — Orchestration (Day 3)
**Objective**: Stateful workflow with LangGraph  
**Output**: Multi-step autonomous workflow with state management  
**What works**: Conditional routing, retry logic, workflow memory, structured state
 
### Phase 4 — Multi-Agent System (Day 4)
**Objective**: CrewAI agents collaborate on research and writing  
**Output**: Full autonomous pipeline — query to PDF to n8n notification  
**What works**: Complete end-to-end agentic system
 
---
## 9. n8n Workflow Architecture
 
### Workflow 1: Research Job Received
 
```
[Webhook: POST /research]
         │
         ▼
[Set Node: Extract job_id, query]
         │
         ▼
[IF Node: depth == "deep"?]
    YES ─→ [Send Slack Notification: "Deep research started"]
    NO  ─→ [Continue]
         │
         ▼
[Wait Node: 30 seconds]
         │
         ▼
[HTTP Request: GET /research/{job_id}/status]
```
 
---
 
### Workflow 2: Report Complete Notification
 
```
[Webhook: POST /webhook/report-complete]
         │
         ▼
[Set Node: Parse payload]
         │
         ▼
[Write Binary File: Save report to /outputs/]
         │
         ├──→ [Send Email: Report ready notification]
         │
         └──→ [HTTP Request: Update job status in DB]
```
 
---
 
### Workflow Diagram
 
```
n8n Workflow: Research Pipeline Monitor
 
 ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
 │   Webhook    │────→│  Extract     │────→│  Conditional     │
 │  (Trigger)   │     │  Payload     │     │  Routing         │
 └──────────────┘     └──────────────┘     └──────┬───────────┘
                                                   │
                              ┌────────────────────┼────────────────────┐
                              ▼                    ▼                    ▼
                     ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
                     │ Save Report  │    │  Send Email  │    │  Update Database │
                     │  to Disk     │    │Notification  │    │     Status       │
                     └──────────────┘    └──────────────┘    └──────────────────┘
```
 
---