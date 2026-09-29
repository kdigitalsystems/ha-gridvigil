"""Constants for the GridVigil integration."""

from datetime import timedelta
import logging

DOMAIN = "gridvigil"
LOGGER = logging.getLogger(__package__)

API_BASE = "https://gridvigil.com/api/v1"
CONF_GRID_ID = "grid_id"

# GridVigil's pipeline refreshes roughly every 6 hours, so polling more
# often than this only repeats the same numbers.
SCAN_INTERVAL = timedelta(minutes=30)

ATTRIBUTION = "Data from GridVigil (gridvigil.com), built from public EIA, grid operator, NERC and NOAA data"

# Pressure bands, lowest to highest (score <40, <60, <80, 80+).
PRESSURE_BANDS = ["good", "warning", "serious", "critical"]
STRESSED_BANDS = ("serious", "critical")
