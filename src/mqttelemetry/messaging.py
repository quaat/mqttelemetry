"""Module for sending messages to a MQTT broker."""

from __future__ import annotations

import logging

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)
DEFAULT_MQTT_PROTOCOL = mqtt.MQTTv5


class MessageService:
    """Service for sending messages to a MQTT broker using a persistent client."""

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        protocol=DEFAULT_MQTT_PROTOCOL,
    ):
        """Initialize the MessageService with the MQTT broker details and set up a persistent client."""
        self.hostname = hostname
        self.auth = {"username": username, "password": password}
        self.protocol = protocol

        # Set up the MQTT client
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, protocol=self.protocol
        )
        self.client.username_pw_set(username, password)

        # Connect to the broker and start the network loop in a background thread.
        self.client.connect(self.hostname)
        self.client.loop_start()

    def send_message(self, topic: str, message: str) -> None:
        """Send a message to a MQTT broker using the persistent client."""
        try:
            # Publish the message using the persistent MQTT client
            result = self.client.publish(topic, payload=message)
            result.wait_for_publish()  # Optionally wait until the message is published
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.error(
                    "Error sending message to topic %s: result code %s",
                    topic,
                    result.rc,
                )
        except Exception as e:
            logger.error("Error sending message to topic %s: %s", topic, e)
            raise

    def disconnect(self) -> None:
        """Disconnect the MQTT client gracefully."""
        self.client.loop_stop()
        self.client.disconnect()
