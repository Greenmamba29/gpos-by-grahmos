"""
Seeded deterministic demo environment for GPOS by Grahmos.
Institution: Howard University · powered by Grahmos.
All 'agent findings' here are structured proposals the kernel later authorizes.
"""
from kernel import now_iso

INSTITUTION = {
    "id": "inst_howard",
    "name": "Howard University",
    "context_label": "Howard University · powered by Grahmos",
    "timezone": "America/New_York",
    "fiscal_year": "FY2026",
    "locales": ["en-US"],
    "policy_version": "policy-v3",
    "accent": "#0D9488",
}

# ---- Actors (Demo Mode identities) ----------------------------------------
ACTORS = [
    {"id": "u_requester", "name": "Dana Okafor", "role": "requester",
     "department": "Student Affairs", "authority_threshold": 0,
     "supervisor": None, "channel": "Slack", "avatar": "DO",
     "title": "Events Coordinator"},
    {"id": "u_operator", "name": "Morgan Reyes", "role": "operator",
     "department": "Procurement", "authority_threshold": 5000,
     "supervisor": None, "channel": "Slack", "avatar": "MR",
     "title": "Procurement Operator"},
    {"id": "u_finance", "name": "Riley Chen", "role": "approver",
     "department": "Finance", "authority_threshold": 50000,
     "supervisor": None, "channel": "Email", "avatar": "RC",
     "title": "Finance Approver", "gate": "FINANCE"},
    {"id": "u_facilities", "name": "Casey Boone", "role": "approver",
     "department": "Facilities", "authority_threshold": 30000,
     "supervisor": None, "channel": "Email", "avatar": "CB",
     "title": "Facilities Approver", "gate": "FACILITIES"},
    {"id": "u_proc_approver", "name": "Jordan Ellis", "role": "approver",
     "department": "Procurement", "authority_threshold": 40000,
     "supervisor": None, "channel": "Email", "avatar": "JE",
     "title": "Procurement Approver", "gate": "PROCUREMENT"},
    {"id": "u_student", "name": "Jamie Carter", "role": "student",
     "department": "Career Services", "authority_threshold": 0,
     "supervisor": "u_supervisor", "channel": "Telegram", "avatar": "JC",
     "title": "Student Fellow"},
    {"id": "u_supervisor", "name": "Alex Nguyen", "role": "supervisor",
     "department": "Procurement", "authority_threshold": 10000,
     "supervisor": None, "channel": "Slack", "avatar": "AN",
     "title": "Work-Learning Supervisor"},
    {"id": "u_executive", "name": "Dr. Taylor Brooks", "role": "executive",
     "department": "Executive Leadership", "authority_threshold": 100000,
     "supervisor": None, "channel": "Email", "avatar": "TB",
     "title": "VP Administration"},
    {"id": "u_supplier", "name": "Sam Rivera", "role": "supplier",
     "department": "Capital Event Group", "authority_threshold": 0,
     "supervisor": None, "channel": "Email", "avatar": "SR",
     "title": "Supplier Account Manager"},
]

# ---- Suppliers + normalized quotes (Founder Day event) --------------------
SUPPLIERS = [
    {"id": "sup_capital", "name": "Capital Event Group", "local": True, "diverse": False,
     "risk": "LOW", "performance": 92, "certifications": ["COI-Verified", "ServSafe"],
     "capabilities": ["AV", "Catering", "Furniture Rental"],
     "location": "Washington, DC", "on_time_rate": 0.96,
     "evidence_refs": ["accio://supplier/capital-event-group", "https://sam.gov/entity/CEG"],
     "unknowns": []},
    {"id": "sup_bison", "name": "Bison AV & Staging", "local": True, "diverse": True,
     "risk": "LOW", "performance": 88, "certifications": ["MBE-Certified", "COI-Verified"],
     "capabilities": ["AV", "Staging", "Lighting"],
     "location": "Washington, DC", "on_time_rate": 0.91,
     "evidence_refs": ["accio://supplier/bison-av", "https://mbe.dc.gov/bison"],
     "unknowns": ["catering_capacity"]},
    {"id": "sup_metro", "name": "MetroCater Collective", "local": False, "diverse": True,
     "risk": "MEDIUM", "performance": 79, "certifications": ["ServSafe"],
     "capabilities": ["Catering"], "location": "Baltimore, MD", "on_time_rate": 0.84,
     "evidence_refs": ["accio://supplier/metrocater"],
     "unknowns": ["liability_insurance_COI"]},  # -> triggers missing-cert exception
    {"id": "sup_atlantic", "name": "Atlantic Furnishings (EU)", "local": False, "diverse": False,
     "risk": "MEDIUM", "performance": 83, "certifications": ["ISO-9001"],
     "capabilities": ["Furniture Rental"], "location": "Dublin, IE", "on_time_rate": 0.81,
     "evidence_refs": ["accio://supplier/atlantic-eu"],
     "unknowns": ["import_lead_time"]},
]

