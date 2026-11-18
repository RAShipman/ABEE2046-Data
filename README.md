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
| `Home_Circuits_2022_Monthly.csv` | Measured electricity of 13 Trent Basin homes in each month of 2022, by end use: lighting, cooking (oven and hob), sockets, other and total | Week 2 |
| `Household_Electricity_2022_Hourly.csv` | Measured electricity of 13 Trent Basin homes in each hour of 2022 (UTC) | Week 1 |
| `Household_Details.csv` | Number of bedrooms of those 13 homes | Week 1 |
| `Site_Electricity_Demand_2022_Hourly.csv` | Baseline electricity demand of the homes in each hour of 2022 (UTC), from the metered homes, scaled up to the 31 homes on the site | Week 2 onwards |
| `Home_Heat_2022_Daily.csv` | Two Trent Basin houses, each day of 2022 (UTC): space heating and hot water from their heat meters, electricity, indoor and outdoor temperature, sunshine | Week 2 |
| `Home_Heat_2022_Hourly.csv` | One of those houses (Home 12), each hour of 2022 (UTC): the same columns. Its meter counts in whole kWh, so use it averaged over many days | Week 2 |
| `Site_Heat_2022_Daily.csv` | The 31 homes' space heating and hot water each day of 2022, pooled from the homes with heat meters and scaled by floor area, with temperatures, electricity and sunshine; days with no meter readings are filled from a model and marked | Week 2 onwards |
| `Site_Heat_2022_Hourly.csv` | The same, hour by hour (the shape of each day comes from the heat meters, averaged over homes) | Week 2 onwards |

All times are UTC, as for smart meter data.

## Sources

- **Appliances and activity profiles:** adapted from the CREST Demand Model (McKenna and Thomson, 2016, *Applied Energy* 165, 445 to 461), whose activity data come from the UK 2000 Time Use Survey. The ECUK columns use the Department for Energy Security and Net Zero's *Energy Consumption in the UK* tables.
- **Irradiance:** ERA5 reanalysis via Open-Meteo. Contains modified Copernicus Climate Change Service information, 2026.
- **Measured homes:** Project SCENe, the University of Nottingham's community energy research project at Trent Basin (Shipman and Gillott, 2019, *Future Cities and Environment* 5(1), 6). Homes are labelled, and the labels cannot be linked to an address.
- **SERL:** summary figures from the Smart Energy Research Lab statistical report on 2022 GB domestic energy use.
