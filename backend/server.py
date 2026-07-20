"""GPOS by Grahmos — FastAPI backend."""
import os
import logging
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, APIRouter, HTTPException, Body
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

import kernel as K
from kernel import PolicyError, append_audit, verify_chain, now_iso, new_id
import seed_data as SEED
from agents import run_live, SHARED_SYS

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="GPOS by Grahmos")
api = APIRouter(prefix="/api")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gpos")

PROJ = {"_id": 0}


# ==========================================================================
# Seeding
# ==========================================================================
async def do_seed():
    cols = SEED.all_collections()
    for name in list(cols.keys()) + ["audit_events", "session", "outbox",
                                      "flow_runs", "exceptions", "meetings", "overrides",
                                      "onboarding"]:
        await db[name].delete_many({})
    for name, docs in cols.items():
        if docs:
            await db[name].insert_many([dict(d) for d in docs])
    # session: current impersonated actor (Demo Mode) + agent mode
    await db.session.insert_one({"id": "session", "actor_id": "u_operator",
                                 "agent_mode": "seeded", "online": True,
                                 "exceptions": []})
    # genesis audit + seeded transition history for the golden case
    await append_audit(db, {"type": "DEMO_SEEDED", "actor": "system",
                            "case_id": None, "note": "Deterministic demo environment seeded"})
    await _replay_history("case_founderday", "APPROVAL_PENDING")


async def _replay_history(case_id, up_to_state):
    """Record audit events for transitions leading to the case's current state."""
    order = K.STATES
    target_idx = order.index(up_to_state)
    path = order[: target_idx + 1]
    prev = None
    for st in path:
        if prev is not None:
            await append_audit(db, {"type": "STATE_TRANSITION", "case_id": case_id,
                                    "actor": "u_operator", "from": prev, "to": st,
                                    "idempotency_key": f"seed-{case_id}-{st}",
                                    "note": K.STAGE_META[st]["blurb"]})
        prev = st
    await append_audit(db, {"type": "EVIDENCE_STORED", "case_id": case_id,
                            "actor": "Grahmos Assist", "artifact_id": "art_bison_quote",
                            "source": "accio://quote/bison-2026"})


async def get_session():
    s = await db.session.find_one({"id": "session"}, PROJ)
    if not s:
        await do_seed()
        s = await db.session.find_one({"id": "session"}, PROJ)
    return s


async def current_actor():
    s = await get_session()
    a = await db.actors.find_one({"id": s["actor_id"]}, PROJ)
    return a, s


# ==========================================================================
# Health + Institution + Demo Mode
# ==========================================================================
@api.get("/")
async def root():
    return {"app": "GPOS by Grahmos", "status": "ok"}


@api.get("/institution")
async def get_institution():
    inst = await db.institutions.find_one({}, PROJ)
    if not inst:
        await do_seed()
        inst = await db.institutions.find_one({}, PROJ)
    return inst


@api.get("/me")
async def me():
    a, s = await current_actor()
    return {"actor": a, "agent_mode": s["agent_mode"], "online": s["online"]}


@api.get("/demo/actors")
async def demo_actors():
    return await db.actors.find({}, PROJ).to_list(100)


class Impersonate(BaseModel):
    actor_id: str


@api.post("/demo/impersonate")
async def impersonate(body: Impersonate):
    a = await db.actors.find_one({"id": body.actor_id}, PROJ)
    if not a:
        raise HTTPException(404, "actor not found")
    await db.session.update_one({"id": "session"}, {"$set": {"actor_id": body.actor_id}})
    await append_audit(db, {"type": "DEMO_IMPERSONATE", "actor": body.actor_id,
                            "case_id": None, "role": a["role"]})
    return {"actor": a}


class AgentMode(BaseModel):
    mode: str  # "seeded" | "live"


@api.post("/demo/agent-mode")
async def set_agent_mode(body: AgentMode):
    await db.session.update_one({"id": "session"}, {"$set": {"agent_mode": body.mode}})
    return {"agent_mode": body.mode}


@api.post("/demo/reset")
async def demo_reset():
    await do_seed()
    return {"status": "reset", "ts": now_iso()}


class JumpStage(BaseModel):
    case_id: str = "case_founderday"
    state: str


@api.post("/demo/jump")
async def demo_jump(body: JumpStage):
    if body.state not in K.STATES:
        raise HTTPException(400, "invalid state")
    case = await db.cases.find_one({"id": body.case_id}, PROJ)
    if not case:
        raise HTTPException(404, "case not found")
    await db.cases.update_one({"id": body.case_id}, {"$set": {"state": body.state}})
    # sync approvals to a sensible status when jumping past approvals
    idx = K.STATES.index(body.state)
    if idx >= K.STATES.index("APPROVED"):
        await db.approvals.update_many({"case_id": body.case_id},
                                       {"$set": {"status": "APPROVED"}})
    await append_audit(db, {"type": "DEMO_JUMP", "actor": "system",
                            "case_id": body.case_id, "to": body.state})
    return {"case_id": body.case_id, "state": body.state}


@api.get("/demo/audit")
async def demo_audit(case_id: Optional[str] = None):
    q = {"case_id": case_id} if case_id else {}
    events = await db.audit_events.find(q, PROJ).sort("seq", 1).to_list(100000)
    ok, info = await verify_chain(db)
    return {"events": events, "chain_valid": ok, "verified_count": info}


EXCEPTIONS = {
    "missing_cert": {"label": "Missing supplier certification",
                     "detail": "MetroCater Collective has no verified liability-insurance COI. "
                               "Grahmos flagged the candidate; selection blocked pending evidence."},
    "over_threshold": {"label": "Quote above approval threshold",
                       "detail": "Selected package exceeds the requester's authority. Routed to "
                                 "Facilities → Finance → Procurement per policy-v3."},
    "approver_unavailable": {"label": "Approver unavailable",
                             "detail": "Finance approver is out-of-office; SLA at risk. "
                                       "Escalation + delegation path offered."},
    "carrier_delay": {"label": "Carrier delay",
                      "detail": "Grahmos Logistics reports a 2-day slip. Alternative delivery "
                                "window proposed; receiving checklist held."},
    "offline_pending": {"label": "Offline action pending sync",
                        "detail": "A receipt note was saved offline. It is queued and will "
                                  "reconcile idempotently on reconnect."},
}


class TriggerException(BaseModel):
    key: str
    case_id: str = "case_founderday"


