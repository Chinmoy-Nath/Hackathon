import json
from app.agents.recommendation_engine import RecommendationEngine
from app.agents.customer_intelligence_agent import CustomerIntelligenceAgent
from app.agents.privacy_agent import PrivacyComplianceAgent
from app.agents.channel_agent import ChannelSelectionAgent
from app.agents.scheduler_agent import SchedulerAgent

customer = {
    "customer_id": "CUST001",
    "first_name": "Aarav",
    "last_name": "Sharma",
    "email": "aarav@example.com",
    "phone": "9876543210",
    "city": "Bangalore",
    "state": "Karnataka",
    "language_preference": "en",
    "age": 35,
    "annual_income": 1800000,
    "current_vehicle": "Nexon",
    "current_vehicle_year": 2019,
    "service_count": 8,
    "website_visits": 25,
    "ev_page_views": 15,
    "brochure_downloads": 3,
    "test_drives_taken": 1,
    "social_engagement_score": 65,
    "email_open_rate": 0.55,
    "campaign_response_rate": 0.3,
    "consent_email": True,
    "consent_whatsapp": True,
    "consent_sms": True,
    "consent_push": True,
    "consent_social": True,
    "is_unsubscribed": False,
    "preferred_channel": "email",
    "vehicle_segment": "premium",
    "customer_segment": "premium",
    "purchase_intent_score": 72,
}

print("=== RECOMMENDATION ENGINE ===")
engine = RecommendationEngine()
rec = engine.generate_recommendation(customer)
print(f"Vehicle: {rec['recommended_vehicle']}")
print(f"Confidence: {rec['confidence_score']}%")
print(f"Reasoning: {rec['reasoning']}")
print(f"Intent: {rec['intent_level']} ({rec['intent_score']})")
print(f"Rules: {rec['rule_triggers']}")
if rec.get("alternative_vehicle"):
    print(f"Alternative: {rec['alternative_vehicle']} ({rec['alternative_confidence']}%)")

print("\n=== CUSTOMER INTELLIGENCE ===")
ci = CustomerIntelligenceAgent()
profile = ci.build_complete_profile(customer)
print(f"Persona: {profile['persona']}")
print(f"Intent: {profile['buying_intent']['intent_level']}")
print(f"Segment: {profile['segment']}")

print("\n=== PRIVACY & COMPLIANCE ===")
privacy = PrivacyComplianceAgent()
consent = privacy.check_consent(customer, "email")
print(f"Email consent: {consent['allowed']} - {consent['reason']}")
anonymized = privacy.anonymize_customer_data(customer)
print(f"Anonymized email: {anonymized.get('email', 'N/A')}")
compliance = privacy.validate_campaign_compliance({"name": "Test", "channels": ["email"]})
print(f"Campaign compliant: {compliance['compliant']}")

print("\n=== CHANNEL SELECTION ===")
campaign = {"objective": "conversion", "channels": json.dumps(["email", "whatsapp", "sms", "push", "instagram"])}
ch = ChannelSelectionAgent().select_channels(customer, campaign)
print(f"Primary: {ch['primary_channel']}")
print(f"Secondary: {ch['secondary_channel']}")
print(f"Reasoning: {ch['reasoning']}")

print("\n=== SCHEDULER ===")
schedule = SchedulerAgent().determine_optimal_schedule(customer, campaign)
print(f"Best Day: {schedule['best_day']}")
print(f"Best Time: {schedule['best_time']}")
print(f"Engagement Score: {schedule['expected_engagement_score']}")

print("\n=== ALL AGENTS OK ===")
