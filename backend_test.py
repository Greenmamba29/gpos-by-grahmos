"""
GPOS by Grahmos — End-to-End Backend API Test

Tests all critical API endpoints with focus on deterministic governance kernel:
- Separation of Duties (SoD)
- Approval workflow sequence
- Immutable audit chain
- State machine transitions
- Offline sync
- Learning loop (student tasks + supervisor attestation)
- Demo controls

Run: python /app/backend_test.py
"""
import requests
import sys
from datetime import datetime

BASE_URL = "https://accio-flows.preview.emergentagent.com/api"

class Colors:
    PASS = "\033[92m✓\033[0m"
    FAIL = "\033[91m✗\033[0m"
    INFO = "\033[94mℹ\033[0m"
    WARN = "\033[93m⚠\033[0m"

class GPOSTester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def test(self, name, method, endpoint, expected_status, data=None, critical=False):
        """Run a single API test"""
        url = f"{BASE_URL}/{endpoint}"
        self.tests_run += 1
        
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"{Colors.PASS} {name}")
                return True, response.json() if response.text else {}
            else:
                print(f"{Colors.FAIL} {name}")
                print(f"  Expected {expected_status}, got {response.status_code}")
                if response.text:
                    print(f"  Response: {response.text[:200]}")
                if critical:
                    self.critical_failures.append(name)
                return False, {}
                
        except Exception as e:
            print(f"{Colors.FAIL} {name}")
            print(f"  Error: {str(e)}")
            if critical:
                self.critical_failures.append(name)
            return False, {}

    def impersonate(self, actor_id):
        """Helper to impersonate an actor"""
        success, resp = self.test(
            f"Impersonate {actor_id}",
            "POST",
            "demo/impersonate",
            200,
            {"actor_id": actor_id}
        )
        return success

