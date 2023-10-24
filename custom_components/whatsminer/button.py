# Standard Library imports
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Awaitable

# Home Assistant imports
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Local imports
from . import WhatsminerCoordinator
from .const import DOMAIN, COORDINATOR
from .entity import WhatsminerEntity

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

@dataclass
class WhatsminerButtonEntityDescriptionMixin:
    press_fn: Callable[[HomeAssistant], Awaitable[Any]]

@dataclass
class WhatsminerButtonEntityDescription(
    ButtonEntityDescription,
    WhatsminerButtonEntityDescriptionMixin,
):
    pass

BUTTONS: tuple[WhatsminerButtonEntityDescription, ...] = (
    WhatsminerButtonEntityDescription(
        key="restart_miner",
        name="Restart Miner",
        icon="mdi:restart",
        entity_category=EntityCategory.CONFIG,
        press_fn=lambda coordinator: coordinator.api.async_restart_miner(),
    ),
    WhatsminerButtonEntityDescription(
        key="reload_configuration",
        name="Reload Miner Configuration",
        icon="mdi:reload",
        entity_category=EntityCategory.CONFIG,
        press_fn=lambda coordinator: coordinator.api.async_reload_config(),
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WhatsminerCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    _LOGGER.debug("Setting up Whatsminer button entities.")
    async_add_entities(
        WhatsminerButtonEntity(coordinator, description) for description in BUTTONS
    )

class WhatsminerButtonEntity(ButtonEntity, WhatsminerEntity):
    def __init__(self, coordinator: WhatsminerCoordinator, description: WhatsminerButtonEntityDescription):
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.device_mac}_{description.key}"

    async def async_press(self) -> None:
        await self.entity_description.press_fn(self.coordinator)
