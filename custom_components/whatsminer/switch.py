import logging
from typing import cast, Tuple

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
    SwitchDeviceClass,
)
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from . import WhatsminerCoordinator
from .const import DOMAIN, COORDINATOR
from .coordinator import OnlineMinerData
from .entity import WhatsminerEntity

SWITCH_TYPES: Tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription(
        key="power",
        name="Power",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG
    ),
)

async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WhatsminerCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    switches = [MinerSwitch(coordinator, entity_description) for entity_description in SWITCH_TYPES]
    buttons = [MinerRestartButton(switch) for switch in switches]

    async_add_entities(switches + buttons)

class MinerSwitch(WhatsminerEntity, SwitchEntity):
    def __init__(self, coordinator, entity_description: SwitchEntityDescription):
        super(WhatsminerEntity, self).__init__(coordinator=coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.device_mac}_{entity_description.key}"

    @property
    def is_on(self) -> bool:
        return isinstance(self.coordinator.data, OnlineMinerData)

    def turn_off(self) -> None:
        raise NotImplemented

    def turn_on(self) -> None:
        raise NotImplemented

    async def async_turn_on(self) -> None:
        await self.coordinator.api.power_on_miner()

    async def async_turn_off(self) -> None:
        await self.coordinator.api.power_off_miner()

    async def restart_miner(self) -> None:
        await self.coordinator.api.restart_miner()

class MinerRestartButton(ButtonEntity):
    def __init__(self, miner_switch: MinerSwitch):
        self.miner_switch = miner_switch
        self._attr_name = f"Restart {miner_switch.name}"
        self._attr_unique_id = f"{miner_switch.unique_id}_restart"

    async def async_press(self) -> None:
        """Simulate pressing the button."""
        await self.miner_switch.restart_miner()
