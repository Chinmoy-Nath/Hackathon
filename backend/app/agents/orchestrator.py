import asyncio
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Optional

from openai import AsyncOpenAI

from app.agents.privacy_agent import PrivacyComplianceAgent
from app.agents.customer_intelligence_agent import CustomerIntelligenceAgent
from app.agents.recommendation_engine import RecommendationEngine
from app.agents.content_agent import ContentGenerationAgent
from app.agents.localization_agent import LocalizationAgent
from app.agents.channel_agent import ChannelSelectionAgent
from app.agents.scheduler_agent import SchedulerAgent
from app.agents.execution_agent import CampaignExecutionAgent
from app.agents.analytics_agent import AnalyticsAgent

logger = logging.getLogger(__name__)


class CampaignOrchestrator:

    VEHICLE_KEYWORDS = [
        "nexon", "nexon ev", "punch", "punch ev", "tiago", "tiago ev",
        "tigor", "tigor ev", "harrier", "safari", "curvv", "curvv ev",
        "avinya", "altroz",
    ]

    CITY_KEYWORDS = [
        "mumbai", "delhi", "bangalore", "bengaluru", "chennai", "hyderabad",
        "pune", "kolkata", "ahmedabad", "jaipur", "lucknow", "chandigarh",
        "kochi", "indore", "nagpur", "bhopal", "patna", "thiruvananthapuram",
        "coimbatore", "visakhapatnam", "noida", "gurgaon", "gurugram",
    ]

    FESTIVAL_KEYWORDS = [
        "diwali", "holi", "eid", "christmas", "new year", "pongal",
        "onam", "navratri", "ganesh chaturthi", "dussehra", "baisakhi",
        "raksha bandhan", "independence day", "republic day",
        "makar sankranti", "ugadi",
    ]

    SEGMENT_KEYWORDS = {
        "ev": "ev_interest",
        "electric": "ev_interest",
        "premium": "premium",
        "luxury": "luxury",
        "budget": "budget_conscious",
        "first-time": "first_time_buyer",
        "first time": "first_time_buyer",
        "upgrade": "upgrade_ready",
        "family": "family",
        "suv": "suv_interest",
    }

    def __init__(self, openai_api_key: str = ""):
        self.openai_api_key = openai_api_key
        self.privacy_agent = PrivacyComplianceAgent()
        self.customer_intelligence_agent = CustomerIntelligenceAgent()
        self.recommendation_engine = RecommendationEngine()
        self.content_agent = ContentGenerationAgent(openai_api_key=openai_api_key)
        self.localization_agent = LocalizationAgent(openai_api_key=openai_api_key)
        self.channel_agent = ChannelSelectionAgent()
        self.scheduler_agent = SchedulerAgent()
        self.execution_agent = CampaignExecutionAgent()
        self.analytics_agent = AnalyticsAgent()

        if openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None

    def _create_initial_state(self, campaign: dict, customers: list[dict]) -> dict:
        return {
            "campaign": campaign,
            "customers": customers,
            "customer_profiles": [],
            "recommendations": [],
            "content": [],
            "channel_selections": [],
            "schedules": [],
            "execution_results": {},
            "analytics": {},
            "agent_statuses": [],
            "compliance_results": [],
            "errors": [],
        }

    def _update_agent_status(
        self, state: dict, agent_name: str, status: str, result_summary: str = ""
    ) -> None:
        state["agent_statuses"].append({
            "agent": agent_name,
            "status": status,
            "result_summary": result_summary,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    async def orchestrate_campaign(
        self, campaign: dict, customers: list[dict]
    ) -> dict:
        state = self._create_initial_state(campaign, customers)
        campaign_id = campaign.get("campaign_id", str(uuid.uuid4()))

        try:
            self._update_agent_status(
                state, "Campaign Orchestrator", "started",
                f"Orchestrating campaign '{campaign.get('name', campaign_id)}' for {len(customers)} customers",
            )

            plan = self._parse_campaign_intent(campaign)
            self._update_agent_status(
                state, "Campaign Orchestrator", "plan_created",
                f"Objective: {plan['objective']}, Vehicle: {plan['vehicle_segment']}",
            )

            self._update_agent_status(state, "Customer Intelligence Agent", "started")
            profiles = []
            for customer in customers:
                try:
                    profile = self.customer_intelligence_agent.build_complete_profile(customer)
                    profiles.append(profile)
                except Exception as e:
                    state["errors"].append({
                        "agent": "Customer Intelligence Agent",
                        "customer_id": customer.get("customer_id"),
                        "error": str(e),
                    })
            state["customer_profiles"] = profiles
            self._update_agent_status(
                state, "Customer Intelligence Agent", "completed",
                f"Built {len(profiles)} customer profiles",
            )

            eligible_profiles = []
            eligible_customers = []
            for profile, customer in zip(profiles, customers):
                consent_ok = not customer.get("is_unsubscribed", False)
                if consent_ok:
                    eligible_profiles.append(profile)
                    eligible_customers.append(customer)
            state["customer_profiles"] = eligible_profiles

            if not eligible_profiles:
                self._update_agent_status(
                    state, "Campaign Orchestrator", "completed",
                    "No eligible customers after privacy/consent filtering",
                )
                return state

            self._update_agent_status(state, "Recommendation Engine", "started")
            self._update_agent_status(state, "Channel Selection Agent", "started")

            recommendation_tasks = []
            channel_tasks = []
            for profile, customer in zip(eligible_profiles, eligible_customers):
                customer_data = {
                    **customer,
                    "customer_segment": profile.get("segment", "mid_range"),
                    "vehicle_segment": profile.get("segment", "mid_range"),
                }
                recommendation_tasks.append(
                    asyncio.get_event_loop().run_in_executor(
                        None, self.recommendation_engine.generate_recommendation, customer_data
                    )
                )
                channel_profile = {
                    **customer,
                    "channel_consents": {
                        "email": customer.get("consent_email", True),
                        "whatsapp": customer.get("consent_whatsapp", True),
                        "sms": customer.get("consent_sms", True),
                        "push": customer.get("consent_push", True),
                        "instagram": True,
                        "facebook": True,
                        "youtube": True,
                    },
                }
                channel_tasks.append(
                    asyncio.get_event_loop().run_in_executor(
                        None, self.channel_agent.select_channels, channel_profile, campaign
                    )
                )

            all_results = await asyncio.gather(
                *recommendation_tasks, *channel_tasks, return_exceptions=True
            )

            num_customers = len(eligible_profiles)
            recommendations = []
            channel_selections = []

            for i in range(num_customers):
                rec_result = all_results[i]
                if isinstance(rec_result, Exception):
                    state["errors"].append({
                        "agent": "Recommendation Engine",
                        "customer_id": eligible_customers[i].get("customer_id"),
                        "error": str(rec_result),
                    })
                    recommendations.append({})
                else:
                    recommendations.append(rec_result)

            for i in range(num_customers):
                ch_result = all_results[num_customers + i]
                if isinstance(ch_result, Exception):
                    state["errors"].append({
                        "agent": "Channel Selection Agent",
                        "customer_id": eligible_customers[i].get("customer_id"),
                        "error": str(ch_result),
                    })
                    channel_selections.append({"primary_channel": "email"})
                else:
                    channel_selections.append(ch_result)

            state["recommendations"] = recommendations
            state["channel_selections"] = channel_selections
            self._update_agent_status(
                state, "Recommendation Engine", "completed",
                f"Generated {len(recommendations)} recommendations",
            )
            self._update_agent_status(
                state, "Channel Selection Agent", "completed",
                f"Selected channels for {len(channel_selections)} customers",
            )

            self._update_agent_status(state, "Content Generation Agent", "started")
            self._update_agent_status(state, "Localization Agent", "started")

            content_items = []
            for i, (profile, customer, recommendation, channel_sel) in enumerate(
                zip(eligible_profiles, eligible_customers, recommendations, channel_selections)
            ):
                try:
                    language = self.localization_agent.get_language_for_customer(customer)
                    primary_channel = channel_sel.get("primary_channel", "email")

                    generated = await self.content_agent.generate_content(
                        campaign=campaign,
                        customer_profile={
                            "name": customer.get("name", "Valued Customer"),
                            "customer_id": customer.get("customer_id"),
                            "persona": profile.get("persona", {}),
                            "segment": profile.get("segment", "mid_range"),
                        },
                        recommendation=recommendation,
                        channel=primary_channel,
                        language=language,
                    )

                    if language == "hi" and generated.get("language") != "hi":
                        vehicle_name = recommendation.get("recommended_vehicle", "Tata Vehicle")
                        generated = await self.localization_agent.localize_content(
                            content=generated,
                            target_language="hi",
                            vehicle_name=vehicle_name,
                        )

                    generated["customer_id"] = customer.get("customer_id")
                    generated["channel"] = primary_channel
                    content_items.append(generated)
                except Exception as e:
                    state["errors"].append({
                        "agent": "Content Generation Agent",
                        "customer_id": customer.get("customer_id"),
                        "error": str(e),
                    })

            state["content"] = content_items
            self._update_agent_status(
                state, "Content Generation Agent", "completed",
                f"Generated {len(content_items)} content pieces",
            )
            self._update_agent_status(
                state, "Localization Agent", "completed",
                f"Processed localization for {len(content_items)} items",
            )

            self._update_agent_status(state, "Scheduler Agent", "started")
            schedules = []
            for profile, customer in zip(eligible_profiles, eligible_customers):
                try:
                    schedule_profile = {
                        "email_open_rate": customer.get("email_open_rate", 0.3),
                        "social_engagement": customer.get("social_engagement_score", 0) / 100.0,
                        "customer_type": "B2C",
                        "purchase_intent_score": profile.get("buying_intent", {}).get("intent_score", 50),
                        "has_consent": not customer.get("is_unsubscribed", False),
                    }
                    schedule = self.scheduler_agent.determine_optimal_schedule(
                        schedule_profile, campaign
                    )
                    schedule["customer_id"] = customer.get("customer_id")
                    schedules.append(schedule)
                except Exception as e:
                    state["errors"].append({
                        "agent": "Scheduler Agent",
                        "customer_id": customer.get("customer_id"),
                        "error": str(e),
                    })
            state["schedules"] = schedules
            self._update_agent_status(
                state, "Scheduler Agent", "completed",
                f"Scheduled {len(schedules)} sends",
            )

            self._update_agent_status(state, "Privacy Compliance Agent", "started")
            campaign_compliance = self.privacy_agent.validate_campaign_compliance(campaign)
            state["compliance_results"].append({
                "type": "campaign_compliance",
                "result": campaign_compliance,
            })

            compliant_executions = []
            for content_item in content_items:
                customer_id = content_item.get("customer_id")
                channel = content_item.get("channel", "email")
                customer = next(
                    (c for c in eligible_customers if c.get("customer_id") == customer_id),
                    None,
                )
                if not customer:
                    continue

                consent_check = self.privacy_agent.check_consent(customer, channel)
                state["compliance_results"].append({
                    "type": "consent_check",
                    "customer_id": customer_id,
                    "channel": channel,
                    "result": consent_check,
                })

                if consent_check.get("allowed", False):
                    compliant_executions.append({
                        "customer_id": customer_id,
                        "channel": channel,
                        "content": content_item,
                    })

            self._update_agent_status(
                state, "Privacy Compliance Agent", "completed",
                f"Campaign compliant: {campaign_compliance.get('compliant', False)}, "
                f"{len(compliant_executions)} sends approved out of {len(content_items)}",
            )

            self._update_agent_status(state, "Campaign Execution Agent", "started")
            if compliant_executions:
                execution_results = await self.execution_agent.execute_batch(
                    campaign_id=campaign_id,
                    executions=compliant_executions,
                )
            else:
                execution_results = {
                    "campaign_id": campaign_id,
                    "total": 0,
                    "sent": 0,
                    "delivered": 0,
                    "failed": 0,
                    "results": [],
                }
            state["execution_results"] = execution_results
            self._update_agent_status(
                state, "Campaign Execution Agent", "completed",
                f"Executed {execution_results.get('total', 0)} sends: "
                f"{execution_results.get('delivered', 0)} delivered, "
                f"{execution_results.get('failed', 0)} failed",
            )

            self._update_agent_status(state, "Analytics Agent", "started")
            analytics = self.analytics_agent.generate_campaign_analytics(
                campaign_id=campaign_id,
                execution_results=execution_results,
                customer_count=len(eligible_customers),
            )
            funnel = self.analytics_agent.get_funnel_data(analytics)
            budget = campaign.get("budget", analytics.get("budget", 10000))
            roi_metrics = self.analytics_agent.calculate_roi_metrics(analytics, budget)

            state["analytics"] = {
                "campaign_analytics": analytics,
                "funnel_data": funnel,
                "roi_metrics": roi_metrics,
            }
            self._update_agent_status(
                state, "Analytics Agent", "completed",
                f"ROI: {roi_metrics.get('roi_percentage', 0)}%, "
                f"Revenue: ₹{analytics.get('revenue', 0):,.2f}",
            )

            self._update_agent_status(
                state, "Campaign Orchestrator", "completed",
                f"Campaign orchestration finished. "
                f"{len(eligible_customers)} customers processed, "
                f"{execution_results.get('delivered', 0)} messages delivered.",
            )

        except Exception as e:
            logger.exception("Campaign orchestration failed")
            state["errors"].append({
                "agent": "Campaign Orchestrator",
                "error": str(e),
            })
            self._update_agent_status(state, "Campaign Orchestrator", "failed", str(e))

        return state

    def _parse_campaign_intent(self, campaign: dict) -> dict:
        return {
            "objective": campaign.get("objective", "engagement"),
            "target_audience": campaign.get("target_audience", "all"),
            "kpis": campaign.get("kpis", ["open_rate", "click_rate", "conversions"]),
            "budget": campaign.get("budget", 0),
            "timeline": campaign.get("timeline", ""),
            "vehicle_segment": campaign.get("vehicle_segment", "all"),
            "festival_context": campaign.get("festival_context", ""),
        }

    async def parse_campaign_request(self, user_input: str) -> dict:
        if self.openai_client and self.openai_api_key:
            try:
                return await self._parse_via_llm(user_input)
            except Exception as e:
                logger.warning(f"LLM parsing failed, using rule-based fallback: {e}")

        return self._parse_rule_based(user_input)

    async def _parse_via_llm(self, user_input: str) -> dict:
        prompt = (
            "Extract campaign parameters from the following natural language request. "
            "Return ONLY valid JSON with these keys:\n"
            '{"campaign_objective": "", "target_vehicle": "", "target_city": "", '
            '"target_segment": "", "festival_context": "", "timeframe": ""}\n\n'
            "If a field is not mentioned, use an empty string.\n\n"
            f"Request: {user_input}"
        )

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        import json
        result = json.loads(response.choices[0].message.content)

        return {
            "campaign_objective": result.get("campaign_objective", ""),
            "target_vehicle": result.get("target_vehicle", ""),
            "target_city": result.get("target_city", ""),
            "target_segment": result.get("target_segment", ""),
            "festival_context": result.get("festival_context", ""),
            "timeframe": result.get("timeframe", ""),
        }

    def _parse_rule_based(self, user_input: str) -> dict:
        text = user_input.lower()

        target_vehicle = ""
        for vehicle in sorted(self.VEHICLE_KEYWORDS, key=len, reverse=True):
            if vehicle in text:
                target_vehicle = vehicle.title()
                break

        target_city = ""
        for city in self.CITY_KEYWORDS:
            if city in text:
                target_city = city.title()
                break

        festival_context = ""
        for festival in sorted(self.FESTIVAL_KEYWORDS, key=len, reverse=True):
            if festival in text:
                festival_context = festival.title()
                break

        target_segment = ""
        for keyword, segment in self.SEGMENT_KEYWORDS.items():
            if keyword in text:
                target_segment = segment
                break

        timeframe = ""
        time_patterns = [
            r"(?:within|last|past)\s+(?:the\s+)?(\d+)\s+(year|month|week|day)s?",
            r"(\d+)\s+(year|month|week|day)s?\s+(?:ago|old)",
            r"next\s+(\d+)\s+(year|month|week|day)s?",
        ]
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                timeframe = match.group(0)
                break

        campaign_objective = ""
        objective_keywords = {
            "launch": "product_launch",
            "promote": "promotion",
            "awareness": "awareness",
            "retain": "retention",
            "engage": "engagement",
            "convert": "conversion",
            "upsell": "upsell",
            "cross-sell": "cross_sell",
            "re-engage": "re_engagement",
            "win back": "win_back",
            "test drive": "test_drive_booking",
            "festive": "festive_campaign",
            "seasonal": "seasonal_campaign",
        }
        for keyword, objective in objective_keywords.items():
            if keyword in text:
                campaign_objective = objective
                break
        if not campaign_objective:
            campaign_objective = "engagement"

        return {
            "campaign_objective": campaign_objective,
            "target_vehicle": target_vehicle,
            "target_city": target_city,
            "target_segment": target_segment,
            "festival_context": festival_context,
            "timeframe": timeframe,
        }

    def get_workflow_status(self, state: dict) -> dict:
        statuses = state.get("agent_statuses", [])
        agent_latest = {}
        for entry in statuses:
            agent_latest[entry["agent"]] = {
                "status": entry["status"],
                "result_summary": entry.get("result_summary", ""),
                "timestamp": entry["timestamp"],
            }

        completed = sum(1 for v in agent_latest.values() if v["status"] == "completed")
        failed = sum(1 for v in agent_latest.values() if v["status"] == "failed")
        in_progress = sum(
            1 for v in agent_latest.values()
            if v["status"] not in ("completed", "failed")
        )

        return {
            "total_agents": len(agent_latest),
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "errors": len(state.get("errors", [])),
            "agents": agent_latest,
        }
