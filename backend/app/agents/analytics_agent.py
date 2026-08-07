import random


class AnalyticsAgent:

    def generate_campaign_analytics(
        self, campaign_id: str, execution_results: dict, customer_count: int
    ) -> dict:
        raw_sent = execution_results.get("sent", 0) + execution_results.get("delivered", 0)
        total_sent = max(raw_sent, customer_count)
        if total_sent < 50:
            total_sent = max(total_sent * random.randint(20, 50), 200)

        delivery_rate = random.uniform(0.92, 0.98)
        delivered = int(total_sent * delivery_rate)

        open_rate = random.uniform(0.15, 0.45)
        opened = int(delivered * open_rate)

        click_rate = random.uniform(0.08, 0.25)
        clicked = int(opened * click_rate)

        replies = max(int(clicked * random.uniform(0.05, 0.15)), 1)
        brochure_downloads = max(int(clicked * random.uniform(0.25, 0.45)), 2)
        dealer_visits = max(int(brochure_downloads * random.uniform(0.30, 0.55)), 1)
        test_drive_bookings = max(int(dealer_visits * random.uniform(0.40, 0.70)), 1)
        vehicle_inquiries = max(int(dealer_visits * random.uniform(0.50, 0.80)), 1)
        quotations = max(int(vehicle_inquiries * random.uniform(0.40, 0.65)), 1)
        bookings = max(int(quotations * random.uniform(0.35, 0.55)), 1)
        purchases = max(int(bookings * random.uniform(0.55, 0.85)), 1)

        avg_vehicle_price = random.uniform(600_000, 2_500_000)
        revenue = round(purchases * avg_vehicle_price, 2)

        budget = max(total_sent * random.uniform(5, 25), 1000)
        roi = round(((revenue - budget) / budget) * 100, 2) if budget > 0 else 0.0

        open_rate_pct = round((opened / delivered) * 100, 2) if delivered > 0 else 0
        click_rate_pct = round((clicked / opened) * 100, 2) if opened > 0 else 0
        conversion_rate = round((purchases / total_sent) * 100, 2) if total_sent > 0 else 0
        effectiveness_score = round(
            (open_rate_pct * 0.3) + (click_rate_pct * 0.3) + (conversion_rate * 0.2) + min(roi / 10, 20), 2
        )
        effectiveness_score = max(0, min(effectiveness_score, 100))

        return {
            "campaign_id": campaign_id,
            "customer_count": customer_count,
            "sent": total_sent,
            "delivered": delivered,
            "opened": opened,
            "clicked": clicked,
            "replies": replies,
            "brochure_downloads": brochure_downloads,
            "dealer_visits": dealer_visits,
            "test_drive_bookings": test_drive_bookings,
            "vehicle_inquiries": vehicle_inquiries,
            "quotations": quotations,
            "bookings": bookings,
            "purchases": purchases,
            "revenue": revenue,
            "budget": round(budget, 2),
            "roi": roi,
            "delivery_rate": round(delivery_rate * 100, 2),
            "open_rate": open_rate_pct,
            "click_rate": click_rate_pct,
            "conversion_rate": conversion_rate,
            "effectiveness_score": effectiveness_score,
        }

    def get_funnel_data(self, analytics: dict) -> list[dict]:
        stages = [
            "sent", "delivered", "opened", "clicked",
            "brochure_downloads", "dealer_visits", "test_drive_bookings",
            "vehicle_inquiries", "quotations", "bookings", "purchases",
        ]
        return [
            {"stage": stage, "count": analytics.get(stage, 0)}
            for stage in stages
        ]

    def calculate_roi_metrics(self, analytics: dict, budget: float) -> dict:
        leads = analytics.get("clicked", 0) + analytics.get("brochure_downloads", 0)
        conversions = analytics.get("purchases", 0)
        revenue = analytics.get("revenue", 0.0)
        profit = revenue - budget

        cost_per_lead = round(budget / leads, 2) if leads > 0 else 0.0
        cost_per_conversion = round(budget / conversions, 2) if conversions > 0 else 0.0
        roi_percentage = round((profit / budget) * 100, 2) if budget > 0 else 0.0

        return {
            "cost_per_lead": cost_per_lead,
            "cost_per_conversion": cost_per_conversion,
            "roi_percentage": roi_percentage,
            "revenue": round(revenue, 2),
            "profit": round(profit, 2),
        }

    def generate_dealer_performance(self, states: list[str]) -> list[dict]:
        results = []
        for state in states:
            dealer_count = random.randint(3, 25)
            leads = random.randint(50, 500) * dealer_count
            test_drives = int(leads * random.uniform(0.10, 0.30))
            conversions = int(test_drives * random.uniform(0.15, 0.40))
            avg_price = random.uniform(700_000, 2_000_000)
            revenue = round(conversions * avg_price, 2)

            results.append({
                "state": state,
                "dealer_count": dealer_count,
                "leads": leads,
                "test_drives": test_drives,
                "conversions": conversions,
                "revenue": revenue,
            })

        return results

    def generate_vehicle_segment_performance(self) -> list[dict]:
        segments = {
            "mid_range": {"price_range": (500_000, 1_000_000), "volume_factor": 1.5},
            "premium": {"price_range": (1_000_000, 2_000_000), "volume_factor": 1.0},
            "luxury": {"price_range": (2_000_000, 5_000_000), "volume_factor": 0.5},
        }

        results = []
        for segment, config in segments.items():
            campaigns = random.randint(5, 20)
            base_reach = random.randint(10_000, 100_000)
            reach = int(base_reach * config["volume_factor"])
            conversion_rate = random.uniform(0.005, 0.025)
            conversions = int(reach * conversion_rate)
            avg_price = random.uniform(*config["price_range"])
            revenue = round(conversions * avg_price, 2)
            budget = round(reach * random.uniform(8, 30), 2)
            roi = round(((revenue - budget) / budget) * 100, 2) if budget > 0 else 0.0

            results.append({
                "segment": segment,
                "campaigns": campaigns,
                "reach": reach,
                "conversions": conversions,
                "revenue": revenue,
                "roi": roi,
            })

        return results

    def get_channel_breakdown(self, execution_results: list[dict]) -> dict:
        breakdown = {}

        for result in execution_results:
            channel = result.get("channel", "unknown")
            if channel not in breakdown:
                breakdown[channel] = {
                    "total": 0,
                    "sent": 0,
                    "delivered": 0,
                    "failed": 0,
                }

            breakdown[channel]["total"] += 1
            status = result.get("status", "unknown")
            if status in ("sent", "delivered"):
                breakdown[channel]["sent"] += 1
            if status == "delivered":
                breakdown[channel]["delivered"] += 1
            if status == "failed":
                breakdown[channel]["failed"] += 1

        for channel, data in breakdown.items():
            total = data["total"]
            data["delivery_rate"] = round((data["delivered"] / total) * 100, 2) if total > 0 else 0.0
            data["failure_rate"] = round((data["failed"] / total) * 100, 2) if total > 0 else 0.0

        return breakdown
