import aiohttp
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.gridvigil.const import CONF_GRID_ID, DOMAIN

from .conftest import API


async def test_picking_a_grid_creates_an_entry(hass: HomeAssistant, mock_api) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_GRID_ID: "ercot"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "ERCOT (Texas)"
    assert result["data"] == {CONF_GRID_ID: "ercot"}


async def test_the_same_grid_cannot_be_added_twice(hass: HomeAssistant, mock_api) -> None:
    MockConfigEntry(domain=DOMAIN, unique_id="ercot", data={CONF_GRID_ID: "ercot"}).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_GRID_ID: "ercot"})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_unreachable_api_aborts_cleanly(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(f"{API}/grids", exc=aiohttp.ClientError())
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"
