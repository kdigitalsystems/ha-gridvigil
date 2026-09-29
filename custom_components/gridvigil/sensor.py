"""Sensors for one grid region."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import PRESSURE_BANDS
from .coordinator import GridVigilConfigEntry, GridVigilCoordinator
from .entity import GridVigilEntity, dig

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class GridVigilSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], StateType]
    attrs_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    # Evaluated once at setup: fields a grid doesn't publish at all (a
    # wholesale price in a market without one) get no entity, rather than
    # a permanently unknown one.
    exists_fn: Callable[[dict[str, Any]], bool] = lambda _: True


SENSORS: tuple[GridVigilSensorDescription, ...] = (
    GridVigilSensorDescription(
        key="pressure_score",
        translation_key="pressure_score",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda d: dig(d, "status", "pressure_score"),
        attrs_fn=lambda d: {"confidence": dig(d, "status", "confidence")},
    ),
    GridVigilSensorDescription(
        key="pressure_band",
        translation_key="pressure_band",
        device_class=SensorDeviceClass.ENUM,
        options=PRESSURE_BANDS,
        value_fn=lambda d: dig(d, "status", "pressure_band"),
    ),
    GridVigilSensorDescription(
        key="demand",
        translation_key="demand",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda d: dig(d, "demand", "current_mw"),
        attrs_fn=lambda d: {"as_of": dig(d, "demand", "as_of")},
    ),
    GridVigilSensorDescription(
        key="recent_peak_demand",
        translation_key="recent_peak_demand",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda d: dig(d, "demand", "recent_peak_mw"),
    ),
    GridVigilSensorDescription(
        key="reserve_margin",
        translation_key="reserve_margin",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda d: dig(d, "capacity", "reserve_margin_pct"),
        attrs_fn=lambda d: {
            "source": dig(d, "capacity", "reserve_margin_source"),
            "as_of": dig(d, "capacity", "reserve_margin_as_of"),
        },
        exists_fn=lambda d: dig(d, "capacity", "reserve_margin_pct") is not None,
    ),
    GridVigilSensorDescription(
        key="wholesale_price",
        translation_key="wholesale_price",
        native_unit_of_measurement="USD/MWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda d: dig(d, "prices", "market_average_per_mwh"),
        attrs_fn=lambda d: {"as_of": dig(d, "prices", "as_of")},
        exists_fn=lambda d: dig(d, "prices", "market_average_per_mwh") is not None,
    ),
    GridVigilSensorDescription(
        key="carbon_intensity",
        translation_key="carbon_intensity",
        native_unit_of_measurement="gCO2/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda d: dig(d, "carbon_intensity", "gco2_per_kwh"),
        attrs_fn=lambda d: {
            "as_of": dig(d, "carbon_intensity", "as_of"),
            "source": dig(d, "carbon_intensity", "source"),
        },
        exists_fn=lambda d: dig(d, "carbon_intensity", "gco2_per_kwh") is not None,
    ),
    GridVigilSensorDescription(
        key="weather_alerts",
        translation_key="weather_alerts",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: len(dig(d, "weather", "active_alert_types") or []),
        attrs_fn=lambda d: {
            "alert_types": dig(d, "weather", "active_alert_types") or [],
            "max_severity": dig(d, "weather", "max_severity"),
        },
        exists_fn=lambda d: dig(d, "weather") is not None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GridVigilConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        GridVigilSensor(coordinator, description) for description in SENSORS if description.exists_fn(coordinator.data)
    )


class GridVigilSensor(GridVigilEntity, SensorEntity):
    entity_description: GridVigilSensorDescription

    def __init__(self, coordinator: GridVigilCoordinator, description: GridVigilSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attrs_fn is None:
            return None
        return self.entity_description.attrs_fn(self.coordinator.data)
