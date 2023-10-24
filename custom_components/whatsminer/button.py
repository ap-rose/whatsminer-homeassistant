from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Awaitable

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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


async def async_setup_entry(
    _hass: HomeAssistant,
    _entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        WhatsminerButtonEntity(description) for description in BUTTONS
    )


class WhatsminerButtonEntity(ButtonEntity):
    entity_description: WhatsminerButtonEntityDescription

    async def async_press(self) -> None:
        await self.entity_description.press_fn(self.hass)
