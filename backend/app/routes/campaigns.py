import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import CampaignOrchestrator
from app.core.config import settings
from app.core.database import get_db
from app.core.rbac import require_role
from app.core.security import get_current_user
from app.models.models import (
    AuditLog,
    Campaign,
    CampaignAnalytics,
    CampaignContent,
    CampaignExecution,
    Customer,
    Recommendation,
)
from app.schemas.schemas import (
    AnalyticsResponse,
    CampaignContentResponse,
    CampaignCreate,
    CampaignResponse,
)

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

VALID_STATUS_TRANSITIONS = {
    "draft": ["active", "cancelled"],
    "active": ["paused", "completed", "cancelled"],
    "paused": ["active", "cancelled"],
    "completed": [],
    "cancelled": [],
}


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: dict = Depends(require_role(["campaign_manager", "CAMPAIGN_MANAGER"])),
    db: AsyncSession = Depends(get_db),
):
    campaign = Campaign(
        campaign_id=str(uuid.uuid4()),
        name=campaign_data.name,
        description=campaign_data.description,
        objective=campaign_data.objective,
        vehicle_id=campaign_data.vehicle_id,
        target_segment=campaign_data.target_segment,
        target_cities=json.dumps(campaign_data.target_cities) if campaign_data.target_cities else None,
        target_states=json.dumps(campaign_data.target_states) if campaign_data.target_states else None,
        budget=campaign_data.budget,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        status="draft",
        created_by=current_user.get("user_id"),
        festival_context=campaign_data.festival_context,
        channels=json.dumps(campaign_data.channels) if campaign_data.channels else None,
        languages=json.dumps(campaign_data.languages) if campaign_data.languages else None,
    )
    db.add(campaign)
    await db.flush()

    audit_log = AuditLog(
        user_id=current_user.get("user_id"),
        action="campaign_created",
        resource_type="campaign",
        resource_id=campaign.campaign_id,
        details=json.dumps({"name": campaign.name, "objective": campaign.objective}),
    )
    db.add(audit_log)
    await db.flush()
    await db.refresh(campaign)
    return campaign


