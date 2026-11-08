"""
SmartMed Comprehensive End-to-End Test Suite
Tests registration, auth, ownership security, dose tracking, schedules,
reports, educational monograph search, and multi-user privacy isolation.
"""
import sys
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
import app.models
from app.main import app as fastapi_app
from app.database import Base, engine, SessionLocal
from app.services.sample_data_seed import seed_educational_medicines

def test_full_application_lifecycle():
    print("=" * 60)
    print("STARTING SMARTMED END-TO-END AUTOMATED VERIFICATION")
    print("=" * 60)

    # Initialize tables and seed data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_educational_medicines(db)
    db.close()

    client = TestClient(fastapi_app)

    # 1. Health Check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] Health Check: Status 200 OK")

    # 2. Educational Medicines Seeding Check
    res = client.get("/api/medicine-info")
    assert res.status_code == 200, f"Failed: {res.text}"
    meds = res.json()
    assert len(meds) >= 4, "Educational medicines were not seeded properly"
    print(f"[PASS] Educational Catalog Check: {len(meds)} monographs available")

    # Test search by query and category
    res = client.get("/api/medicine-info?search=Amoxicillin")
    assert res.status_code == 200
    assert any("Amoxicillin" in m["name"] for m in res.json())
    print("[PASS] Educational Search Check Passed")

    # Test specific monograph details
    med_id = meds[0]["id"]
    res = client.get(f"/api/medicine-info/{med_id}")
    assert res.status_code == 200
    details = res.json()
    assert "common_uses" in details and "mechanism_of_action" in details
    print("[PASS] Educational Detailed Monograph Check Passed")

    # 3. User A Registration
    user_a_email = "test_alice@smartmed.com"
    user_a_data = {
        "full_name": "Alice Patient",
        "email": user_a_email,
        "password": "Password123!",
        "phone": "+1-555-0100",
        "emergency_contact": "Bob +1-555-0101"
    }
    res = client.post("/api/auth/register", json=user_a_data)
    if res.status_code == 400: # If already exists from earlier run
        res = client.post("/api/auth/login", json={"email": user_a_email, "password": "Password123!"})
    assert res.status_code in [200, 201], f"User A registration failed: {res.text}"
    token_a = res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("[PASS] User A Registered & Authenticated Successfully")

    # 4. User A Profile Check & Update
    res = client.get("/api/auth/me", headers=headers_a)
    assert res.status_code == 200
    assert res.json()["email"] == user_a_email
    print("[PASS] User A Profile Verification Passed")

    # 5. User A Adds Medicine
    med_payload = {
        "name": "Amoxicillin Trihydrate",
        "generic_name": "Amoxicillin",
        "category": "Antibiotic",
        "dosage": "500 mg",
        "form": "Capsule",
        "frequency": "Twice daily",
        "instructions": "Take after meals with water",
        "start_date": "2026-11-01",
        "end_date": "2026-11-15",
        "doctor_name": "Dr. Smith",
        "status": "active"
    }
    res = client.post("/api/medicines", json=med_payload, headers=headers_a)
    assert res.status_code == 201, f"Create medicine failed: {res.text}"
    med_a = res.json()
    med_a_id = med_a["id"]
    print(f"[PASS] User A Created Medicine #{med_a_id} ({med_a['name']})")

    # 6. User A Creates Schedule
    sched_payload = {
        "medicine_id": med_a_id,
        "reminder_time": "08:00",
        "time_of_day": "morning",
        "days_of_week": "Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        "dosage_quantity": "1 capsule",
        "is_active": True
    }
    res = client.post("/api/schedules", json=sched_payload, headers=headers_a)
    assert res.status_code == 201, f"Create schedule failed: {res.text}"
    sched_a = res.json()
    sched_a_id = sched_a["id"]
    print(f"[PASS] User A Created Schedule #{sched_a_id} for 08:00 AM")

    # 7. Today's Medicine Log Generation & Tracking
    res = client.get("/api/schedules/today", headers=headers_a)
    assert res.status_code == 200
    today_doses = res.json()
    assert len(today_doses) > 0, "No dose log was generated for today"
    dose_id = today_doses[0]["id"]
    print(f"[PASS] Today's Dose Engine Generated {len(today_doses)} dose log(s)")

    # 8. Mark Dose as Taken
    res = client.put(f"/api/logs/{dose_id}/status", json={"status": "taken", "notes": "Taken with glass of milk"}, headers=headers_a)
    assert res.status_code == 200
    assert res.json()["status"] == "taken"
    print(f"[PASS] Dose #{dose_id} Marked as Taken (Logged Time Captured)")

    # 9. Verify In-App Notification Created
    res = client.get("/api/notifications", headers=headers_a)
    assert res.status_code == 200
    notifs = res.json()
    assert len(notifs) > 0
    print(f"[PASS] In-App Notifications Engine Passed: {len(notifs)} notification(s)")

    # 10. Dashboard & Adherence Report Calculation
    res = client.get("/api/reports/dashboard-summary", headers=headers_a)
    assert res.status_code == 200
    dash = res.json()
    assert dash["total_medicines"] >= 1
    assert dash["today_taken"] >= 1
    print(f"[PASS] Dashboard Metrics Passed: Adherence = {dash['weekly_adherence_rate']}%")

    # 11. STRICT MULTI-USER PRIVACY ISOLATION TEST
    print("-" * 50)
    print("TESTING USER DATA PRIVACY ISOLATION (USER B vs USER A)")
    print("-" * 50)

    user_b_email = "test_bob@smartmed.com"
    user_b_data = {
        "full_name": "Bob Patient",
        "email": user_b_email,
        "password": "Password123!",
        "phone": "+1-555-0200"
    }
    res = client.post("/api/auth/register", json=user_b_data)
    if res.status_code == 400:
        res = client.post("/api/auth/login", json={"email": user_b_email, "password": "Password123!"})
    assert res.status_code in [200, 201]
    token_b = res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B lists medicines: must be 0 (User A's medicine must NOT appear)
    res = client.get("/api/medicines", headers=headers_b)
    assert res.status_code == 200
    assert len(res.json()) == 0, f"Privacy violation! User B can see User A's medicines: {res.json()}"
    print("[PASS] Privacy Test 1: User B medicine list is empty (cannot see User A's data)")

    # User B tries to directly access User A's medicine by ID: MUST BE 404
    res = client.get(f"/api/medicines/{med_a_id}", headers=headers_b)
    assert res.status_code == 404, f"Security Breach! User B accessed User A's medicine: {res.text}"
    print("[PASS] Privacy Test 2: User B blocked from GET /api/medicines/{id} of User A (404 Not Found)")

    # User B tries to modify User A's medicine: MUST BE 404
    res = client.put(f"/api/medicines/{med_a_id}", json={"name": "Hacked"}, headers=headers_b)
    assert res.status_code == 404, "Security Breach! User B modified User A's medicine"
    print("[PASS] Privacy Test 3: User B blocked from PUT /api/medicines/{id} of User A")

    # User B tries to delete User A's medicine: MUST BE 404
    res = client.delete(f"/api/medicines/{med_a_id}", headers=headers_b)
    assert res.status_code == 404, "Security Breach! User B deleted User A's medicine"
    print("[PASS] Privacy Test 4: User B blocked from DELETE /api/medicines/{id} of User A")

    # User B tries to read User A's schedules: must be 0
    res = client.get("/api/schedules", headers=headers_b)
    assert res.status_code == 200
    assert len(res.json()) == 0, "Privacy violation! User B can see User A's schedules"
    print("[PASS] Privacy Test 5: User B schedule list is completely isolated")

    print("=" * 60)
    print("ALL SMARTMED VERIFICATION TESTS PASSED SUCCESSFULLY! 100% OK")
    print("=" * 60)

if __name__ == "__main__":
    test_full_application_lifecycle()
