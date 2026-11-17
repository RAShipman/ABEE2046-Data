"""
Reference version of the hourly household electricity model (week 1 builds it, week 2 calibrates it).

A home's electricity is the sum of its appliances and its lighting. Each appliance has an annual
energy use, spread over the year in proportion to how likely its activity is at that hour:
    cold appliances      -> evenly (they run all the time)
    'ACTIVE_OCC' items   -> when someone is at home and awake
    'ACT_TV', 'ACT_COOKING', ... -> when that activity is happening
Standby use is spread evenly. Lighting follows the people at home and awake, but only when it is dark
outside (irradiance below 60 W/m2, as in CREST).

Larger households do more of everything, so annual use is scaled by how much more often the linked
activity happens for that household size than for CREST's average household (2.08 people).
"""
import numpy as np
import pandas as pd

CREST_HOUSEHOLD_MIX = {1: 0.339, 2: 0.401, 3: 0.137, 4: 0.088, 5: 0.035}   # CREST 'ActivityStats'
DARK_BELOW_W_M2 = 60
SIGNAL = {"LEVEL": None, "ACTIVE_OCC": "p_active", "ACT_TV": "p_TV", "ACT_COOKING": "p_Cooking",
          "ACT_LAUNDRY": "p_Laundry", "ACT_WASHDRESS": "p_WashDress", "ACT_IRON": "p_Iron",
          "ACT_HOUSECLEAN": "p_HouseClean"}
BANK_HOLIDAYS_2022 = ["2022-01-03", "2022-04-15", "2022-04-18", "2022-05-02", "2022-06-02", "2022-06-03",
                      "2022-08-29", "2022-09-19", "2022-12-26", "2022-12-27"]   # England


def clock(hours_utc, holidays=BANK_HOLIDAYS_2022):
    """UK clock hour and day type for each UTC hour."""
    local = hours_utc.tz_localize("UTC").tz_convert("Europe/London")
    weekend = (local.dayofweek >= 5) | pd.Index(local.date.astype(str)).isin(holidays)
    return np.asarray(local.hour), np.where(weekend, "weekend", "weekday")


def profile_for(profiles, residents, working_from_home=0.0):
    """Profile table (index: day_type, hour) for any household size, including fractions such as 2.6
    (linear between whole sizes). working_from_home moves that share of weekdays towards the weekend pattern."""
    lo = int(np.clip(np.floor(residents), 1, 5))
    hi = int(np.clip(lo + 1, 1, 5))
    f = float(np.clip(residents - lo, 0, 1)) if hi != lo else 0.0
    cols = [c for c in profiles.columns if c not in ("residents", "day_type", "hour")]
    get = lambda n: profiles[profiles.residents == n].set_index(["day_type", "hour"])[cols]
    p = (1 - f) * get(lo) + f * get(hi)
    if working_from_home:
        wd, we = p.loc["weekday"], p.loc["weekend"]
        p.loc["weekday", cols] = ((1 - working_from_home) * wd + working_from_home * we).values
    return p


def mean_signal(profiles, residents, column):
    """Average of a profile column over a typical week (5 weekdays, 2 weekend days)."""
    p = profile_for(profiles, residents)
    return (5 * p.loc["weekday", column].mean() + 2 * p.loc["weekend", column].mean()) / 7


def household_demand(hours_utc, residents, appliances, lighting_kWh, profiles, irradiance,
                     working_from_home=0.0, by_appliance=False):
    """Hourly electricity (kWh) for one home.

    appliances: DataFrame with columns appliance, linked_to, ownership, annual_kWh, standby_W
                (annual_kWh is for an owning household of CREST's average size, standby included)
    irradiance: hourly global horizontal irradiance (W/m2) for the same hours
    """
    hour, day = clock(hours_utc)
    p = profile_for(profiles, residents, working_from_home)
    key = pd.MultiIndex.from_arrays([day, hour])
    out = {}
    for a in appliances.itertuples():
        standby = a.standby_W * 8.76                                  # kWh per year
        running = max(a.annual_kWh - standby, 0.0)
        column = SIGNAL[a.linked_to]
        if column is None:
            shape = np.ones(len(hours_utc))
            scale = 1.0
        else:
            shape = p[column].reindex(key).to_numpy()
            ref = sum(w * mean_signal(profiles, n, column) for n, w in CREST_HOUSEHOLD_MIX.items())
            scale = mean_signal(profiles, residents, column) / ref
        energy = running * scale * len(hours_utc) / 8760              # kWh in this period
        hourly = standby / 8760 + energy * shape / shape.sum()
        out[a.appliance] = a.ownership * hourly
    # lighting: people at home and awake, when it is dark
    dark = (np.asarray(irradiance) < DARK_BELOW_W_M2).astype(float)
    shape = p["lighting_people"].reindex(key).to_numpy() * dark
    ref = sum(w * mean_signal(profiles, n, "lighting_people") for n, w in CREST_HOUSEHOLD_MIX.items())
    scale = mean_signal(profiles, residents, "lighting_people") / ref
    out["LIGHTING"] = lighting_kWh * scale * (len(hours_utc) / 8760) * shape / shape.sum()
    table = pd.DataFrame(out, index=hours_utc)
    return table if by_appliance else table.sum(axis=1)


