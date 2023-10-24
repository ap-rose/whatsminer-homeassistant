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

# Define types if we're type checking
if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Dataclass for the mixin
@dataclass
class WhatsminerButtonEntityDescriptionMixin:
    press_fn: Callable[[HomeAssistant], Awaitable[Any]]

# Combined dataclass for button entity description
@dataclass
class WhatsminerButtonEntityDescription(
    ButtonEntityDescription,
    WhatsminerButtonEntityDescriptionMixin,
):
    pass

# Define buttons and their properties
BUTTONS: tuple[WhatsminerButtonEntityDescription, ...] = (
    WhatsminerButtonEntityDescription(
        key="restart_miner",
        name="Restart Miner",
        icon="mdi:restart",
        entity_category=EntityCategory.CONFIG,
        press_fn=lambda hass: hass.data[DOMAIN][COORDINATOR].api.async_restart_miner(),
    ),
    WhatsminerButtonEntityDescription(
        key="reload_configuration",
        name="Reload Miner Configuration",
        icon="mdi:reload",
        entity_category=EntityCategory.CONFIG,
        press_fn=lambda hass: hass.data[DOMAIN][COORDINATOR].api.async_reload_config(),
    ),
)

# Function to setup button entities
async def async_setup_entry(
    _hass: HomeAssistant,
    _entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug("Setting up Whatsminer button entities.")
    async_add_entities(
        WhatsminerButtonEntity(description=description) for description in BUTTONS
    )

# Define the custom button entity class
class WhatsminerButtonEntity(ButtonEntity):
    def __init__(self, description: WhatsminerButtonEntityDescription):
        super().__init__()
        self.entity_description = description

    async def async_press(self) -> None:
        await self.entity_description.press_fn(self.hass)
