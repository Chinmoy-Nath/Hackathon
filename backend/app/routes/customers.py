from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.customer_intelligence_agent import CustomerIntelligenceAgent
from app.agents.privacy_agent import PrivacyComplianceAgent
from app.agents.recommendation_engine import RecommendationEngine
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Customer
from app.schemas.schemas import CustomerResponse

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("/segments/summary")
async def get_segments_summary(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    segment_result = await db.execute(
        select(Customer.customer_segment, func.count(Customer.id))
        .group_by(Customer.customer_segment)
    )
    segment_counts = {row[0]: row[1] for row in segment_result.all()}

    all_customers = await db.execute(select(Customer.purchase_intent_score))
    scores = [row[0] for row in all_customers.all()]
    intent_counts = {"low": 0, "medium": 0, "high": 0}
    for s in scores:
        if s is None or s < 30:
            intent_counts["low"] += 1
        elif s <= 65:
            intent_counts["medium"] += 1
        else:
            intent_counts["high"] += 1

    channel_result = await db.execute(
        select(Customer.preferred_channel, func.count(Customer.id))
        .group_by(Customer.preferred_channel)
    )
    channel_counts = {row[0]: row[1] for row in channel_result.all()}

    return {
        "segments": segment_counts,
        "intent_levels": intent_counts,
        "preferred_channels": channel_counts,
    }


@router.get("/", response_model=list[CustomerResponse])
async def list_customers(
    segment: str | None = None,
    city: str | None = None,
    state: str | None = None,
    intent_level: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Customer)
    if segment:
        query = query.where(Customer.customer_segment == segment)
    if city:
        query = query.where(Customer.city == city)
    if state:
        query = query.where(Customer.state == state)
    if intent_level:
        if intent_level == "low":
            query = query.where(Customer.purchase_intent_score < 30)
        elif intent_level == "medium":
            query = query.where(
                Customer.purchase_intent_score >= 30,
                Customer.purchase_intent_score <= 65,
            )
        elif intent_level == "high":
            query = query.where(Customer.purchase_intent_score > 65)

    query = query.order_by(Customer.id).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    customers = result.scalars().all()

    privacy_agent = PrivacyComplianceAgent()
    anonymized = []
    for c in customers:
        customer_dict = {
            "email": c.email,
            "phone": c.phone,
            "annual_income": c.annual_income,
        }
        anon = privacy_agent.anonymize_customer_data(customer_dict)
        c.email = anon.get("email", c.email)
        c.phone = anon.get("phone", c.phone)
        anonymized.append(c)

    return anonymized


@router.get("/{customer_id}/profile")
async def get_customer_profile(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Customer).where(Customer.customer_id == customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    customer_dict = {
        "customer_id": customer.customer_id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "phone": customer.phone,
        "city": customer.city,
        "state": customer.state,
        "language_preference": customer.language_preference,
        "age": customer.age,
        "gender": customer.gender,
        "annual_income": customer.annual_income,
        "current_vehicle": customer.current_vehicle,
        "current_vehicle_year": customer.current_vehicle_year,
        "vehicle_year": customer.current_vehicle_year,
        "service_count": customer.service_count,
        "website_visits": customer.website_visits,
        "ev_page_views": customer.ev_page_views,
        "brochure_downloads": customer.brochure_downloads,
        "test_drives_taken": customer.test_drives_taken,
        "social_engagement_score": customer.social_engagement_score,
        "email_open_rate": customer.email_open_rate,
        "campaign_response_rate": customer.campaign_response_rate,
        "consent_email": customer.consent_email,
        "consent_whatsapp": customer.consent_whatsapp,
        "consent_sms": customer.consent_sms,
        "consent_push": customer.consent_push,
        "consent_social": customer.consent_social,
        "is_unsubscribed": customer.is_unsubscribed,
        "preferred_channel": customer.preferred_channel,
        "vehicle_segment": customer.vehicle_segment,
        "customer_segment": customer.customer_segment,
        "purchase_intent_score": customer.purchase_intent_score,
    }

    intelligence_agent = CustomerIntelligenceAgent()
    profile = intelligence_agent.build_complete_profile(customer_dict)
    return profile


@router.get("/{customer_id}/recommendation")
async def get_customer_recommendation(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Customer).where(Customer.customer_id == customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    customer_dict = {
        "customer_id": customer.customer_id,
        "age": customer.age,
        "annual_income": customer.annual_income,
        "current_vehicle": customer.current_vehicle,
        "current_vehicle_year": customer.current_vehicle_year,
        "service_count": customer.service_count,
        "website_visits": customer.website_visits,
        "ev_page_views": customer.ev_page_views,
        "brochure_downloads": customer.brochure_downloads,
        "test_drives_taken": customer.test_drives_taken,
        "social_engagement_score": customer.social_engagement_score,
        "email_open_rate": customer.email_open_rate,
        "campaign_response_rate": customer.campaign_response_rate,
        "vehicle_segment": customer.vehicle_segment,
        "customer_segment": customer.customer_segment,
    }

    engine = RecommendationEngine()
    recommendation = engine.generate_recommendation(customer_dict)
    return recommendation
