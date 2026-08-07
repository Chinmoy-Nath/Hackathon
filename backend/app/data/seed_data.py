import json
import random
import uuid
from datetime import datetime, timedelta

from app.core.security import get_password_hash
from app.models.models import (
    AuditLog,
    Campaign,
    CampaignAnalytics,
    CampaignContent,
    ConsentLog,
    Customer,
    User,
    Vehicle,
)

TATA_VEHICLES = [
    {
        "name": "Tiago",
        "category": "Petrol",
        "segment": "Mid Range",
        "price_range_min": 5.5,
        "price_range_max": 8.5,
        "key_features": [
            "Harman Infotainment System",
            "Connected Car Tech",
            "Dual Airbags",
            "ABS with EBD",
            "Revotron 1.2L Engine",
            "Multi-drive Modes",
        ],
        "target_audience": "Young professionals and first-time car buyers seeking a reliable, feature-rich hatchback",
    },
    {
        "name": "Tigor",
        "category": "Petrol",
        "segment": "Mid Range",
        "price_range_min": 6.5,
        "price_range_max": 10.0,
        "key_features": [
            "Stylish Sedan Design",
            "Harman Infotainment",
            "Automatic Climate Control",
            "Projector Headlamps",
            "Revotron 1.2L Engine",
            "Boot Space 419L",
        ],
        "target_audience": "Budget-conscious families looking for a compact sedan with premium features",
    },
    {
        "name": "Punch",
        "category": "Petrol",
        "segment": "Mid Range",
        "price_range_min": 6.0,
        "price_range_max": 10.0,
        "key_features": [
            "ALFA Architecture",
            "Terrain Response Modes",
            "90-degree Door Opening",
            "Touchscreen Infotainment",
            "Dual Airbags",
            "5-Star GNCAP Safety",
        ],
        "target_audience": "Urban adventurers and young families wanting a micro-SUV with rugged capability",
    },
    {
        "name": "Nexon",
        "category": "Petrol",
        "segment": "Mid Range",
        "price_range_min": 8.0,
        "price_range_max": 15.0,
        "key_features": [
            "5-Star GNCAP Safety",
            "Connected Car Tech",
            "Ventilated Seats",
            "Electric Sunroof",
            "Terrain Response Modes",
            "iRA Connected Car Technology",
        ],
        "target_audience": "Safety-conscious families and professionals seeking a feature-loaded compact SUV",
    },
    {
        "name": "Nexon EV",
        "category": "EV",
        "segment": "Premium",
        "price_range_min": 14.5,
        "price_range_max": 20.0,
        "key_features": [
            "Ziptron EV Technology",
            "312 km Range",
            "Fast Charging",
            "Connected Car Tech",
            "Regenerative Braking",
            "Multi-mode Regen",
            "iRA Connected Car Technology",
        ],
        "target_audience": "Eco-conscious urban professionals ready to switch to electric mobility",
    },
    {
        "name": "Curvv",
        "category": "Petrol",
        "segment": "Premium",
        "price_range_min": 10.0,
        "price_range_max": 18.0,
        "key_features": [
            "Coupe SUV Design",
            "Panoramic Sunroof",
            "Level 2 ADAS",
            "Ventilated Front Seats",
            "360-degree Camera",
            "10.25-inch Touchscreen",
        ],
        "target_audience": "Style-conscious millennials and professionals seeking a premium coupe-SUV experience",
    },
    {
        "name": "Curvv EV",
        "category": "EV",
        "segment": "Premium",
        "price_range_min": 17.5,
        "price_range_max": 22.0,
        "key_features": [
            "Acti.ev Platform",
            "500+ km Range",
            "Fast Charging DC",
            "Coupe SUV Design",
            "Level 2 ADAS",
            "Connected Car Tech",
            "Vehicle-to-Load",
        ],
        "target_audience": "Tech-savvy early adopters wanting a stylish electric coupe-SUV with cutting-edge features",
    },
    {
        "name": "Harrier",
        "category": "Petrol",
        "segment": "Premium",
        "price_range_min": 15.0,
        "price_range_max": 26.0,
        "key_features": [
            "OMEGARC Architecture",
            "Panoramic Sunroof",
            "JBL Sound System",
            "ADAS Suite",
            "Fiat 2.0L Kryotec Engine",
            "Terrain Response Modes",
            "Connected Car Tech",
        ],
        "target_audience": "Premium SUV buyers seeking a commanding road presence with advanced features",
    },
    {
        "name": "Safari",
        "category": "Petrol",
        "segment": "Premium",
        "price_range_min": 16.0,
        "price_range_max": 28.0,
        "key_features": [
            "OMEGARC Architecture",
            "Captain Seats Option",
            "6/7 Seater Configuration",
            "JBL Sound System",
            "ADAS Suite",
            "Panoramic Sunroof",
            "Terrain Response Modes",
        ],
        "target_audience": "Large families and enthusiasts wanting a flagship 3-row SUV with heritage appeal",
    },
    {
        "name": "Tiago EV",
        "category": "EV",
        "segment": "Mid Range",
        "price_range_min": 8.5,
        "price_range_max": 12.0,
        "key_features": [
            "Ziptron EV Technology",
            "315 km Range",
            "DC Fast Charging",
            "Regenerative Braking",
            "Connected Car Tech",
            "Multi-mode Regen",
        ],
        "target_audience": "First-time EV buyers looking for an affordable and practical electric hatchback",
    },
    {
        "name": "Punch EV",
        "category": "EV",
        "segment": "Mid Range",
        "price_range_min": 10.0,
        "price_range_max": 14.0,
        "key_features": [
            "Acti.ev Platform",
            "421 km Range",
            "Fast Charging",
            "Connected Car Tech",
            "Terrain Response Modes",
            "Regenerative Braking",
        ],
        "target_audience": "Urban commuters seeking an affordable electric micro-SUV with SUV practicality",
    },
    {
        "name": "Avinya (Concept)",
        "category": "EV",
        "segment": "Luxury",
        "price_range_min": 30.0,
        "price_range_max": 50.0,
        "key_features": [
            "Gen 3 EV Architecture",
            "500+ km Range",
            "Ultra-fast Charging",
            "Autonomous Driving Ready",
            "Lounge-like Interior",
            "AI-powered Cabin",
            "Sustainable Materials",
        ],
        "target_audience": "Visionary luxury EV enthusiasts and early adopters awaiting Tata's flagship electric concept",
    },
]