# Normalized quotes (multi-currency to demo conversion provenance)
QUOTES = [
    {"id": "q_capital", "supplier_id": "sup_capital", "case_id": "case_founderday",
     "currency": "USD", "total": 17500, "total_usd": 17500, "lead_time_days": 12,
     "validity_days": 30, "moq": None, "shipping": 400, "taxes": 1100,
     "fx_source": None, "fx_ts": None,
     "line_items": [{"item": "AV package (stage, sound, screens)", "qty": 1, "unit": 6800},
                    {"item": "Catering (150 pax, plated)", "qty": 150, "unit": 62},
                    {"item": "Chairs (banquet)", "qty": 150, "unit": 8}],
     "evidence_refs": ["accio://quote/capital-2026", "artifact://quote-capital.pdf"]},
    {"id": "q_bison", "supplier_id": "sup_bison", "case_id": "case_founderday",
     "currency": "USD", "total": 18200, "total_usd": 18200, "lead_time_days": 8,
     "validity_days": 21, "moq": None, "shipping": 250, "taxes": 1200, "fx_source": None,
     "line_items": [{"item": "AV + staging + lighting", "qty": 1, "unit": 9200},
                    {"item": "Catering (partner)", "qty": 150, "unit": 55},
                    {"item": "Chairs (premium)", "qty": 150, "unit": 5}],
     "evidence_refs": ["accio://quote/bison-2026"]},
    {"id": "q_metro", "supplier_id": "sup_metro", "case_id": "case_founderday",
     "currency": "USD", "total": 16850, "total_usd": 16850, "lead_time_days": 10,
     "validity_days": 14, "moq": 100, "shipping": 300, "taxes": 950, "fx_source": None,
     "line_items": [{"item": "Catering (150 pax)", "qty": 150, "unit": 58},
                    {"item": "AV (subcontracted)", "qty": 1, "unit": 5200},
                    {"item": "Chairs (standard)", "qty": 150, "unit": 6}],
     "evidence_refs": ["accio://quote/metrocater-2026"]},
    {"id": "q_atlantic", "supplier_id": "sup_atlantic", "case_id": "case_founderday",
     "currency": "EUR", "total": 15200, "total_usd": 16480, "lead_time_days": 21,
     "validity_days": 30, "moq": 150, "shipping": 900, "taxes": 0,
     "fx_source": "ECB reference rate", "fx_ts": "2026-07-18T09:00:00Z", "fx_rate": 1.084,
     "line_items": [{"item": "Chairs + tables (import)", "qty": 150, "unit": 95}],
     "evidence_refs": ["accio://quote/atlantic-eu-2026"]},
]

# ---- Decision map (Founder Day) -------------------------------------------
DECISION = {
    "id": "dec_founderday", "case_id": "case_founderday",
    "criteria": [
        {"key": "landed_cost", "label": "Landed cost", "weight": 0.35},
        {"key": "lead_time", "label": "Lead time", "weight": 0.25},
        {"key": "diversity_local", "label": "Local / diverse", "weight": 0.20},
        {"key": "risk", "label": "Risk", "weight": 0.20},
    ],
    "options": [
        {"supplier_id": "sup_capital", "scores": {"landed_cost": 88, "lead_time": 82,
         "diversity_local": 70, "risk": 95}, "weighted": 85.6},
        {"supplier_id": "sup_bison", "scores": {"landed_cost": 80, "lead_time": 95,
         "diversity_local": 96, "risk": 92}, "weighted": 88.2},
        {"supplier_id": "sup_metro", "scores": {"landed_cost": 92, "lead_time": 86,
         "diversity_local": 78, "risk": 62}, "weighted": 80.4},
    ],
    "recommendation": "sup_bison",
    "rationale": ("Bison AV & Staging wins on lead time and diversity/local preference while "
                  "staying within budget. Capital Event Group is the low-risk runner-up. "
                  "MetroCater is cheapest but carries an unresolved liability-insurance unknown."),
    "prepared_by": "Grahmos Assist",
    "dissent": [{"who": "Facilities", "why": "Prefers single-vendor accountability (Capital)."}],
    "unknowns": ["Bison catering capacity for 150 plated covers unconfirmed."],
    "conflicts": [],
    "historical_note": "Last year's Founder Day used Capital at $19,400 for 130 attendees.",
    "vs_last_year": {"cost_delta_pct": -6.2, "attendees_delta": 20},
}

