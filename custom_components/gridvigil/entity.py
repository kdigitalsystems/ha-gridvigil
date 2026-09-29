"""Base entity: one device per grid region."""

from typing import Any

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import GridVigilCoordinator


def dig(data: dict[str, Any], *keys: str) -> Any:
    """Nested lookup that returns None when any level is missing or null."""
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


class GridVigilEntity(CoordinatorEntity[GridVigilCoordinator]):
    """Shared device info and naming for every GridVigil entity."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: GridVigilCoordinator, key: str) -> None:
        super().__init__(coordinator)
        grid_id = coordinator.grid_id
        self._attr_unique_id = f"{grid_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, grid_id)},
            name=coordinator.data.get("name") or grid_id,
            manufacturer="GridVigil",
            model=coordinator.data.get("iso_rto"),
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=f"https://gridvigil.com/region/{grid_id}/",
        )