INDIAN_CITIES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Karnataka": ["Bangalore", "Mysore"],
    "Tamil Nadu": ["Chennai", "Coimbatore"],
    "Delhi NCR": ["New Delhi", "Gurgaon", "Noida"],
    "Gujarat": ["Ahmedabad", "Surat"],
    "Telangana": ["Hyderabad"],
    "West Bengal": ["Kolkata"],
    "Rajasthan": ["Jaipur"],
    "Kerala": ["Kochi", "Thiruvananthapuram"],
    "Uttar Pradesh": ["Lucknow"],
}

FESTIVALS = [
    {"name": "Makar Sankranti", "month": 1, "marketing_theme": "New Beginnings Drive - Start your year with a new Tata vehicle"},
    {"name": "Holi", "month": 3, "marketing_theme": "Colors of Innovation - Experience the vibrant range of Tata Motors"},
    {"name": "Ugadi/Gudi Padwa", "month": 4, "marketing_theme": "Auspicious Drives - Celebrate new year traditions with a new ride"},
    {"name": "Akshaya Tritiya", "month": 5, "marketing_theme": "Golden Opportunities - Invest in your dream Tata vehicle today"},
    {"name": "Independence Day", "month": 8, "marketing_theme": "Freedom to Explore - Drive the pride of India with Tata Motors"},
    {"name": "Onam", "month": 9, "marketing_theme": "Prosperity on Wheels - Celebrate Onam with exclusive Tata offers"},
    {"name": "Ganesh Chaturthi", "month": 9, "marketing_theme": "Auspicious Beginnings - Bring home blessings and a new Tata car"},
    {"name": "Navratri", "month": 10, "marketing_theme": "Nine Nights of Power - Unleash the power of Tata SUVs"},
    {"name": "Dussehra", "month": 10, "marketing_theme": "Victory Drives - Conquer every road with Tata Motors"},
    {"name": "Diwali", "month": 11, "marketing_theme": "Festival of Lights Special - Illuminate your journey with Tata vehicles"},
    {"name": "Christmas/New Year", "month": 12, "marketing_theme": "Year-End Celebration - Ring in the new year with unbeatable Tata deals"},
]

FIRST_NAMES_MALE = [
    "Aarav", "Vivaan", "Aditya", "Rohit", "Arjun",
    "Sai", "Rahul", "Vikram", "Karthik", "Pranav",
    "Suresh", "Rajesh", "Amit", "Deepak", "Nikhil",
]