# ---- Approval gates (Founder Day: Facilities -> Finance -> Procurement) ----
APPROVALS = [
    {"id": "appr_fac", "case_id": "case_founderday", "gate": "FACILITIES", "order": 1,
     "approver_id": "u_facilities", "status": "PENDING", "sla_hours": 24,
     "decided_at": None, "conditions": None},
    {"id": "appr_fin", "case_id": "case_founderday", "gate": "FINANCE", "order": 2,
     "approver_id": "u_finance", "status": "BLOCKED", "sla_hours": 24,
     "decided_at": None, "conditions": None},
    {"id": "appr_proc", "case_id": "case_founderday", "gate": "PROCUREMENT", "order": 3,
     "approver_id": "u_proc_approver", "status": "BLOCKED", "sla_hours": 24,
     "decided_at": None, "conditions": None},
]

# ---- Cases: Founder Day (golden) + 3 lane templates -----------------------
def _base_request(cat, need, budget, needed_by, qty):
    return {"raw": need, "category": cat, "risk": "MEDIUM",
            "normalized": {"budget_amount": budget, "currency": "USD",
                           "needed_by": needed_by, "location": None, "quantity_items": qty},
            "missing_fields": [], "risk_flags": []}


CASES = [
    {"id": "case_founderday", "title": "Founder Day — AV, Catering & 150 Chairs",
     "lane": "EVENT", "category": "EVENT", "state": "APPROVAL_PENDING", "risk": "MEDIUM",
     "amount": 18200, "currency": "USD", "requester_id": "u_requester", "owner_id": "u_operator",
     "sourcers": ["u_operator"], "po_issuer_id": None, "policy_version": "policy-v3",
     "sla_due": "2026-10-03T17:00:00Z", "needed_by": "2026-10-10", "created_at": now_iso(),
     "channel": "Slack", "is_golden": True,
     "request": {"raw": "We need AV, catering, and 150 chairs for Founder Day on Oct 10. "
                 "Budget about $18k.",
                 "category": "EVENT", "risk": "MEDIUM",
                 "normalized": {"budget_amount": 18000, "currency": "USD",
                                "needed_by": "2026-10-10", "location": "Blackburn Center",
                                "quantity_items": [{"item": "chairs", "qty": 150},
                                                   {"item": "AV package", "qty": 1},
                                                   {"item": "catering covers", "qty": 150}]},
                 "missing_fields": ["start_time", "dietary_accessibility", "delivery_window"],
                 "risk_flags": ["date_bound", "multi_stakeholder"]},
     "selected_supplier_id": "sup_bison",
     "prepared_by": "Grahmos Assist"},

    {"id": "case_figma", "title": "Design Software Licenses (Figma Org, 40 seats)",
     "lane": "IT_SAAS", "category": "IT_SAAS", "state": "SOURCING", "risk": "MEDIUM",
     "amount": 21600, "currency": "USD", "requester_id": "u_requester", "owner_id": "u_operator",
     "sourcers": ["u_operator"], "policy_version": "policy-v3",
     "sla_due": "2026-08-01T17:00:00Z", "needed_by": "2026-08-15", "created_at": now_iso(),
     "channel": "Slack", "is_golden": False,
     "request": _base_request("IT_SAAS", "Need 40 Figma Org seats for the design program.",
                              21600, "2026-08-15", [{"item": "Figma Org seat", "qty": 40}]),
     "note": "Existing-tool check flagged 12 unused Adobe XD seats — renewal savings opportunity."},

    {"id": "case_hvac", "title": "HVAC Blower Motor — Repair vs Buy vs Microfactory",
     "lane": "FACILITIES", "category": "FACILITIES", "state": "REVIEW_READY", "risk": "MEDIUM",
     "amount": 3400, "currency": "USD", "requester_id": "u_requester", "owner_id": "u_operator",
     "sourcers": ["u_operator"], "policy_version": "policy-v3",
     "sla_due": "2026-07-25T17:00:00Z", "needed_by": "2026-07-30", "created_at": now_iso(),
     "channel": "Telegram", "is_golden": False,
     "request": _base_request("FACILITIES", "Blower motor failed in Douglass Hall AHU-3.",
                              3400, "2026-07-30", [{"item": "blower motor", "qty": 1}]),
     "bmr": {"buy": {"cost": 3400, "time_days": 6, "risk": "LOW"},
             "repair": {"cost": 1250, "time_days": 3, "risk": "MEDIUM"},
             "microfactory": {"cost": 620, "time_days": 2, "risk": "REVIEW_REQUIRED",
                              "note": "3D-printed housing bracket only; motor must be sourced."}}},

    {"id": "case_goggles", "title": "Bulk Lab Safety Goggles (600 units)",
     "lane": "CLASSROOM_LAB", "category": "CLASSROOM_LAB", "state": "TRIAGED", "risk": "LOW",
     "amount": 4200, "currency": "USD", "requester_id": "u_requester", "owner_id": "u_operator",
     "sourcers": ["u_operator"], "policy_version": "policy-v3",
     "sla_due": "2026-08-20T17:00:00Z", "needed_by": "2026-09-01", "created_at": now_iso(),
     "channel": "Slack", "is_golden": False,
     "request": _base_request("CLASSROOM_LAB", "600 ANSI Z87.1 safety goggles for chem labs.",
                              4200, "2026-09-01", [{"item": "safety goggles", "qty": 600}])},
]

