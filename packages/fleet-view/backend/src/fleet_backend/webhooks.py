from __future__ import annotations

import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

VALID_EVENT_TYPES = {"defect.critical", "inspection.completed", "sync.received", "detention.risk"}


class WebhookManager:
    def __init__(self) -> None:
        self.webhooks: dict[str, dict] = {}
        self.delivery_log: list[dict] = []

    def configure(self, url: str, events: list[str]) -> str:
        invalid = set(events) - VALID_EVENT_TYPES
        if invalid:
            raise ValueError(f"Invalid event types: {invalid}")

        webhook_id = f"WH-{uuid.uuid4().hex[:8]}"
        self.webhooks[webhook_id] = {
            "id": webhook_id,
            "url": url,
            "events": events,
            "created_at": datetime.now().isoformat(),
            "active": True,
        }
        logger.info("Webhook %s configured for %s -> %s", webhook_id, events, url)
        return webhook_id

    def trigger(self, event_type: str, payload: dict) -> None:
        for wh_id, wh in self.webhooks.items():
            if not wh["active"]:
                continue
            if event_type in wh["events"]:
                delivery = {
                    "webhook_id": wh_id,
                    "url": wh["url"],
                    "event_type": event_type,
                    "payload": payload,
                    "delivered_at": datetime.now().isoformat(),
                    "status": "simulated",
                }
                self.delivery_log.append(delivery)
                logger.info("Webhook triggered: %s -> %s (%s)", event_type, wh["url"], wh_id)

    def test(self, webhook_id: str) -> bool:
        wh = self.webhooks.get(webhook_id)
        if wh is None:
            return False

        self.trigger("test.ping", {"message": "Webhook test delivery", "webhook_id": webhook_id})
        return True

    def get_webhook(self, webhook_id: str) -> dict | None:
        return self.webhooks.get(webhook_id)

    def list_webhooks(self) -> list[dict]:
        return list(self.webhooks.values())

    def get_delivery_log(self, webhook_id: str | None = None) -> list[dict]:
        if webhook_id:
            return [d for d in self.delivery_log if d["webhook_id"] == webhook_id]
        return list(self.delivery_log)
