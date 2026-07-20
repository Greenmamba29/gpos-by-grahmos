"""
GPOS by Grahmos — CORE POC (isolation test)

Proves the critical build boundary works BEFORE building the full app:

    Real LLM reasoning  ->  schema-valid JSON proposals
                        ->  deterministic GPOS governance kernel (validates + executes)
                        ->  (simulated adapters would follow)

What this proves:
  A) AgentProvider (Claude Sonnet 4.5 primary, GPT-5 fallback) returns SCHEMA-VALID JSON for
     (1) intake normalization and (2) supplier discovery + quote normalization w/ evidence + unknowns.
  B) Deterministic kernel:
       - Idempotent state-machine transitions
       - Separation-of-Duties (blocks requester self-approval above threshold)
       - Approval threshold routing
       - Evidence lineage recorded + resolvable
       - Immutable append-only AUDIT HASH CHAIN (tamper-evident)
       - Offline outbox queue replays idempotently (dedupe by idempotency key)

Run:  cd /app/backend && python test_core.py
"""
import os
import sys
import json
import uuid
import hashlib
import asyncio
from datetime import datetime, timezone
from copy import deepcopy

from dotenv import load_dotenv
from jsonschema import validate as js_validate, ValidationError

load_dotenv()

from emergentintegrations.llm.chat import LlmChat, UserMessage

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")

# ---------------------------------------------------------------------------
# small print helpers
# ---------------------------------------------------------------------------
PASS, FAIL = "\033[92mPASS\033[0m", "\033[91mFAIL\033[0m"
results = []


def check(name, ok, detail=""):
    results.append((name, ok))
    tag = PASS if ok else FAIL
    print(f"  [{tag}] {name}" + (f"  --  {detail}" if detail else ""))
    return ok


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ===========================================================================
# A) AGENT PROVIDER  (model-neutral; Claude Sonnet 4.5 primary, GPT-5 fallback)
# ===========================================================================
PRIMARY = ("anthropic", "claude-sonnet-4-5-20250929")
FALLBACK = ("openai", "gpt-5")


class AgentProvider:
    """Model-neutral LLM interface that returns parsed, schema-validated JSON.
    The model *proposes*; it never mutates state."""

    def __init__(self, provider=PRIMARY[0], model=PRIMARY[1]):
        self.provider = provider
        self.model = model

    async def _raw(self, system_message: str, user_text: str) -> str:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"gpos-{uuid.uuid4()}",
            system_message=system_message,
        ).with_model(self.provider, self.model)
        resp = await chat.send_message(UserMessage(text=user_text))
        return resp if isinstance(resp, str) else str(resp)

    @staticmethod
    def _extract_json(text: str):
        text = text.strip()
        # strip markdown fences
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:]
        # take outermost braces
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON object found in model output")
        return json.loads(text[start:end + 1])

    async def propose(self, system_message: str, user_text: str, schema: dict, retries=2):
        """Call model; parse + schema-validate JSON. Falls back to secondary model."""
        last_err = None
        attempts = [(self.provider, self.model)] + [FALLBACK]
        json_instruction = (
            "\n\nReturn ONLY a single valid JSON object that conforms to the required schema. "
            "No prose, no markdown fences."
        )
        for (prov, mod) in attempts:
            self.provider, self.model = prov, mod
            for _ in range(retries):
                try:
                    raw = await self._raw(system_message, user_text + json_instruction)
                    data = self._extract_json(raw)
                    js_validate(instance=data, schema=schema)
                    return data, f"{prov}:{mod}"
                except (ValueError, ValidationError, json.JSONDecodeError) as e:
                    last_err = e
                    continue
        raise RuntimeError(f"AgentProvider failed schema-valid JSON: {last_err}")


# ---- Schemas -------------------------------------------------------------
SHARED_SYS = (
    "You are a GPOS procurement agent operating for Howard University. "
    "Separate verified facts, user statements, and inferences. Never fabricate suppliers, "
    "quotes, certifications, approvals, or shipment events. Preserve source references and "
    "timestamps for every material claim. Recommendations do NOT authorize spend."
)