# ---- Evidence artifacts ----------------------------------------------------
ARTIFACTS = [
    {"id": "art_intake", "case_id": "case_founderday", "type": "intake",
     "source": "Slack channel #procurement", "actor": "u_requester",
     "uri": "slack://msg/founderday-001", "ts": now_iso(),
     "summary": "Original request preserved verbatim from Slack."},
    {"id": "art_capital_quote", "case_id": "case_founderday", "type": "quote",
     "source": "accio://quote/capital-2026", "actor": "Grahmos Assist",
     "uri": "artifact://quote-capital.pdf", "ts": now_iso(),
     "summary": "Capital Event Group quote captured from Accio."},
    {"id": "art_bison_quote", "case_id": "case_founderday", "type": "quote",
     "source": "accio://quote/bison-2026", "actor": "Grahmos Assist",
     "uri": "artifact://quote-bison.pdf", "ts": now_iso(),
     "summary": "Bison AV & Staging quote captured from Accio."},
    {"id": "art_policy", "case_id": "case_founderday", "type": "policy_snapshot",
     "source": "Campus Policy Engine", "actor": "system",
     "uri": "policy://policy-v3", "ts": now_iso(),
     "summary": "Signed policy snapshot policy-v3 applied to case."},
]

# ---- Learning task (validate a supplier quote) ----------------------------
LEARNING_TASK = {
    "id": "lt_quote_validation", "case_id": "case_founderday",
    "title": "Validate a Supplier Quote", "competency": "Quote Normalization & Analysis",
    "learner_id": "u_student", "supervisor_id": "u_supervisor",
    "goal": "Learn to distinguish price from landed cost and validate a supplier quote.",
    "pay_rate": 18.0, "hours_logged": 0.0, "status": "AVAILABLE",
    "stages": [
        {"key": "orient", "label": "Orient", "done": False,
         "content": "Why quotes are normalized; price vs landed cost."},
        {"key": "teach", "label": "Micro-lesson", "done": False,
         "content": "MOQ, lead time, incoterms/shipping, validity, taxes, substitutions, certs."},
        {"key": "check", "label": "Knowledge check", "done": False},
        {"key": "practice", "label": "Supervised practice", "done": False},
        {"key": "supervise", "label": "Supervisor review", "done": False},
        {"key": "attest", "label": "Attestation", "done": False},
    ],
    "quiz": [
        {"q": "Which of these is NOT part of landed cost?",
         "options": ["Shipping", "Taxes", "Marketing badge", "Import duties"], "answer": 2},
        {"q": "A quote 'validity' of 14 days means:",
         "options": ["Delivery in 14 days", "Price guaranteed 14 days",
                     "14 day return window", "Payment due in 14 days"], "answer": 1},
        {"q": "Two quotes are in USD and EUR. To compare you must:",
         "options": ["Ignore FX", "Normalize with FX source + timestamp",
                     "Pick the lower number", "Ask the supplier"], "answer": 1},
    ],
    "rubric": [
        {"criterion": "Identified all landed-cost components", "max": 4},
        {"criterion": "Normalized multi-currency correctly", "max": 4},
        {"criterion": "Flagged missing evidence / unknowns", "max": 2},
    ],
    "evidence": [], "competency_result": None, "attested": False,
}

