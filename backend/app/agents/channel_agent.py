import random
import logging

logger = logging.getLogger(__name__)


ALL_CHANNELS = ["email", "whatsapp", "sms", "instagram", "facebook", "push", "youtube"]

OBJECTIVE_CHANNEL_BOOSTS = {
    "awareness": {"instagram": 15, "facebook": 15, "youtube": 15},
    "conversion": {"email": 15, "whatsapp": 15},
    "retention": {"email": 15, "push": 15},
    "engagement": {"instagram": 15, "facebook": 15, "whatsapp": 15, "youtube": 15},
}


class ChannelSelectionAgent:

    def select_channels(self, customer_profile: dict, campaign: dict) -> dict:
        allowed_channels = campaign.get("channels", ALL_CHANNELS)
        consents = customer_profile.get("channel_consents", {})
        preferred_channel = customer_profile.get("preferred_channel", "")
        age = customer_profile.get("age", 30)
        email_open_rate = customer_profile.get("email_open_rate", 0.0)
        social_engagement_score = customer_profile.get("social_engagement_score", 0)
        objective = campaign.get("objective", "").lower()

        scores = {}

        for channel in ALL_CHANNELS:
            if channel not in allowed_channels:
                continue

            channel_consent = consents.get(channel, True)
            if not channel_consent:
                scores[channel] = 0
                continue

            score = 0

            if preferred_channel and channel == preferred_channel:
                score += 30

            if email_open_rate > 0.4 and channel == "email":
                score += 20

            if social_engagement_score > 50 and channel in ("instagram", "facebook"):
                score += 15

            if age < 35:
                if channel == "whatsapp":
                    score += 15
                if channel == "instagram":
                    score += 10

            if age > 45:
                if channel == "email":
                    score += 10
                if channel == "sms":
                    score += 10

            objective_boosts = OBJECTIVE_CHANNEL_BOOSTS.get(objective, {})
            score += objective_boosts.get(channel, 0)

            score += random.uniform(0, 5)

            scores[channel] = round(score, 2)

        sorted_channels = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        primary_channel = sorted_channels[0][0] if sorted_channels else "email"
        primary_score = sorted_channels[0][1] if sorted_channels else 0
        secondary_channel = sorted_channels[1][0] if len(sorted_channels) > 1 else None
        secondary_score = sorted_channels[1][1] if len(sorted_channels) > 1 else 0

        confidence = min(primary_score / 100, 0.99)

        reasoning_parts = [f"Primary: {primary_channel} (score: {primary_score})"]
        if secondary_channel:
            reasoning_parts.append(f"Secondary: {secondary_channel} (score: {secondary_score})")
        if preferred_channel:
            reasoning_parts.append(f"Customer prefers {preferred_channel}")
        if age < 35:
            reasoning_parts.append("Younger demographic favors WhatsApp and Instagram")
        elif age > 45:
            reasoning_parts.append("Older demographic favors Email and SMS")
        if objective:
            reasoning_parts.append(f"Campaign objective '{objective}' boosted relevant channels")
        if email_open_rate > 0.4:
            reasoning_parts.append("High email open rate boosted email score")
        if social_engagement_score > 50:
            reasoning_parts.append("High social engagement boosted social channel scores")

        return {
            "primary_channel": primary_channel,
            "secondary_channel": secondary_channel,
            "channel_scores": scores,
            "channel_confidence": round(confidence, 4),
            "reasoning": ". ".join(reasoning_parts) + ".",
        }
