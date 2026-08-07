import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="campaign_manager")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaigns = relationship("Campaign", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="user")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(String(100), unique=True, index=True, default=generate_uuid)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(20))
    city = Column(String(100))
    state = Column(String(100))
    language_preference = Column(String(10), default="en")
    age = Column(Integer)
    gender = Column(String(20))
    annual_income = Column(Float)
    current_vehicle = Column(String(100))
    current_vehicle_year = Column(Integer)
    purchase_date = Column(DateTime)
    service_count = Column(Integer, default=0)
    last_service_date = Column(DateTime)
    website_visits = Column(Integer, default=0)
    ev_page_views = Column(Integer, default=0)
    brochure_downloads = Column(Integer, default=0)
    test_drives_taken = Column(Integer, default=0)
    social_engagement_score = Column(Float, default=0.0)
    email_open_rate = Column(Float, default=0.0)
    campaign_response_rate = Column(Float, default=0.0)
    consent_email = Column(Boolean, default=False)
    consent_whatsapp = Column(Boolean, default=False)
    consent_sms = Column(Boolean, default=False)
    consent_push = Column(Boolean, default=False)
    consent_social = Column(Boolean, default=False)
    is_unsubscribed = Column(Boolean, default=False)
    unsubscribed_at = Column(DateTime, nullable=True)
    preferred_channel = Column(String(50))
    vehicle_segment = Column(String(50))
    customer_segment = Column(String(100))
    purchase_intent_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    executions = relationship("CampaignExecution", back_populates="customer")
    recommendations = relationship("Recommendation", back_populates="customer")
    consent_logs = relationship("ConsentLog", back_populates="customer")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    segment = Column(String(50), nullable=False)
    price_range_min = Column(Float)
    price_range_max = Column(Float)
    key_features = Column(String(2000))
    target_audience = Column(String(500))
    is_active = Column(Boolean, default=True)

    campaigns = relationship("Campaign", back_populates="vehicle")
    recommendations = relationship("Recommendation", back_populates="recommended_vehicle")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(String(100), unique=True, index=True, default=generate_uuid)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    objective = Column(String(500))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    target_segment = Column(String(100))
    target_cities = Column(String(2000))
    target_states = Column(String(2000))
    budget = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50), default="draft")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    festival_context = Column(String(200))
    channels = Column(String(1000))
    languages = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="campaigns")
    creator = relationship("User", back_populates="campaigns")
    contents = relationship("CampaignContent", back_populates="campaign")
    executions = relationship("CampaignExecution", back_populates="campaign")
    recommendations = relationship("Recommendation", back_populates="campaign")
    analytics = relationship("CampaignAnalytics", back_populates="campaign", uselist=False)


class CampaignContent(Base):
    __tablename__ = "campaign_contents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    channel = Column(String(50), nullable=False)
    language = Column(String(10), default="en")
    subject = Column(String(500))
    body = Column(Text)
    cta_text = Column(String(200))
    cta_url = Column(String(500))
    media_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="contents")


class CampaignExecution(Base):
    __tablename__ = "campaign_executions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    channel = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    campaign = relationship("Campaign", back_populates="executions")
    customer = relationship("Customer", back_populates="executions")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    recommended_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    confidence_score = Column(Float, nullable=False)
    reasoning = Column(Text)
    intent_score = Column(Float)
    rule_triggers = Column(String(2000))
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="recommendations")
    campaign = relationship("Campaign", back_populates="recommendations")
    recommended_vehicle = relationship("Vehicle", back_populates="recommendations")


class CampaignAnalytics(Base):
    __tablename__ = "campaign_analytics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), unique=True, nullable=False)
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    total_replies = Column(Integer, default=0)
    brochure_downloads = Column(Integer, default=0)
    dealer_visits = Column(Integer, default=0)
    test_drive_bookings = Column(Integer, default=0)
    vehicle_inquiries = Column(Integer, default=0)
    quotations = Column(Integer, default=0)
    bookings = Column(Integer, default=0)
    purchases = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    effectiveness_score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="analytics")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(100))
    details = Column(Text)
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


class ConsentLog(Base):
    __tablename__ = "consent_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    channel = Column(String(50), nullable=False)
    consent_given = Column(Boolean, nullable=False)
    consent_date = Column(DateTime, default=datetime.utcnow)
    source = Column(String(100))

    customer = relationship("Customer", back_populates="consent_logs")
