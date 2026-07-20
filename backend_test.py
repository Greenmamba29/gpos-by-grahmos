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
    # 13. OTHER ENDPOINTS
    # ========================================================================
    print("\n[13] Other Endpoints")
    print("-" * 80)
    tester.test("GET /api/campus-memory", "GET", "campus-memory", 200)
    tester.test("GET /api/campus-memory?q=policy", "GET", "campus-memory?q=policy", 200)
    tester.test("GET /api/impact", "GET", "impact", 200)
    tester.test("GET /api/flows", "GET", "flows", 200)
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
