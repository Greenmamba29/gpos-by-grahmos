# GPOS by Grahmos — Demo Build Plan (FARM)

## 1) Objectives
- Prove the **core boundary** works: **Real LLM reasoning → schema-valid proposals → deterministic GPOS kernel validates/executes → simulated adapters**.
- Deliver an end-to-end **Founder Day Golden Demo Run** with seeded exceptions, **8 branded flywheel screens**, and **Demo Mode role-switching**.
- Ensure governance primitives are real: **state machine, SoD, thresholds, immutable audit chain, evidence lineage, offline queue+sync, retries+idempotency, operator controls, learning competency updates**.

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation) (must pass before app build)
**User stories**
1. As an operator, I can submit a plain-language Founder Day request and get a **schema-valid** normalized Request/Case proposal.
2. As the system, I reject any agent output that fails JSON schema validation or lacks evidence/unknowns.
3. As Finance, I can’t be self-approved by the requester when spend exceeds threshold (SoD enforced).
4. As an auditor, I can verify an **append-only audit chain** and trace each decision to evidence artifacts.
5. As a mobile user, I can create an action offline and see it **deduped + synchronized** later.

**Steps**
- Websearch: best practices for **(a) JSON schema enforcement for LLM outputs**, (b) **idempotent state machines** + outbox pattern.
- Add backend env + LLM harness:
  - Use `EMERGENT_LLM_KEY`; implement `AgentProvider` with Claude Sonnet 4.5 primary + GPT-5 fallback.
  - Implement “JSON-only” prompting + strict parsing + `jsonschema` validation.
- Implement minimal GPOS kernel (pure Python, no FastAPI yet):
  - State machine + `transition(case, command, actor, idempotency_key)`.
  - SoD + role/authority + approval threshold checks.
  - AuditEvent append-only with hash-chain fields.
  - Evidence Artifact model + lineage links from proposals/decisions.
  - Offline OutboxEvent queue + deterministic sync replay + conflict detection hook.
- Create `test_core.py` to prove:
  - LLM returns valid JSON for (1) intake normalization, (2) supplier candidates + quote normalization w/ evidence_refs + unknowns.
  - Kernel applies proposed transition only when authorized; blocks self-approval and over-threshold w/o right approver.
  - Audit chain verifies; evidence lineage resolvable.
  - Offline outbox replays idempotently.
- Iterate until `test_core.py` is consistently green.

**testing_agent_v3 todo (Phase 1)**
- Run `python test_core.py` multiple times; verify schema validation failures handled gracefully; confirm SoD block + audit hash chain verification.

---

### Phase 2 — V1 App Development (Backend + Frontend MVP)
**User stories**
1. As any role, I can open **Grahmos Today** and see my personalized “what needs attention” tiles.
2. As a requester, I can follow the Founder Day case in a **Decision Room** with rationale + deadlines.
3. As an approver, I can approve/deny in **Approval Center** with SoD/threshold context and evidence.
4. As an operator, I can run sourcing and review candidates in **Supplier 360** and publish a decision map.
5. As a student, I can complete a learning task and get competency updated only after supervisor attestation.

**Backend (FastAPI + Motor)**
- Create Mongo collections per domain model; seed **Howard University** institution + actors/roles.
- Promote kernel into backend modules:
  - `policy_engine`, `sod_engine`, `workflow_kernel`, `audit_chain`, `evidence_store`, `offline_sync`.
- Simulated adapters + flow engine:
  - Implement Flow catalog F01–F12 as deterministic “flow runners” with retries + idempotency.
  - Sandbox adapters for Channels/ERP/Calendar/Carrier/Payment/Accio/Activepieces (never expose names in UI).
- API routes (`/api`):
  - Demo Mode: `GET /me`, `POST /demo/impersonate`, `POST /demo/reset`, `POST /demo/jump_stage`, `GET /demo/audit`.
  - Cases: create/intake, get, timeline, commands (transition requests), approvals, suppliers/quotes, shipments.
  - Agents: endpoints that run LLM to produce **proposals** only; kernel endpoint to **apply validated commands**.
  - Learning: tasks, quiz result, supervisor attestation, competency update.
  - Operator views: saved views CRUD + query endpoints.

**Seeded fixtures + exceptions**
- Founder Day happy path + controlled failures toggled via Demo controls:
  - Missing supplier certification, quote above threshold, approver unavailable, carrier delay, offline pending sync.

**Frontend (React + shadcn/ui + Tailwind)**
- Global shell + branding:
  - “GPOS by Grahmos” + workspace header “Howard University · powered by Grahmos”.
  - Navy/Teal/Purple semantics; no white-label forks.
  - Demo Mode role switcher (clearly labeled).
- Implement flywheel screens (MVP fidelity, real data):
  - Grahmos Today (home), Decision Room, Campus Memory, Approval Center, Supplier 360,
    Student Work Board, Skills Passport & Career Launch, Impact Command Center.
- Operator control plane:
  - Airtable-style saved views (filter/sort/group), record drawer, policy-gated bulk actions.
- Deep-link notifications:
  - Simulated Slack/Telegram items that link into Decision Room/Supplier 360/Student Work.

**testing_agent_v3 todo (Phase 2)**
- E2E: Reset Demo → run full Founder Day flow → trigger each exception once → verify SoD blocks, audit trail shows evidence lineage, offline sync replays, retries are idempotent.

---

### Phase 3 — Stabilization + Coverage + UX polish
**User stories**
1. As an executive, I can view Impact metrics that reconcile to underlying cases and audit events.
2. As an approver, I can delegate with expiry and see it reflected in SoD checks.
3. As an operator, I can replay any simulated flow run idempotently after a failure.
4. As a user, I can search Campus Memory and open the evidence artifacts for past decisions.
5. As a supplier, I can view a limited Supplier portal view of required docs/status (demo-only).

**Steps**
- Harden schemas + validation: strict enums, required evidence, “facts vs inference” fields.
- Add conflict UI for offline sync + “policy changed while offline” block.
- Expand Acceptance Tests AT-01..AT-10 coverage in automated tests.
- Improve accessibility (WCAG 2.2 AA) on core paths + keyboard navigation.
- Add more seeded templates for the other Phase-1 lanes (IT/SaaS, Facilities+Microfactory, Classroom/Lab) using the same workflow engine.

**testing_agent_v3 todo (Phase 3)**
- Full regression: all screens + role switching + acceptance tests + malicious supplier content handling.

---

## 3) Next Actions
1. Create `/plan.md` (this file).
2. Phase 1: implement `AgentProvider` + schemas + `test_core.py`; run until green.
3. Once green: scaffold FastAPI/Mongo modules by extracting POC kernel into app.
4. Build frontend shell + Grahmos Today + Decision Room first; then add remaining screens.
5. Add demo fixtures + Reset/Jump/Audit endpoints and run full Golden Demo with exceptions.

## 4) Success Criteria
- `test_core.py` passes reliably: schema-valid LLM proposals; kernel blocks unauthorized transitions; SoD enforced; audit hash chain verifies; evidence lineage resolvable; offline sync dedupes.
- Founder Day Golden Demo runs end-to-end in UI with seeded exceptions and recovery.
- No “Accio”/“Activepieces” branding leaks; all surfaced as Grahmos-native objects.
- Operator views + approvals + learning loop update competencies only with supervisor attestation.
- One-click Reset + Jump-to-Stage + Show Audit Trail works for every demo run.
