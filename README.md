# ABEE2046 Data

Data and model files for the ABEE2046 Smart Energy and the Built Environment workshop notebooks (University of Nottingham). The notebooks download these files themselves, so you don't need to download anything from here.

## Files

| File | What it holds | Used in |
|---|---|---|
| `household_model.py` | Hourly household electricity model: appliances spread over the hours of 2022 by activity, plus lighting | Week 1 onwards |
| `Demand_Appliances.csv` | One row per appliance type: ownership, power when running and on standby, annual energy use | Week 1 onwards |
| `Demand_Time_Profiles.csv` | Chance of each activity (at home and awake, TV, cooking, laundry, ...) by household size, weekday or weekend, and hour | Week 1 onwards |
| `Trent_Basin_Irradiance_2022_Hourly.csv` | Global horizontal irradiance at Trent Basin, Nottingham, every hour of 2022 (UTC) | Week 1 (lighting), Week 3 (solar PV) |
| `Evidence_SERL_2022.csv` | Average household electricity use in Great Britain in 2022, by number of people and by time of day | Week 1 |

All times are UTC, as for smart meter data.

## Sources

- **Appliances and activity profiles:** adapted from the CREST Demand Model (McKenna and Thomson, 2016, *Applied Energy* 165, 445 to 461), whose activity data come from the UK 2000 Time Use Survey. The ECUK columns use the Department for Energy Security and Net Zero's *Energy Consumption in the UK* tables.
- **Irradiance:** ERA5 reanalysis via Open-Meteo. Contains modified Copernicus Climate Change Service information, 2026.
- **SERL:** summary figures from the Smart Energy Research Lab statistical report on 2022 GB domestic energy use.
