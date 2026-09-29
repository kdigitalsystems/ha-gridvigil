import json
from pathlib import Path

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"

FIXTURES = Path(__file__).parent / "fixtures"
API = "https://gridvigil.com/api/v1"
# What the live API currently sends for these extensionless files.
OCTET_STREAM = {"Content-Type": "application/octet-stream"}


def fixture_json(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture
def mock_api(aioclient_mock):
    aioclient_mock.get(f"{API}/grids", text=(FIXTURES / "grids.json").read_text(), headers=OCTET_STREAM)
    for grid in ("ercot", "spp"):
        aioclient_mock.get(
            f"{API}/grid/{grid}/status",
            text=(FIXTURES / f"status_{grid}.json").read_text(),
            headers=OCTET_STREAM,
        )
    return aioclient_mock
