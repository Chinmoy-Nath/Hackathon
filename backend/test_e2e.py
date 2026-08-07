import httpx
import json
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))

base = "http://localhost:8000/api"
client = httpx.Client(follow_redirects=True, timeout=120)

r = client.post(f"{base}/auth/login", data={"username": "campaign_manager@tata.com", "password": "admin123"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
safe_print("Logged in as Campaign Manager")

campaign_data = {
    "name": "Diwali EV Launch 2026",
    "description": "Launch campaign for Nexon EV during Diwali festival targeting premium customers in Bangalore",
    "objective": "conversion",
    "vehicle_id": 5,
    "target_segment": "aspiring_premium",
    "target_cities": ["Bangalore"],
    "target_states": ["Karnataka"],
    "budget": 500000,
    "festival_context": "Diwali",
    "channels": ["email", "whatsapp", "sms"],
    "languages": ["en", "hi"],
}

r = client.post(f"{base}/campaigns", json=campaign_data, headers=headers)
safe_print(f"Create Campaign: {r.status_code}")
campaign = r.json()
cid = campaign["campaign_id"]
safe_print(f"  Campaign ID: {cid}")
safe_print(f"  Status: {campaign['status']}")

safe_print(f"\nExecuting campaign (full multi-agent orchestration)...")
r = client.post(f"{base}/campaigns/{cid}/execute", headers=headers)
safe_print(f"Execute: {r.status_code}")
if r.status_code == 200:
    result = r.json()
    safe_print(f"  Customers targeted: {result.get('customers_targeted')}")
    safe_print(f"  Content generated: {result.get('content_generated')}")
    safe_print(f"  Delivered: {result.get('delivered')}")
    safe_print(f"  Failed: {result.get('failed')}")

    wf = result.get("workflow_status", {})
    safe_print(f"\n  Agent Statuses ({wf.get('completed')}/{wf.get('total_agents')} completed):")
    for name, info in wf.get("agents", {}).items():
        summary = info.get("result_summary", "")
        summary_safe = summary.replace("\u20b9", "Rs.") if summary else ""
        safe_print(f"    [{info['status']}] {name}: {summary_safe[:100]}")

    analytics = result.get("analytics_summary", {})
    ca = analytics.get("campaign_analytics", {})
    roi = analytics.get("roi_metrics", {})
    safe_print(f"\n  Analytics:")
    safe_print(f"    Sent: {ca.get('sent')}, Delivered: {ca.get('delivered')}")
    safe_print(f"    Opened: {ca.get('opened')}, Clicked: {ca.get('clicked')}")
    safe_print(f"    Purchases: {ca.get('purchases')}")
    revenue = ca.get("revenue", 0)
    safe_print(f"    Revenue: Rs.{revenue:,.2f}" if revenue else "    Revenue: N/A")
    safe_print(f"    ROI: {roi.get('roi_percentage')}%")

    if result.get("errors"):
        safe_print(f"\n  Errors ({len(result['errors'])}):")
        for e in result["errors"][:3]:
            safe_print(f"    {e.get('agent')}: {e.get('error', '')[:80]}")
else:
    safe_print(f"  Error: {r.text[:300]}")

safe_print(f"\nFetching analytics from DB...")
r = client.get(f"{base}/campaigns/{cid}/analytics", headers=headers)
safe_print(f"Analytics: {r.status_code}")
if r.status_code == 200:
    a = r.json()
    safe_print(f"  Sent={a['total_sent']}, Delivered={a['total_delivered']}, Opened={a['total_opened']}")
    safe_print(f"  Clicked={a['total_clicked']}, Purchases={a['purchases']}")
    safe_print(f"  ROI={a['roi']}%, Effectiveness={a['effectiveness_score']}")

r = client.get(f"{base}/campaigns/{cid}/content", headers=headers)
safe_print(f"\nContent pieces: {len(r.json()) if r.status_code == 200 else 'error'}")
if r.status_code == 200:
    for c in r.json()[:2]:
        subj = str(c.get("subject", ""))[:60]
        safe_print(f"  [{c['channel']}/{c['language']}] {subj}")

safe_print("\n=== END-TO-END ORCHESTRATION TEST COMPLETE ===")
client.close()
