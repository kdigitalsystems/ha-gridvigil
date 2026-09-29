"""A single on/off signal for automations: is this grid under serious pressure?"""

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import STRESSED_BANDS
from .coordinator import GridVigilConfigEntry, GridVigilCoordinator
from .entity import GridVigilEntity, dig

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GridVigilConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([GridStressedSensor(entry.runtime_data)])


class GridStressedSensor(GridVigilEntity, BinarySensorEntity):
    """On when the Power Pressure Score is in the elevated or critical band (60+)."""

    _attr_translation_key = "grid_stressed"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: GridVigilCoordinator) -> None:
        super().__init__(coordinator, "grid_stressed")

    @property
    def is_on(self) -> bool | None:
        band = dig(self.coordinator.data, "status", "pressure_band")
        return None if band is None else band in STRESSED_BANDS

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "pressure_score": dig(self.coordinator.data, "status", "pressure_score"),
            "pressure_band": dig(self.coordinator.data, "status", "pressure_band_label"),
        }
