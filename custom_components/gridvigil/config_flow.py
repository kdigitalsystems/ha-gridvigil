"""Config flow: pick which grid region to track."""

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
import voluptuous as vol

from .api import GridVigilApiError, fetch_grids
from .const import CONF_GRID_ID, DOMAIN


class GridVigilConfigFlow(ConfigFlow, domain=DOMAIN):
    """One config entry per grid region."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        try:
            grids = await fetch_grids(async_get_clientsession(self.hass))
        except GridVigilApiError:
            return self.async_abort(reason="cannot_connect")
        names = {g["grid_id"]: g["name"] for g in grids}

        if user_input is not None:
            grid_id = user_input[CONF_GRID_ID]
            await self.async_set_unique_id(grid_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=names.get(grid_id, grid_id), data={CONF_GRID_ID: grid_id})

        schema = vol.Schema(
            {
                vol.Required(CONF_GRID_ID): SelectSelector(
                    SelectSelectorConfig(
                        options=[SelectOptionDict(value=gid, label=name) for gid, name in names.items()],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