def sap_occupancy(floor_area_m2):
    """Assumed number of occupants from total floor area (SAP 10, Table 1b)."""
    a = np.asarray(floor_area_m2, dtype=float)
    return np.where(a > 13.9, 1 + 1.76 * (1 - np.exp(-0.000349 * (a - 13.9) ** 2)) + 0.0013 * (a - 13.9), 1.0)


def nmbe_cvrmse(simulated, measured):
    """NMBE and CV(RMSE) in %, over hours where both exist (measured as the reference)."""
    ok = measured.notna() & simulated.notna()
    e = simulated[ok] - measured[ok]
    return 100 * e.sum() / measured[ok].sum(), 100 * np.sqrt((e ** 2).mean()) / measured[ok].mean()


# =============================================================================================
# Student-facing functions (Week 1 onwards). Students import this module and use these two functions;
# everything above is the machinery behind them.
# =============================================================================================
DATA_URL = "https://raw.githubusercontent.com/RAShipman/ABEE2046-Data/main"
_cache = {}


def _inputs():
    """Time profiles and 2022 irradiance, read once from DATA_URL."""
    if DATA_URL not in _cache:
        profiles = pd.read_csv(f"{DATA_URL}/Demand_Time_Profiles.csv")
        irradiance = pd.read_csv(f"{DATA_URL}/Trent_Basin_Irradiance_2022_Hourly.csv", index_col=0, parse_dates=True)
        _cache[DATA_URL] = (profiles, irradiance.iloc[:, 0])
    return _cache[DATA_URL]


def activity_profile(column, residents):
    """The chance of an activity in every hour of 2022, for a household of this size.

    column:    'p_active' (someone at home and awake), 'p_TV', 'p_Cooking', 'p_Laundry',
               'p_WashDress', 'p_Iron', 'p_HouseClean' or 'lighting_people'
    residents: number of people in the home, 1 to 5
    Returns a pandas Series with one value for each hour of 2022 (times in UTC).
    """
    profiles, irradiance = _inputs()
    hours = irradiance.index
    hour, day = clock(hours)
    p = profile_for(profiles, residents)
    values = p[column].reindex(pd.MultiIndex.from_arrays([day, hour])).to_numpy()
    return pd.Series(values, index=hours, name=column)


def home_demand(appliances, residents, lighting_kWh=715):
    """Hourly electricity (kWh) for an average home in 2022.

    appliances:   the appliance table (columns appliance, linked_to, ownership, annual_kWh_CREST, standby_W)
    residents:    number of people in the home, 1 to 5
    lighting_kWh: annual lighting energy for a home of average size (CREST: 715 kWh)
    Returns a DataFrame with one row for each hour of 2022 (times in UTC) and one column for each
    appliance, plus LIGHTING. Add across the columns for the whole home: demand.sum(axis=1).
    """
    profiles, irradiance = _inputs()
    table = appliances.rename(columns={"annual_kWh_CREST": "annual_kWh"})
    demand = household_demand(irradiance.index, residents, table, lighting_kWh, profiles,
                              irradiance.to_numpy(), by_appliance=True)
    demand.index.name = "Time (UTC)"
    return demand


# ---------------------------------------------------------------------------------------------
# Week 2: testing the model against one home's meters


def end_uses(demand):
    """Group the model's hourly demand into the end uses that a home's circuit meters record.

    demand: the table from home_demand()
    Returns a DataFrame with one row for each hour and three columns (kWh in the hour):
      'lighting'  the lights
      'cooking'   the oven and the hob
      'sockets'   everything else, which is plugged into sockets
    """
    cooking = demand[["OVEN", "HOB"]].sum(axis=1)
    sockets = demand.drop(columns=["LIGHTING", "OVEN", "HOB"]).sum(axis=1)
    return pd.DataFrame({"lighting": demand["LIGHTING"], "cooking": cooking, "sockets": sockets})


def measured_monthly(home):
    """Measured electricity of one Trent Basin home in each month of 2022, by end use.

    home: a home label, such as 'Home 22'
    Returns a DataFrame with one row for each month (labelled by its first day) and the columns (kWh):
      'lighting', 'cooking', 'sockets'  the home's circuit meters
      'other'    electricity that is not on a monitored circuit (the boiler and other fixed equipment)
      'total'    the whole home: the four columns above added together
      'hours'    the number of hours in the month
    """
    table = pd.read_csv(f"{DATA_URL}/Home_Circuits_2022_Monthly.csv", parse_dates=["month"])
    table = table[table["home"] == home]
    if len(table) == 0:
        raise ValueError(f"No measurements for {home!r}. Use a label such as 'Home 22'.")
    table = table.set_index("month").drop(columns=["home", "coverage"])
    table.columns = [c.replace("_kWh", "") for c in table.columns]
    return table[["lighting", "cooking", "sockets", "other", "total", "hours"]]


def measured_hourly(home):
    """Measured electricity of one Trent Basin home in each hour of 2022 (kWh, times in UTC).

    home: a home label, such as 'Home 22'
    Returns a pandas Series. A few hours have no reading; these are left empty (NaN).
    """
    table = pd.read_csv(f"{DATA_URL}/Household_Electricity_2022_Hourly_Phase1.csv", index_col=0, parse_dates=True)
    if home not in table.columns:
        raise ValueError(f"No measurements for {home!r}. Use a label such as 'Home 22'.")
    return table[home]