@api.post("/demo/exception")
async def trigger_exception(body: TriggerException):
    if body.key not in EXCEPTIONS:
        raise HTTPException(400, "unknown exception")
    meta = EXCEPTIONS[body.key]
    rec = {"id": new_id("exc"), "key": body.key, "case_id": body.case_id,
           "label": meta["label"], "detail": meta["detail"], "ts": now_iso(),
           "resolved": False}
    await db.exceptions.insert_one(dict(rec))
    # side effects
    if body.key == "carrier_delay":
        await db.shipments.update_one({"case_id": body.case_id}, {"$set": {
            "status": "DELAYED", "eta": "2026-10-10",
        }, "$push": {"exceptions": "2-day carrier slip; alternate window proposed"}})
    if body.key == "approver_unavailable":
        await db.approvals.update_one({"case_id": body.case_id, "gate": "FINANCE"},
                                      {"$set": {"status": "AT_RISK"}})
    if body.key == "offline_pending":
        await db.session.update_one({"id": "session"}, {"$set": {"online": False}})
        await db.outbox.insert_one({"id": new_id("ob"), "case_id": body.case_id,
                                    "idempotency_key": f"off-{body.case_id}-recvnote",
                                    "action": "NOTE", "payload": "Receipt note (offline)",
                                    "policy_version": "policy-v3", "high_risk": False,
                                    "status": "PENDING", "ts": now_iso()})
    await append_audit(db, {"type": "EXCEPTION_INJECTED", "actor": "system",
                            "case_id": body.case_id, "key": body.key, "label": meta["label"]})
    rec.pop("_id", None)
    return rec


@api.get("/exceptions")
async def list_exceptions(case_id: Optional[str] = None):
    q = {"case_id": case_id} if case_id else {}
    return await db.exceptions.find(q, PROJ).sort("ts", -1).to_list(100)


# ==========================================================================
# Cases + timeline + transitions (kernel-authorized)
# ==========================================================================
@api.get("/cases")
async def list_cases(lane: Optional[str] = None):
    q = {"lane": lane} if lane else {}
    cases = await db.cases.find(q, PROJ).to_list(100)
    for c in cases:
        c["stage_meta"] = K.STAGE_META.get(c["state"], {})
    return cases


@api.get("/cases/{case_id}")
async def get_case(case_id: str):
    c = await db.cases.find_one({"id": case_id}, PROJ)
    if not c:
        raise HTTPException(404, "case not found")
    c["stage_meta"] = K.STAGE_META.get(c["state"], {})
    c["allowed_transitions"] = K.TRANSITIONS.get(c["state"], [])
    c["requester"] = await db.actors.find_one({"id": c.get("requester_id")}, PROJ)
    c["owner"] = await db.actors.find_one({"id": c.get("owner_id")}, PROJ)
    return c


@api.get("/cases/{case_id}/timeline")
async def case_timeline(case_id: str):
    events = await db.audit_events.find({"case_id": case_id}, PROJ).sort("seq", 1).to_list(10000)
    return {"stages": K.STATES, "stage_meta": K.STAGE_META, "events": events}


class TransitionBody(BaseModel):
    target: str
    idempotency_key: Optional[str] = None
    evidence_refs: Optional[List[str]] = None


@api.post("/cases/{case_id}/transition")
async def transition_case(case_id: str, body: TransitionBody):
    case = await db.cases.find_one({"id": case_id}, PROJ)
    if not case:
        raise HTTPException(404, "case not found")
    actor, _ = await current_actor()
    key = body.idempotency_key or new_id("k")
    # idempotency: same key already applied -> noop
    dup = await db.audit_events.find_one({"case_id": case_id, "type": "STATE_TRANSITION",
                                          "detail.idempotency_key": key})
    if dup:
        return {"case_id": case_id, "state": case["state"], "status": "IDEMPOTENT_NOOP"}
    try:
        K.validate_transition(case, body.target, body.evidence_refs)
    except PolicyError as e:
        await append_audit(db, {"type": "TRANSITION_BLOCKED", "actor": actor["id"],
                                "case_id": case_id, "reason": str(e), "target": body.target})
        raise HTTPException(422, str(e))
    await db.cases.update_one({"id": case_id}, {"$set": {"state": body.target}})
    await append_audit(db, {"type": "STATE_TRANSITION", "actor": actor["id"], "case_id": case_id,
                            "from": case["state"], "to": body.target, "idempotency_key": key,
                            "evidence_refs": body.evidence_refs or [],
                            "note": K.STAGE_META[body.target]["blurb"]})
    return {"case_id": case_id, "state": body.target, "status": "APPLIED"}


# ==========================================================================
# Suppliers / quotes / decision
# ==========================================================================
@api.get("/suppliers")
async def list_suppliers():
    return await db.suppliers.find({}, PROJ).to_list(100)


@api.get("/cases/{case_id}/suppliers")
async def case_suppliers(case_id: str):
    quotes = await db.quotes.find({"case_id": case_id}, PROJ).to_list(100)
    out = []
    for q in quotes:
        sup = await db.suppliers.find_one({"id": q["supplier_id"]}, PROJ)
        out.append({"supplier": sup, "quote": q})
    return out


@api.get("/cases/{case_id}/decision")
async def case_decision(case_id: str):
    dec = await db.decisions.find_one({"case_id": case_id}, PROJ)
    if not dec:
        raise HTTPException(404, "no decision")
    for opt in dec.get("options", []):
        opt["supplier"] = await db.suppliers.find_one({"id": opt["supplier_id"]}, PROJ)
    dec["recommended_supplier"] = await db.suppliers.find_one(
        {"id": dec.get("recommendation")}, PROJ)
    return dec


# ==========================================================================
# Approvals (SoD-enforced)
# ==========================================================================
@api.get("/approvals")
async def list_approvals(case_id: Optional[str] = None, approver_id: Optional[str] = None):
    q = {}
    if case_id:
        q["case_id"] = case_id
    if approver_id:
        q["approver_id"] = approver_id
    apprs = await db.approvals.find(q, PROJ).sort("order", 1).to_list(100)
    for a in apprs:
        a["approver"] = await db.actors.find_one({"id": a["approver_id"]}, PROJ)
        a["case"] = await db.cases.find_one({"id": a["case_id"]},
                                            {"_id": 0, "title": 1, "amount": 1, "state": 1,
                                             "requester_id": 1})
    return apprs


