"""Polls one grid's status from the GridVigil API."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GridVigilApiError, fetch_status
from .const import CONF_GRID_ID, DOMAIN, LOGGER, SCAN_INTERVAL

type GridVigilConfigEntry = ConfigEntry[GridVigilCoordinator]


class GridVigilCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches the status payload shared by every entity of one grid."""

    config_entry: GridVigilConfigEntry

    def __init__(self, hass: HomeAssistant, entry: GridVigilConfigEntry) -> None:
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{entry.data[CONF_GRID_ID]}",
            update_interval=SCAN_INTERVAL,
        )
        self.grid_id: str = entry.data[CONF_GRID_ID]
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await fetch_status(self._session, self.grid_id)
        except GridVigilApiError as err:
            raise UpdateFailed(str(err)) from err
