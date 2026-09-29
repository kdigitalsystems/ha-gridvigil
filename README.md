# GridVigil for Home Assistant

Live grid pressure for the 10 major U.S. power grids, in Home Assistant. Know when your grid is under strain, and automate around it: delay EV charging, pre-cool the house, or just get a heads-up before a heat wave tightens supply.

Data comes from [GridVigil](https://gridvigil.com), which builds a 0-100 **Power Pressure Score** for each region from public EIA, grid operator, NERC and NOAA data. Free, no API key.

Supported regions: ERCOT (Texas), PJM (Mid-Atlantic / Midwest), CAISO (California), MISO (Midcontinent), SPP (Southwest Power Pool), NYISO (New York), ISO-NE (New England), and the Southeast, Mountain West and Florida regions outside an ISO.

## Installation

### HACS (recommended)

1. In HACS, open the menu (top right) and choose **Custom repositories**.
2. Add `https://github.com/kdigitalsystems/ha-gridvigil` with type **Integration**.
3. Install **GridVigil**, then restart Home Assistant.

### Manual

Copy `custom_components/gridvigil` into your Home Assistant `config/custom_components/` folder and restart.

## Setup

**Settings → Devices & services → Add integration → GridVigil**, then pick your grid region. Add it again to track more than one region.

## Entities

Each region is a device with these entities:

| Entity | Meaning |
|---|---|
| Power Pressure Score | 0-100; higher means supply is tighter relative to demand |
| Pressure level | Low (under 40), Moderate (40-59), Elevated (60-79) or Critical (80+) |
| Grid stressed | Binary sensor, **on** at Elevated or Critical (score 60+). Built for automations |
| Demand | Current electricity demand across the region, in MW |
| Recent peak demand | Highest demand over roughly the past two weeks, in MW |
| Reserve margin | Planning reserve margin from the grid operator or NERC, in % |
| Wholesale price | Day-ahead market price in USD/MWh (ERCOT, CAISO and NYISO only) |
| Carbon intensity | Estimated from the generation mix, in gCO2/kWh |
| Active weather alerts | Number of active National Weather Service alert types, with the list as an attribute |

Entities a region doesn't publish (for example, a wholesale price outside ERCOT, CAISO and NYISO) aren't created.

GridVigil refreshes its data about every 6 hours; the integration checks every 30 minutes.

## Example automations

Get a notification when the Texas grid comes under elevated pressure:

```yaml
automation:
  - alias: "Texas grid stressed"
    triggers:
      - trigger: state
        entity_id: binary_sensor.ercot_texas_grid_stressed
        to: "on"
    actions:
      - action: notify.notify
        data:
          message: >
            ERCOT is under elevated pressure (score
            {{ state_attr('binary_sensor.ercot_texas_grid_stressed', 'pressure_score') }}).
            Consider holding off on heavy loads.
```

Pause EV charging while the grid is stressed:

```yaml
automation:
  - alias: "Pause EV charging during grid stress"
    triggers:
      - trigger: state
        entity_id: binary_sensor.ercot_texas_grid_stressed
        to: "on"
    actions:
      - action: switch.turn_off
        target:
          entity_id: switch.ev_charger
```

Entity IDs follow your region's name, so `ercot_texas` becomes `pjm_mid_atlantic_midwest`, `caiso_california`, and so on. Check **Settings → Entities** for the exact IDs.

## About the data

The Power Pressure Score combines demand growth, reserve margins, large-load (data center) interconnection requests, generation additions and retirements, weather, and, where market data allows, transmission congestion. See [GridVigil's methodology](https://gridvigil.com/methodology/) for how it's calculated, and the [API docs](https://gridvigil.com/developers/) if you'd rather query it directly.

GridVigil is independent and isn't affiliated with ERCOT, PJM or any other grid operator. It's an information tool, not an official emergency notice: for conservation appeals and outage alerts, follow your grid operator and utility.

## License

MIT
