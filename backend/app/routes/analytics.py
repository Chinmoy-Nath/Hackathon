import json
import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.analytics_agent import AnalyticsAgent
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Campaign, CampaignAnalytics, CampaignExecution, Customer

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard/campaign-manager")
async def campaign_manager_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status_result = await db.execute(
        select(Campaign.status, func.count(Campaign.id)).group_by(Campaign.status)
    )
    campaign_stats = {row[0]: row[1] for row in status_result.all()}

    recent_result = await db.execute(
        select(Campaign).order_by(Campaign.created_at.desc()).limit(10)
    )
    recent_campaigns = recent_result.scalars().all()

    recent_with_metrics = []
    for c in recent_campaigns:
        analytics_result = await db.execute(
            select(CampaignAnalytics).where(CampaignAnalytics.campaign_id == c.id)
        )
        analytics = analytics_result.scalar_one_or_none()
        metrics = {}
        if analytics:
            metrics = {
                "total_sent": analytics.total_sent,
                "total_delivered": analytics.total_delivered,
                "total_opened": analytics.total_opened,
                "total_clicked": analytics.total_clicked,
                "revenue": analytics.revenue,
                "roi": analytics.roi,
                "effectiveness_score": analytics.effectiveness_score,
            }
        recent_with_metrics.append({
            "campaign_id": c.campaign_id,
            "name": c.name,
            "status": c.status,
            "target_segment": c.target_segment,
            "budget": c.budget,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "metrics": metrics,
        })

    channel_distribution = {}
    exec_result = await db.execute(
        select(CampaignExecution.channel, func.count(CampaignExecution.id))
        .group_by(CampaignExecution.channel)
    )
    for row in exec_result.all():
        channel_distribution[row[0]] = row[1]

    if not channel_distribution:
        channel_distribution = {
            "email": random.randint(2000, 8000),
            "whatsapp": random.randint(1500, 6000),
            "sms": random.randint(1000, 4000),
            "push": random.randint(500, 2000),
            "social": random.randint(800, 3000),
        }

    top_result = await db.execute(
        select(CampaignAnalytics)
        .order_by(CampaignAnalytics.effectiveness_score.desc())
        .limit(5)
    )
    top_analytics = top_result.scalars().all()
    top_performing = []
    for a in top_analytics:
        camp_result = await db.execute(
            select(Campaign).where(Campaign.id == a.campaign_id)
        )
        camp = camp_result.scalar_one_or_none()
        if camp:
            top_performing.append({
                "campaign_id": camp.campaign_id,
                "name": camp.name,
                "effectiveness_score": a.effectiveness_score,
                "roi": a.roi,
                "revenue": a.revenue,
                "total_sent": a.total_sent,
                "purchases": a.purchases,
            })

    return {
        "campaign_stats": campaign_stats,
        "recent_campaigns": recent_with_metrics,
        "channel_distribution": channel_distribution,
        "top_performing": top_performing,
    }


@router.get("/dashboard/retail-manager")
async def retail_manager_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    revenue_result = await db.execute(
        select(func.sum(CampaignAnalytics.revenue))
    )
    total_revenue = revenue_result.scalar() or 0.0

    budget_result = await db.execute(
        select(func.sum(Campaign.budget))
    )
    total_budget = budget_result.scalar() or 0.0

    purchases_result = await db.execute(
        select(func.sum(CampaignAnalytics.purchases))
    )
    total_purchases = purchases_result.scalar() or 0

    overall_roi = round(((total_revenue - total_budget) / total_budget) * 100, 2) if total_budget > 0 else 0.0

    analytics_agent = AnalyticsAgent()

    states = ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi NCR", "Gujarat",
              "Telangana", "West Bengal", "Rajasthan", "Kerala", "Uttar Pradesh"]
    dealer_performance = analytics_agent.generate_dealer_performance(states)
    vehicle_segment_performance = analytics_agent.generate_vehicle_segment_performance()

    effectiveness_result = await db.execute(
        select(func.avg(CampaignAnalytics.effectiveness_score))
    )
    avg_effectiveness = round(effectiveness_result.scalar() or 0.0, 2)

    campaign_count_result = await db.execute(select(func.count(Campaign.id)))
    total_campaigns = campaign_count_result.scalar() or 0

    active_result = await db.execute(
        select(func.count(Campaign.id)).where(Campaign.status == "active")
    )
    active_campaigns = active_result.scalar() or 0

    customer_count_result = await db.execute(select(func.count(Customer.id)))
    total_customers = customer_count_result.scalar() or 0

    return {
        "revenue_summary": {
            "total_revenue": round(total_revenue, 2),
            "total_budget": round(total_budget, 2),
            "total_purchases": total_purchases,
            "overall_roi": overall_roi,
        },
        "dealer_performance": dealer_performance,
        "vehicle_segment_performance": vehicle_segment_performance,
        "campaign_effectiveness": {
            "avg_effectiveness_score": avg_effectiveness,
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
        },
        "executive_kpis": {
            "total_customers": total_customers,
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_revenue": round(total_revenue, 2),
            "overall_roi": overall_roi,
            "avg_effectiveness": avg_effectiveness,
        },
    }


@router.get("/campaigns/{campaign_id}/funnel")
async def get_campaign_funnel(
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

    analytics_agent = AnalyticsAgent()
    analytics_dict = {
        "sent": analytics.total_sent,
        "delivered": analytics.total_delivered,
        "opened": analytics.total_opened,
        "clicked": analytics.total_clicked,
        "brochure_downloads": analytics.brochure_downloads,
        "dealer_visits": analytics.dealer_visits,
        "test_drive_bookings": analytics.test_drive_bookings,
        "vehicle_inquiries": analytics.vehicle_inquiries,
        "quotations": analytics.quotations,
        "bookings": analytics.bookings,
        "purchases": analytics.purchases,
    }
    funnel = analytics_agent.get_funnel_data(analytics_dict)
    return {"campaign_id": campaign_id, "funnel": funnel}


@router.get("/campaigns/{campaign_id}/roi")
async def get_campaign_roi(
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

    analytics_agent = AnalyticsAgent()
    analytics_dict = {
        "clicked": analytics.total_clicked,
        "brochure_downloads": analytics.brochure_downloads,
        "purchases": analytics.purchases,
        "revenue": analytics.revenue,
    }
    budget = campaign.budget or 0.0
    roi_metrics = analytics_agent.calculate_roi_metrics(analytics_dict, budget)
    return {"campaign_id": campaign_id, "roi_metrics": roi_metrics}


@router.get("/dealer-performance")
async def get_dealer_performance(
    current_user: dict = Depends(get_current_user),
):
    analytics_agent = AnalyticsAgent()
    states = ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi NCR", "Gujarat",
              "Telangana", "West Bengal", "Rajasthan", "Kerala", "Uttar Pradesh"]
    return analytics_agent.generate_dealer_performance(states)


@router.get("/vehicle-segments")
async def get_vehicle_segments(
    current_user: dict = Depends(get_current_user),
):
    analytics_agent = AnalyticsAgent()
    return analytics_agent.generate_vehicle_segment_performance()