REQUEST_SCHEMA = {
    "type": "object",
    "required": ["need", "category", "risk", "normalized", "missing_fields", "risk_flags"],
    "properties": {
        "need": {"type": "string"},
        "category": {"type": "string",
                     "enum": ["EVENT", "IT_SAAS", "FACILITIES", "CLASSROOM_LAB", "OTHER"]},
        "risk": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
        "normalized": {
            "type": "object",
            "required": ["budget_amount", "currency", "needed_by", "quantity_items"],
            "properties": {
                "budget_amount": {"type": ["number", "null"]},
                "currency": {"type": "string"},
                "needed_by": {"type": ["string", "null"]},
                "location": {"type": ["string", "null"]},
                "quantity_items": {"type": "array", "items": {"type": "object"}},
            },
        },
        "missing_fields": {"type": "array", "items": {"type": "string"}},
        "risk_flags": {"type": "array", "items": {"type": "string"}},
    },
}

SUPPLIERS_SCHEMA = {
    "type": "object",
    "required": ["candidates"],
    "properties": {
        "candidates": {
            "type": "array",
            "minItems": 3,
            "items": {
                "type": "object",
                "required": ["supplier_name", "quote", "evidence_refs", "unknowns"],
                "properties": {
                    "supplier_name": {"type": "string"},
                    "quote": {
                        "type": "object",
                        "required": ["currency", "total", "lead_time_days", "validity_days"],
                        "properties": {
                            "currency": {"type": "string"},
                            "total": {"type": "number"},
                            "lead_time_days": {"type": "number"},
                            "validity_days": {"type": "number"},
                            "line_items": {"type": "array"},
                        },
                    },
                    "certifications": {"type": "array", "items": {"type": "string"}},
                    "evidence_refs": {"type": "array", "minItems": 1,
                                      "items": {"type": "string"}},
                    "unknowns": {"type": "array", "items": {"type": "string"}},
                },
            },
        }
    },
}


async def poc_agents():
    print("\n=== A) LLM AgentProvider -> schema-valid JSON proposals ===")
    provider = AgentProvider()

    # (1) Intake normalization
    intake_user = (
        "Normalize this campus request into the Request schema. Mark any missing material "
        "fields explicitly; do NOT invent budget, date, or authority.\n\n"
        "REQUEST: \"We need AV, catering, and 150 chairs for Founder Day on Oct 10. "
        "Budget about $18k.\""
    )
    req, model_used = await provider.propose(SHARED_SYS, intake_user, REQUEST_SCHEMA)
    ok1 = check("Intake normalization returns schema-valid Request JSON", True,
                f"category={req.get('category')} risk={req.get('risk')} via {model_used}")
    ok2 = check("Missing material fields surfaced (venue/time/accessibility not invented)",
                len(req.get("missing_fields", [])) > 0,
                f"missing={req.get('missing_fields')}")

    # (2) Supplier discovery + quote normalization
    provider2 = AgentProvider()
    sup_user = (
        "Provide 3-5 realistic candidate suppliers for an event package (AV + catering + 150 "
        "chairs) near a US university for a ~$18,000 budget. Normalize each quote (currency, "
        "total, lead_time_days, validity_days). Every candidate MUST include evidence_refs "
        "(source URLs/artifact ids) and unknowns. Do NOT treat marketplace badges as verified "
        "certifications."
    )
    sup, model_used2 = await provider2.propose(SHARED_SYS, sup_user, SUPPLIERS_SCHEMA)
    cands = sup.get("candidates", [])
    ok3 = check("Supplier discovery returns >=3 candidates w/ normalized quotes", len(cands) >= 3,
                f"n={len(cands)} via {model_used2}")
    ok4 = check("Every candidate carries evidence_refs + unknowns (facts vs inference)",
                all(c.get("evidence_refs") and "unknowns" in c for c in cands))

    return {"request": req, "suppliers": sup} if all([ok1, ok2, ok3, ok4]) else None


# ===========================================================================
# B) DETERMINISTIC GPOS KERNEL
# ===========================================================================

