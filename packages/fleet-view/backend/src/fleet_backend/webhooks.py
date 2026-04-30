from __future__ import annotations

import ipaddress
import logging
import socket
import uuid
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

VALID_EVENT_TYPES = {"defect.critical", "inspection.completed", "sync.received", "detention.risk"}

_BLOCKED_HOSTNAMES = {"localhost", "localhost.localdomain", "0.0.0.0"}


def _is_private_ip(host: str) -> bool:
    try:
        addr = ipaddress.ip_address(host)
        return addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved
    except ValueError:
        pass
    try:
        resolved = socket.getaddrinfo(host, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for _, _, _, _, sockaddr in resolved:
            addr = ipaddress.ip_address(sockaddr[0])
            if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
                return True
    except (socket.gaierror, OSError):
        pass
    return False


def _validate_webhook_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme != "https":
        raise ValueError(f"Webhook URL must use https:// (got '{parsed.scheme}://')")

    if not parsed.hostname:
        raise ValueError("Webhook URL has no hostname")

    hostname = parsed.hostname.lower()
    if hostname in _BLOCKED_HOSTNAMES:
        raise ValueError(f"Webhook URL cannot target {hostname}")

    if _is_private_ip(hostname):
        raise ValueError("Webhook URL cannot target private/internal IP addresses")


class WebhookManager:
    def __init__(self) -> None:
        self.webhooks: dict[str, dict] = {}
        self.delivery_log: list[dict] = []

    def configure(self, url: str, events: list[str]) -> str:
        invalid = set(events) - VALID_EVENT_TYPES
        if invalid:
            raise ValueError(f"Invalid event types: {invalid}")

        _validate_webhook_url(url)

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
