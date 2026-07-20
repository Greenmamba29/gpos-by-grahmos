# GPOS by Grahmos — Demo Build Plan (FARM) **(Updated)**

## 1) Objectives
- ✅ Deliver a production-grade **Founder Day Golden Demo Run** with deterministic seeded fixtures, **8+ branded flywheel screens**, and **Demo Mode role-switching** (Howard University workspace).
- ✅ Ensure governance primitives are **genuine deterministic application code** (not mocked): **state machine, SoD, thresholds, immutable audit hash-chain, evidence lineage, offline queue+sync, retries/idempotency, operator controls, learning competency updates**.
- ✅ Implement the **core boundary** in a demo-safe way:
  - **Seeded findings mode (default)** for repeatable demos with no credit usage.
  - **Live AI toggle** (Claude Sonnet 4.5 primary, GPT-5 fallback) behind a model-neutral AgentProvider interface that **proposes schema-validated JSON only** and **never mutates workflow state**.
- 🎯 Phase 3 objective: optional hardening/polish (offline conflict UI, deeper lane flows, order/logistics surfaces, accessibility pass) + enable Live AI once key balance exists (zero rework).

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation) (must pass before app build)
**Status: COMPLETE (Kernel validated).**

**User stories**
1. As an operator, I can submit a plain-language Founder Day request and get a **schema-valid** normalized Request/Case proposal.
2. As the system, I reject any agent output that fails JSON schema validation or lacks evidence/unknowns.
3. As Finance, I can’t be self-approved by the requester when spend exceeds threshold (SoD enforced).
4. As an auditor, I can verify an **append-only audit chain** and trace each decision to evidence artifacts.
5. As a mobile user, I can create an action offline and see it **deduped + synchronized** later.

**Steps (performed)**
- Implemented minimal GPOS kernel (pure Python) proving deterministic governance:
  - State machine + idempotent `transition()`
  - SoD + role/authority + approval threshold checks
  - AuditEvent append-only **hash chain** (tamper-evident)
  - Evidence Artifact model + lineage links
  - Offline outbox replay + dedupe + stale-policy conflict block
- Created and executed `test_core.py` to validate kernel behavior.

**Phase 1 results**
- ✅ Deterministic governance kernel validated in isolation (11/11 checks):
  - state machine idempotency
  - SoD self-approval block
  - illegal transition reject
  - evidence gating
  - evidence lineage
  - offline dedupe + stale-policy high-risk block
  - tamper-evident audit hash chain
- ⚠️ Live LLM calls blocked by exhausted key budget ($1.25/$1.00). This does **not** block the demo: seeded mode is the Golden Demo default.

**testing_agent_v3 todo (Phase 1)**
- ✅ Completed via isolation testing + validation of kernel invariants.

---

### Phase 2 — V1 App Development (Backend + Frontend MVP)
**Status: COMPLETE and TESTED (testing_agent_v3 iteration_1: 100% backend 56/56, 100% frontend).**

**User stories**
1. As any role, I can open **Grahmos Today** and see my personalized “what needs attention” tiles.
2. As a requester, I can follow the Founder Day case in a **Decision Room** with rationale + deadlines.
3. As an approver, I can approve/deny in **Approval Center** with SoD/threshold context and evidence.
4. As an operator, I can run sourcing and review candidates in **Supplier 360** and publish a decision map.
5. As a student, I can complete a learning task and get competency updated only after supervisor attestation.

**Backend (FastAPI + Motor) — implemented**
- Seeded deterministic demo environment (Howard University):
  - 9 demo actors (Requester, Operator, Finance/Facilities/Procurement Approvers, Student, Supervisor, Executive, Supplier)
  - 4 cases: Founder Day golden + 3 Phase-1 lane templates (IT/SaaS, Facilities+Microfactory, Classroom/Lab)
  - 4 suppliers + normalized quotes (incl multi-currency EUR w/ FX source + timestamp)
  - Decision map w/ dissent + unknowns
  - 3 approval gates (Facilities → Finance → Procurement) w/ SoD enforcement
  - Evidence artifacts, campus memory docs, impact metrics, notifications, shipment fixture
  - 12 simulated flow records (Grahmos-native, no Accio/Activepieces branding)
- Genuine deterministic governance in `kernel.py`:
  - State machine validation
  - SoD/authority checks
  - Immutable audit hash-chain with verification endpoint
  - Evidence lineage + receiving evidence gate
- Agent layer in `agents.py`:
  - Model-neutral interface (Claude Sonnet 4.5 primary, GPT-5 fallback)
  - **Seeded mode default** + **live mode toggle** with graceful fallback when key budget is exhausted
  - Model outputs are proposals only; kernel validates/executes transitions