class ApprovalDecision(BaseModel):
    decision: str  # APPROVED | REJECTED
    rationale: Optional[str] = None


@api.post("/approvals/{approval_id}/decide")
async def decide_approval(approval_id: str, body: ApprovalDecision):
    appr = await db.approvals.find_one({"id": approval_id}, PROJ)
    if not appr:
        raise HTTPException(404, "approval not found")
    case = await db.cases.find_one({"id": appr["case_id"]}, PROJ)
    actor, _ = await current_actor()
    approver = await db.actors.find_one({"id": actor["id"]}, PROJ)

    # SoD + authority enforcement (deterministic)
    try:
        K.check_sod(case, appr["gate"], approver, threshold=5000.0)
        # the acting user must be the assigned approver for that gate
        if approver["id"] != appr["approver_id"]:
            raise PolicyError(
                f"Wrong approver: {appr['gate']} gate is assigned to another actor")
    except PolicyError as e:
        await append_audit(db, {"type": "APPROVAL_BLOCKED_SOD", "actor": approver["id"],
                                "case_id": case["id"], "gate": appr["gate"], "reason": str(e)})
        raise HTTPException(422, str(e))

    status = "APPROVED" if body.decision == "APPROVED" else "REJECTED"
    await db.approvals.update_one({"id": approval_id}, {"$set": {
        "status": status, "decided_at": now_iso(), "rationale": body.rationale}})
    await append_audit(db, {"type": f"APPROVAL_{status}", "actor": approver["id"],
                            "case_id": case["id"], "gate": appr["gate"],
                            "amount": case.get("amount"), "rationale": body.rationale})
    # unblock next gate in sequence
    nxt = await db.approvals.find_one({"case_id": case["id"], "order": appr["order"] + 1}, PROJ)
    if nxt and status == "APPROVED":
        await db.approvals.update_one({"id": nxt["id"]}, {"$set": {"status": "PENDING"}})
    # if all approved -> allow move to APPROVED
    remaining = await db.approvals.count_documents(
        {"case_id": case["id"], "status": {"$nin": ["APPROVED"]}})
    all_done = remaining == 0
    if all_done and case["state"] == "APPROVAL_PENDING":
        await db.cases.update_one({"id": case["id"]}, {"$set": {"state": "APPROVED"}})
        await append_audit(db, {"type": "STATE_TRANSITION", "actor": "system",
                                "case_id": case["id"], "from": "APPROVAL_PENDING",
                                "to": "APPROVED", "idempotency_key": new_id("k"),
                                "note": "All approval gates cleared"})
    return {"approval_id": approval_id, "status": status, "all_gates_cleared": all_done}