COMPETENCIES = [
    {"id": "comp_quote", "learner_id": "u_student", "name": "Quote Normalization & Analysis",
     "level": "In progress", "verified": False, "evidence_refs": [], "hours": 0.0},
    {"id": "comp_supplier", "learner_id": "u_student", "name": "Supplier Research",
     "level": "Beginner", "verified": True, "evidence_refs": ["art_bison_quote"], "hours": 6.5},
]

JOB_OPPORTUNITIES = [
    {"id": "job1", "title": "Procurement Analyst Intern", "employer": "Capital Event Group",
     "match": 86, "skills": ["Quote Normalization & Analysis", "Supplier Research"],
     "pay": "$22/hr", "type": "Internship"},
    {"id": "job2", "title": "Sourcing Associate", "employer": "Howard Procurement Office",
     "match": 74, "skills": ["Supplier Research", "Contract Basics"],
     "pay": "$25/hr", "type": "Part-time"},
]

# ---- Activepieces flow catalog (simulated, Grahmos-native) ----------------
FLOWS = [
    {"id": "F01", "name": "Channel Intake", "trigger": "message/webhook", "version": "1.4",
     "status": "OK", "runs": 12, "last_run": now_iso()},
    {"id": "F02", "name": "Policy Plan", "trigger": "request.created", "version": "1.2",
     "status": "OK", "runs": 12, "last_run": now_iso()},
    {"id": "F03", "name": "Sourcing", "trigger": "case.sourcing", "version": "2.0",
     "status": "OK", "runs": 9, "last_run": now_iso()},
    {"id": "F04", "name": "Human Review", "trigger": "review.ready", "version": "1.1",
     "status": "OK", "runs": 8, "last_run": now_iso()},
    {"id": "F05", "name": "Approvals", "trigger": "approval.requested", "version": "1.5",
     "status": "WAITING", "runs": 8, "last_run": now_iso()},
    {"id": "F06", "name": "Meeting", "trigger": "meeting.requested", "version": "1.0",
     "status": "OK", "runs": 4, "last_run": now_iso()},
    {"id": "F07", "name": "Contract", "trigger": "supplier.selected", "version": "1.1",
     "status": "OK", "runs": 3, "last_run": now_iso()},
    {"id": "F08", "name": "Order Handoff", "trigger": "case.approved", "version": "1.0",
     "status": "IDLE", "runs": 2, "last_run": now_iso()},
    {"id": "F09", "name": "Logistics", "trigger": "order.placed", "version": "1.2",
     "status": "IDLE", "runs": 2, "last_run": now_iso()},
    {"id": "F10", "name": "Learning", "trigger": "task.assignable", "version": "1.0",
     "status": "OK", "runs": 5, "last_run": now_iso()},
    {"id": "F11", "name": "Offline Sync", "trigger": "node.connected", "version": "1.0",
     "status": "OK", "runs": 7, "last_run": now_iso()},
    {"id": "F12", "name": "Close + Learn", "trigger": "receipt.accepted", "version": "1.0",
     "status": "IDLE", "runs": 1, "last_run": now_iso()},
]

