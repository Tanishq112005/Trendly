import requests
import time
import uuid

BASE_URL = "http://127.0.0.1:8000/api/chat/"

def run_chat(session_id, message):
    payload = {
        "session_id": session_id,
        "message": message
    }
    print(f"\n[User]: {message}")
    response = requests.post(BASE_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"[Agent]: {data.get('response')}")
        return data
    else:
        print(f"[Error]: {response.status_code} - {response.text}")
        return None

def test_happy_path_order_status():
    print("\n--- Test 1: Happy Path Order Status (TR-4521) ---")
    session_id = str(uuid.uuid4())
    run_chat(session_id, "Hi, I am Ananya. My email is ananya.rao@example.com and phone is +91-98765-10001.")
    time.sleep(1) # wait to prevent groq rate limit
    run_chat(session_id, "What is the status of my order TR-4521?")

def test_missing_auth():
    print("\n--- Test 2: Missing Authentication Context ---")
    session_id = str(uuid.uuid4())
    run_chat(session_id, "Where is my order TR-4522?")
    time.sleep(1)
    run_chat(session_id, "My email is marcus.bell@example.com")
    time.sleep(1)
    run_chat(session_id, "Phone: +1-415-555-0102")

def test_policy_grounding():
    print("\n--- Test 3: Policy Grounding (Return Window) ---")
    session_id = str(uuid.uuid4())
    run_chat(session_id, "What is your return policy window?")

def test_return_rejected_out_of_window():
    print("\n--- Test 4: Return Rejected - Out of Window (TR-4523) ---")
    session_id = str(uuid.uuid4())
    run_chat(session_id, "Hi, priya.nair@example.com, +91-98765-10003. I want to return TR-4523.")

def test_return_rejected_jewellery():
    print("\n--- Test 5: Return Rejected - Jewellery (TR-4527) ---")
    session_id = str(uuid.uuid4())
    run_chat(session_id, "Hi, priya.nair@example.com, +91-98765-10003. I want to return TR-4527.")

def test_delayed_compensation():
    print("\n--- Test 6: Delayed Compensation (TR-4525) ---")
    session_id = str(uuid.uuid4())
    run_chat(session_id, "Hi, diego.ramos@example.com, +34-600-555-104. Why is TR-4525 taking so long?")

def test_lost_in_transit_escalation():
    print("\n--- Test 7: Lost in Transit Escalation (TR-4526) ---")
    session_id = str(uuid.uuid4())
    run_chat(session_id, "Hi, marcus.bell@example.com, +1-415-555-0102. Where is TR-4526?")

def test_guardrails_refusal():
    print("\n--- Test 8: Guardrails - Unrelated Query ---")
    session_id = str(uuid.uuid4())
    run_chat(session_id, "Can you tell me a joke about dogs?")

if __name__ == "__main__":
    print("Starting E2E Tests. Note: Groq API rate limits may cause 'Thinking...' delays if run too fast.")
    # Rate limits might break this if run back to back on free tier
    test_happy_path_order_status()
    time.sleep(5)
    test_missing_auth()
    time.sleep(5)
    test_policy_grounding()
    time.sleep(5)
    test_return_rejected_out_of_window()
    time.sleep(5)
    test_return_rejected_jewellery()
    time.sleep(5)
    test_delayed_compensation()
    time.sleep(5)
    test_lost_in_transit_escalation()
    time.sleep(5)
    test_guardrails_refusal()
    print("\nAll tests completed.")
