from datetime import datetime, timezone
import copy


class PrivacyComplianceAgent:

    CHANNEL_CONSENT_MAP = {
        "email": "consent_email",
        "whatsapp": "consent_whatsapp",
        "sms": "consent_sms",
        "push": "consent_push",
        "social": "consent_social",
    }

    def check_consent(self, customer: dict, channel: str) -> dict:
        if customer.get("is_unsubscribed", False):
            return {
                "allowed": False,
                "reason": "Customer has unsubscribed from all communications",
                "channel": channel,
            }

        consent_field = self.CHANNEL_CONSENT_MAP.get(channel)
        if not consent_field:
            return {
                "allowed": False,
                "reason": f"Unknown channel: {channel}",
                "channel": channel,
            }

        has_consent = customer.get(consent_field, False)
        if has_consent:
            return {
                "allowed": True,
                "reason": f"Customer has given consent for {channel}",
                "channel": channel,
            }
        return {
            "allowed": False,
            "reason": f"Customer has not given consent for {channel}",
            "channel": channel,
        }

    def anonymize_customer_data(self, customer: dict) -> dict:
        anonymized = copy.deepcopy(customer)

        if "email" in anonymized and anonymized["email"]:
            email = anonymized["email"]
            if "@" in email:
                local, domain = email.split("@", 1)
                anonymized["email"] = local[:2] + "***@" + domain
            else:
                anonymized["email"] = "***"

        if "phone" in anonymized and anonymized["phone"]:
            phone = str(anonymized["phone"])
            anonymized["phone"] = "****" + phone[-4:]

        anonymized.pop("annual_income", None)

        return anonymized

    def validate_campaign_compliance(self, campaign: dict) -> dict:
        checks = []
        violations = []

        has_consent = campaign.get("consent_basis", False)
        checks.append({
            "check": "GDPR consent",
            "passed": bool(has_consent),
            "detail": "Campaign has valid consent basis" if has_consent else "Missing consent basis",
        })
        if not has_consent:
            violations.append("Missing GDPR consent basis")

        has_unsubscribe = campaign.get("unsubscribe_mechanism", False)
        checks.append({
            "check": "CAN-SPAM compliance",
            "passed": bool(has_unsubscribe),
            "detail": "Unsubscribe mechanism present" if has_unsubscribe else "Missing unsubscribe mechanism",
        })
        if not has_unsubscribe:
            violations.append("Missing CAN-SPAM unsubscribe mechanism")

        has_minimization = campaign.get("data_minimization", False)
        checks.append({
            "check": "data minimization",
            "passed": bool(has_minimization),
            "detail": "Data minimization applied" if has_minimization else "Data minimization not applied",
        })
        if not has_minimization:
            violations.append("Data minimization not applied")

        has_unsub_mechanism = campaign.get("unsubscribe_mechanism", False)
        checks.append({
            "check": "unsubscribe mechanism",
            "passed": bool(has_unsub_mechanism),
            "detail": "Unsubscribe mechanism available" if has_unsub_mechanism else "No unsubscribe mechanism",
        })
        if not has_unsub_mechanism and "Missing CAN-SPAM unsubscribe mechanism" not in violations:
            violations.append("No unsubscribe mechanism provided")

        has_retention = campaign.get("data_retention_policy", False)
        checks.append({
            "check": "data retention policy",
            "passed": bool(has_retention),
            "detail": "Data retention policy defined" if has_retention else "Missing data retention policy",
        })
        if not has_retention:
            violations.append("Missing data retention policy")

        return {
            "compliant": len(violations) == 0,
            "checks": checks,
            "violations": violations,
        }

    def generate_audit_log(self, user_id, action, resource_type, resource_id, details) -> dict:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
        }

    def handle_unsubscribe(self, customer_id: str) -> dict:
        return {
            "customer_id": customer_id,
            "actions": [
                "Update all consent flags to False",
                "Set is_unsubscribed to True",
                "Remove from all active campaign queues",
                "Prevent inclusion in future campaign targeting",
                "Record unsubscribe timestamp for compliance audit",
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def check_data_retention(self, customer: dict, retention_days: int = 365 * 3) -> dict:
        last_activity = customer.get("last_activity_date")
        if not last_activity:
            return {
                "should_purge": True,
                "last_activity": None,
                "days_since_activity": -1,
            }

        if isinstance(last_activity, str):
            last_activity_date = datetime.fromisoformat(last_activity)
        else:
            last_activity_date = last_activity

        if last_activity_date.tzinfo is None:
            last_activity_date = last_activity_date.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        days_since = (now - last_activity_date).days

        return {
            "should_purge": days_since > retention_days,
            "last_activity": last_activity_date.isoformat(),
            "days_since_activity": days_since,
        }