# ---- Campus Memory (Notion-like institutional memory) ---------------------
CAMPUS_MEMORY = [
    {"id": "cm_policy_sod", "collection": "Policies", "title": "Separation of Duties Policy",
     "body": "Requester may not be sole approver above $5,000. Sourcer may not finalize "
             "supplier selection alone. PO issuer may not be sole receiver for controlled "
             "categories. All overrides require reason, policy citation, and expiry.",
     "tags": ["SoD", "governance"], "updated": now_iso(), "linked_cases": ["case_founderday"]},
    {"id": "cm_policy_thresholds", "collection": "Policies", "title": "Approval Thresholds",
     "body": "Facilities ≤ $30k · Finance ≤ $50k · Procurement ≤ $40k · Executive ≤ $100k. "
             "Events over $15k require Facilities → Finance → Procurement.",
     "tags": ["thresholds"], "updated": now_iso(), "linked_cases": ["case_founderday"]},
    {"id": "cm_dec_fd2025", "collection": "Decisions", "title": "Founder Day 2025 — Vendor Decision",
     "body": "Selected Capital Event Group at $19,400 for 130 attendees. On-time delivery; "
             "minor AV latency issue noted in receiving.",
     "tags": ["event", "history"], "updated": now_iso(), "linked_cases": []},
    {"id": "cm_contract_capital", "collection": "Contracts", "title": "Capital Event Group MSA",
     "body": "Master service agreement, COI on file, net-30 terms, cancellation 72h.",
     "tags": ["contract"], "updated": now_iso(), "linked_cases": ["case_founderday"]},
    {"id": "cm_sup_bison", "collection": "Suppliers", "title": "Bison AV & Staging — Profile",
     "body": "MBE-certified, local (DC). 91% on-time. Strong AV/staging; catering via partner.",
     "tags": ["supplier", "MBE"], "updated": now_iso(), "linked_cases": ["case_founderday"]},
    {"id": "cm_ev_bundle", "collection": "Evidence", "title": "Founder Day Evidence Bundle",
     "body": "Intake message, 4 supplier quotes, policy snapshot policy-v3, decision rationale.",
     "tags": ["evidence"], "updated": now_iso(), "linked_cases": ["case_founderday"]},
]

# ---- Impact Command Center metrics ----------------------------------------
IMPACT = {
    "kpis": {
        "avg_cycle_time_days": 4.2, "cycle_time_delta": -1.8,
        "savings_ytd": 128400, "savings_delta_pct": 12.4,
        "on_time_delivery": 0.93, "paid_student_hours": 512,
        "employment_conversions": 7, "policy_violations_prevented": 14,
    },
    "cycle_trend": [
        {"month": "Feb", "days": 7.1}, {"month": "Mar", "days": 6.4},
        {"month": "Apr", "days": 5.9}, {"month": "May", "days": 5.2},
        {"month": "Jun", "days": 4.7}, {"month": "Jul", "days": 4.2},
    ],
    "savings_by_lane": [
        {"lane": "Event", "savings": 41200}, {"lane": "IT & SaaS", "savings": 52800},
        {"lane": "Facilities", "savings": 22600}, {"lane": "Classroom/Lab", "savings": 11800},
    ],
    "supplier_perf": [
        {"supplier": "Capital Event Group", "score": 92, "on_time": 0.96},
        {"supplier": "Bison AV & Staging", "score": 88, "on_time": 0.91},
        {"supplier": "MetroCater Collective", "score": 79, "on_time": 0.84},
    ],
}

# ---- Notifications (channel deep-links; Grahmos is system of record) -------
NOTIFICATIONS = [
    {"id": "n1", "channel": "Slack", "actor": "u_operator",
     "text": "Grahmos found 4 qualified suppliers for Founder Day.",
     "deeplink": {"screen": "supplier360", "case_id": "case_founderday"}, "ts": now_iso(),
     "unread": True},
    {"id": "n2", "channel": "Email", "actor": "u_facilities",
     "text": "Approval workflow is waiting for Facilities.",
     "deeplink": {"screen": "approvals", "case_id": "case_founderday"}, "ts": now_iso(),
     "unread": True},
    {"id": "n3", "channel": "Telegram", "actor": "u_student",
     "text": "A paid quote-validation assignment is available.",
     "deeplink": {"screen": "student", "case_id": "case_founderday"}, "ts": now_iso(),
     "unread": True},
]

# ---- Shipment (used post-order) -------------------------------------------
SHIPMENT = {
    "id": "ship_fd", "case_id": "case_founderday", "carrier": "Grahmos Logistics (sim)",
    "status": "NOT_STARTED", "eta": "2026-10-08", "events": [], "exceptions": [],
    "receiving_checklist": [
        {"item": "AV package operational", "checked": False},
        {"item": "150 chairs counted", "checked": False},
        {"item": "Catering headcount confirmed", "checked": False},
    ]}


def all_collections():
    return {
        "institutions": [INSTITUTION],
        "actors": ACTORS,
        "suppliers": SUPPLIERS,
        "quotes": QUOTES,
        "decisions": [DECISION],
        "approvals": APPROVALS,
        "cases": CASES,
        "artifacts": ARTIFACTS,
        "learning_tasks": [LEARNING_TASK],
        "competencies": COMPETENCIES,
        "job_opportunities": JOB_OPPORTUNITIES,
        "flows": FLOWS,
        "campus_memory": CAMPUS_MEMORY,
        "notifications": NOTIFICATIONS,
        "shipments": [SHIPMENT],
    }
