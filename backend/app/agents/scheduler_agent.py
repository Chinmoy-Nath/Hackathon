import random
from datetime import datetime, timedelta


FESTIVAL_DATES = {
    "diwali": 10,
    "holi": 3,
    "eid": 4,
    "christmas": 12,
    "new_year": 1,
    "pongal": 1,
    "onam": 8,
    "navratri": 10,
    "ganesh_chaturthi": 9,
    "dussehra": 10,
    "baisakhi": 4,
    "raksha_bandhan": 8,
    "independence_day": 8,
    "republic_day": 1,
    "makar_sankranti": 1,
    "ugadi": 3,
}


class SchedulerAgent:

    def determine_optimal_schedule(self, customer_profile: dict, campaign: dict) -> dict:
        email_open_rate = customer_profile.get("email_open_rate", 0.3)
        social_engagement = customer_profile.get("social_engagement", 0.3)
        customer_type = customer_profile.get("customer_type", "B2C")
        purchase_intent_score = customer_profile.get("purchase_intent_score", 50)
        has_consent = customer_profile.get("has_consent", True)
        campaign_objective = campaign.get("objective", "engagement")
        festival_context = campaign.get("festival_context", None)

        if email_open_rate > 0.5:
            best_time = "10:00 AM IST"
            time_slot = "morning"
        elif social_engagement > 0.5:
            best_time = f"{random.choice([6, 7, 8])}:00 PM IST"
            time_slot = "evening"
        else:
            best_time = f"{random.choice([2, 3])}:00 PM IST"
            time_slot = "afternoon"

        now = datetime.now()

        if festival_context and festival_context.lower() in FESTIVAL_DATES:
            festival_month = FESTIVAL_DATES[festival_context.lower()]
            festival_year = now.year if festival_month >= now.month else now.year + 1
            festival_approx = datetime(festival_year, festival_month, 15)
            days_before = random.randint(3, 5)
            target_date = festival_approx - timedelta(days=days_before)
            best_day = target_date.strftime("%A")
        elif customer_type.upper() == "B2C":
            days_ahead = random.randint(1, 14)
            target_date = now + timedelta(days=days_ahead)
            while target_date.weekday() not in (5, 6):
                target_date += timedelta(days=1)
            best_day = target_date.strftime("%A")
        elif campaign_objective.lower() == "awareness":
            days_ahead = random.randint(1, 14)
            target_date = now + timedelta(days=days_ahead)
            while target_date.weekday() not in (1, 2, 3):
                target_date += timedelta(days=1)
            best_day = target_date.strftime("%A")
        else:
            days_ahead = random.randint(1, 14)
            target_date = now + timedelta(days=days_ahead)
            while target_date.weekday() not in (1, 5):
                target_date += timedelta(days=1)
            best_day = target_date.strftime("%A")

        expected_engagement_score = 40.0

        if festival_context:
            expected_engagement_score += 15

        if (email_open_rate > 0.5 and time_slot == "morning") or \
           (social_engagement > 0.5 and time_slot == "evening"):
            expected_engagement_score += 10

        if has_consent:
            expected_engagement_score += 10

        if purchase_intent_score > 60:
            expected_engagement_score += 15

        if customer_type.upper() == "B2C" and target_date.weekday() in (5, 6):
            expected_engagement_score += 10

        expected_engagement_score = min(expected_engagement_score, 95.0)

        reasoning_parts = []
        if festival_context:
            reasoning_parts.append(f"Scheduled around {festival_context} festival for maximum impact")
        if time_slot == "morning":
            reasoning_parts.append("Customer shows high email open rates, targeting morning hours")
        elif time_slot == "evening":
            reasoning_parts.append("Customer has high social engagement, targeting evening hours")
        else:
            reasoning_parts.append("Using default afternoon slot for balanced reach")
        if purchase_intent_score > 60:
            reasoning_parts.append("High purchase intent detected, prioritizing engagement")
        reasoning = ". ".join(reasoning_parts) + "."

        alt_days = {"Monday": "Wednesday", "Tuesday": "Thursday", "Wednesday": "Friday",
                    "Thursday": "Saturday", "Friday": "Sunday", "Saturday": "Monday",
                    "Sunday": "Tuesday"}
        alt_times = {"morning": "2:00 PM IST", "evening": "10:00 AM IST", "afternoon": "7:00 PM IST"}

        return {
            "best_day": best_day,
            "best_date": target_date.strftime("%Y-%m-%d"),
            "best_time": best_time,
            "expected_engagement_score": round(expected_engagement_score, 1),
            "reasoning": reasoning,
            "festival_context": festival_context,
            "alternative_slot": {
                "day": alt_days.get(best_day, "Wednesday"),
                "time": alt_times.get(time_slot, "2:00 PM IST"),
            },
        }
