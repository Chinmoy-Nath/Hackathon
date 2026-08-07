from datetime import datetime, timezone

from app.data.seed_data import TATA_VEHICLES


class RecommendationEngine:

    def __init__(self, vehicles: list[dict] | None = None):
        self.vehicles = vehicles if vehicles is not None else TATA_VEHICLES

    def get_vehicle_by_name(self, name: str) -> dict | None:
        for vehicle in self.vehicles:
            if vehicle["name"].lower() == name.lower():
                return vehicle
        return None

    def apply_business_rules(self, customer_profile: dict) -> list[dict]:
        matches = []

        current_vehicle = customer_profile.get("current_vehicle")
        current_vehicle_year = customer_profile.get("current_vehicle_year")
        age = customer_profile.get("age", 30)
        annual_income = customer_profile.get("annual_income", 0)
        ev_page_views = customer_profile.get("ev_page_views", 0)
        brochure_downloads = customer_profile.get("brochure_downloads", 0)
        service_count = customer_profile.get("service_count", 0)
        vehicle_segment = customer_profile.get("vehicle_segment", "mid_range")
        customer_segment = customer_profile.get("customer_segment", "budget_conscious")

        current_year = datetime.now(timezone.utc).year
        ownership_years = (current_year - current_vehicle_year) if current_vehicle_year else 0

        if current_vehicle and current_vehicle.lower() == "tiago" and ownership_years >= 5:
            for recommended in ["Punch", "Nexon"]:
                matches.append({
                    "vehicle_name": recommended,
                    "rule_name": "upgrade_rule",
                    "priority": 8,
                    "reason": f"Customer has owned {current_vehicle} for {ownership_years} years, making them a strong candidate for an upgrade to {recommended}",
                })

        if ev_page_views > 5:
            for ev_name in ["Nexon EV", "Tiago EV", "Punch EV", "Curvv EV"]:
                matches.append({
                    "vehicle_name": ev_name,
                    "rule_name": "ev_interest_rule",
                    "priority": 7,
                    "reason": f"Customer has viewed EV pages {ev_page_views} times, indicating strong EV interest",
                })

        if annual_income > 25:
            for v in ["Harrier", "Safari", "Avinya (Concept)"]:
                matches.append({
                    "vehicle_name": v,
                    "rule_name": "income_based_rule",
                    "priority": 6,
                    "reason": f"Based on customer's financial profile, {v} aligns with their purchasing capacity",
                })
        elif annual_income >= 12:
            for v in ["Nexon", "Curvv", "Harrier"]:
                matches.append({
                    "vehicle_name": v,
                    "rule_name": "income_based_rule",
                    "priority": 6,
                    "reason": f"Based on customer's financial profile, {v} aligns with their purchasing capacity",
                })
        else:
            for v in ["Tiago", "Tigor", "Punch"]:
                matches.append({
                    "vehicle_name": v,
                    "rule_name": "income_based_rule",
                    "priority": 6,
                    "reason": f"Based on customer's financial profile, {v} aligns with their purchasing capacity",
                })

        if age > 35 and current_vehicle and current_vehicle.lower() in ("tiago", "tigor"):
            for v in ["Safari", "Harrier"]:
                matches.append({
                    "vehicle_name": v,
                    "rule_name": "family_vehicle_rule",
                    "priority": 7,
                    "reason": "Customer's family profile suggests need for spacious SUV",
                })

        if not current_vehicle:
            for v in ["Tiago", "Punch", "Tiago EV"]:
                matches.append({
                    "vehicle_name": v,
                    "rule_name": "first_time_buyer_rule",
                    "priority": 5,
                    "reason": f"As a first-time buyer, {v} offers excellent value and features",
                })

        if brochure_downloads > 0:
            if ev_page_views > 5:
                category = "EV"
                brochure_vehicles = ["Nexon EV", "Curvv EV", "Tiago EV", "Punch EV"]
            elif annual_income > 25:
                category = "Premium"
                brochure_vehicles = ["Harrier", "Safari"]
            elif annual_income >= 12:
                category = "Mid-Premium"
                brochure_vehicles = ["Nexon", "Curvv"]
            else:
                category = "Entry"
                brochure_vehicles = ["Tiago", "Punch"]
            for v in brochure_vehicles:
                matches.append({
                    "vehicle_name": v,
                    "rule_name": "brochure_interest_rule",
                    "priority": 6,
                    "reason": f"Customer downloaded brochure for {category} vehicles {brochure_downloads} times",
                })

        if service_count > 8 and ownership_years > 4:
            upgrade_targets = []
            if current_vehicle:
                vehicle_info = self.get_vehicle_by_name(current_vehicle)
                if vehicle_info:
                    if vehicle_info["segment"] == "Mid Range":
                        upgrade_targets = ["Nexon", "Curvv", "Harrier"]
                    elif vehicle_info["segment"] == "Premium":
                        upgrade_targets = ["Harrier", "Safari", "Curvv EV"]
                    else:
                        upgrade_targets = ["Safari", "Avinya (Concept)"]
                else:
                    upgrade_targets = ["Nexon", "Punch"]
            for v in upgrade_targets:
                matches.append({
                    "vehicle_name": v,
                    "rule_name": "service_dissatisfaction_rule",
                    "priority": 9,
                    "reason": "High service frequency indicates readiness for a newer, more reliable vehicle",
                })

        if vehicle_segment in ("premium", "luxury") or customer_segment in ("aspiring_premium", "luxury_seeker"):
            premium_vehicles = [v for v in self.vehicles if v["segment"] in ("Premium", "Luxury")]
            if current_vehicle:
                current_info = self.get_vehicle_by_name(current_vehicle)
                if current_info and current_info["segment"] in ("Premium", "Luxury"):
                    for v in premium_vehicles:
                        if v["name"] != current_vehicle:
                            matches.append({
                                "vehicle_name": v["name"],
                                "rule_name": "segment_loyalty_rule",
                                "priority": 5,
                                "reason": "Customer's premium segment loyalty suggests interest in premium/luxury offerings",
                            })

        matches.sort(key=lambda x: x["priority"], reverse=True)
        return matches

    def calculate_intent_score(self, customer_profile: dict) -> dict:
        scoring_config = [
            ("website_visits", 1.5, 30),
            ("ev_page_views", 2.5, 25),
            ("brochure_downloads", 12, 20),
            ("test_drives_taken", 18, 15),
            ("social_engagement_score", 0.3, 10),
            ("email_open_rate", 25, 10),
            ("campaign_response_rate", 20, 10),
        ]

        contributing_factors = []
        total_score = 0.0
        max_possible = sum(cfg[2] for cfg in scoring_config)

        for factor, weight, max_contribution in scoring_config:
            value = customer_profile.get(factor, 0)
            raw_contribution = value * weight
            capped_contribution = min(raw_contribution, max_contribution)
            total_score += capped_contribution
            contributing_factors.append({
                "factor": factor,
                "value": value,
                "contribution": round(capped_contribution, 2),
            })

        normalized_score = round((total_score / max_possible) * 100, 2) if max_possible > 0 else 0.0
        normalized_score = min(normalized_score, 100.0)

        if normalized_score < 30:
            intent_level = "low"
        elif normalized_score <= 65:
            intent_level = "medium"
        else:
            intent_level = "high"

        sorted_factors = sorted(contributing_factors, key=lambda x: x["contribution"], reverse=True)
        top_signals = [f["factor"] for f in sorted_factors[:3]]

        return {
            "intent_score": normalized_score,
            "intent_level": intent_level,
            "contributing_factors": contributing_factors,
            "top_signals": top_signals,
        }

    def generate_recommendation(self, customer_profile: dict) -> dict:
        rule_matches = self.apply_business_rules(customer_profile)
        intent_data = self.calculate_intent_score(customer_profile)
        intent_score = intent_data["intent_score"]

        vehicle_scores: dict[str, dict] = {}

        for match in rule_matches:
            name = match["vehicle_name"]
            if name not in vehicle_scores:
                vehicle_scores[name] = {
                    "base_score": 0.0,
                    "intent_contribution": 0.0,
                    "segment_bonus": 0.0,
                    "recency_bonus": 0.0,
                    "rules": [],
                }
            current_base = (match["priority"] / 10.0) * 40
            if current_base > vehicle_scores[name]["base_score"]:
                vehicle_scores[name]["base_score"] = current_base
            if match["rule_name"] not in vehicle_scores[name]["rules"]:
                vehicle_scores[name]["rules"].append(match["rule_name"])

        for name in vehicle_scores:
            vehicle_scores[name]["intent_contribution"] = (intent_score / 100.0) * 30

        customer_segment = customer_profile.get("vehicle_segment", "mid_range")
        for name in vehicle_scores:
            vehicle_info = self.get_vehicle_by_name(name)
            if vehicle_info:
                vehicle_seg = vehicle_info["segment"].lower().replace(" ", "_")
                if vehicle_seg == customer_segment or (
                    customer_segment == "luxury" and vehicle_seg == "premium"
                ) or (
                    customer_segment == "premium" and vehicle_seg == "luxury"
                ):
                    vehicle_scores[name]["segment_bonus"] = 15.0
                elif customer_segment == "mid_range" and vehicle_seg == "mid_range":
                    vehicle_scores[name]["segment_bonus"] = 15.0
                elif customer_segment == "premium" and vehicle_seg == "mid_range":
                    vehicle_scores[name]["segment_bonus"] = 5.0
                elif customer_segment == "mid_range" and vehicle_seg == "premium":
                    vehicle_scores[name]["segment_bonus"] = 8.0

        website_visits = customer_profile.get("website_visits", 0)
        ev_page_views = customer_profile.get("ev_page_views", 0)
        brochure_downloads = customer_profile.get("brochure_downloads", 0)
        test_drives_taken = customer_profile.get("test_drives_taken", 0)
        recent_activity = website_visits + ev_page_views + brochure_downloads + test_drives_taken
        recency_score = min((recent_activity / 50.0) * 15, 15.0)
        for name in vehicle_scores:
            vehicle_scores[name]["recency_bonus"] = round(recency_score, 2)

        scored_vehicles = []
        for name, scores in vehicle_scores.items():
            total = (
                scores["base_score"]
                + scores["intent_contribution"]
                + scores["segment_bonus"]
                + scores["recency_bonus"]
            )
            scored_vehicles.append((name, round(total, 2), scores["rules"]))

        scored_vehicles.sort(key=lambda x: x[1], reverse=True)

        if not scored_vehicles:
            return {
                "recommended_vehicle": "Tiago",
                "confidence_score": 25.0,
                "reasoning": "No specific signals detected. Tiago is recommended as a versatile entry-level option.",
                "intent_score": intent_score,
                "intent_level": intent_data["intent_level"],
                "rule_triggers": [],
                "contributing_factors": intent_data["contributing_factors"],
                "alternative_vehicle": "Punch",
                "alternative_confidence": 20.0,
            }

        top_vehicle, top_score, top_rules = scored_vehicles[0]
        confidence = min(round(top_score, 2), 100.0)

        if len(scored_vehicles) > 1:
            alt_vehicle, alt_score, _ = scored_vehicles[1]
            alt_confidence = min(round(alt_score, 2), 100.0)
        else:
            alt_vehicle = "Punch" if top_vehicle != "Punch" else "Tiago"
            alt_confidence = 20.0

        all_rules = set()
        for match in rule_matches:
            all_rules.add(match["rule_name"])

        reasoning = self._build_reasoning(
            customer_profile, top_vehicle, confidence, intent_data, rule_matches, ownership_years=self._get_ownership_years(customer_profile)
        )

        return {
            "recommended_vehicle": top_vehicle,
            "confidence_score": confidence,
            "reasoning": reasoning,
            "intent_score": intent_score,
            "intent_level": intent_data["intent_level"],
            "rule_triggers": sorted(all_rules),
            "contributing_factors": intent_data["contributing_factors"],
            "alternative_vehicle": alt_vehicle,
            "alternative_confidence": alt_confidence,
        }

    def _get_ownership_years(self, customer_profile: dict) -> int:
        current_vehicle_year = customer_profile.get("current_vehicle_year")
        if current_vehicle_year:
            return datetime.now(timezone.utc).year - current_vehicle_year
        return 0

    def _build_reasoning(
        self,
        customer_profile: dict,
        recommended: str,
        confidence: float,
        intent_data: dict,
        rule_matches: list[dict],
        ownership_years: int,
    ) -> str:
        parts = []

        current_vehicle = customer_profile.get("current_vehicle")
        if current_vehicle and ownership_years > 0:
            vehicle_info = self.get_vehicle_by_name(current_vehicle)
            category = vehicle_info["category"] if vehicle_info else "Petrol"
            parts.append(f"Customer owns a {ownership_years}-year-old {current_vehicle} {category}")
        elif not current_vehicle:
            parts.append("Customer is a first-time buyer")

        brochure_downloads = customer_profile.get("brochure_downloads", 0)
        if brochure_downloads > 0:
            parts.append(f"downloaded brochures {brochure_downloads} time{'s' if brochure_downloads != 1 else ''}")

        ev_page_views = customer_profile.get("ev_page_views", 0)
        if ev_page_views > 0:
            parts.append(f"visited EV pages {ev_page_views} times in the last month")

        email_open_rate = customer_profile.get("email_open_rate", 0)
        if email_open_rate > 0.3:
            email_count = max(1, int(email_open_rate * 10))
            parts.append(f"opened {email_count} recent campaign emails")

        segment_label = customer_profile.get("vehicle_segment", "mid_range").replace("_", " ")
        parts.append(f"Based on their {segment_label} segment profile")

        if intent_data["intent_level"] == "high":
            parts.append("strong purchase intent")
        elif intent_data["intent_level"] == "medium":
            parts.append("moderate purchase intent")

        if ev_page_views > 5:
            parts.append("strong EV interest")

        narrative = ", ".join(parts[:4])
        analysis = " and ".join(parts[4:]) if len(parts) > 4 else ""

        if analysis:
            reasoning = f"{narrative}. {analysis}, {recommended} is the top recommendation with {confidence:.0f}% confidence."
        else:
            reasoning = f"{narrative}. {recommended} is the top recommendation with {confidence:.0f}% confidence."

        return reasoning