# ==========================================================================
# Grahmos Today (role-aware dashboard)
# ==========================================================================
@api.get("/today")
async def today():
    actor, s = await current_actor()
    cases = await db.cases.find({}, PROJ).to_list(100)
    pending = await db.approvals.count_documents({"status": "PENDING"})
    at_risk = await db.approvals.count_documents({"status": "AT_RISK"})
    active = len([c for c in cases if c["state"] not in ("CLOSED", "CANCELLED")])
    tasks = await db.learning_tasks.find({}, PROJ).to_list(50)
    notifs = await db.notifications.find({}, PROJ).sort("ts", -1).to_list(20)
    findings = [
        {"title": "Grahmos found 4 qualified suppliers", "case_id": "case_founderday",
         "detail": "Bison AV & Staging recommended; MetroCater flagged (missing COI).",
         "evidence": "Evidence captured from Accio", "kind": "sourcing"},
        {"title": "Grahmos Assist prepared this comparison", "case_id": "case_founderday",
         "detail": "Landed-cost normalized across 4 quotes incl. 1 EUR conversion.",
         "evidence": "Prepared by Grahmos Assist", "kind": "decision"},
        {"title": "Renewal savings detected", "case_id": "case_figma",
         "detail": "12 unused Adobe XD seats — consolidate to Figma Org.",
         "evidence": "Evidence captured from Accio", "kind": "savings"},
    ]
    return {
        "actor": actor,
        "kpis": {"pending_approvals": pending, "at_risk_slas": at_risk,
                 "active_cases": active,
                 "student_hours_week": SEED.IMPACT["kpis"]["paid_student_hours"] // 30},
        "my_queue": cases,
        "agent_findings": findings,
        "student_assignments": tasks,
        "notifications": notifs,
        "impact_snapshot": SEED.IMPACT["kpis"],
    }


# ==========================================================================
# Campus Memory / Impact / Flows / Notifications
# ==========================================================================
@api.get("/campus-memory")
async def campus_memory(q: Optional[str] = None, collection: Optional[str] = None):
    query = {}
    if collection and collection != "All":
        query["collection"] = collection
    docs = await db.campus_memory.find(query, PROJ).to_list(200)
    if q:
        ql = q.lower()
        docs = [d for d in docs if ql in d["title"].lower() or ql in d["body"].lower()
                or any(ql in t.lower() for t in d.get("tags", []))]
    collections = ["All", "Policies", "Contracts", "Decisions", "Suppliers", "Evidence"]
    return {"docs": docs, "collections": collections}


@api.get("/impact")
async def impact():
    return SEED.IMPACT


@api.get("/flows")
async def flows():
    return await db.flows.find({}, PROJ).to_list(50)


@api.get("/notifications")
async def notifications():
    return await db.notifications.find({}, PROJ).sort("ts", -1).to_list(50)


# ==========================================================================
# Student Work Board + Skills Passport + Learning loop
# ==========================================================================
@api.get("/student/tasks")
async def student_tasks():
    return await db.learning_tasks.find({}, PROJ).to_list(50)


@api.get("/student/tasks/{task_id}")
async def student_task(task_id: str):
    t = await db.learning_tasks.find_one({"id": task_id}, PROJ)
    if not t:
        raise HTTPException(404, "task not found")
    t["learner"] = await db.actors.find_one({"id": t["learner_id"]}, PROJ)
    t["supervisor"] = await db.actors.find_one({"id": t["supervisor_id"]}, PROJ)
    return t


class TaskAccept(BaseModel):
    task_id: str


@api.post("/student/tasks/accept")
async def accept_task(body: TaskAccept):
    await db.learning_tasks.update_one({"id": body.task_id},
                                       {"$set": {"status": "IN_PROGRESS"}})
    t = await db.learning_tasks.find_one({"id": body.task_id}, PROJ)
    t["stages"][0]["done"] = True
    await db.learning_tasks.update_one({"id": body.task_id}, {"$set": {"stages": t["stages"]}})
    await append_audit(db, {"type": "LEARNING_TASK_ACCEPTED", "actor": t["learner_id"],
                            "case_id": t["case_id"], "task": body.task_id})
    return {"status": "IN_PROGRESS"}


class QuizSubmit(BaseModel):
    task_id: str
    answers: List[int]


@api.post("/student/tasks/quiz")
async def submit_quiz(body: QuizSubmit):
    t = await db.learning_tasks.find_one({"id": body.task_id}, PROJ)
    if not t:
        raise HTTPException(404, "task not found")
    correct = sum(1 for i, qq in enumerate(t["quiz"])
                  if i < len(body.answers) and body.answers[i] == qq["answer"])
    passed = correct >= 2
    for st in t["stages"]:
        if st["key"] in ("teach", "check"):
            st["done"] = passed
        if st["key"] == "practice" and passed:
            st["done"] = True
    await db.learning_tasks.update_one({"id": body.task_id}, {"$set": {
        "stages": t["stages"], "quiz_score": correct,
        "status": "AWAITING_SUPERVISOR" if passed else "IN_PROGRESS",
        "hours_logged": 1.5 if passed else t.get("hours_logged", 0)}})
    await append_audit(db, {"type": "LEARNING_QUIZ_SUBMITTED", "actor": t["learner_id"],
                            "case_id": t["case_id"], "score": correct, "passed": passed})
    return {"correct": correct, "total": len(t["quiz"]), "passed": passed,
            "note": "Quiz passed — awaiting supervisor review. "
                    "Passing a quiz alone does NOT grant competency." if passed
                    else "Review the micro-lesson and try again."}


class Attest(BaseModel):
    task_id: str
    level: str = "Proficient"
    hours: float = 2.0


@api.post("/student/tasks/attest")
async def attest_task(body: Attest):
    actor, _ = await current_actor()
    t = await db.learning_tasks.find_one({"id": body.task_id}, PROJ)
    if not t:
        raise HTTPException(404, "task not found")
    # only a supervisor may attest competency (deterministic rule)
    if actor["role"] != "supervisor":
        await append_audit(db, {"type": "ATTEST_BLOCKED", "actor": actor["id"],
                                "case_id": t["case_id"],
                                "reason": "Only a supervisor may attest competency"})
        raise HTTPException(422, "Only a supervisor may attest competency (SoD).")
    if t.get("status") != "AWAITING_SUPERVISOR":
        raise HTTPException(422, "Task is not awaiting supervisor review.")
    for st in t["stages"]:
        st["done"] = True
    await db.learning_tasks.update_one({"id": body.task_id}, {"$set": {
        "stages": t["stages"], "status": "COMPLETED", "attested": True,
        "competency_result": body.level, "hours_logged": body.hours,
        "supervisor_attested_by": actor["id"]}})
    await db.competencies.update_one({"id": "comp_quote"}, {"$set": {
        "level": body.level, "verified": True, "hours": body.hours,
        "evidence_refs": ["art_bison_quote"]}})
    await append_audit(db, {"type": "COMPETENCY_ATTESTED", "actor": actor["id"],
                            "case_id": t["case_id"], "level": body.level, "hours": body.hours})
    return {"status": "COMPLETED", "competency": body.level, "verified": True}


@api.get("/student/passport")
async def passport(learner_id: str = "u_student"):
    comps = await db.competencies.find({"learner_id": learner_id}, PROJ).to_list(50)
    jobs = await db.job_opportunities.find({}, PROJ).to_list(50)
    tasks = await db.learning_tasks.find({"learner_id": learner_id}, PROJ).to_list(50)
    total_hours = sum(c.get("hours", 0) for c in comps)
    return {"competencies": comps, "opportunities": jobs, "tasks": tasks,
            "total_hours": total_hours,
            "learner": await db.actors.find_one({"id": learner_id}, PROJ)}


# ==========================================================================
# Offline queue + sync (deterministic, idempotent)
# ==========================================================================
@api.get("/offline/queue")
async def offline_queue():
    s = await get_session()
    items = await db.outbox.find({}, PROJ).sort("ts", 1).to_list(200)
    return {"online": s["online"], "queue": items}


class EnqueueBody(BaseModel):
    case_id: str
    action: str
    payload: Optional[str] = None
    high_risk: bool = False


@api.post("/offline/enqueue")
async def offline_enqueue(body: EnqueueBody):
    item = {"id": new_id("ob"), "case_id": body.case_id,
            "idempotency_key": new_id("off"), "action": body.action,
            "payload": body.payload, "policy_version": "policy-v3",
            "high_risk": body.high_risk, "status": "PENDING", "ts": now_iso()}
    await db.outbox.insert_one(dict(item))
    item.pop("_id", None)
    return item


@api.post("/offline/sync")
async def offline_sync():
    await db.session.update_one({"id": "session"}, {"$set": {"online": True}})
    inst = await db.institutions.find_one({}, PROJ)
    current_policy = inst["policy_version"]
    items = await db.outbox.find({"status": "PENDING"}, PROJ).sort("ts", 1).to_list(500)
    applied, deduped, blocked = [], [], []
    seen = set()
    for it in items:
        key = it["idempotency_key"]
        if key in seen:
            deduped.append(key)
            await db.outbox.update_one({"id": it["id"]}, {"$set": {"status": "DEDUPED"}})
            continue
        seen.add(key)
        if it.get("high_risk") and it.get("policy_version") != current_policy:
            blocked.append(key)
            await db.outbox.update_one({"id": it["id"]}, {"$set": {"status": "CONFLICT_STALE_POLICY"}})
            await append_audit(db, {"type": "SYNC_BLOCKED_STALE_POLICY", "actor": "system",
                                    "case_id": it["case_id"], "idempotency_key": key})
            continue
        applied.append(key)
        await db.outbox.update_one({"id": it["id"]}, {"$set": {"status": "APPLIED"}})
        await append_audit(db, {"type": "SYNC_APPLIED", "actor": "system",
                                "case_id": it["case_id"], "action": it["action"],
                                "idempotency_key": key})
    await append_audit(db, {"type": "WORKFLOW_RESUMED", "actor": "system", "case_id": None,
                            "note": "Workflow resumed after reconnecting"})
    return {"applied": applied, "deduped": deduped, "blocked": blocked,
            "message": "Workflow resumed after reconnecting."}


# ==========================================================================
# Operator saved views
# ==========================================================================
VIEW_DEFS = {
    "my_queue": {"label": "My Queue", "states": None},
    "needs_info": {"label": "Needs Info", "states": ["NEEDS_INFO", "DRAFT"]},
    "sourcing": {"label": "Sourcing", "states": ["SOURCING", "TRIAGED", "POLICY_PLANNED"]},
    "approval_aging": {"label": "Approval Aging", "states": ["APPROVAL_PENDING", "REVIEW_READY"]},
    "exceptions": {"label": "Exceptions", "states": None},
    "in_transit": {"label": "In Transit", "states": ["ORDERED", "IN_TRANSIT"]},
    "student_tasks": {"label": "Student Tasks", "states": None},
    "offline_conflicts": {"label": "Offline Conflicts", "states": None},
}


@api.get("/operator/views")
async def operator_views():
    counts = {}
    cases = await db.cases.find({}, PROJ).to_list(100)
    for key, d in VIEW_DEFS.items():
        if d["states"]:
            counts[key] = len([c for c in cases if c["state"] in d["states"]])
        elif key == "exceptions":
            counts[key] = await db.exceptions.count_documents({})
        elif key == "student_tasks":
            counts[key] = await db.learning_tasks.count_documents({})
        elif key == "offline_conflicts":
            counts[key] = await db.outbox.count_documents(
                {"status": {"$in": ["PENDING", "CONFLICT_STALE_POLICY"]}})
        else:
            counts[key] = len(cases)
    return {"views": [{"key": k, **v, "count": counts.get(k, 0)}
                      for k, v in VIEW_DEFS.items()]}


@api.get("/operator/view/{key}")
async def operator_view(key: str):
    d = VIEW_DEFS.get(key)
    if not d:
        raise HTTPException(404, "view not found")
    if key == "exceptions":
        return {"kind": "exceptions",
                "rows": await db.exceptions.find({}, PROJ).sort("ts", -1).to_list(100)}
    if key == "student_tasks":
        return {"kind": "tasks", "rows": await db.learning_tasks.find({}, PROJ).to_list(100)}
    if key == "offline_conflicts":
        return {"kind": "offline",
                "rows": await db.outbox.find({}, PROJ).sort("ts", -1).to_list(100)}
    cases = await db.cases.find({}, PROJ).to_list(100)
    if d["states"]:
        cases = [c for c in cases if c["state"] in d["states"]]
    for c in cases:
        c["stage_meta"] = K.STAGE_META.get(c["state"], {})
    return {"kind": "cases", "rows": cases}


# ==========================================================================
# Agents (proposal only; seeded default, live Claude toggle)
# ==========================================================================
AGENT_META = {
    "intake": {"name": "Intake + Decision Agent"},
    "research": {"name": "Procurement Research Agent"},
    "supplier": {"name": "Supplier Discovery / Vetting Agent"},
    "decision": {"name": "GPOS Team Lead"},
    "coach": {"name": "Learning Coach + Evidence Agent"},
}


def _seeded_proposal(agent_key, case):
    if agent_key == "intake":
        return {"category": case.get("category"), "risk": case.get("risk"),
                "normalized": case.get("request", {}).get("normalized", {}),
                "missing_fields": case.get("request", {}).get("missing_fields", []),
                "summary": "Normalized the request; missing material facts surfaced (not invented)."}
    if agent_key in ("supplier", "research"):
        return {"summary": "Grahmos found 4 qualified suppliers with normalized quotes.",
                "candidates": [q["supplier_id"] for q in SEED.QUOTES],
                "note": "MetroCater flagged: unresolved liability-insurance COI (unknown)."}
    if agent_key == "decision":
        return {"recommendation": SEED.DECISION["recommendation"],
                "rationale": SEED.DECISION["rationale"],
                "dissent": SEED.DECISION["dissent"], "unknowns": SEED.DECISION["unknowns"]}
    if agent_key == "coach":
        return {"lesson": "Landed cost = price + shipping + taxes + duties − substitutions.",
                "check": "Identify three missing fields in a sample quote.",
                "reminder": "Completion is not competence; supervisor attestation required."}
    return {"summary": "ok"}


class AgentRun(BaseModel):
    agent: str
    case_id: str = "case_founderday"


@api.post("/agents/run")
async def agents_run(body: AgentRun):
    if body.agent not in AGENT_META:
        raise HTTPException(400, "unknown agent")
    _, s = await current_actor()
    case = await db.cases.find_one({"id": body.case_id}, PROJ)
    seeded = _seeded_proposal(body.agent, case or {})
    provenance = {"mode": "seeded", "agent": AGENT_META[body.agent]["name"]}
    if s.get("agent_mode") == "live":
        schema = {"type": "object"}
        try:
            instruction = f"You are the {AGENT_META[body.agent]['name']}. " \
                          f"Produce a JSON proposal for case {body.case_id}."
            user = f"CASE:\n{str(case)[:3500]}\n\n{instruction}"
            data, model = await run_live(SHARED_SYS + " " + instruction, user, schema)
            return {"proposal": data, "provenance": {"mode": "live", "model": model,
                    "agent": AGENT_META[body.agent]["name"]}}
        except Exception as ex:
            provenance = {"mode": "seeded_fallback", "agent": AGENT_META[body.agent]["name"],
                          "error": str(ex)[:160]}
    await append_audit(db, {"type": "AGENT_RUN", "actor": "Grahmos Assist",
                            "case_id": body.case_id, "agent": body.agent,
                            "mode": provenance["mode"]})
    return {"proposal": seeded, "provenance": provenance}


# ==========================================================================
# PHASE 3 \u2014 Request Hub (intake), case lifecycle, governance depth
# ==========================================================================
LANE_TEMPLATES = {
    "EVENT": {"label": "Event Procurement", "icon": "calendar",
              "questions": ["Event date", "Expected attendees", "Venue / location",
                            "Budget estimate", "Dietary / accessibility needs", "Delivery window"],
              "why": "Events are date-bound and multi-stakeholder \u2014 these drive risk & approvals."},
    "IT_SAAS": {"label": "IT & SaaS", "icon": "monitor",
                "questions": ["Tool / software name", "Number of seats", "Annual budget",
                              "Data sensitivity", "Existing similar tools?"],
                "why": "IT spend is high and duplicated \u2014 we check for existing tools & renewals."},
    "FACILITIES": {"label": "Facilities & Microfactory", "icon": "wrench",
                   "questions": ["Part / equipment", "Building / room", "Failure symptom",
                                 "Budget estimate", "Safety-critical?"],
                   "why": "Facilities requests weigh repair vs buy vs local fabrication."},
    "CLASSROOM_LAB": {"label": "Classroom & Low-Risk Lab", "icon": "flask",
                      "questions": ["Item", "Quantity", "Standard / spec (e.g. ANSI)",
                                    "Budget estimate", "Needed by"],
                      "why": "High-volume, standardized items \u2014 great for bulk quotes."},
}


@api.get("/requests/templates")
async def request_templates():
    return {"lanes": [{"key": k, **v} for k, v in LANE_TEMPLATES.items()]}


class CreateRequest(BaseModel):
    lane: str
    title: str
    raw_text: str
    budget_amount: Optional[float] = None
    needed_by: Optional[str] = None
    location: Optional[str] = None
    quantity: Optional[str] = None


@api.post("/requests/preview")
async def request_preview(body: CreateRequest):
    """Intake normalization + duplicate-demand + existing-contract detection (no invention)."""
    missing = []
    tmpl = LANE_TEMPLATES.get(body.lane, {})
    if body.budget_amount is None:
        missing.append("budget estimate")
    if not body.needed_by:
        missing.append("needed-by date")
    if body.lane == "EVENT" and not body.location:
        missing.append("venue / location")
    # duplicate-demand detection (deterministic: same lane, similar words)
    existing = await db.cases.find({"lane": body.lane}, PROJ).to_list(100)
    words = set(body.title.lower().split())
    dupes = [c["title"] for c in existing
             if len(words & set(c["title"].lower().split())) >= 2]
    # existing-contract suggestion
    contracts = await db.campus_memory.find({"collection": "Contracts"}, PROJ).to_list(50)
    contract_hits = [c["title"] for c in contracts
                     if any(w in c["title"].lower() or w in c["body"].lower()
                            for w in words if len(w) > 3)]
    return {"category": body.lane, "risk": "MEDIUM" if body.lane in ("EVENT", "FACILITIES", "IT_SAAS") else "LOW",
            "missing_fields": missing, "duplicate_suggestions": dupes,
            "existing_contracts": contract_hits, "template": tmpl}


@api.post("/requests")
async def create_request(body: CreateRequest):
    actor, _ = await current_actor()
    preview = await request_preview(body)
    cid = new_id("case")
    state = "NEEDS_INFO" if preview["missing_fields"] else "TRIAGED"
    case = {"id": cid, "title": body.title, "lane": body.lane, "category": body.lane,
            "state": state, "risk": preview["risk"], "amount": body.budget_amount or 0,
            "currency": "USD", "requester_id": actor["id"], "owner_id": "u_operator",
            "sourcers": ["u_operator"], "policy_version": "policy-v3",
            "sla_due": None, "needed_by": body.needed_by, "created_at": now_iso(),
            "channel": "Web", "is_golden": False,
            "request": {"raw": body.raw_text, "category": body.lane, "risk": preview["risk"],
                        "normalized": {"budget_amount": body.budget_amount, "currency": "USD",
                                       "needed_by": body.needed_by, "location": body.location,
                                       "quantity_items": [{"item": body.quantity or "items", "qty": 1}]},
                        "missing_fields": preview["missing_fields"], "risk_flags": []}}
    await db.cases.insert_one(dict(case))
    await append_audit(db, {"type": "REQUEST_CREATED", "actor": actor["id"], "case_id": cid,
                            "note": f"Intake normalized \u2014 {state}", "channel": "Web"})
    if preview["missing_fields"]:
        await append_audit(db, {"type": "NEEDS_INFO", "actor": "Grahmos Assist", "case_id": cid,
                                "note": "Missing material facts \u2014 sourcing not started",
                                "missing": preview["missing_fields"]})
    case.pop("_id", None)
    return {"case": case, "preview": preview}


# ---- Meeting (F06): propose windows, consent gate before send ----
MEETING_WINDOWS = [
    {"id": "w1", "start": "2026-09-22T14:00:00Z", "label": "Mon Sep 22, 10:00 AM EDT"},
    {"id": "w2", "start": "2026-09-23T18:00:00Z", "label": "Tue Sep 23, 2:00 PM EDT"},
    {"id": "w3", "start": "2026-09-24T13:30:00Z", "label": "Wed Sep 24, 9:30 AM EDT"},
]


@api.get("/cases/{case_id}/meeting")
async def get_meeting(case_id: str):
    m = await db.meetings.find_one({"case_id": case_id}, PROJ)
    return m or {"case_id": case_id, "status": "NONE", "windows": [], "sent": False}


@api.post("/cases/{case_id}/meeting/propose")
async def propose_meeting(case_id: str):
    m = {"id": new_id("mtg"), "case_id": case_id, "status": "PROPOSED",
         "windows": MEETING_WINDOWS, "sent": False, "invite_id": None,
         "agenda": "Supplier clarification: catering capacity, delivery window, COI.",
         "ts": now_iso()}
    await db.meetings.update_one({"case_id": case_id}, {"$set": m}, upsert=True)
    await append_audit(db, {"type": "MEETING_PROPOSED", "actor": "Grahmos Assist",
                            "case_id": case_id, "note": "3 windows proposed (timezone-aware)"})
    m.pop("_id", None)
    return m


class MeetingSend(BaseModel):
    window_id: str
    send_authorized: bool = False


@api.post("/cases/{case_id}/meeting/send")
async def send_meeting(case_id: str, body: MeetingSend):
    if not body.send_authorized:
        raise HTTPException(422, "Consent required: send_authorized must be true before inviting.")
    actor, _ = await current_actor()
    invite = "invite_" + new_id("x").split("_")[1]
    await db.meetings.update_one({"case_id": case_id}, {"$set": {
        "status": "SENT", "sent": True, "invite_id": invite, "chosen_window": body.window_id}})
    await append_audit(db, {"type": "MEETING_SENT", "actor": actor["id"], "case_id": case_id,
                            "note": f"Invite sent after consent \u2014 provider id {invite}"})
    return {"status": "SENT", "invite_id": invite}


# ---- Contract (F07): clause matrix ----
@api.get("/cases/{case_id}/contract")
async def get_contract(case_id: str):
    return {"case_id": case_id, "prepared_by": "Grahmos Assist", "supplier": "Bison AV & Staging",
            "clauses": [
                {"clause": "Payment terms (Net-30)", "status": "acceptable"},
                {"clause": "Certificate of Insurance", "status": "acceptable"},
                {"clause": "Cancellation (72h)", "status": "deviation",
                 "note": "Supplier proposes 5-day cancellation vs 72h policy."},
                {"clause": "Data protection addendum", "status": "missing",
                 "note": "Not present \u2014 required for student data exposure."},
                {"clause": "Indemnification cap", "status": "legal_review",
                 "note": "Cap below institutional threshold \u2014 route to Legal."},
            ]}


# ---- Order Handoff (F08): mock PO/ERP ----
@api.post("/cases/{case_id}/order")
async def order_handoff(case_id: str):
    case = await db.cases.find_one({"id": case_id}, PROJ)
    if not case:
        raise HTTPException(404, "case not found")
    actor, _ = await current_actor()
    try:
        K.validate_transition(case, "ORDERED")
    except PolicyError as e:
        raise HTTPException(422, str(e))
    po = "PO-" + new_id("x").split("_")[1].upper()[:8]
    await db.cases.update_one({"id": case_id}, {"$set": {"state": "ORDERED", "po_ref": po,
                              "po_issuer_id": actor["id"]}})
    await db.shipments.update_one({"case_id": case_id}, {"$set": {"status": "ORDERED"}}, upsert=True)
    await append_audit(db, {"type": "ORDER_HANDOFF", "actor": actor["id"], "case_id": case_id,
                            "note": f"Mock ERP PO {po} created; supplier confirmation sent (sandbox)",
                            "idempotency_key": new_id("k"), "from": "APPROVED", "to": "ORDERED"})
    return {"po_ref": po, "state": "ORDERED"}


# ---- Logistics (F09) ----
@api.post("/cases/{case_id}/ship/advance")
async def ship_advance(case_id: str):
    case = await db.cases.find_one({"id": case_id}, PROJ)
    K.validate_transition(case, "IN_TRANSIT")
    await db.cases.update_one({"id": case_id}, {"$set": {"state": "IN_TRANSIT"}})
    await db.shipments.update_one({"case_id": case_id}, {"$set": {"status": "IN_TRANSIT"},
        "$push": {"events": {"ts": now_iso(), "event": "Picked up by Grahmos Logistics (sim)"}}}, upsert=True)
    await append_audit(db, {"type": "STATE_TRANSITION", "actor": "system", "case_id": case_id,
                            "from": "ORDERED", "to": "IN_TRANSIT", "idempotency_key": new_id("k"),
                            "note": "Logistics tracking active"})
    return {"state": "IN_TRANSIT"}


class Receive(BaseModel):
    checklist_confirmed: bool = False


@api.post("/cases/{case_id}/receive")
async def receive(case_id: str, body: Receive):
    if not body.checklist_confirmed:
        raise HTTPException(422, "Receiving requires a confirmed checklist (receiving evidence).")
    case = await db.cases.find_one({"id": case_id}, PROJ)
    art = "art_receipt_" + case_id[-6:]
    try:
        K.validate_transition(case, "RECEIVED", evidence_refs=[art])
    except PolicyError as e:
        raise HTTPException(422, str(e))
    await db.cases.update_one({"id": case_id}, {"$set": {"state": "RECEIVED"}})
    await db.shipments.update_one({"case_id": case_id}, {"$set": {"status": "RECEIVED"}})
    await db.artifacts.insert_one({"id": art, "case_id": case_id, "type": "receipt",
        "source": "Receiving checklist", "actor": (await current_actor())[0]["id"],
        "uri": f"artifact://{art}", "ts": now_iso(), "summary": "Signed receiving evidence."})
    await append_audit(db, {"type": "STATE_TRANSITION", "actor": (await current_actor())[0]["id"],
                            "case_id": case_id, "from": "IN_TRANSIT", "to": "RECEIVED",
                            "idempotency_key": new_id("k"), "evidence_refs": [art],
                            "note": "Delivery accepted with evidence"})
    return {"state": "RECEIVED", "evidence": art}


@api.post("/cases/{case_id}/close")
async def close_case(case_id: str):
    case = await db.cases.find_one({"id": case_id}, PROJ)
    K.validate_transition(case, "CLOSED")
    await db.cases.update_one({"id": case_id}, {"$set": {"state": "CLOSED"}})
    await append_audit(db, {"type": "STATE_TRANSITION", "actor": "system", "case_id": case_id,
                            "from": "RECEIVED", "to": "CLOSED", "idempotency_key": new_id("k"),
                            "note": "Case closed \u2014 supplier score & institutional memory updated"})
    await append_audit(db, {"type": "MEMORY_UPDATED", "actor": "Grahmos Assist", "case_id": case_id,
                            "note": "Decision, evidence & supplier performance saved to Campus Memory"})
    return {"state": "CLOSED"}


# ---- Buy / Make / Repair ----
@api.get("/cases/{case_id}/bmr")
async def get_bmr(case_id: str):
    case = await db.cases.find_one({"id": case_id}, {"_id": 0, "bmr": 1})
    if not case or not case.get("bmr"):
        raise HTTPException(404, "no buy/make/repair analysis for this case")
    return case["bmr"]


# ---- Override (reason + policy citation + expiry) ----
class Override(BaseModel):
    reason: str
    policy_id: str
    expiry: str


@api.post("/cases/{case_id}/override")
async def override_case(case_id: str, body: Override):
    if not (body.reason and body.policy_id and body.expiry):
        raise HTTPException(422, "Override requires reason, policy citation, and expiry.")
    actor, _ = await current_actor()
    rec = {"id": new_id("ovr"), "case_id": case_id, "actor": actor["id"], "reason": body.reason,
           "policy_id": body.policy_id, "expiry": body.expiry, "ts": now_iso()}
    await db.overrides.insert_one(dict(rec))
    await append_audit(db, {"type": "OVERRIDE", "actor": actor["id"], "case_id": case_id,
                            "reason": body.reason, "policy_id": body.policy_id, "expiry": body.expiry})
    rec.pop("_id", None)
    return rec


# ---- Delegation (approval with expiry) ----
class Delegate(BaseModel):
    to_actor_id: str
    expiry: str


@api.post("/approvals/{approval_id}/delegate")
async def delegate_approval(approval_id: str, body: Delegate):
    appr = await db.approvals.find_one({"id": approval_id}, PROJ)
    if not appr:
        raise HTTPException(404, "approval not found")
    actor, _ = await current_actor()
    to = await db.actors.find_one({"id": body.to_actor_id}, PROJ)
    if not to:
        raise HTTPException(404, "delegate actor not found")
    await db.approvals.update_one({"id": approval_id}, {"$set": {
        "approver_id": body.to_actor_id, "delegated_from": appr["approver_id"],
        "delegation_expiry": body.expiry}})
    await append_audit(db, {"type": "APPROVAL_DELEGATED", "actor": actor["id"],
                            "case_id": appr["case_id"], "gate": appr["gate"],
                            "to": body.to_actor_id, "expiry": body.expiry})
    return {"approval_id": approval_id, "delegated_to": to["name"], "expiry": body.expiry}


# ---- Flow replay (idempotent) ----
@api.post("/flows/{flow_id}/replay")
async def replay_flow(flow_id: str):
    f = await db.flows.find_one({"id": flow_id}, PROJ)
    if not f:
        raise HTTPException(404, "flow not found")
    await db.flows.update_one({"id": flow_id}, {"$set": {"status": "OK", "last_run": now_iso()},
                                                "$inc": {"runs": 1}})
    await append_audit(db, {"type": "FLOW_REPLAYED", "actor": "system", "case_id": None,
                            "note": f"{f['name']} ({flow_id}) replayed idempotently"})
    return {"flow_id": flow_id, "status": "OK", "runs": f["runs"] + 1}


# ---- Offline conflict resolve ----
class ResolveConflict(BaseModel):
    resolution: str  # "discard" | "refresh_and_apply"


@api.post("/offline/resolve/{item_id}")
async def resolve_conflict(item_id: str, body: ResolveConflict):
    it = await db.outbox.find_one({"id": item_id}, PROJ)
    if not it:
        raise HTTPException(404, "outbox item not found")
    status = "DISCARDED" if body.resolution == "discard" else "APPLIED"
    await db.outbox.update_one({"id": item_id}, {"$set": {"status": status}})
    await append_audit(db, {"type": "CONFLICT_RESOLVED", "actor": (await current_actor())[0]["id"],
                            "case_id": it["case_id"], "resolution": body.resolution,
                            "idempotency_key": it["idempotency_key"]})
    return {"item_id": item_id, "status": status}


# ==========================================================================
# PHASE 4 \u2014 Onboarding (Mobbin-grounded), admin config, supplier portal
# ==========================================================================
class OnboardingSave(BaseModel):
    track: str            # admin | requester | operator | student
    current_step: int
    data: Optional[dict] = None
    completed: bool = False


@api.get("/onboarding")
async def get_onboarding(track: str):
    doc = await db.onboarding.find_one({"track": track}, PROJ)
    return doc or {"track": track, "current_step": 0, "data": {}, "completed": False}


@api.post("/onboarding")
async def save_onboarding(body: OnboardingSave):
    doc = {"track": body.track, "current_step": body.current_step,
           "data": body.data or {}, "completed": body.completed, "ts": now_iso()}
    await db.onboarding.update_one({"track": body.track}, {"$set": doc}, upsert=True)
    if body.completed:
        await append_audit(db, {"type": "ONBOARDING_COMPLETED", "actor": "system",
                                "case_id": None, "track": body.track})
    return {"saved": True, **doc}


@api.get("/onboarding/status")
async def onboarding_status():
    tracks = ["admin", "requester", "operator", "student"]
    out = []
    for t in tracks:
        d = await db.onboarding.find_one({"track": t}, PROJ)
        out.append({"track": t, "current_step": d["current_step"] if d else 0,
                    "completed": d["completed"] if d else False})
    return {"tracks": out}


class InstitutionProfile(BaseModel):
    timezone: Optional[str] = None
    fiscal_year: Optional[str] = None
    campuses: Optional[str] = None
    launch_lanes: Optional[List[str]] = None


@api.post("/admin/institution")
async def update_institution(body: InstitutionProfile):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if updates:
        await db.institutions.update_one({}, {"$set": updates})
        await append_audit(db, {"type": "INSTITUTION_CONFIGURED", "actor": "u_executive",
                                "case_id": None, "fields": list(updates.keys())})
    return await db.institutions.find_one({}, PROJ)


@api.get("/supplier/portal")
async def supplier_portal(supplier_id: str = "sup_capital"):
    sup = await db.suppliers.find_one({"id": supplier_id}, PROJ)
    if not sup:
        raise HTTPException(404, "supplier not found")
    quotes = await db.quotes.find({"supplier_id": supplier_id}, PROJ).to_list(50)
    engagements = []
    for q in quotes:
        case = await db.cases.find_one({"id": q["case_id"]},
                                       {"_id": 0, "id": 1, "title": 1, "state": 1,
                                        "selected_supplier_id": 1})
        if case:
            engagements.append({
                "case": case, "quote": q,
                "selected": case.get("selected_supplier_id") == supplier_id,
                "quote_status": "Selected" if case.get("selected_supplier_id") == supplier_id
                                else "Under review"})
    # required documents / compliance (deterministic from certifications + unknowns)
    docs = [
        {"name": "Certificate of Insurance (COI)", "required": True,
         "status": "on_file" if "COI-Verified" in sup["certifications"] else "missing"},
        {"name": "W-9 Tax Form", "required": True, "status": "on_file"},
        {"name": "Diversity / MBE certification", "required": False,
         "status": "on_file" if sup.get("diverse") else "not_applicable"},
        {"name": "Food-safety (ServSafe)", "required": "Catering" in sup["capabilities"],
         "status": "on_file" if "ServSafe" in sup["certifications"] else "missing"},
    ]
    return {"supplier": sup, "engagements": engagements, "documents": docs,
            "unknowns": sup.get("unknowns", [])}


# ==========================================================================
app.include_router(api)
app.add_middleware(CORSMiddleware, allow_credentials=True,
                   allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
                   allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def startup():
    if await db.session.count_documents({}) == 0:
        await do_seed()
        logger.info("GPOS demo environment seeded on startup")


@app.on_event("shutdown")
async def shutdown():
    client.close()
