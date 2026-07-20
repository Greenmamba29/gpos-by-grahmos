"""
GPOS governance kernel — the genuine deterministic authority layer.
Pure functions + a Mongo-backed audit hash chain. The LLM proposes; THIS executes.
"""
import json
import hashlib
import uuid
from datetime import datetime, timezone

# ---- Case state machine ---------------------------------------------------
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

STAGE_ORDER = {s: i for i, s in enumerate(STATES)}

# Human-facing stage metadata (Grahmos-native language)
STAGE_META = {
    "DRAFT": {"label": "Draft", "blurb": "Request captured"},
    "NEEDS_INFO": {"label": "Needs Info", "blurb": "Awaiting missing material facts"},
    "TRIAGED": {"label": "Triaged", "blurb": "Intent normalized"},
    "POLICY_PLANNED": {"label": "Policy Planned", "blurb": "Approval & SoD plan generated"},
    "SOURCING": {"label": "Sourcing", "blurb": "Grahmos is sourcing suppliers"},
    "REVIEW_READY": {"label": "Review Ready", "blurb": "Decision packet prepared"},
    "APPROVAL_PENDING": {"label": "Approval Pending", "blurb": "Approval workflow in progress"},
    "APPROVED": {"label": "Approved", "blurb": "Authorized to order"},
    "ORDERED": {"label": "Ordered", "blurb": "Purchase order issued"},
    "IN_TRANSIT": {"label": "In Transit", "blurb": "Logistics tracking active"},
    "RECEIVED": {"label": "Received", "blurb": "Delivery accepted with evidence"},
    "CLOSED": {"label": "Closed", "blurb": "Case closed; memory updated"},
}


class PolicyError(Exception):
    pass


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


# ---- Audit hash chain (tamper-evident) ------------------------------------
def compute_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


async def append_audit(db, event: dict):
    """Append an immutable, hash-chained audit event."""
    last = await db.audit_events.find_one({}, sort=[("seq", -1)], projection={"_id": 0})
    prev = last["hash"] if last else "GENESIS"
    seq = (last["seq"] + 1) if last else 0
    body = {
        "id": new_id("evt"),
        "seq": seq,
        "prev_hash": prev,
        "ts": now_iso(),
        "type": event.get("type"),
        "case_id": event.get("case_id"),
        "actor": event.get("actor"),
        "detail": {k: v for k, v in event.items()
                   if k not in ("type", "case_id", "actor")},
    }
    body["hash"] = compute_hash({k: v for k, v in body.items() if k != "hash"})
    await db.audit_events.insert_one(dict(body))
    body.pop("_id", None)
    return body


async def verify_chain(db):
    events = await db.audit_events.find({}, {"_id": 0}).sort("seq", 1).to_list(100000)
    prev = "GENESIS"
    for e in events:
        body = {k: v for k, v in e.items() if k != "hash"}
        if compute_hash(body) != e["hash"] or e["prev_hash"] != prev:
            return False, e["seq"]
        prev = e["hash"]
    return True, len(events)


# ---- Transition validation ------------------------------------------------
def can_transition(current: str, target: str) -> bool:
    return target in TRANSITIONS.get(current, [])


def validate_transition(case: dict, target: str, evidence_refs=None):
    cur = case["state"]
    if target in SIDE_STATES:
        return
    if not can_transition(cur, target):
        raise PolicyError(f"Illegal transition {cur} → {target}")
    if target == "RECEIVED" and not evidence_refs:
        raise PolicyError("Cannot mark RECEIVED without receiving evidence")
    if target == "SOURCING" and case.get("state") == "NEEDS_INFO":
        raise PolicyError("Cannot start sourcing while request NEEDS_INFO")


# ---- Separation of Duties -------------------------------------------------
def check_sod(case: dict, gate: str, approver: dict, threshold: float):
    """Raise PolicyError on any SoD violation. Deterministic authority."""
    amount = case.get("amount", 0) or 0
    # Requester cannot be sole approver above threshold
    if amount > threshold and approver["id"] == case.get("requester_id"):
        raise PolicyError("SoD: requester cannot self-approve above threshold")
    # Sourcer cannot finalize supplier selection alone
    if gate == "SELECTION" and approver["id"] in case.get("sourcers", []):
        raise PolicyError("SoD: sourcer cannot finalize supplier selection alone")
    # PO issuer cannot be sole receiver for controlled categories
    if gate == "RECEIPT" and approver["id"] == case.get("po_issuer_id") \
            and case.get("category") in ("FACILITIES", "CLASSROOM_LAB"):
        raise PolicyError("SoD: PO issuer cannot be sole receiver for controlled category")
    # Approver must have authority for this gate/threshold
    if amount > (approver.get("authority_threshold", 0) or 0):
        raise PolicyError(
            f"Authority: {approver.get('name')} threshold "
            f"${approver.get('authority_threshold',0):,.0f} < amount ${amount:,.0f}")


def evidence_id(source, content):
    return "art_" + hashlib.sha256(f"{source}{content}".encode()).hexdigest()[:12]
