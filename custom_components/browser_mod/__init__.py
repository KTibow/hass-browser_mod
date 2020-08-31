import logging

from .connection import setup_connection
from .const import (
    CONFIG_DEVICES,
    DATA_ADDERS,
    DATA_ALIASES,
    DATA_CONFIG,
    DATA_DEVICES,
    DOMAIN,
)
from .mod_view import setup_view
from .service import setup_service

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):

    await setup_connection(hass, config)
    setup_view(hass)

    aliases = {}
    for d in config[DOMAIN].get(CONFIG_DEVICES, {}):
        name = config[DOMAIN][CONFIG_DEVICES][d].get("name", None)
        if name:
            aliases[name] = d.replace("_", "-")

    hass.data[DOMAIN] = {
        DATA_DEVICES: {},
        DATA_ALIASES: aliases,
        DATA_ADDERS: {},
        DATA_CONFIG: config[DOMAIN],
    }

    await hass.helpers.discovery.async_load_platform("media_player", DOMAIN, {}, config)
    await hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, config)
    await hass.helpers.discovery.async_load_platform(
        "binary_sensor", DOMAIN, {}, config
    )
    await hass.helpers.discovery.async_load_platform("light", DOMAIN, {}, config)
    await hass.helpers.discovery.async_load_platform("camera", DOMAIN, {}, config)

    await setup_service(hass)

    return True
