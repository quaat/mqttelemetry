"""Submodel for MQTT-based telemetry"""

from __future__ import annotations

from .messaging import MessageService
from .models import MessagePayload

__all__ = ["MessagePayload", "MessageService"]
