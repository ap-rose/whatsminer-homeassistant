import dataclasses
from datetime import datetime, date
from decimal import Decimal
from typing import Callable, Optional, Union, Tuple

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorEntityDescription,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    FREQUENCY_MEGAHERTZ,
    TEMP_CELSIUS,
    FREQUENCY_HERTZ,
    POWER_WATT,
    TIME_SECONDS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import WhatsminerCoordinator
from .const import DOMAIN, COORDINATOR
from .coordinator import OnlineMinerData
from .entity import OnlineWhatsminerEntity


@dataclasses.dataclass
class WhatsminerSensorEntityDescription(SensorEntityDescription):
    value: Optional[Callable[
        [OnlineMinerData], Union[StateType, date, datetime, Decimal]
    ]] = None


SENSOR_TYPES: Tuple[WhatsminerSensorEntityDescription, ...] = (
    WhatsminerSensorEntityDescription(
        key="hash_rate_average",
        name="Hash Rate (average)",
        native_unit_of_measurement="GH/s",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.average_hash_rate,
    ),
    WhatsminerSensorEntityDescription(
        key="hash_rate_5_m",
        name="Hash Rate (5 min)",
        native_unit_of_measurement="GH/s",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.hash_rate_5m,
    ),
    WhatsminerSensorEntityDescription(
        key="hash_rate_1_m",
        name="Hash Rate (1 min)",
        native_unit_of_measurement="GH/s",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.hash_rate_1m,
    ),
    WhatsminerSensorEntityDescription(
        key="hash_rate_15_m",
        name="Hash Rate (15 min)",
        native_unit_of_measurement="GH/s",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.hash_rate_15m,
    ),
    WhatsminerSensorEntityDescription(
        key="hash_rate_target",
        name="Target Hash Rate",
        native_unit_of_measurement="GH/s",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        entity_category=EntityCategory.CONFIG,
        value=lambda x: x.summary.target_hash_rate,
    ),
    WhatsminerSensorEntityDescription(
        key="frequency_average",
        name="Frequency (average)",
        native_unit_of_measurement=FREQUENCY_MEGAHERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.average_frequency,
    ),
    WhatsminerSensorEntityDescription(
        key="frequency_target",
        name="Target Frequency",
        native_unit_of_measurement=FREQUENCY_MEGAHERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        entity_category=EntityCategory.CONFIG,
        value=lambda x: x.summary.target_frequency,
    ),
    WhatsminerSensorEntityDescription(
        key="temperature_chip_min",
        name="Chip Temperature (minimum)",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.chip_temperature_minimum,
    ),
    WhatsminerSensorEntityDescription(
        key="temperature_chip_max",
        name="Chip Temperature (maximum)",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.chip_temperature_maximum,
    ),
    WhatsminerSensorEntityDescription(
        key="temperature_chip_avg",
        name="Chip Temperature (average)",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.chip_temperature_average,
    ),
    WhatsminerSensorEntityDescription(
        key="temperature_device",
        name="Device Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.temperature,
    ),
    WhatsminerSensorEntityDescription(
        key="temperature_environment",
        name="Environment Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.environment_temperature,
    ),
    WhatsminerSensorEntityDescription(
        key="fan_in",
        name="Intake Fan Speed",
        native_unit_of_measurement="RPM",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:fan",
        value=lambda x: x.summary.fan_speed_in,
    ),
    WhatsminerSensorEntityDescription(
        key="fan_out",
        name="Outtake Fan Speed",
        native_unit_of_measurement="RPM",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:fan",
        value=lambda x: x.summary.fan_speed_out,
    ),
    # WhatsminerSensorEntityDescription(
    #     key="fan_psu",
    #     name="PSU Fan Speed",
    #     native_unit_of_measurement=FREQUENCY_HERTZ,
    #     state_class=SensorStateClass.MEASUREMENT,
    #     device_class=SensorDeviceClass.FREQUENCY,
    #     entity_category=EntityCategory.DIAGNOSTIC,
    #     value=lambda x: x.power_unit.fan_speed,
    # ),
    WhatsminerSensorEntityDescription(
        key="power",
        name="Power Usage",
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.power,
    ),
    WhatsminerSensorEntityDescription(
        key="power_rate",
        name="Power Rate",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.power_rate,
    ),
    WhatsminerSensorEntityDescription(
        key="power_mode",
        name="Power Mode",
        entity_category=EntityCategory.CONFIG,
        value=lambda x: x.summary.power_mode,
    ),
    WhatsminerSensorEntityDescription(
        key="uptime",
        name="Uptime",
        native_unit_of_measurement=TIME_SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.uptime,
    ),
    WhatsminerSensorEntityDescription(
        key="accepted",
        name="Accepted",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.accepted,
    ),
    WhatsminerSensorEntityDescription(
        key="rejected",
        name="Rejected",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.rejected,
    ),
    WhatsminerSensorEntityDescription(
        key="rejected_percent",
        name="Rejected Percent",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.pool_rejected_percent,
    ),
    WhatsminerSensorEntityDescription(
        key="stale_percent",
        name="Stale Percent",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda x: x.summary.pool_stale_percent,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: WhatsminerCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    async_add_entities(
        [WhatsminerSensor(coordinator, description) for description in SENSOR_TYPES]
    )


class WhatsminerSensor(OnlineWhatsminerEntity, SensorEntity):
    def __init__(
        self,
        coordinator: WhatsminerCoordinator,
        entity_description: WhatsminerSensorEntityDescription,
    ):
        super(WhatsminerSensor, self).__init__(coordinator)
        self.entity_description: WhatsminerSensorEntityDescription = entity_description
        self._attr_unique_id = f"{coordinator.device_mac}_{entity_description.key}"

    @property
    def native_value(self) -> Union[StateType, date, datetime, Decimal]:
        if not isinstance(self.coordinator.data, OnlineMinerData):
            return None
        return self.entity_description.value(self.coordinator.data)