- API routes (`/api`) — implemented:
  - Demo Mode: `/me`, `/demo/impersonate`, `/demo/reset`, `/demo/jump`, `/demo/audit`, `/demo/exception`, `/demo/agent-mode`
  - Cases: list/get, timeline, transitions (legal transition enforcement + idempotency)
  - Approvals: queue + SoD-enforced decide + auto-unblock next gate + auto-transition to APPROVED when all gates clear
  - Suppliers/quotes/decision packet
  - Campus Memory, Impact, Flows, Notifications
  - Student learning loop (accept task, quiz, supervisor-only attestation, competency update)
  - Offline queue + sync (reconnect message: “Workflow resumed after reconnecting.”)
  - Operator saved views endpoints

**Seeded fixtures + exceptions — implemented**
- Founder Day happy path + controlled exceptions via Demo Controls:
  - Missing supplier certification
  - Quote above approval threshold
  - Approver unavailable
  - Carrier delay
  - Offline action pending sync

**Frontend (React + shadcn/ui + Tailwind) — implemented**
- Global shell + branding:
  - “GPOS by Grahmos” (Grahmos shield) + institution pill “Howard University · powered by Grahmos”
  - Navy/Teal/Purple semantics
  - Live AI toggle (seeded default)
  - Online/offline sync control
  - Demo Mode role switcher (clearly labeled)
  - Demo Controls drawer (Reset/Jump/Audit/Exception injection)
- Flywheel screens implemented (customer-facing experience layer):
  - Grahmos Today (home)
  - Decision Room (teal recommendation vs navy authorized decision separation + audit trail)
  - Approval Center (SoD + policy path)
  - Supplier 360 (comparison grid + FX normalization)
  - Campus Memory (search)
  - Student Work Board (learning loop + supervisor gate)
  - Skills Passport & Career Launch
  - Impact Command Center (recharts)
- Operator control plane:
  - Operator Workspace with saved views (cases, exceptions, student tasks, offline queue)
- Channel deep-link narrative:
  - Notifications simulate Slack/Telegram/Email as entry points but deep-link into Grahmos screens

**testing_agent_v3 todo (Phase 2)**
- ✅ Completed:
  - End-to-end approval sequence + SoD blocks
  - Audit hash chain verification
  - Offline sync + reconnection
  - Learning loop: quiz does not grant competency; supervisor attestation required
  - All 9 screens navigable; key interactions validated

---

### Phase 3 — Stabilization + Coverage + UX polish
**Status: OPTIONAL / NEXT (not required for the working demo; recommended hardening).**

**User stories**
1. As an executive, I can view Impact metrics that reconcile to underlying cases and audit events.
2. As an approver, I can delegate with expiry and see it reflected in SoD checks.
3. As an operator, I can replay any simulated flow run idempotently after a failure.
4. As a user, I can search Campus Memory and open the evidence artifacts for past decisions.
5. As a supplier, I can view a limited Supplier portal view of required docs/status (demo-only).

**Steps (revised based on current state)**
- **Live AI enablement (no rework):** once key balance exists, verify Claude Sonnet 4.5 live proposals and schema validation; keep seeded as demo default.
- **Offline conflict-resolution UI:** implement explicit conflict review for `CONFLICT_STALE_POLICY` and multi-write resolution.
- **Deeper lane templates:** add richer end-to-end flows and screens for IT/SaaS renewals, Facilities buy/make/repair, Classroom/Lab standardization.
- **Order/meeting/logistics UI surfaces:** add explicit “Order Handoff”, “Meeting Setup”, and “Logistics Tracking” panels (still simulated adapters) while keeping governance kernel authoritative.
- **Accessibility pass (WCAG 2.2 AA):** keyboard reachability for tables/drawers, focus management, contrast checks.
- **Test automation:** promote backend/UI tests into repeatable CI-like scripts (keep `backend_test.py`, extend coverage).

**testing_agent_v3 todo (Phase 3)**
- Run full regression including offline conflict UI, delegation, and deeper lane templates.

---

## 3) Next Actions
1. ✅ Confirm demo is stable and seeded: use **Demo Controls → Reset Demo** before each run.
2. (Optional) Add Universal Key balance and validate **Live AI toggle** behavior end-to-end (must remain “proposal only”).
3. Implement Phase 3 enhancements as needed: offline conflict UI, deeper lane flows, order/logistics/meeting surfaces, accessibility pass.

## 4) Success Criteria
- ✅ Governance kernel is deterministic and authoritative:
  - SoD enforced, thresholds enforced, illegal transitions blocked, receiving requires evidence, idempotency guaranteed.
- ✅ Immutable audit hash-chain verifies, and evidence lineage is visible.
- ✅ Founder Day Golden Demo runs end-to-end in UI with seeded exceptions and recovery.
- ✅ No “Accio”/“Activepieces” branding leaks; surfaced as Grahmos-native objects.
- ✅ Learning loop updates competencies only with supervisor attestation.
- ✅ One-click Reset + Jump-to-Stage + Show Audit Trail works for every demo run.
- 🎯 Optional: Live AI toggle works when key has balance, with schema-validated proposals and graceful fallback to seeded mode.
