import json
import logging
from typing import Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class ContentGenerationAgent:

    CHANNEL_FORMAT_INSTRUCTIONS = {
        "email": "Generate an email with: subject line, body (200-300 words), and a clear call-to-action.",
        "whatsapp": "Generate a WhatsApp message: short (50-100 words) with a clear call-to-action.",
        "sms": "Generate an SMS message: very short (160 characters max) with a call-to-action.",
        "instagram": "Generate an Instagram caption (100-150 words) with relevant hashtags.",
        "facebook": "Generate a Facebook post (150-200 words) with a clear call-to-action.",
        "push": "Generate a push notification: title (50 chars max) and body (100 chars max).",
        "youtube": "Generate a YouTube video description (200 words) with relevant tags.",
    }

    FALLBACK_TEMPLATES = {
        "email": {
            "subject": "Discover the {vehicle_name} – Exclusive {festival} Offer for You, {customer_name}!",
            "body": (
                "Dear {customer_name},\n\n"
                "We are thrilled to present the all-new {vehicle_name} from Tata Motors. "
                "Built for the modern Indian road, this vehicle combines cutting-edge technology, "
                "unmatched safety, and bold design that turns heads everywhere you go.\n\n"
                "{offer}\n\n"
                "This {festival} season, make the drive of your dreams a reality. "
                "Visit your nearest Tata Motors showroom or book a test drive online today.\n\n"
                "Warm regards,\nTata Motors"
            ),
            "cta_text": "Book Your Test Drive Now",
        },
        "whatsapp": {
            "body": (
                "Hi {customer_name}! 🚗 The {vehicle_name} awaits you this {festival}. "
                "{offer} "
                "Book your test drive today and experience the future of driving!"
            ),
            "cta_text": "Book Test Drive",
        },
        "sms": {
            "body": "{customer_name}, {vehicle_name} awaits! {offer} Book test drive: {cta_url}",
            "cta_text": "Book Now",
        },
        "instagram": {
            "body": (
                "The all-new {vehicle_name} is here to redefine your journey. "
                "Bold design. Unmatched performance. Pure Tata Motors excellence. "
                "{offer} "
                "This {festival}, elevate your drive. Link in bio."
            ),
            "cta_text": "Link in Bio",
            "hashtags": [
                "#TataMotors", "#{vehicle_tag}", "#DriveTheFuture",
                "#IndianRoads", "#{festival_tag}Offers",
            ],
        },
        "facebook": {
            "body": (
                "Introducing the {vehicle_name} – a masterpiece of engineering by Tata Motors. "
                "Whether it's the daily commute or the weekend getaway, this vehicle delivers "
                "an experience like no other.\n\n"
                "{offer}\n\n"
                "This {festival}, drive home your dream. Book a test drive today!"
            ),
            "cta_text": "Book Your Test Drive",
        },
        "push": {
            "body": "{vehicle_name}: {offer}",
            "cta_text": "View Offer",
        },
        "youtube": {
            "body": (
                "Discover the all-new {vehicle_name} from Tata Motors. "
                "In this video, explore the stunning design, powerful performance, "
                "advanced safety features, and cutting-edge technology that make this vehicle "
                "the perfect companion for every Indian road.\n\n"
                "{offer}\n\n"
                "Visit {cta_url} to book your test drive today."
            ),
            "cta_text": "Book Test Drive",
            "hashtags": [
                "#TataMotors", "#{vehicle_tag}", "#CarReview",
                "#IndianCars", "#{festival_tag}",
            ],
        },
    }

    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = openai_api_key
        self.model = model
        if openai_api_key:
            self.client = AsyncOpenAI(api_key=openai_api_key)
        else:
            self.client = None

    async def generate_content(
        self,
        campaign: dict,
        customer_profile: dict,
        recommendation: dict,
        channel: str,
        language: str = "en",
    ) -> dict:
        vehicle_name = recommendation.get("recommended_vehicle", "Tata Vehicle")
        confidence_score = recommendation.get("confidence_score", 0.0)
        reasoning = recommendation.get("reasoning", "")

        if self.client and self.api_key:
            try:
                return await self._generate_via_llm(
                    campaign, customer_profile, recommendation,
                    channel, language, vehicle_name,
                )
            except Exception as e:
                logger.warning(f"LLM content generation failed, using fallback: {e}")

        return self._generate_fallback(
            campaign, customer_profile, recommendation, channel, vehicle_name,
        )

    async def _generate_via_llm(
        self,
        campaign: dict,
        customer_profile: dict,
        recommendation: dict,
        channel: str,
        language: str,
        vehicle_name: str,
    ) -> dict:
        festival_context = campaign.get("festival_context", "")
        campaign_name = campaign.get("name", "")
        campaign_objective = campaign.get("objective", "")
        budget = campaign.get("budget", "")

        format_instruction = self.CHANNEL_FORMAT_INSTRUCTIONS.get(channel, "")

        prompt = f"""You are a marketing content specialist for Tata Motors, India.

Generate marketing content for the following campaign and customer.

IMPORTANT: The recommended vehicle is {vehicle_name}. Do NOT suggest or recommend any other vehicle. Use ONLY this vehicle in the content.

Campaign Details:
- Name: {campaign_name}
- Objective: {campaign_objective}
- Budget Context: {budget}
{"- Festival Context: " + festival_context if festival_context else ""}

Customer Persona:
{json.dumps(customer_profile, indent=2, default=str)}

Recommendation Details:
- Vehicle: {vehicle_name}
- Confidence: {recommendation.get('confidence_score', '')}
- Reasoning: {recommendation.get('reasoning', '')}
- Key Features: {recommendation.get('key_features', '')}
- Price Range: {recommendation.get('price_range', '')}

Channel: {channel}
{format_instruction}

Language: {"Hindi (Devanagari script, keep vehicle names and brand name in English, keep ₹ pricing)" if language == "hi" else "English"}

Brand Tone: Professional, Aspirational, Indian context. Speak to the aspirations of Indian customers.

Include the vehicle name, key features, and pricing range from the recommendation.

Respond ONLY in valid JSON with these exact keys:
{{
    "subject": "email subject line or null if not email",
    "body": "main content text",
    "cta_text": "call to action text",
    "cta_url": "a plausible Tata Motors URL",
    "hashtags": ["list", "of", "hashtags"] or null if not social media,
    "media_suggestion": "description of suggested image or video creative"
}}"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)

        return {
            "channel": channel,
            "language": language,
            "subject": result.get("subject"),
            "body": result.get("body", ""),
            "cta_text": result.get("cta_text", "Learn More"),
            "cta_url": result.get("cta_url", "https://www.tatamotors.com/test-drive/"),
            "hashtags": result.get("hashtags"),
            "media_suggestion": result.get("media_suggestion", ""),
        }

    def _generate_fallback(
        self,
        campaign: dict,
        customer_profile: dict,
        recommendation: dict,
        channel: str,
        vehicle_name: str,
    ) -> dict:
        template = self.FALLBACK_TEMPLATES.get(channel, self.FALLBACK_TEMPLATES["email"])
        festival = campaign.get("festival_context", "festive")
        customer_name = customer_profile.get("name", customer_profile.get("customer_name", "Valued Customer"))
        price_range = recommendation.get("price_range", "")
        key_features = recommendation.get("key_features", "")

        offer = ""
        if price_range:
            offer += f"Starting at {price_range}."
        if key_features:
            offer += f" Featuring {key_features}."
        if not offer:
            offer = "Exclusive offers available for a limited time."

        vehicle_tag = vehicle_name.replace(" ", "")
        festival_tag = festival.replace(" ", "") if festival else "Festive"
        cta_url = "https://www.tatamotors.com/test-drive/"

        format_kwargs = {
            "vehicle_name": vehicle_name,
            "customer_name": customer_name,
            "offer": offer,
            "festival": festival if festival else "festive",
            "cta_url": cta_url,
            "vehicle_tag": vehicle_tag,
            "festival_tag": festival_tag,
        }

        body = template["body"].format(**format_kwargs)
        cta_text = template.get("cta_text", "Learn More")
        subject = template.get("subject", "").format(**format_kwargs) if "subject" in template else None

        hashtags = None
        if "hashtags" in template:
            hashtags = [h.format(**format_kwargs) for h in template["hashtags"]]

        media_suggestion = f"High-quality lifestyle image of the {vehicle_name} in an aspirational Indian setting."

        return {
            "channel": channel,
            "language": "en",
            "subject": subject if channel == "email" else None,
            "body": body,
            "cta_text": cta_text,
            "cta_url": cta_url,
            "hashtags": hashtags,
            "media_suggestion": media_suggestion,
        }
