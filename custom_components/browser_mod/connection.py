import logging

import voluptuous as vol
from homeassistant.components.websocket_api import (
    async_register_command,
    event_message,
    result_message,
    websocket_command,
)
from homeassistant.helpers.entity import Entity, async_generate_entity_id

from .const import DOMAIN, WS_CAMERA, WS_CONNECT, WS_UPDATE
from .helpers import create_entity, get_config, get_devices

_LOGGER = logging.getLogger(__name__)


async def setup_connection(hass, config):
    @websocket_command(
        {
            vol.Required("type"): WS_CONNECT,
            vol.Required("deviceID"): str,
        }
    )
    def handle_connect(hass, connection, msg):
        deviceID = msg["deviceID"]

        device = get_devices(hass).get(deviceID, BrowserModConnection(hass, deviceID))
        device.connect(connection, msg["id"])
        get_devices(hass)[deviceID] = device

        connection.send_message(result_message(msg["id"]))

    @websocket_command(
        {
            vol.Required("type"): WS_UPDATE,
            vol.Required("deviceID"): str,
            vol.Optional("data"): dict,
        }
    )
    def handle_update(hass, connection, msg):
        devices = get_devices(hass)
        deviceID = msg["deviceID"]
        if deviceID in devices:
            devices[deviceID].update(msg.get("data", None))

    async_register_command(hass, handle_connect)
    async_register_command(hass, handle_update)


class BrowserModConnection:
    def __init__(self, hass, deviceID):
        self.hass = hass
        self.deviceID = deviceID
        self.connection = []

        self.media_player = None
        self.screen = None
        self.sensor = None
        self.fully = None
        self.camera = None

    def connect(self, connection, cid):
        self.connection.append((connection, cid))
        self.send("update", **get_config(self.hass, self.deviceID))

        def disconnect():
            self.connection.remove((connection, cid))

        connection.subscriptions[cid] = disconnect

    def send(self, command, **kwargs):
        if self.connection:
            connection, cid = self.connection[-1]
            connection.send_message(
                event_message(
                    cid,
                    {
                        "command": command,
                        **kwargs,
                    },
                )
            )

    def update(self, data):
        if data.get("browser"):
            self.sensor = self.sensor or create_entity(
                self.hass, "sensor", self.deviceID, self
            )
            if self.sensor:
                self.sensor.data = data.get("browser")

        if data.get("player"):
            self.media_player = self.media_player or create_entity(
                self.hass, "media_player", self.deviceID, self
            )
            if self.media_player:
                self.media_player.data = data.get("player")

        if data.get("screen"):
            self.screen = self.screen or create_entity(
                self.hass, "light", self.deviceID, self
            )
            if self.screen:
                self.screen.data = data.get("screen")

        if data.get("fully"):
            self.fully = self.fully or create_entity(
                self.hass, "binary_sensor", self.deviceID, self
            )
            if self.fully:
                self.fully.data = data.get("fully")

        if data.get("camera"):
            self.camera = self.camera or create_entity(
                self.hass, "camera", self.deviceID, self
            )
            if self.camera:
                self.camera.data = data.get("camera")
