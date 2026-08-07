from datetime import datetime, timezone

from app.agents.privacy_agent import PrivacyComplianceAgent


class CustomerIntelligenceAgent:

    def __init__(self):
        self.privacy_agent = PrivacyComplianceAgent()

    def generate_customer_persona(self, customer: dict) -> dict:
        age = customer.get("age", 30)
        income = customer.get("annual_income", 0)
        current_vehicle = customer.get("current_vehicle")
        ev_page_views = customer.get("ev_page_views", 0)
        website_visits = customer.get("website_visits", 0)
        vehicle_year = customer.get("vehicle_year", 2024)
        social_engagement = customer.get("social_engagement_score", 0)

        if ev_page_views > 10 and income > 1200000:
            persona = "Tech-Savvy EV Enthusiast"
        elif current_vehicle and vehicle_year < 2020:
            persona = "Upgrade-Ready Owner"
        elif income > 2000000 and social_engagement > 60:
            persona = "Premium Lifestyle Seeker"
        elif not current_vehicle:
            persona = "First-Time Car Buyer"
        else:
            persona = "Value-Conscious Family Buyer"

        return {
            "persona": persona,
            "age": age,
            "income_bracket": self.get_customer_segment(customer),
        }

    def calculate_buying_intent(self, customer: dict) -> dict:
        website_visits = customer.get("website_visits", 0)
        ev_page_views = customer.get("ev_page_views", 0)
        brochure_downloads = customer.get("brochure_downloads", 0)
        test_drives_taken = customer.get("test_drives_taken", 0)
        social_engagement_score = customer.get("social_engagement_score", 0)
        email_open_rate = customer.get("email_open_rate", 0)
        campaign_response_rate = customer.get("campaign_response_rate", 0)

        signals = []
        score = 0.0

        visit_contribution = website_visits * 1.5
        if visit_contribution > 0:
            signals.append(f"Website visits: {website_visits} (+{visit_contribution:.1f})")
        score += visit_contribution

        ev_contribution = ev_page_views * 2.0
        if ev_contribution > 0:
            signals.append(f"EV page views: {ev_page_views} (+{ev_contribution:.1f})")
        score += ev_contribution

        brochure_contribution = brochure_downloads * 10
        if brochure_contribution > 0:
            signals.append(f"Brochure downloads: {brochure_downloads} (+{brochure_contribution})")
        score += brochure_contribution

        test_drive_contribution = test_drives_taken * 15
        if test_drive_contribution > 0:
            signals.append(f"Test drives taken: {test_drives_taken} (+{test_drive_contribution})")
        score += test_drive_contribution

        social_contribution = social_engagement_score * 0.3
        if social_contribution > 0:
            signals.append(f"Social engagement: {social_engagement_score} (+{social_contribution:.1f})")
        score += social_contribution

        email_contribution = email_open_rate * 20
        if email_contribution > 0:
            signals.append(f"Email open rate: {email_open_rate} (+{email_contribution:.1f})")
        score += email_contribution

        campaign_contribution = campaign_response_rate * 15
        if campaign_contribution > 0:
            signals.append(f"Campaign response rate: {campaign_response_rate} (+{campaign_contribution:.1f})")
        score += campaign_contribution

        score = min(score, 100)

        if score < 30:
            intent_level = "low"
        elif score <= 65:
            intent_level = "medium"
        else:
            intent_level = "high"

        return {
            "intent_level": intent_level,
            "intent_score": round(score, 2),
            "signals": signals,
        }

    def get_customer_segment(self, customer: dict) -> str:
        income = customer.get("annual_income", 0)
        if income < 1000000:
            return "mid_range"
        elif income <= 2500000:
            return "premium"
        else:
            return "luxury"

    def get_preferred_communication(self, customer: dict) -> dict:
        return {
            "channel": customer.get("preferred_channel", "email"),
            "language": customer.get("language_preference", "English"),
        }

    def get_vehicle_ownership_profile(self, customer: dict) -> dict:
        current_vehicle = customer.get("current_vehicle")
        vehicle_year = customer.get("vehicle_year")
        service_count = customer.get("service_count", 0)

        if not current_vehicle or not vehicle_year:
            return {
                "current_vehicle": None,
                "ownership_years": 0,
                "service_frequency": "low",
                "likely_upgrade": False,
            }

        current_year = datetime.now(timezone.utc).year
        ownership_years = current_year - vehicle_year

        if ownership_years > 0:
            avg_services = service_count / ownership_years
        else:
            avg_services = service_count

        if avg_services < 1:
            service_frequency = "low"
        elif avg_services <= 3:
            service_frequency = "medium"
        else:
            service_frequency = "high"

        return {
            "current_vehicle": current_vehicle,
            "ownership_years": ownership_years,
            "service_frequency": service_frequency,
            "likely_upgrade": ownership_years > 4,
        }

    def build_complete_profile(self, customer: dict) -> dict:
        anonymized = self.privacy_agent.anonymize_customer_data(customer)

        persona = self.generate_customer_persona(customer)
        buying_intent = self.calculate_buying_intent(customer)
        segment = self.get_customer_segment(customer)
        communication = self.get_preferred_communication(customer)
        ownership = self.get_vehicle_ownership_profile(customer)

        return {
            "customer_id": customer.get("customer_id"),
            "anonymized_data": anonymized,
            "persona": persona,
            "buying_intent": buying_intent,
            "segment": segment,
            "preferred_communication": communication,
            "vehicle_ownership": ownership,
            "profile_generated_at": datetime.now(timezone.utc).isoformat(),
        }