STATES = ["DRAFT", "NEEDS_INFO", "TRIAGED", "POLICY_PLANNED", "SOURCING",
          "REVIEW_READY", "APPROVAL_PENDING", "APPROVED", "ORDERED",
          "IN_TRANSIT", "RECEIVED", "CLOSED"]
SIDE_STATES = ["ON_HOLD", "EXCEPTION", "CANCELLED"]
TRANSITIONS = {
    "DRAFT": ["NEEDS_INFO", "TRIAGED"],
    "NEEDS_INFO": ["TRIAGED"],
    "TRIAGED": ["POLICY_PLANNED"],
    "POLICY_PLANNED": ["SOURCING"],
    "SOURCING": ["REVIEW_READY"],
    "REVIEW_READY": ["APPROVAL_PENDING"],
    "APPROVAL_PENDING": ["APPROVED"],
    "APPROVED": ["ORDERED"],
    "ORDERED": ["IN_TRANSIT"],
    "IN_TRANSIT": ["RECEIVED"],
    "RECEIVED": ["CLOSED"],
}


class AuditChain:
    """Append-only, tamper-evident hash chain."""

    def __init__(self):
        self.events = []

    def append(self, event: dict):
        prev = self.events[-1]["hash"] if self.events else "GENESIS"
        payload = {**event, "prev_hash": prev, "ts": now_iso(),
                   "seq": len(self.events)}
        h = hashlib.sha256(
            (json.dumps(payload, sort_keys=True, default=str)).encode()).hexdigest()
        payload["hash"] = h
        self.events.append(payload)
        return payload

    def verify(self) -> bool:
        prev = "GENESIS"
        for e in self.events:
            body = {k: v for k, v in e.items() if k != "hash"}
            body["prev_hash"] = prev
            recomputed = hashlib.sha256(
                json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
            if recomputed != e["hash"] or e["prev_hash"] != prev:
                return False
            prev = e["hash"]
        return True


class PolicyError(Exception):
    pass


class GposKernel:
    """Deterministic authority: validates + executes every consequential transition."""

    def __init__(self):
        self.audit = AuditChain()
        self.evidence = {}          # artifact_id -> artifact
        self._applied_keys = set()  # idempotency keys already applied

    # -- evidence lineage ---------------------------------------------------
    def store_evidence(self, source, actor, content):
        artifact_id = "art_" + hashlib.sha256(
            f"{source}{content}".encode()).hexdigest()[:12]
        self.evidence[artifact_id] = {
            "artifact_id": artifact_id, "source": source, "actor": actor,
            "content_hash": hashlib.sha256(str(content).encode()).hexdigest(),
            "ts": now_iso(),
        }
        self.audit.append({"type": "EVIDENCE_STORED", "artifact_id": artifact_id,
                           "actor": actor, "source": source})
        return artifact_id

    def resolve_evidence(self, artifact_id):
        return self.evidence.get(artifact_id)

    # -- state machine ------------------------------------------------------
    def transition(self, case, target, actor, idempotency_key, evidence_refs=None):
        # idempotency: applying the same key twice is a no-op (offline-safe)
        if idempotency_key in self._applied_keys:
            return case, "IDEMPOTENT_NOOP"
        cur = case["state"]
        if target not in TRANSITIONS.get(cur, []):
            raise PolicyError(f"Illegal transition {cur} -> {target}")
        # evidence gate for receiving
        if target == "RECEIVED" and not evidence_refs:
            raise PolicyError("Cannot mark RECEIVED without receiving evidence")
        case["state"] = target
        self._applied_keys.add(idempotency_key)
        self.audit.append({"type": "STATE_TRANSITION", "case_id": case["id"],
                           "from": cur, "to": target, "actor": actor,
                           "idempotency_key": idempotency_key,
                           "evidence_refs": evidence_refs or []})
        return case, "APPLIED"

    # -- SoD + approval threshold ------------------------------------------
    def request_approval(self, case, gate, approver, threshold=5000.0):
        amount = case.get("amount", 0)
        # SoD: requester cannot be sole approver above threshold
        if amount > threshold and approver["id"] == case["requester_id"]:
            self.audit.append({"type": "APPROVAL_BLOCKED_SOD", "case_id": case["id"],
                               "gate": gate, "actor": approver["id"],
                               "reason": "requester cannot self-approve above threshold"})
            raise PolicyError("SoD violation: requester cannot self-approve above threshold")
        # SoD: sourcer cannot be sole selector
        if gate == "SELECTION" and approver["id"] in case.get("sourcers", []):
            raise PolicyError("SoD violation: sourcer cannot finalize selection alone")
        self.audit.append({"type": "APPROVAL_GRANTED", "case_id": case["id"],
                           "gate": gate, "approver": approver["id"], "amount": amount})
        return True

    # -- override (requires reason + policy citation + expiry) -------------
    def override(self, case, actor, reason, policy_id, expiry):
        if not (reason and policy_id and expiry):
            raise PolicyError("Override requires reason, policy citation, and expiry")
        self.audit.append({"type": "OVERRIDE", "case_id": case["id"], "actor": actor,
                           "reason": reason, "policy_id": policy_id, "expiry": expiry})
        return True


class OfflineOutbox:
    """Local queued writes; drains idempotently with dedupe."""

    def __init__(self):
        self.queue = []

    def enqueue(self, action):
        # idempotency key ensures dedupe on replay
        if "idempotency_key" not in action:
            action["idempotency_key"] = str(uuid.uuid4())
        self.queue.append(action)
        return action["idempotency_key"]

    def drain(self, kernel, case, policy_version_current):
        applied, skipped, blocked = [], [], []
        for action in self.queue:
            # policy freshness: block high-risk transition if snapshot stale
            if action.get("high_risk") and action.get("policy_version") != policy_version_current:
                blocked.append(action["idempotency_key"])
                kernel.audit.append({"type": "SYNC_BLOCKED_STALE_POLICY",
                                     "idempotency_key": action["idempotency_key"]})
                continue
            try:
                _, status = kernel.transition(
                    case, action["target"], action["actor"],
                    action["idempotency_key"], action.get("evidence_refs"))
                (applied if status == "APPLIED" else skipped).append(
                    action["idempotency_key"])
            except PolicyError:
                blocked.append(action["idempotency_key"])
        self.queue = []
        return applied, skipped, blocked


def poc_kernel(agent_output):
    print("\n=== B) Deterministic GPOS governance kernel ===")
    kernel = GposKernel()

    # evidence lineage from the LLM supplier proposal
    first_cand = agent_output["suppliers"]["candidates"][0]
    art_id = kernel.store_evidence(
        source=first_cand["evidence_refs"][0], actor="agent:supplier_discovery",
        content=first_cand)
    ok_ev = check("Evidence artifact stored + resolvable (lineage)",
                  kernel.resolve_evidence(art_id) is not None, art_id)

    # build a case from normalized proposal (amount from budget)
    amount = agent_output["request"]["normalized"].get("budget_amount") or 18000
    case = {"id": "case_" + uuid.uuid4().hex[:8], "state": "DRAFT",
            "requester_id": "user_requester", "amount": amount,
            "sourcers": ["user_operator"]}

    requester = {"id": "user_requester", "role": "requester"}
    finance = {"id": "user_finance", "role": "approver"}

    # Story 1 & 3: missing info -> NEEDS_INFO blocks sourcing until triaged (AT-01)
    kernel.transition(case, "NEEDS_INFO", "system", "k-needsinfo")
    ok_state = check("Case routed DRAFT -> NEEDS_INFO (missing fields, sourcing not started)",
                     case["state"] == "NEEDS_INFO")

    # idempotency: replaying same key is a no-op (AT-05 / AT-09)
    _, status_dup = kernel.transition(case, "NEEDS_INFO", "system", "k-needsinfo")
    ok_idem = check("Idempotent transition: duplicate key -> NOOP",
                    status_dup == "IDEMPOTENT_NOOP")

    # advance to approval stage
    for tgt, key in [("TRIAGED", "k1"), ("POLICY_PLANNED", "k2"),
                     ("SOURCING", "k3"), ("REVIEW_READY", "k4"),
                     ("APPROVAL_PENDING", "k5")]:
        kernel.transition(case, tgt, "user_operator", key)

    # SoD (AT-03): requester self-approval above threshold is BLOCKED
    self_approve_blocked = False
    try:
        kernel.request_approval(case, "FINANCE", requester, threshold=5000)
    except PolicyError:
        self_approve_blocked = True
    ok_sod = check("SoD: requester self-approval above threshold BLOCKED", self_approve_blocked)

    # Correct approver (Finance) succeeds
    ok_appr = check("Authorized approver (Finance) approval granted",
                    kernel.request_approval(case, "FINANCE", finance, threshold=5000))

    # illegal transition rejected
    illegal_blocked = False
    try:
        kernel.transition(case, "CLOSED", "user_operator", "k-illegal")
    except PolicyError:
        illegal_blocked = True
    ok_illegal = check("Illegal state jump rejected (APPROVAL_PENDING -> CLOSED)", illegal_blocked)

    # receiving without evidence blocked, with evidence allowed
    kernel.transition(case, "APPROVED", "user_finance", "k6")
    kernel.transition(case, "ORDERED", "user_operator", "k7")
    kernel.transition(case, "IN_TRANSIT", "system", "k8")
    recv_blocked = False
    try:
        kernel.transition(case, "RECEIVED", "user_operator", "k9-noev")
    except PolicyError:
        recv_blocked = True
    ok_recv = check("Receiving without evidence BLOCKED", recv_blocked)
    kernel.transition(case, "RECEIVED", "user_operator", "k9", evidence_refs=[art_id])
    ok_recv2 = check("Receiving WITH evidence allowed", case["state"] == "RECEIVED")

    # Offline outbox: enqueue + drain idempotently (AT-05, AT-06)
    outbox = OfflineOutbox()
    case2 = {"id": "case_off", "state": "APPROVED", "requester_id": "u", "amount": 1000}
    k = outbox.enqueue({"target": "ORDERED", "actor": "user_operator",
                        "policy_version": "v1"})
    outbox.enqueue({"target": "ORDERED", "actor": "user_operator",
                    "idempotency_key": k, "policy_version": "v1"})  # duplicate
    # stale policy high-risk action should be blocked
    outbox.enqueue({"target": "IN_TRANSIT", "actor": "system", "high_risk": True,
                    "policy_version": "v0"})
    applied, skipped, blocked = outbox.drain(kernel, case2, policy_version_current="v1")
    ok_sync = check("Offline sync: 1 applied, duplicate deduped, stale-policy high-risk blocked",
                    len(applied) == 1 and len(blocked) == 1,
                    f"applied={applied} skipped={skipped} blocked={blocked}")

    # Audit hash chain integrity (AT tamper-evident)
    ok_audit = check("Immutable audit hash-chain verifies", kernel.audit.verify(),
                     f"{len(kernel.audit.events)} events")
    # tamper detection
    tampered = deepcopy(kernel)
    if tampered.audit.events:
        tampered.audit.events[1]["actor"] = "HACKER"
    ok_tamper = check("Audit chain detects tampering", not tampered.audit.verify())

    return all([ok_ev, ok_state, ok_idem, ok_sod, ok_appr, ok_illegal, ok_recv,
                ok_recv2, ok_sync, ok_audit, ok_tamper])


# ===========================================================================
async def main():
    print("=" * 70)
    print("GPOS by Grahmos — CORE POC")
    print("=" * 70)
    if not EMERGENT_LLM_KEY:
        print("ERROR: EMERGENT_LLM_KEY missing")
        sys.exit(1)

    agent_output = await poc_agents()
    if not agent_output:
        print("\nAgent layer failed — stopping.")
        sys.exit(1)

    kernel_ok = poc_kernel(agent_output)

    print("\n" + "=" * 70)
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"RESULT: {passed}/{total} checks passed")
    print("=" * 70)
    sys.exit(0 if passed == total and kernel_ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
