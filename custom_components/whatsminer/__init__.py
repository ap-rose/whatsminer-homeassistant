"""
Expose Whatsminer to HA
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import WhatsminerMachine
from .const import DOMAIN, COORDINATOR, MINER
from .coordinator import WhatsminerCoordinator

# Added Platform.BUTTON to the PLATFORMS list
PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.BUTTON]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    miner_coordinator = WhatsminerCoordinator(hass, entry)
    await miner_coordinator.async_refresh()
    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})[
        COORDINATOR
    ] = miner_coordinator

    result = True
    for platform in PLATFORMS:
        result = result & await hass.config_entries.async_forward_entry_setup(entry=entry, domain=platform)
    return result


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
