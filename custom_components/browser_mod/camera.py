import base64
import logging
from datetime import datetime

from homeassistant.components.camera import Camera
from homeassistant.const import STATE_IDLE, STATE_OFF, STATE_ON, STATE_UNAVAILABLE

from .helpers import BrowserModEntity, setup_platform

PLATFORM = "camera"


async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    return setup_platform(hass, config, async_add_devices, PLATFORM, BrowserModCamera)


class BrowserModCamera(Camera, BrowserModEntity):
    domain = PLATFORM

    def __init__(self, hass, connection, deviceID, alias=None):
        Camera.__init__(self)
        BrowserModEntity.__init__(self, hass, connection, deviceID, alias)
        self.last_seen = None

    def updated(self):
        if self.last_seen is not None and (datetime.now() - self.last_seen).total_seconds() > 60:
            self.last_seen = datetime.now()
        self.schedule_update_ha_state()

    def camera_image(self):
        return base64.b64decode(self.data.split(",")[1])

    @property
    def device_state_attributes(self):
        return {
            "type": "browser_mod",
            "deviceID": self.deviceID,
            "last_seen": self.last_seen,
        }
