import httpx
import json
import sys

base = "http://localhost:8000/api"
client = httpx.Client(follow_redirects=True, timeout=30)

try:
    r = client.get(f"{base}/health")
    print(f"Health: {r.status_code} {r.json()}")
except Exception as e:
    print(f"Server not reachable: {e}")
    sys.exit(1)

form_data = {"username": "campaign_manager@tata.com", "password": "admin123"}
r = client.post(f"{base}/auth/login", data=form_data)
print(f"Login CM: {r.status_code} role={r.json().get('role')}")
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

r = client.get(f"{base}/vehicles", headers=headers)
print(f"Vehicles: {r.status_code} count={len(r.json())}")
for v in r.json()[:3]:
    print(f"  - {v['name']} ({v['category']}/{v['segment']})")

r = client.get(f"{base}/customers?limit=3", headers=headers)
print(f"Customers: {r.status_code} count={len(r.json())}")
for c in r.json():
    print(f"  - {c['first_name']} {c['last_name']} ({c['city']}) Segment: {c['customer_segment']}")

r = client.get(f"{base}/customers/segments/summary", headers=headers)
print(f"Segments: {r.status_code} {r.json()}")

r = client.get(f"{base}/campaigns", headers=headers)
campaigns = r.json()
print(f"Campaigns: {r.status_code} count={len(campaigns)}")

r = client.post(
    f"{base}/campaigns/parse-request",
    json={"user_input": "Launch a Diwali campaign for Nexon EV customers in Bangalore who purchased within the last 3 years"},
    headers=headers,
)
print(f"Parse NL: {r.status_code} {json.dumps(r.json(), indent=2)}")

r = client.get(f"{base}/analytics/dashboard/campaign-manager", headers=headers)
print(f"CM Dashboard: {r.status_code} keys={list(r.json().keys())}")

form_data2 = {"username": "retail_manager@tata.com", "password": "admin123"}
r2 = client.post(f"{base}/auth/login", data=form_data2)
print(f"Login RM: {r2.status_code} role={r2.json().get('role')}")
rm_token = r2.json()["access_token"]
headers2 = {"Authorization": f"Bearer {rm_token}"}

r = client.get(f"{base}/analytics/dashboard/retail-manager", headers=headers2)
print(f"RM Dashboard: {r.status_code} keys={list(r.json().keys())}")

if campaigns:
    cid = campaigns[0]["campaign_id"]
    r = client.get(f"{base}/campaigns/{cid}", headers=headers)
    print(f"Campaign Detail: {r.status_code} name={r.json().get('name')}")

r = client.get(f"{base}/customers?limit=1", headers=headers)
if r.status_code == 200 and r.json():
    customer_id = r.json()[0]["customer_id"]
    r = client.get(f"{base}/customers/{customer_id}/profile", headers=headers)
    print(f"Profile: {r.status_code}")
    profile = r.json()
    print(f"  Persona: {profile.get('persona')}")
    print(f"  Intent: {profile.get('buying_intent', {}).get('intent_level')}")
    print(f"  Segment: {profile.get('segment')}")

    r = client.get(f"{base}/customers/{customer_id}/recommendation", headers=headers)
    rec = r.json()
    print(f"Recommendation: {r.status_code}")
    print(f"  Vehicle: {rec.get('recommended_vehicle')}")
    print(f"  Confidence: {rec.get('confidence_score')}%")
    reasoning = str(rec.get("reasoning", ""))
    print(f"  Reasoning: {reasoning[:150]}...")
    print(f"  Intent: {rec.get('intent_level')} ({rec.get('intent_score')})")

r = client.post(f"{base}/campaigns", json={"name": "Test", "channels": ["email"]}, headers=headers2)
print(f"RBAC Test (RM create campaign): {r.status_code} (expected 403)")

print("\n=== ALL API TESTS COMPLETE ===")
client.close()
