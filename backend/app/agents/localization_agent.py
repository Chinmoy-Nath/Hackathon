import json
import logging
from typing import Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class LocalizationAgent:

    HINDI_BELT_STATES = [
        "Uttar Pradesh",
        "Delhi NCR",
        "Rajasthan",
        "Madhya Pradesh",
        "Bihar",
        "Jharkhand",
        "Uttarakhand",
        "Haryana",
        "Himachal Pradesh",
        "Chhattisgarh",
    ]

    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = openai_api_key
        self.model = model
        if openai_api_key:
            self.client = AsyncOpenAI(api_key=openai_api_key)
        else:
            self.client = None

    async def localize_content(
        self,
        content: dict,
        target_language: str,
        vehicle_name: str,
        offer_details: str = "",
    ) -> dict:
        if target_language == "en":
            return content

        if target_language == "hi":
            return await self._localize_to_hindi(content, vehicle_name, offer_details)

        return content

    async def _localize_to_hindi(
        self,
        content: dict,
        vehicle_name: str,
        offer_details: str,
    ) -> dict:
        if not self.client or not self.api_key:
            return self._fallback_localization(content)

        try:
            fields_to_localize = {}
            if content.get("subject"):
                fields_to_localize["subject"] = content["subject"]
            if content.get("body"):
                fields_to_localize["body"] = content["body"]
            if content.get("cta_text"):
                fields_to_localize["cta_text"] = content["cta_text"]

            prompt = f"""You are an expert Hindi localization specialist for Tata Motors marketing content.

Localize the following marketing content to Hindi. This is NOT a literal translation — adapt the content culturally for a Hindi-speaking Indian audience.

Rules:
- Use Devanagari script for Hindi text
- Keep vehicle names in English exactly as given: {vehicle_name}
- Keep the brand name "Tata Motors" in English
- Keep all pricing in original format using ₹ symbol
- Adapt idioms, expressions, and cultural references for Hindi-speaking audience
- Maintain a professional and aspirational brand tone
- Keep offer details exactly as provided: {offer_details}
- Do NOT transliterate English vehicle names into Devanagari

Content to localize:
{json.dumps(fields_to_localize, indent=2, ensure_ascii=False)}

Respond ONLY in valid JSON with the same keys as the input, containing the Hindi-localized text."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                response_format={"type": "json_object"},
            )

            localized = json.loads(response.choices[0].message.content)

            result = dict(content)
            if "subject" in localized:
                result["subject"] = localized["subject"]
            if "body" in localized:
                result["body"] = localized["body"]
            if "cta_text" in localized:
                result["cta_text"] = localized["cta_text"]
            result["language"] = "hi"

            return result

        except Exception as e:
            logger.warning(f"Hindi localization failed: {e}")
            return self._fallback_localization(content)

    def _fallback_localization(self, content: dict) -> dict:
        result = dict(content)
        result["language"] = "hi"
        result["_localization_note"] = "Localization failed; content remains in original language."
        return result

    def get_language_for_customer(self, customer: dict) -> str:
        language_pref = customer.get("language_preference")
        if language_pref:
            if language_pref.lower() in ("hi", "hindi"):
                return "hi"
            if language_pref.lower() in ("en", "english"):
                return "en"

        state = customer.get("state", "")
        if state in self.HINDI_BELT_STATES:
            return "hi"

        return "en"