FIRST_NAMES_FEMALE = [
    "Ananya", "Priya", "Sneha", "Divya", "Pooja",
    "Meera", "Kavita", "Lakshmi", "Riya", "Nisha",
    "Sunita", "Swati", "Neha", "Anjali", "Ishita",
]

LAST_NAMES = [
    "Sharma", "Patel", "Reddy", "Kumar", "Singh",
    "Nair", "Gupta", "Joshi", "Iyer", "Mehta",
    "Verma", "Rao", "Das", "Pillai", "Choudhary",
]

HINDI_BELT_STATES = {"Uttar Pradesh", "Delhi NCR", "Rajasthan", "Maharashtra"}

CHANNEL_WEIGHTS = {
    "email": 0.30,
    "whatsapp": 0.30,
    "sms": 0.15,
    "push": 0.10,
    "social": 0.15,
}


def _weighted_channel():
    channels = list(CHANNEL_WEIGHTS.keys())
    weights = list(CHANNEL_WEIGHTS.values())
    return random.choices(channels, weights=weights, k=1)[0]


def _random_phone():
    return f"+91{random.randint(7000000000, 9999999999)}"


def generate_customers(count=200):
    customers = []
    states = list(INDIAN_CITIES.keys())
    vehicle_names = [v["name"] for v in TATA_VEHICLES]

    for i in range(count):
        gender = random.choice(["M", "F"])
        if gender == "M":
            first_name = random.choice(FIRST_NAMES_MALE)
        else:
            first_name = random.choice(FIRST_NAMES_FEMALE)
        last_name = random.choice(LAST_NAMES)

        state = random.choice(states)
        city = random.choice(INDIAN_CITIES[state])

        if state in HINDI_BELT_STATES:
            language_preference = "hi" if random.random() > 0.3 else "en"
        else:
            language_preference = "en" if random.random() > 0.3 else "hi"

        age = random.randint(25, 60)

        income_band = random.random()
        if income_band < 0.4:
            annual_income = round(random.uniform(4.0, 10.0), 2)
        elif income_band < 0.8:
            annual_income = round(random.uniform(10.0, 25.0), 2)
        else:
            annual_income = round(random.uniform(25.0, 50.0), 2)

        has_vehicle = random.random() > 0.2
        if has_vehicle:
            current_vehicle = random.choice(vehicle_names)
            current_vehicle_year = random.randint(2016, 2024)
            vehicle_age = 2025 - current_vehicle_year
            purchase_month = random.randint(1, 12)
            purchase_date = datetime(current_vehicle_year, purchase_month, random.randint(1, 28))
            service_count = random.randint(0, min(15, vehicle_age * 2))
            last_service_days_ago = random.randint(30, 365)
            last_service_date = datetime.utcnow() - timedelta(days=last_service_days_ago)
        else:
            current_vehicle = None
            current_vehicle_year = None
            purchase_date = None
            service_count = 0
            last_service_date = None

        website_visits = random.randint(0, 50)

        if annual_income > 20:
            ev_page_views = random.randint(5, 30)
        elif annual_income > 12:
            ev_page_views = random.randint(2, 20)
        else:
            ev_page_views = random.randint(0, 10)

        brochure_downloads = random.randint(0, 5)
        test_drives_taken = random.randint(0, 3)
        social_engagement_score = round(random.uniform(0, 100), 2)
        email_open_rate = round(random.uniform(0.1, 0.8), 3)
        campaign_response_rate = round(random.uniform(0.05, 0.5), 3)

        consent_email = random.random() > 0.1
        consent_whatsapp = random.random() > 0.1
        consent_sms = random.random() > 0.1
        consent_push = random.random() > 0.1
        consent_social = random.random() > 0.1

        preferred_channel = _weighted_channel()

        if annual_income < 10:
            vehicle_segment = "mid_range"
            customer_segment = "budget_conscious"
        elif annual_income <= 25:
            vehicle_segment = "premium"
            customer_segment = "aspiring_premium"
        else:
            vehicle_segment = "luxury"
            customer_segment = "luxury_seeker"

        intent_score = min(100, round(
            (website_visits / 50) * 25
            + (ev_page_views / 30) * 25
            + (brochure_downloads / 5) * 25
            + (test_drives_taken / 3) * 25,
            2,
        ))

        email_local = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
        email_domain = random.choice(["gmail.com", "yahoo.co.in", "outlook.com", "hotmail.com", "rediffmail.com"])
        email = f"{email_local}@{email_domain}"

        customers.append({
            "customer_id": str(uuid.uuid4()),
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": _random_phone(),
            "city": city,
            "state": state,
            "language_preference": language_preference,
            "age": age,
            "gender": gender,
            "annual_income": annual_income,
            "current_vehicle": current_vehicle,
            "current_vehicle_year": current_vehicle_year,
            "purchase_date": purchase_date,
            "service_count": service_count,
            "last_service_date": last_service_date,
            "website_visits": website_visits,
            "ev_page_views": ev_page_views,
            "brochure_downloads": brochure_downloads,
            "test_drives_taken": test_drives_taken,
            "social_engagement_score": social_engagement_score,
            "email_open_rate": email_open_rate,
            "campaign_response_rate": campaign_response_rate,
            "consent_email": consent_email,
            "consent_whatsapp": consent_whatsapp,
            "consent_sms": consent_sms,
            "consent_push": consent_push,
            "consent_social": consent_social,
            "is_unsubscribed": False,
            "preferred_channel": preferred_channel,
            "vehicle_segment": vehicle_segment,
            "customer_segment": customer_segment,
            "purchase_intent_score": intent_score,
        })

    return customers


