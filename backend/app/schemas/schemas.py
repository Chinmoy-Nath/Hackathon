from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "campaign_manager"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    language_preference: Optional[str] = "en"
    age: Optional[int] = None
    gender: Optional[str] = None
    current_vehicle: Optional[str] = None
    current_vehicle_year: Optional[int] = None
    vehicle_segment: Optional[str] = None
    customer_segment: Optional[str] = None
    purchase_intent_score: Optional[float] = 0.0
    preferred_channel: Optional[str] = None
    consent_email: bool = False
    consent_whatsapp: bool = False
    consent_sms: bool = False
    consent_push: bool = False
    consent_social: bool = False
    is_unsubscribed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CustomerPersona(BaseModel):
    persona: str
    buying_intent: str
    segment: str
    preferred_channel: str
    preferred_language: str
    vehicle_ownership_profile: str


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    segment: str
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    key_features: Optional[str] = None
    target_audience: Optional[str] = None
    is_active: bool = True


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    objective: Optional[str] = None
    vehicle_id: Optional[int] = None
    target_segment: Optional[str] = None
    target_cities: Optional[list[str]] = None
    target_states: Optional[list[str]] = None
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    festival_context: Optional[str] = None
    channels: Optional[list[str]] = None
    languages: Optional[list[str]] = None


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: str
    name: str
    description: Optional[str] = None
    objective: Optional[str] = None
    vehicle_id: Optional[int] = None
    target_segment: Optional[str] = None
    target_cities: Optional[str] = None
    target_states: Optional[str] = None
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "draft"
    created_by: Optional[int] = None
    festival_context: Optional[str] = None
    channels: Optional[str] = None
    languages: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CampaignContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: int
    channel: str
    language: str = "en"
    subject: Optional[str] = None
    body: Optional[str] = None
    cta_text: Optional[str] = None
    cta_url: Optional[str] = None
    media_url: Optional[str] = None
    created_at: Optional[datetime] = None


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    campaign_id: Optional[int] = None
    recommended_vehicle_id: int
    confidence_score: float
    reasoning: Optional[str] = None
    intent_score: Optional[float] = None
    created_at: Optional[datetime] = None


class ChannelRecommendation(BaseModel):
    primary_channel: str
    secondary_channel: str
    channel_confidence: float
    reasoning: str


class ScheduleRecommendation(BaseModel):
    best_day: str
    best_time: str
    expected_engagement_score: float
    reasoning: str


class AnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: int
    total_sent: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_replies: int = 0
    brochure_downloads: int = 0
    dealer_visits: int = 0
    test_drive_bookings: int = 0
    vehicle_inquiries: int = 0
    quotations: int = 0
    bookings: int = 0
    purchases: int = 0
    revenue: float = 0.0
    roi: float = 0.0
    effectiveness_score: float = 0.0
    updated_at: Optional[datetime] = None


class CampaignExecutionStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: int
    customer_id: int
    channel: str
    status: str = "pending"
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0


class AgentStatus(BaseModel):
    agent_name: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_summary: Optional[str] = None


class OrchestratorPlan(BaseModel):
    campaign_objective: str
    target_audience: str
    kpis: list[str]
    budget: float
    timeline: str
    vehicle_segment: str
    execution_plan: list[AgentStatus]