@router.get("/", response_model=list[CampaignResponse])
async def list_campaigns(
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Campaign)
    if status_filter:
        query = query.where(Campaign.status == status_filter)
    query = query.order_by(Campaign.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    campaigns = result.scalars().all()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(Campaign.campaign_id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return campaign


@router.post("/{campaign_id}/execute")
async def execute_campaign(
    campaign_id: str,
    current_user: dict = Depends(require_role(["campaign_manager", "CAMPAIGN_MANAGER"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(Campaign.campaign_id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    customer_query = select(Customer).where(Customer.is_unsubscribed == False)
    if campaign.target_segment:
        customer_query = customer_query.where(
            Customer.customer_segment == campaign.target_segment
        )
    if campaign.target_cities:
        try:
            cities = json.loads(campaign.target_cities)
            if cities:
                customer_query = customer_query.where(Customer.city.in_(cities))
        except (json.JSONDecodeError, TypeError):
            pass
    if campaign.target_states:
        try:
            states = json.loads(campaign.target_states)
            if states:
                customer_query = customer_query.where(Customer.state.in_(states))
        except (json.JSONDecodeError, TypeError):
            pass

    cust_result = await db.execute(customer_query)
    customers = cust_result.scalars().all()

    campaign_dict = {
        "campaign_id": campaign.campaign_id,
        "name": campaign.name,
        "description": campaign.description,
        "objective": campaign.objective,
        "target_segment": campaign.target_segment,
        "budget": campaign.budget,
        "festival_context": campaign.festival_context,
        "channels": campaign.channels,
        "languages": campaign.languages,
    }

    customer_dicts = []
    for c in customers:
        customer_dicts.append({
            "customer_id": c.customer_id,
            "name": f"{c.first_name} {c.last_name}",
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "phone": c.phone,
            "city": c.city,
            "state": c.state,
            "language_preference": c.language_preference,
            "age": c.age,
            "gender": c.gender,
            "annual_income": c.annual_income,
            "current_vehicle": c.current_vehicle,
            "current_vehicle_year": c.current_vehicle_year,
            "service_count": c.service_count,
            "website_visits": c.website_visits,
            "ev_page_views": c.ev_page_views,
            "brochure_downloads": c.brochure_downloads,
            "test_drives_taken": c.test_drives_taken,
            "social_engagement_score": c.social_engagement_score,
            "email_open_rate": c.email_open_rate,
            "campaign_response_rate": c.campaign_response_rate,
            "consent_email": c.consent_email,
            "consent_whatsapp": c.consent_whatsapp,
            "consent_sms": c.consent_sms,
            "consent_push": c.consent_push,
            "consent_social": c.consent_social,
            "is_unsubscribed": c.is_unsubscribed,
            "preferred_channel": c.preferred_channel,
            "vehicle_segment": c.vehicle_segment,
            "customer_segment": c.customer_segment,
            "purchase_intent_score": c.purchase_intent_score,
        })

    orchestrator = CampaignOrchestrator(openai_api_key=settings.OPENAI_API_KEY)
    orchestration_result = await orchestrator.orchestrate_campaign(campaign_dict, customer_dicts)

    for content_item in orchestration_result.get("content", []):
        content_record = CampaignContent(
            campaign_id=campaign.id,
            channel=content_item.get("channel", "email"),
            language=content_item.get("language", "en"),
            subject=content_item.get("subject", ""),
            body=content_item.get("body", ""),
            cta_text=content_item.get("cta_text", ""),
            cta_url=content_item.get("cta_url", ""),
        )
        db.add(content_record)

    exec_results = orchestration_result.get("execution_results", {})
    for exec_item in exec_results.get("results", []):
        cust_result_q = await db.execute(
            select(Customer).where(Customer.customer_id == exec_item.get("customer_id"))
        )
        cust_obj = cust_result_q.scalar_one_or_none()
        if cust_obj:
            execution_record = CampaignExecution(
                campaign_id=campaign.id,
                customer_id=cust_obj.id,
                channel=exec_item.get("channel", "email"),
                status=exec_item.get("status", "sent"),
                sent_at=datetime.utcnow() if exec_item.get("status") in ("sent", "delivered") else None,
                delivered_at=datetime.utcnow() if exec_item.get("status") == "delivered" else None,
            )
            db.add(execution_record)

    for rec_item in orchestration_result.get("recommendations", []):
        if not rec_item:
            continue
        recommended_vehicle_name = rec_item.get("recommended_vehicle")
        if not recommended_vehicle_name:
            continue
        from app.models.models import Vehicle
        veh_result = await db.execute(
            select(Vehicle).where(Vehicle.name == recommended_vehicle_name)
        )
        veh_obj = veh_result.scalar_one_or_none()
        if not veh_obj:
            continue
        customer_id_str = rec_item.get("customer_id")
        if customer_id_str:
            cr = await db.execute(
                select(Customer).where(Customer.customer_id == customer_id_str)
            )
            cust_for_rec = cr.scalar_one_or_none()
        else:
            cust_for_rec = None
        if cust_for_rec:
            rec_record = Recommendation(
                customer_id=cust_for_rec.id,
                campaign_id=campaign.id,
                recommended_vehicle_id=veh_obj.id,
                confidence_score=rec_item.get("confidence_score", 0.0),
                reasoning=rec_item.get("reasoning", ""),
                intent_score=rec_item.get("intent_score", 0.0),
                rule_triggers=json.dumps(rec_item.get("rule_triggers", [])),
            )
            db.add(rec_record)

    analytics_data = orchestration_result.get("analytics", {}).get("campaign_analytics", {})
    if analytics_data:
        existing_analytics = await db.execute(
            select(CampaignAnalytics).where(CampaignAnalytics.campaign_id == campaign.id)
        )
        if existing_analytics.scalar_one_or_none() is None:
            analytics_record = CampaignAnalytics(
                campaign_id=campaign.id,
                total_sent=analytics_data.get("sent", 0),
                total_delivered=analytics_data.get("delivered", 0),
                total_failed=exec_results.get("failed", 0),
                total_opened=analytics_data.get("opened", 0),
                total_clicked=analytics_data.get("clicked", 0),
                total_replies=analytics_data.get("replies", 0),
                brochure_downloads=analytics_data.get("brochure_downloads", 0),
                dealer_visits=analytics_data.get("dealer_visits", 0),
                test_drive_bookings=analytics_data.get("test_drive_bookings", 0),
                vehicle_inquiries=analytics_data.get("vehicle_inquiries", 0),
                quotations=analytics_data.get("quotations", 0),
                bookings=analytics_data.get("bookings", 0),
                purchases=analytics_data.get("purchases", 0),
                revenue=analytics_data.get("revenue", 0.0),
                roi=analytics_data.get("roi", 0.0),
                effectiveness_score=analytics_data.get("effectiveness_score", 0.0),
            )
            db.add(analytics_record)

    campaign.status = "active"
    await db.flush()

    workflow_status = orchestrator.get_workflow_status(orchestration_result)

    return {
        "campaign_id": campaign.campaign_id,
        "status": "active",
        "customers_targeted": len(customer_dicts),
        "content_generated": len(orchestration_result.get("content", [])),
        "executions": exec_results.get("total", 0),
        "delivered": exec_results.get("delivered", 0),
        "failed": exec_results.get("failed", 0),
        "analytics_summary": orchestration_result.get("analytics", {}),
        "workflow_status": workflow_status,
        "errors": orchestration_result.get("errors", []),
    }


@router.get("/{campaign_id}/analytics", response_model=AnalyticsResponse)
async def get_campaign_analytics(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(Campaign.campaign_id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    analytics_result = await db.execute(
        select(CampaignAnalytics).where(CampaignAnalytics.campaign_id == campaign.id)
    )
    analytics = analytics_result.scalar_one_or_none()
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analytics not found for this campaign",
        )
    return analytics


@router.get("/{campaign_id}/content", response_model=list[CampaignContentResponse])
async def get_campaign_content(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(Campaign.campaign_id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    content_result = await db.execute(
        select(CampaignContent).where(CampaignContent.campaign_id == campaign.id)
    )
    contents = content_result.scalars().all()
    return contents


@router.patch("/{campaign_id}/status")
async def update_campaign_status(
    campaign_id: str,
    status_update: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status field is required",
        )

    result = await db.execute(
        select(Campaign).where(Campaign.campaign_id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    allowed = VALID_STATUS_TRANSITIONS.get(campaign.status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from '{campaign.status}' to '{new_status}'. Allowed: {allowed}",
        )

    campaign.status = new_status
    await db.flush()
    return {"campaign_id": campaign.campaign_id, "status": campaign.status}


@router.post("/parse-request")
async def parse_campaign_request(
    request_data: dict,
    current_user: dict = Depends(get_current_user),
):
    user_input = request_data.get("user_input", "")
    if not user_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_input is required",
        )

    orchestrator = CampaignOrchestrator(openai_api_key=settings.OPENAI_API_KEY)
    parsed = await orchestrator.parse_campaign_request(user_input)
    return parsed