def generate_campaign_analytics():
    total_sent = random.randint(5000, 50000)
    delivery_rate = random.uniform(0.85, 0.98)
    total_delivered = int(total_sent * delivery_rate)
    total_failed = total_sent - total_delivered

    open_rate = random.uniform(0.15, 0.45)
    total_opened = int(total_delivered * open_rate)

    click_rate = random.uniform(0.05, 0.25)
    total_clicked = int(total_opened * click_rate)

    reply_rate = random.uniform(0.01, 0.08)
    total_replies = int(total_opened * reply_rate)

    brochure_downloads = int(total_clicked * random.uniform(0.3, 0.6))
    dealer_visits = int(total_clicked * random.uniform(0.1, 0.3))
    test_drive_bookings = int(dealer_visits * random.uniform(0.3, 0.7))
    vehicle_inquiries = int(total_clicked * random.uniform(0.15, 0.4))
    quotations = int(vehicle_inquiries * random.uniform(0.3, 0.6))
    bookings = int(quotations * random.uniform(0.2, 0.5))
    purchases = int(bookings * random.uniform(0.4, 0.8))

    avg_vehicle_price = random.uniform(8.0, 20.0) * 100000
    revenue = round(purchases * avg_vehicle_price, 2)

    budget = random.uniform(500000, 5000000)
    roi = round(((revenue - budget) / budget) * 100, 2) if budget > 0 else 0.0

    effectiveness_score = round(
        (open_rate * 25 + click_rate * 25 + (purchases / max(total_sent, 1)) * 25 + min(roi / 100, 1) * 25) * 100,
        2,
    )
    effectiveness_score = min(100.0, max(0.0, effectiveness_score))

    return {
        "total_sent": total_sent,
        "total_delivered": total_delivered,
        "total_failed": total_failed,
        "total_opened": total_opened,
        "total_clicked": total_clicked,
        "total_replies": total_replies,
        "brochure_downloads": brochure_downloads,
        "dealer_visits": dealer_visits,
        "test_drive_bookings": test_drive_bookings,
        "vehicle_inquiries": vehicle_inquiries,
        "quotations": quotations,
        "bookings": bookings,
        "purchases": purchases,
        "revenue": revenue,
        "roi": roi,
        "effectiveness_score": effectiveness_score,
    }