def main():
    print("=" * 80)
    print("GPOS by Grahmos — Backend API Test Suite")
    print("=" * 80)
    print(f"Testing against: {BASE_URL}\n")
    
    tester = GPOSTester()
    
    # ========================================================================
    # 1. HEALTH & SEEDING
    # ========================================================================
    print("\n[1] Health & Seeding")
    print("-" * 80)
    tester.test("GET /api/ health check", "GET", "", 200, critical=True)
    tester.test("GET /api/institution", "GET", "institution", 200)
    
    # ========================================================================
    # 2. DEMO MODE & IMPERSONATION
    # ========================================================================
    print("\n[2] Demo Mode & Impersonation")
    print("-" * 80)
    success, me = tester.test("GET /api/me (current actor)", "GET", "me", 200, critical=True)
    if success:
        print(f"  {Colors.INFO} Current actor: {me.get('actor', {}).get('name')} ({me.get('actor', {}).get('role')})")
        print(f"  {Colors.INFO} Agent mode: {me.get('agent_mode')} | Online: {me.get('online')}")
    
    tester.test("GET /api/demo/actors", "GET", "demo/actors", 200)
    tester.impersonate("u_operator")
    
    # ========================================================================
    # 3. GRAHMOS TODAY (role-aware dashboard)
    # ========================================================================
    print("\n[3] Grahmos Today Dashboard")
    print("-" * 80)
    success, today = tester.test("GET /api/today", "GET", "today", 200, critical=True)
    if success:
        kpis = today.get("kpis", {})
        print(f"  {Colors.INFO} Pending approvals: {kpis.get('pending_approvals')}")
        print(f"  {Colors.INFO} Active cases: {kpis.get('active_cases')}")
        print(f"  {Colors.INFO} My queue: {len(today.get('my_queue', []))} cases")
        print(f"  {Colors.INFO} Agent findings: {len(today.get('agent_findings', []))}")
    
    # ========================================================================
    # 4. CASES & DECISION
    # ========================================================================
    print("\n[4] Cases & Decision Room")
    print("-" * 80)
    success, cases = tester.test("GET /api/cases", "GET", "cases", 200, critical=True)
    if success:
        print(f"  {Colors.INFO} Total cases: {len(cases)}")
    
    success, case = tester.test("GET /api/cases/case_founderday", "GET", "cases/case_founderday", 200, critical=True)
    if success:
        print(f"  {Colors.INFO} Case state: {case.get('state')}")
        print(f"  {Colors.INFO} Amount: ${case.get('amount')}")
        print(f"  {Colors.INFO} Allowed transitions: {case.get('allowed_transitions')}")
    
    success, decision = tester.test("GET /api/cases/case_founderday/decision", "GET", "cases/case_founderday/decision", 200, critical=True)
    if success:
        print(f"  {Colors.INFO} Recommendation: {decision.get('recommendation')}")
        print(f"  {Colors.INFO} Options: {len(decision.get('options', []))}")
    
    success, suppliers = tester.test("GET /api/cases/case_founderday/suppliers", "GET", "cases/case_founderday/suppliers", 200, critical=True)
    if success:
        print(f"  {Colors.INFO} Suppliers: {len(suppliers)}")
        # Check for EUR conversion
        for s in suppliers:
            quote = s.get("quote", {})
            if quote.get("currency") == "EUR":
                print(f"  {Colors.INFO} EUR quote found: fx_source={quote.get('fx_source')}, fx_rate={quote.get('fx_rate')}")
    
    # ========================================================================
    # 5. SEPARATION OF DUTIES (CRITICAL)
    # ========================================================================
    print("\n[5] Separation of Duties (SoD) — CRITICAL")
    print("-" * 80)
    
    # Reset to known state first
    tester.test("POST /api/demo/reset", "POST", "demo/reset", 200)
    
    # Get approval gates
    success, approvals = tester.test("GET /api/approvals?case_id=case_founderday", "GET", "approvals?case_id=case_founderday", 200)
    if success:
        print(f"  {Colors.INFO} Approval gates: {len(approvals)}")
        for appr in approvals:
            print(f"    - {appr.get('gate')}: {appr.get('status')} (approver: {appr.get('approver_id')})")
    
    # TEST: Requester cannot self-approve (SoD violation)
    tester.impersonate("u_requester")
    success, resp = tester.test(
        "SoD: Requester self-approval BLOCKED (422)",
        "POST",
        "approvals/appr_fac/decide",
        422,
        {"decision": "APPROVED", "rationale": "Looks good"},
        critical=True
    )
    if success:
        print(f"  {Colors.PASS} SoD correctly blocked requester self-approval")
    
    # TEST: Wrong approver acting on gate assigned to someone else
    tester.impersonate("u_finance")
    success, resp = tester.test(
        "SoD: Wrong approver on Facilities gate BLOCKED (422)",
        "POST",
        "approvals/appr_fac/decide",
        422,
        {"decision": "APPROVED", "rationale": "Approved"},
        critical=True
    )
    if success:
        print(f"  {Colors.PASS} SoD correctly blocked wrong approver")
    
    # TEST: Correct approver (Facilities) approves
    tester.impersonate("u_facilities")
    success, resp = tester.test(
        "Facilities approver approves appr_fac (200)",
        "POST",
        "approvals/appr_fac/decide",
        200,
        {"decision": "APPROVED", "rationale": "Facilities approved"},
        critical=True
    )
    if success:
        print(f"  {Colors.PASS} Facilities approval succeeded")
        print(f"  {Colors.INFO} All gates cleared: {resp.get('all_gates_cleared')}")
    
    # ========================================================================
    # 6. APPROVAL SEQUENCE (Finance gate should unblock after Facilities)
    # ========================================================================
    print("\n[6] Approval Workflow Sequence")
    print("-" * 80)
    success, approvals = tester.test("GET /api/approvals?case_id=case_founderday", "GET", "approvals?case_id=case_founderday", 200)
    if success:
        finance_gate = next((a for a in approvals if a.get("gate") == "FINANCE"), None)
        if finance_gate:
            print(f"  {Colors.INFO} Finance gate status after Facilities approval: {finance_gate.get('status')}")
            if finance_gate.get("status") == "PENDING":
                print(f"  {Colors.PASS} Finance gate correctly unblocked")
            else:
                print(f"  {Colors.WARN} Finance gate should be PENDING, got {finance_gate.get('status')}")
    
    # Approve Finance gate
    tester.impersonate("u_finance")
    tester.test(
        "Finance approver approves appr_fin",
        "POST",
        "approvals/appr_fin/decide",
        200,
        {"decision": "APPROVED", "rationale": "Finance approved"}
    )
    
    # Approve Procurement gate
    tester.impersonate("u_proc_approver")
    success, resp = tester.test(
        "Procurement approver approves appr_proc",
        "POST",
        "approvals/appr_proc/decide",
        200,
        {"decision": "APPROVED", "rationale": "Procurement approved"}
    )
    if success and resp.get("all_gates_cleared"):
        print(f"  {Colors.PASS} All approval gates cleared")
    
    # Check if case transitioned to APPROVED
    success, case = tester.test("GET /api/cases/case_founderday", "GET", "cases/case_founderday", 200)
    if success:
        if case.get("state") == "APPROVED":
            print(f"  {Colors.PASS} Case automatically transitioned to APPROVED")
        else:
            print(f"  {Colors.WARN} Case state: {case.get('state')} (expected APPROVED)")
    
    # ========================================================================
    # 7. IMMUTABLE AUDIT CHAIN
    # ========================================================================
    print("\n[7] Immutable Audit Chain")
    print("-" * 80)
    success, audit = tester.test("GET /api/demo/audit?case_id=case_founderday", "GET", "demo/audit?case_id=case_founderday", 200, critical=True)
    if success:
        print(f"  {Colors.INFO} Audit events: {len(audit.get('events', []))}")
        print(f"  {Colors.INFO} Chain valid: {audit.get('chain_valid')}")
        print(f"  {Colors.INFO} Verified count: {audit.get('verified_count')}")
        if audit.get("chain_valid"):
            print(f"  {Colors.PASS} Audit chain integrity verified")
    
    # ========================================================================
    # 8. STATE MACHINE TRANSITIONS
    # ========================================================================
    print("\n[8] State Machine Transitions")
    print("-" * 80)
    
    # Reset and jump to SOURCING
    tester.test("POST /api/demo/reset", "POST", "demo/reset", 200)
    tester.test("POST /api/demo/jump to SOURCING", "POST", "demo/jump", 200, {"case_id": "case_founderday", "state": "SOURCING"})
    
    # Legal transition
    tester.impersonate("u_operator")
    success, resp = tester.test(
        "Legal transition SOURCING -> REVIEW_READY",
        "POST",
        "cases/case_founderday/transition",
        200,
        {"target": "REVIEW_READY", "idempotency_key": "test-legal-1"}
    )
    if success:
        print(f"  {Colors.INFO} Status: {resp.get('status')}")
    
    # Idempotency test
    success, resp = tester.test(
        "Idempotent transition (same key)",
        "POST",
        "cases/case_founderday/transition",
        200,
        {"target": "REVIEW_READY", "idempotency_key": "test-legal-1"}
    )
    if success and resp.get("status") == "IDEMPOTENT_NOOP":
        print(f"  {Colors.PASS} Idempotency correctly handled")
    
    # Illegal transition
    success, resp = tester.test(
        "Illegal transition REVIEW_READY -> CLOSED (422)",
        "POST",
        "cases/case_founderday/transition",
        422,
        {"target": "CLOSED", "idempotency_key": "test-illegal-1"}
    )
    if success:
        print(f"  {Colors.PASS} Illegal transition correctly blocked")
    
    # ========================================================================
    # 9. OFFLINE SYNC
    # ========================================================================
    print("\n[9] Offline Sync")
    print("-" * 80)
    
    # Trigger offline_pending exception
    success, exc = tester.test(
        "POST /api/demo/exception (offline_pending)",
        "POST",
        "demo/exception",
        200,
        {"key": "offline_pending", "case_id": "case_founderday"}
    )
    if success:
        print(f"  {Colors.INFO} Exception: {exc.get('label')}")
    
    # Check session is offline
    success, me = tester.test("GET /api/me", "GET", "me", 200)
    if success:
        print(f"  {Colors.INFO} Online status: {me.get('online')}")
    
    # Check outbox queue
    success, queue = tester.test("GET /api/offline/queue", "GET", "offline/queue", 200)
    if success:
        print(f"  {Colors.INFO} Outbox queue: {len(queue.get('queue', []))} items")
    
    # Sync
    success, sync = tester.test("POST /api/offline/sync", "POST", "offline/sync", 200, critical=True)
    if success:
        print(f"  {Colors.INFO} Applied: {len(sync.get('applied', []))}")
        print(f"  {Colors.INFO} Deduped: {len(sync.get('deduped', []))}")
        print(f"  {Colors.INFO} Blocked: {len(sync.get('blocked', []))}")
        print(f"  {Colors.INFO} Message: {sync.get('message')}")
        if sync.get("message") == "Workflow resumed after reconnecting.":
            print(f"  {Colors.PASS} Offline sync message correct")
    
    # ========================================================================
    # 10. DEMO CONTROLS (exceptions)
    # ========================================================================
    print("\n[10] Demo Controls & Exceptions")
    print("-" * 80)
    
    exception_keys = ["missing_cert", "over_threshold", "approver_unavailable", "carrier_delay"]
    for key in exception_keys:
        tester.test(
            f"POST /api/demo/exception ({key})",
            "POST",
            "demo/exception",
            200,
            {"key": key, "case_id": "case_founderday"}
        )
    
    success, exceptions = tester.test("GET /api/exceptions?case_id=case_founderday", "GET", "exceptions?case_id=case_founderday", 200)
    if success:
        print(f"  {Colors.INFO} Total exceptions: {len(exceptions)}")
    
    # ========================================================================
    # 11. LEARNING LOOP (Student Tasks + Supervisor Attestation)
    # ========================================================================
    print("\n[11] Learning Loop (Student Tasks)")
    print("-" * 80)
    
    # Reset to get fresh task
    tester.test("POST /api/demo/reset", "POST", "demo/reset", 200)
    
    success, tasks = tester.test("GET /api/student/tasks", "GET", "student/tasks", 200, critical=True)
    if success:
        print(f"  {Colors.INFO} Student tasks: {len(tasks)}")
        if tasks:
            task_id = tasks[0].get("id")
            print(f"  {Colors.INFO} Task ID: {task_id}")
            
            # Accept task
            tester.impersonate("u_student")
            tester.test(
                "POST /api/student/tasks/accept",
                "POST",
                "student/tasks/accept",
                200,
                {"task_id": task_id}
            )
            
            # Submit quiz (correct answers: [2, 1, 1])
            success, quiz = tester.test(
                "POST /api/student/tasks/quiz (correct answers)",
                "POST",
                "student/tasks/quiz",
                200,
                {"task_id": task_id, "answers": [2, 1, 1]}
            )
            if success:
                print(f"  {Colors.INFO} Quiz passed: {quiz.get('passed')}")
                print(f"  {Colors.INFO} Score: {quiz.get('correct')}/{quiz.get('total')}")
            
            # Try to attest as non-supervisor (should fail)
            success, resp = tester.test(
                "POST /api/student/tasks/attest as non-supervisor (422)",
                "POST",
                "student/tasks/attest",
                422,
                {"task_id": task_id, "level": "Proficient", "hours": 2.0},
                critical=True
            )
            if success:
                print(f"  {Colors.PASS} Non-supervisor attestation correctly blocked")
            
            # Attest as supervisor
            tester.impersonate("u_supervisor")
            success, attest = tester.test(
                "POST /api/student/tasks/attest as supervisor (200)",
                "POST",
                "student/tasks/attest",
                200,
                {"task_id": task_id, "level": "Proficient", "hours": 2.0},
                critical=True
            )
            if success:
                print(f"  {Colors.PASS} Supervisor attestation succeeded")
                print(f"  {Colors.INFO} Competency verified: {attest.get('verified')}")
    
    # ========================================================================
    # 12. SKILLS PASSPORT
    # ========================================================================
    print("\n[12] Skills Passport")
    print("-" * 80)
    success, passport = tester.test("GET /api/student/passport?learner_id=u_student", "GET", "student/passport?learner_id=u_student", 200)
    if success:
        print(f"  {Colors.INFO} Competencies: {len(passport.get('competencies', []))}")
        print(f"  {Colors.INFO} Opportunities: {len(passport.get('opportunities', []))}")
        print(f"  {Colors.INFO} Total hours: {passport.get('total_hours')}")
    
    # ========================================================================
    # 13. PHASE 3: REQUEST HUB (intake)
    # ========================================================================
    print("\n[13] PHASE 3: Request Hub (Intake)")
    print("-" * 80)
    
    # Get templates
    success, templates = tester.test("GET /api/requests/templates", "GET", "requests/templates", 200, critical=True)
    if success:
        lanes = templates.get("lanes", [])
        print(f"  {Colors.INFO} Lanes: {len(lanes)}")
        lane_keys = [l.get("key") for l in lanes]
        if set(lane_keys) == {"EVENT", "IT_SAAS", "FACILITIES", "CLASSROOM_LAB"}:
            print(f"  {Colors.PASS} All 4 lanes present: {lane_keys}")
        else:
            print(f"  {Colors.WARN} Expected 4 lanes, got: {lane_keys}")
    
    # Preview request (missing fields)
    success, preview = tester.test(
        "POST /api/requests/preview (missing fields)",
        "POST",
        "requests/preview",
        200,
        {
            "lane": "EVENT",
            "title": "Founder Day gala AV",
            "raw_text": "need AV for Founder Day event"
        },
        critical=True
    )
    if success:
        print(f"  {Colors.INFO} Missing fields: {preview.get('missing_fields')}")
        print(f"  {Colors.INFO} Duplicate suggestions: {len(preview.get('duplicate_suggestions', []))}")
        if "budget estimate" in preview.get("missing_fields", []):
            print(f"  {Colors.PASS} Budget missing detected")
        if any("Founder" in d for d in preview.get("duplicate_suggestions", [])):
            print(f"  {Colors.PASS} Duplicate Founder Day case detected")
    
    # Create request (incomplete -> NEEDS_INFO)
    success, req1 = tester.test(
        "POST /api/requests (incomplete -> NEEDS_INFO)",
        "POST",
        "requests",
        200,
        {
            "lane": "EVENT",
            "title": "Test incomplete request",
            "raw_text": "need something"
        }
    )
    if success:
        case = req1.get("case", {})
        if case.get("state") == "NEEDS_INFO":
            print(f"  {Colors.PASS} Incomplete request -> NEEDS_INFO")
        print(f"  {Colors.INFO} Case ID: {case.get('id')}")
    
    # Create request (complete -> TRIAGED)
    success, req2 = tester.test(
        "POST /api/requests (complete -> TRIAGED)",
        "POST",
        "requests",
        200,
        {
            "lane": "EVENT",
            "title": "Complete event request",
            "raw_text": "need AV for event",
            "budget_amount": 5000,
            "needed_by": "2026-10-15",
            "location": "Blackburn Center"
        }
    )
    if success:
        case = req2.get("case", {})
        if case.get("state") == "TRIAGED":
            print(f"  {Colors.PASS} Complete request -> TRIAGED")
        print(f"  {Colors.INFO} Case ID: {case.get('id')}")
    
    # ========================================================================
    # 14. PHASE 3: MEETING (consent gate)
    # ========================================================================
    print("\n[14] PHASE 3: Meeting (Consent Gate)")
    print("-" * 80)
    
    # Propose meeting
    success, meeting = tester.test(
        "POST /api/cases/case_founderday/meeting/propose",
        "POST",
        "cases/case_founderday/meeting/propose",
        200,
        critical=True
    )
    if success:
        windows = meeting.get("windows", [])
        print(f"  {Colors.INFO} Windows proposed: {len(windows)}")
        if len(windows) == 3:
            print(f"  {Colors.PASS} 3 windows returned")
    
    # Send without consent (should fail)
    success, resp = tester.test(
        "POST /api/cases/case_founderday/meeting/send (no consent -> 422)",
        "POST",
        "cases/case_founderday/meeting/send",
        422,
        {"window_id": "w1", "send_authorized": False},
        critical=True
    )
    if success:
        print(f"  {Colors.PASS} Consent gate correctly enforced")
    
    # Send with consent
    success, sent = tester.test(
        "POST /api/cases/case_founderday/meeting/send (with consent -> 200)",
        "POST",
        "cases/case_founderday/meeting/send",
        200,
        {"window_id": "w1", "send_authorized": True},
        critical=True
    )
    if success:
        print(f"  {Colors.INFO} Invite ID: {sent.get('invite_id')}")
        if sent.get("invite_id"):
            print(f"  {Colors.PASS} Meeting sent with invite ID")
    
    # ========================================================================
    # 15. PHASE 3: CONTRACT
    # ========================================================================
    print("\n[15] PHASE 3: Contract")
    print("-" * 80)
    
    success, contract = tester.test(
        "GET /api/cases/case_founderday/contract",
        "GET",
        "cases/case_founderday/contract",
        200,
        critical=True
    )
    if success:
        clauses = contract.get("clauses", [])
        print(f"  {Colors.INFO} Clauses: {len(clauses)}")
        if len(clauses) == 5:
            print(f"  {Colors.PASS} 5 clauses returned")
        statuses = [c.get("status") for c in clauses]
        expected = {"acceptable", "deviation", "missing", "legal_review"}
        if expected.issubset(set(statuses)):
            print(f"  {Colors.PASS} All expected clause statuses present")
    
    # ========================================================================
    # 16. PHASE 3: BUY/MAKE/REPAIR
    # ========================================================================
    print("\n[16] PHASE 3: Buy/Make/Repair")
    print("-" * 80)
    
    success, bmr = tester.test(
        "GET /api/cases/case_hvac/bmr",
        "GET",
        "cases/case_hvac/bmr",
        200,
        critical=True
    )
    if success:
        if "buy" in bmr and "repair" in bmr and "microfactory" in bmr:
            print(f"  {Colors.PASS} All 3 options present (buy, repair, microfactory)")
            print(f"  {Colors.INFO} Buy: ${bmr['buy']['cost']}")
            print(f"  {Colors.INFO} Repair: ${bmr['repair']['cost']}")
            print(f"  {Colors.INFO} Microfactory: ${bmr['microfactory']['cost']}")
    
    # ========================================================================
    # 17. PHASE 3: ORDER -> LOGISTICS LIFECYCLE
    # ========================================================================
    print("\n[17] PHASE 3: Order -> Logistics Lifecycle")
    print("-" * 80)
    
    # Reset and jump to APPROVED
    tester.test("POST /api/demo/reset", "POST", "demo/reset", 200)
    tester.test("POST /api/demo/jump to APPROVED", "POST", "demo/jump", 200, {"case_id": "case_founderday", "state": "APPROVED"})
    
    # Order
    tester.impersonate("u_operator")
    success, order = tester.test(
        "POST /api/cases/case_founderday/order",
        "POST",
        "cases/case_founderday/order",
        200,
        critical=True
    )
    if success:
        print(f"  {Colors.INFO} PO ref: {order.get('po_ref')}")
        if order.get("state") == "ORDERED":
            print(f"  {Colors.PASS} Case transitioned to ORDERED")
    
    # Ship advance
    success, ship = tester.test(
        "POST /api/cases/case_founderday/ship/advance",
        "POST",
        "cases/case_founderday/ship/advance",
        200,
        critical=True
    )
    if success:
        if ship.get("state") == "IN_TRANSIT":
            print(f"  {Colors.PASS} Case transitioned to IN_TRANSIT")
    
    # Receive without checklist (should fail)
    success, resp = tester.test(
        "POST /api/cases/case_founderday/receive (no checklist -> 422)",
        "POST",
        "cases/case_founderday/receive",
        422,
        {"checklist_confirmed": False},
        critical=True
    )
    if success:
        print(f"  {Colors.PASS} Receiving checklist gate enforced")
    
    # Receive with checklist
    success, receive = tester.test(
        "POST /api/cases/case_founderday/receive (with checklist -> 200)",
        "POST",
        "cases/case_founderday/receive",
        200,
        {"checklist_confirmed": True},
        critical=True
    )
    if success:
        if receive.get("state") == "RECEIVED":
            print(f"  {Colors.PASS} Case transitioned to RECEIVED")
        print(f"  {Colors.INFO} Evidence: {receive.get('evidence')}")
    
    # Close
    success, close = tester.test(
        "POST /api/cases/case_founderday/close",
        "POST",
        "cases/case_founderday/close",
        200,
        critical=True
    )
    if success:
        if close.get("state") == "CLOSED":
            print(f"  {Colors.PASS} Case transitioned to CLOSED")
    
    # ========================================================================
    # 18. PHASE 3: OVERRIDE
    # ========================================================================
    print("\n[18] PHASE 3: Override")
    print("-" * 80)
    
    # Reset
    tester.test("POST /api/demo/reset", "POST", "demo/reset", 200)
    
    # Override without required fields (should fail)
    success, resp = tester.test(
        "POST /api/cases/case_founderday/override (missing fields -> 422)",
        "POST",
        "cases/case_founderday/override",
        422,
        {"reason": "Emergency"},
        critical=True
    )
    if success:
        print(f"  {Colors.PASS} Override validation enforced")
    
    # Override with all fields
    success, override = tester.test(
        "POST /api/cases/case_founderday/override (complete -> 200)",
        "POST",
        "cases/case_founderday/override",
        200,
        {
            "reason": "Emergency procurement for safety",
            "policy_id": "policy-v3#4.2",
            "expiry": "2026-10-01"
        },
        critical=True
    )
    if success:
        print(f"  {Colors.INFO} Override ID: {override.get('id')}")
        if override.get("id"):
            print(f"  {Colors.PASS} Override recorded")
    
    # ========================================================================
    # 19. PHASE 3: DELEGATION
    # ========================================================================
    print("\n[19] PHASE 3: Delegation")
    print("-" * 80)
    
    # Reset to get fresh approvals
    tester.test("POST /api/demo/reset", "POST", "demo/reset", 200)
    
    # Get approval ID
    success, approvals = tester.test("GET /api/approvals?case_id=case_founderday", "GET", "approvals?case_id=case_founderday", 200)
    if success and approvals:
        appr_id = approvals[0].get("id")
        
        # Delegate
        success, delegate = tester.test(
            "POST /api/approvals/{id}/delegate",
            "POST",
            f"approvals/{appr_id}/delegate",
            200,
            {
                "to_actor_id": "u_executive",
                "expiry": "2026-10-01"
            },
            critical=True
        )
        if success:
            print(f"  {Colors.INFO} Delegated to: {delegate.get('delegated_to')}")
            if delegate.get("delegated_to"):
                print(f"  {Colors.PASS} Delegation succeeded")
    
    # ========================================================================
    # 20. PHASE 3: FLOW REPLAY
    # ========================================================================
    print("\n[20] PHASE 3: Flow Replay")
    print("-" * 80)
    
    # Get flows
    success, flows = tester.test("GET /api/flows", "GET", "flows", 200)
    if success and flows:
        flow_id = flows[0].get("id")
        initial_runs = flows[0].get("runs", 0)
        
        # Replay
        success, replay = tester.test(
            "POST /api/flows/{id}/replay",
            "POST",
            f"flows/{flow_id}/replay",
            200,
            critical=True
        )
        if success:
            print(f"  {Colors.INFO} Flow: {flow_id}")
            print(f"  {Colors.INFO} Runs: {replay.get('runs')} (was {initial_runs})")
            if replay.get("runs") == initial_runs + 1:
                print(f"  {Colors.PASS} Replay incremented runs")
            if replay.get("status") == "OK":
                print(f"  {Colors.PASS} Replay status OK")
    
    # ========================================================================
    # 21. PHASE 3: OFFLINE CONFLICT RESOLVE
    # ========================================================================
    print("\n[21] PHASE 3: Offline Conflict Resolve")
    print("-" * 80)
    
    # Inject offline_pending exception
    success, exc = tester.test(
        "POST /api/demo/exception (offline_pending)",
        "POST",
        "demo/exception",
        200,
        {"key": "offline_pending", "case_id": "case_founderday"}
    )
    
    # Get outbox items
    success, queue = tester.test("GET /api/offline/queue", "GET", "offline/queue", 200)
    if success:
        items = queue.get("queue", [])
        if items:
            item_id = items[0].get("id")
            
            # Resolve conflict
            success, resolve = tester.test(
                "POST /api/offline/resolve/{id}",
                "POST",
                f"offline/resolve/{item_id}",
                200,
                {"resolution": "refresh_and_apply"},
                critical=True
            )
            if success:
                print(f"  {Colors.INFO} Item ID: {item_id}")
                print(f"  {Colors.INFO} Status: {resolve.get('status')}")
                if resolve.get("status") == "APPLIED":
                    print(f"  {Colors.PASS} Conflict resolved")
    
    # ========================================================================
    # 22. PHASE 3: REGRESSION CHECKS
    # ========================================================================
    print("\n[22] PHASE 3: Regression Checks")
    print("-" * 80)
    
    # Reset
    tester.test("POST /api/demo/reset", "POST", "demo/reset", 200)
    
    # SoD still enforced
    tester.impersonate("u_requester")
    success, resp = tester.test(
        "REGRESSION: SoD still enforced (requester self-approve -> 422)",
        "POST",
        "approvals/appr_fac/decide",
        422,
        {"decision": "APPROVED", "rationale": "Test"}
    )
    if success:
        print(f"  {Colors.PASS} SoD regression check passed")
    
    # Audit chain still valid
    success, audit = tester.test("GET /api/demo/audit", "GET", "demo/audit", 200)
    if success:
        if audit.get("chain_valid"):
            print(f"  {Colors.PASS} Audit chain regression check passed")
    
    # Student learning attestation still supervisor-gated
    success, tasks = tester.test("GET /api/student/tasks", "GET", "student/tasks", 200)
    if success and tasks:
        task_id = tasks[0].get("id")
        tester.impersonate("u_student")
        tester.test("POST /api/student/tasks/accept", "POST", "student/tasks/accept", 200, {"task_id": task_id})
        tester.test("POST /api/student/tasks/quiz", "POST", "student/tasks/quiz", 200, {"task_id": task_id, "answers": [2, 1, 1]})
        
        success, resp = tester.test(
            "REGRESSION: Student attestation still supervisor-gated (422)",
            "POST",
            "student/tasks/attest",
            422,
            {"task_id": task_id, "level": "Proficient", "hours": 2.0}
        )
        if success:
            print(f"  {Colors.PASS} Learning loop regression check passed")
    
    # ========================================================================
    # 23. OTHER ENDPOINTS
    # ========================================================================
    print("\n[23] Other Endpoints")
    print("-" * 80)
    tester.test("GET /api/campus-memory", "GET", "campus-memory", 200)
    tester.test("GET /api/campus-memory?q=policy", "GET", "campus-memory?q=policy", 200)
    tester.test("GET /api/impact", "GET", "impact", 200)
    tester.test("GET /api/notifications", "GET", "notifications", 200)
    tester.test("GET /api/operator/views", "GET", "operator/views", 200)
    tester.test("GET /api/operator/view/my_queue", "GET", "operator/view/my_queue", 200)
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {tester.tests_run}")
    print(f"Passed: {tester.tests_passed} ({tester.tests_passed * 100 // tester.tests_run}%)")
    print(f"Failed: {tester.tests_run - tester.tests_passed}")
    
    if tester.critical_failures:
        print(f"\n{Colors.FAIL} CRITICAL FAILURES:")
        for failure in tester.critical_failures:
            print(f"  - {failure}")
        print("\n⚠️  Critical issues detected. Main agent should fix these first.")
        return 1
    
    if tester.tests_passed == tester.tests_run:
        print(f"\n{Colors.PASS} All tests passed!")
        return 0
    else:
        print(f"\n{Colors.WARN} Some tests failed. See details above.")
        return 0  # Non-critical failures

if __name__ == "__main__":
    sys.exit(main())
