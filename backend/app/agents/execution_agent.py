import asyncio
import random
import uuid
from datetime import datetime, timedelta


CHANNEL_SUCCESS_RATES = {
    "email": 0.95,
    "whatsapp": 0.98,
    "sms": 0.90,
    "push": 0.85,
    "social": 0.88,
}


class CampaignExecutionAgent:

    async def execute_campaign(
        self, campaign_id: str, customer_id: str, channel: str, content: dict
    ) -> dict:
        await asyncio.sleep(random.uniform(0.01, 0.05))

        success_rate = CHANNEL_SUCCESS_RATES.get(channel.lower(), 0.85)
        sent_at = datetime.utcnow()
        message_id = str(uuid.uuid4())

        if random.random() <= success_rate:
            delivery_delay = random.uniform(0.5, 5.0)
            delivered_at = sent_at + timedelta(seconds=delivery_delay)
            status = random.choice(["sent", "delivered", "delivered"])
            return {
                "campaign_id": campaign_id,
                "customer_id": customer_id,
                "channel": channel.lower(),
                "status": status,
                "sent_at": sent_at.isoformat(),
                "delivered_at": delivered_at.isoformat() if status == "delivered" else None,
                "error_message": None,
                "retry_count": 0,
                "message_id": message_id,
            }

        error_messages = {
            "email": "Mailbox full or invalid address",
            "whatsapp": "User not on WhatsApp",
            "sms": "Network delivery failure",
            "push": "Device token expired",
            "social": "API rate limit exceeded",
        }

        return {
            "campaign_id": campaign_id,
            "customer_id": customer_id,
            "channel": channel.lower(),
            "status": "failed",
            "sent_at": sent_at.isoformat(),
            "delivered_at": None,
            "error_message": error_messages.get(channel.lower(), "Unknown delivery error"),
            "retry_count": 0,
            "message_id": message_id,
        }

    async def execute_batch(
        self, campaign_id: str, executions: list[dict]
    ) -> dict:
        tasks = [
            self.execute_campaign(
                campaign_id=campaign_id,
                customer_id=ex["customer_id"],
                channel=ex["channel"],
                content=ex.get("content", {}),
            )
            for ex in executions
        ]

        results = await asyncio.gather(*tasks)

        sent_count = sum(1 for r in results if r["status"] in ("sent", "delivered"))
        delivered_count = sum(1 for r in results if r["status"] == "delivered")
        failed_count = sum(1 for r in results if r["status"] == "failed")

        return {
            "campaign_id": campaign_id,
            "total": len(results),
            "sent": sent_count,
            "delivered": delivered_count,
            "failed": failed_count,
            "results": list(results),
        }

    async def retry_failed(self, failed_executions: list[dict]) -> list[dict]:
        retried = []
        for ex in failed_executions:
            await asyncio.sleep(random.uniform(0.01, 0.03))
            sent_at = datetime.utcnow()

            if random.random() <= 0.80:
                delivery_delay = random.uniform(0.5, 5.0)
                delivered_at = sent_at + timedelta(seconds=delivery_delay)
                retried.append({
                    "campaign_id": ex.get("campaign_id", ""),
                    "customer_id": ex.get("customer_id", ""),
                    "channel": ex.get("channel", ""),
                    "status": "delivered",
                    "sent_at": sent_at.isoformat(),
                    "delivered_at": delivered_at.isoformat(),
                    "error_message": None,
                    "retry_count": ex.get("retry_count", 0) + 1,
                    "message_id": ex.get("message_id", str(uuid.uuid4())),
                })
            else:
                retried.append({
                    "campaign_id": ex.get("campaign_id", ""),
                    "customer_id": ex.get("customer_id", ""),
                    "channel": ex.get("channel", ""),
                    "status": "failed",
                    "sent_at": sent_at.isoformat(),
                    "delivered_at": None,
                    "error_message": "Retry failed: " + ex.get("error_message", "Unknown error"),
                    "retry_count": ex.get("retry_count", 0) + 1,
                    "message_id": ex.get("message_id", str(uuid.uuid4())),
                })

        return retried