async def seed_database(session):
    from sqlalchemy import select

    existing_user = await session.execute(select(User).limit(1))
    if existing_user.scalar_one_or_none() is not None:
        return

    user1 = User(
        email="campaign_manager@tata.com",
        full_name="Priya Sharma",
        hashed_password=get_password_hash("admin123"),
        role="campaign_manager",
        is_active=True,
    )
    user2 = User(
        email="retail_manager@tata.com",
        full_name="Rajesh Kumar",
        hashed_password=get_password_hash("admin123"),
        role="retail_manager",
        is_active=True,
    )
    session.add(user1)
    session.add(user2)
    await session.flush()

    vehicle_objects = []
    for v in TATA_VEHICLES:
        vehicle = Vehicle(
            name=v["name"],
            category=v["category"],
            segment=v["segment"],
            price_range_min=v["price_range_min"],
            price_range_max=v["price_range_max"],
            key_features=json.dumps(v["key_features"]),
            target_audience=v["target_audience"],
            is_active=True,
        )
        session.add(vehicle)
        vehicle_objects.append(vehicle)
    await session.flush()

    customer_data = generate_customers(200)
    customer_objects = []
    for cd in customer_data:
        customer = Customer(
            customer_id=cd["customer_id"],
            first_name=cd["first_name"],
            last_name=cd["last_name"],
            email=cd["email"],
            phone=cd["phone"],
            city=cd["city"],
            state=cd["state"],
            language_preference=cd["language_preference"],
            age=cd["age"],
            gender=cd["gender"],
            annual_income=cd["annual_income"],
            current_vehicle=cd["current_vehicle"],
            current_vehicle_year=cd["current_vehicle_year"],
            purchase_date=cd["purchase_date"],
            service_count=cd["service_count"],
            last_service_date=cd["last_service_date"],
            website_visits=cd["website_visits"],
            ev_page_views=cd["ev_page_views"],
            brochure_downloads=cd["brochure_downloads"],
            test_drives_taken=cd["test_drives_taken"],
            social_engagement_score=cd["social_engagement_score"],
            email_open_rate=cd["email_open_rate"],
            campaign_response_rate=cd["campaign_response_rate"],
            consent_email=cd["consent_email"],
            consent_whatsapp=cd["consent_whatsapp"],
            consent_sms=cd["consent_sms"],
            consent_push=cd["consent_push"],
            consent_social=cd["consent_social"],
            is_unsubscribed=cd["is_unsubscribed"],
            preferred_channel=cd["preferred_channel"],
            vehicle_segment=cd["vehicle_segment"],
            customer_segment=cd["customer_segment"],
            purchase_intent_score=cd["purchase_intent_score"],
        )
        session.add(customer)
        customer_objects.append(customer)
    await session.flush()

    sample_campaigns = [
        {
            "name": "Diwali Mega Offer - Nexon EV",
            "description": "Exclusive Diwali festival campaign promoting Nexon EV with special financing and exchange offers",
            "objective": "Drive Nexon EV sales during Diwali festival season",
            "vehicle_index": 4,
            "target_segment": "premium",
            "target_cities": json.dumps(["Mumbai", "Pune", "Bangalore", "Hyderabad"]),
            "target_states": json.dumps(["Maharashtra", "Karnataka", "Telangana"]),
            "budget": 2500000.0,
            "start_date": datetime(2025, 10, 20),
            "end_date": datetime(2025, 11, 15),
            "status": "completed",
            "festival_context": "Diwali",
            "channels": json.dumps(["email", "whatsapp", "sms"]),
            "languages": json.dumps(["en", "hi"]),
        },
        {
            "name": "Summer Drive - Punch SUV",
            "description": "Summer adventure campaign targeting young professionals for the Tata Punch",
            "objective": "Increase Punch test drive bookings among urban millennials",
            "vehicle_index": 2,
            "target_segment": "mid_range",
            "target_cities": json.dumps(["New Delhi", "Gurgaon", "Noida", "Jaipur"]),
            "target_states": json.dumps(["Delhi NCR", "Rajasthan"]),
            "budget": 1500000.0,
            "start_date": datetime(2025, 4, 1),
            "end_date": datetime(2025, 5, 31),
            "status": "completed",
            "festival_context": "Akshaya Tritiya",
            "channels": json.dumps(["email", "social", "push"]),
            "languages": json.dumps(["en", "hi"]),
        },
        {
            "name": "Navratri Special - Harrier Launch",
            "description": "Navratri festival campaign for the premium Harrier with exclusive color editions",
            "objective": "Boost Harrier premium segment sales during Navratri",
            "vehicle_index": 7,
            "target_segment": "premium",
            "target_cities": json.dumps(["Ahmedabad", "Surat", "Mumbai", "Pune"]),
            "target_states": json.dumps(["Gujarat", "Maharashtra"]),
            "budget": 3000000.0,
            "start_date": datetime(2025, 9, 22),
            "end_date": datetime(2025, 10, 15),
            "status": "active",
            "festival_context": "Navratri",
            "channels": json.dumps(["email", "whatsapp", "social"]),
            "languages": json.dumps(["en", "hi"]),
        },
        {
            "name": "EV Revolution - Curvv EV Pre-Launch",
            "description": "Pre-launch awareness campaign for the all-new Curvv EV targeting tech-savvy buyers",
            "objective": "Generate pre-booking leads for Curvv EV launch",
            "vehicle_index": 6,
            "target_segment": "premium",
            "target_cities": json.dumps(["Bangalore", "Chennai", "Hyderabad", "Mumbai", "New Delhi"]),
            "target_states": json.dumps(["Karnataka", "Tamil Nadu", "Telangana", "Maharashtra", "Delhi NCR"]),
            "budget": 5000000.0,
            "start_date": datetime(2025, 11, 1),
            "end_date": datetime(2025, 12, 31),
            "status": "draft",
            "festival_context": "Christmas/New Year",
            "channels": json.dumps(["email", "whatsapp", "social", "push"]),
            "languages": json.dumps(["en"]),
        },
        {
            "name": "Safari Adventure Challenge",
            "description": "Experiential marketing campaign inviting Safari owners and prospects to adventure drives",
            "objective": "Strengthen Safari brand loyalty and generate referral leads",
            "vehicle_index": 8,
            "target_segment": "premium",
            "target_cities": json.dumps(["Kolkata", "Kochi", "Lucknow", "Jaipur"]),
            "target_states": json.dumps(["West Bengal", "Kerala", "Uttar Pradesh", "Rajasthan"]),
            "budget": 2000000.0,
            "start_date": datetime(2025, 8, 1),
            "end_date": datetime(2025, 8, 31),
            "status": "active",
            "festival_context": "Independence Day",
            "channels": json.dumps(["email", "sms"]),
            "languages": json.dumps(["en", "hi"]),
        },
    ]

    campaign_objects = []
    for sc in sample_campaigns:
        campaign = Campaign(
            campaign_id=str(uuid.uuid4()),
            name=sc["name"],
            description=sc["description"],
            objective=sc["objective"],
            vehicle_id=vehicle_objects[sc["vehicle_index"]].id,
            target_segment=sc["target_segment"],
            target_cities=sc["target_cities"],
            target_states=sc["target_states"],
            budget=sc["budget"],
            start_date=sc["start_date"],
            end_date=sc["end_date"],
            status=sc["status"],
            created_by=user1.id,
            festival_context=sc["festival_context"],
            channels=sc["channels"],
            languages=sc["languages"],
        )
        session.add(campaign)
        campaign_objects.append(campaign)
    await session.flush()

    for campaign in campaign_objects:
        if campaign.status == "completed":
            analytics_data = generate_campaign_analytics()
            analytics = CampaignAnalytics(
                campaign_id=campaign.id,
                total_sent=analytics_data["total_sent"],
                total_delivered=analytics_data["total_delivered"],
                total_failed=analytics_data["total_failed"],
                total_opened=analytics_data["total_opened"],
                total_clicked=analytics_data["total_clicked"],
                total_replies=analytics_data["total_replies"],
                brochure_downloads=analytics_data["brochure_downloads"],
                dealer_visits=analytics_data["dealer_visits"],
                test_drive_bookings=analytics_data["test_drive_bookings"],
                vehicle_inquiries=analytics_data["vehicle_inquiries"],
                quotations=analytics_data["quotations"],
                bookings=analytics_data["bookings"],
                purchases=analytics_data["purchases"],
                revenue=analytics_data["revenue"],
                roi=analytics_data["roi"],
                effectiveness_score=analytics_data["effectiveness_score"],
            )
            session.add(analytics)

    audit_actions = [
        ("user_login", "user", "Authentication"),
        ("campaign_created", "campaign", "Campaign Management"),
        ("campaign_updated", "campaign", "Campaign Management"),
        ("customer_imported", "customer", "Data Management"),
        ("report_generated", "report", "Analytics"),
        ("consent_updated", "customer", "Compliance"),
    ]

    for _ in range(10):
        action, resource_type, category = random.choice(audit_actions)
        audit_user = random.choice([user1, user2])
        log = AuditLog(
            user_id=audit_user.id,
            action=action,
            resource_type=resource_type,
            resource_id=str(random.randint(1, 200)),
            details=json.dumps({"category": category, "status": "success"}),
            ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
        )
        session.add(log)

    consent_channels = ["email", "whatsapp", "sms", "push", "social"]
    consent_sources = ["website_signup", "showroom_visit", "test_drive_form", "campaign_optin", "mobile_app"]

    for _ in range(20):
        customer = random.choice(customer_objects)
        channel = random.choice(consent_channels)
        consent_log = ConsentLog(
            customer_id=customer.id,
            channel=channel,
            consent_given=random.random() > 0.15,
            consent_date=datetime.utcnow() - timedelta(days=random.randint(0, 180)),
            source=random.choice(consent_sources),
        )
        session.add(consent_log)

    await session.commit()
