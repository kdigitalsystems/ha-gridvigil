import json

import aiohttp
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.gridvigil.const import CONF_GRID_ID, DOMAIN

from .conftest import API, OCTET_STREAM, fixture_json


async def _setup(hass: HomeAssistant, grid_id: str) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, unique_id=grid_id, data={CONF_GRID_ID: grid_id}, title=grid_id)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _state(hass: HomeAssistant, platform: str, unique_id: str):
    entity_id = er.async_get(hass).async_get_entity_id(platform, DOMAIN, unique_id)
    return hass.states.get(entity_id) if entity_id else None


async def test_ercot_entities_match_the_api(hass: HomeAssistant, mock_api) -> None:
    await _setup(hass, "ercot")
    s = fixture_json("status_ercot.json")

    assert float(_state(hass, "sensor", "ercot_pressure_score").state) == s["status"]["pressure_score"]
    assert _state(hass, "sensor", "ercot_pressure_band").state == s["status"]["pressure_band"]
    demand = _state(hass, "sensor", "ercot_demand")
    assert float(demand.state) == s["demand"]["current_mw"]
    assert demand.attributes["unit_of_measurement"] == "MW"
    assert float(_state(hass, "sensor", "ercot_reserve_margin").state) == s["capacity"]["reserve_margin_pct"]
    assert float(_state(hass, "sensor", "ercot_wholesale_price").state) == s["prices"]["market_average_per_mwh"]
    assert float(_state(hass, "sensor", "ercot_carbon_intensity").state) == s["carbon_intensity"]["gco2_per_kwh"]
    alerts = _state(hass, "sensor", "ercot_weather_alerts")
    assert int(alerts.state) == len(s["weather"]["active_alert_types"])
    assert alerts.attributes["alert_types"] == s["weather"]["active_alert_types"]

    stressed = _state(hass, "binary_sensor", "ercot_grid_stressed")
    expected = "on" if s["status"]["pressure_band"] in ("serious", "critical") else "off"
    assert stressed.state == expected


async def test_a_grid_without_a_price_gets_no_price_sensor(hass: HomeAssistant, mock_api) -> None:
    assert fixture_json("status_spp.json")["prices"] is None
    await _setup(hass, "spp")
    assert _state(hass, "sensor", "spp_pressure_score") is not None
    assert er.async_get(hass).async_get_entity_id("sensor", DOMAIN, "spp_wholesale_price") is None


async def test_critical_pressure_turns_grid_stressed_on(hass: HomeAssistant, aioclient_mock) -> None:
    s = fixture_json("status_ercot.json")
    s["status"].update(pressure_score=85.0, pressure_band="critical", pressure_band_label="Critical pressure")
    aioclient_mock.get(f"{API}/grid/ercot/status", text=json.dumps(s), headers=OCTET_STREAM)
    await _setup(hass, "ercot")
    assert _state(hass, "binary_sensor", "ercot_grid_stressed").state == "on"


async def test_a_failed_refresh_marks_entities_unavailable(hass: HomeAssistant, mock_api) -> None:
    entry = await _setup(hass, "ercot")
    mock_api.clear_requests()
    mock_api.get(f"{API}/grid/ercot/status", exc=aiohttp.ClientError())
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert _state(hass, "sensor", "ercot_pressure_score").state == STATE_UNAVAILABLE


async def test_unload(hass: HomeAssistant, mock_api) -> None:
    entry = await _setup(hass, "ercot")
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED
