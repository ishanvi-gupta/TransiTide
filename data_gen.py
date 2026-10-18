"""Generate synthetic hourly station entries (2023-2024).
Swap this for real data (e.g. NYC MTA ridership) - see README."""
import os, numpy as np, pandas as pd
from config import STATIONS, HOURS

rng = np.random.default_rng(42)
g = lambda h, mu, s: np.exp(-0.5 * ((h - mu) / s) ** 2)
PROFILES = {
    "residential": lambda h: 1.0*g(h, 8.5, 1.5) + 0.55*g(h, 18.5, 2) + 0.2*g(h, 13, 3),
    "business":    lambda h: 0.5*g(h, 9, 1.5) + 1.0*g(h, 18, 1.8) + 0.25*g(h, 13, 3),
    "mixed":       lambda h: 0.8*g(h, 9, 1.5) + 0.85*g(h, 18, 1.8) + 0.45*g(h, 13, 3),
}
WEEKEND = {"residential": 0.7, "business": 0.45, "mixed": 0.8}

dates = pd.date_range("2023-01-01", "2024-12-31")
fixed = {(1, 26), (8, 15), (10, 2), (12, 25)}
wkdays = dates[dates.dayofweek < 5].values
extra = set(pd.to_datetime(rng.choice(wkdays, 16, replace=False)))
holidays = {d for d in dates if (d.month, d.day) in fixed} | extra

ts = pd.DataFrame([(d, h) for d in dates for h in HOURS], columns=["date", "hour"])
ts["dow"] = ts.date.dt.dayofweek
ts["month"] = ts.date.dt.month
ts["is_weekend"] = (ts.dow >= 5).astype(int)
ts["is_holiday"] = ts.date.isin(holidays).astype(int)
doy = ts.date.dt.dayofyear
day_noise = ts.groupby("date")["hour"].transform(lambda x: rng.normal(0, 2))
ts["temp"] = (25 + 10*np.sin(2*np.pi*(doy-100)/365) + day_noise
              + 3*np.sin(np.pi*(ts.hour-8)/12)).round(1)
wet = np.where(ts.month.isin([7, 8, 9]), 0.35, 0.06)
ts["rain"] = ((rng.random(len(ts)) < wet) * rng.exponential(4, len(ts))).round(1)
ts["ts"] = ts.date + pd.to_timedelta(ts.hour, unit="h")

out = []
for s in STATIONS:
    d = ts.copy()
    d["station"], d["station_id"] = s["code"], s["id"]
    ev_days = set(pd.to_datetime(rng.choice(dates.values, 25, replace=False)))
    d["event"] = (d.date.isin(ev_days) & d.hour.between(16, 22)).astype(int)
    off = (d.is_weekend | d.is_holiday).astype(bool)
    mu = (s["peak"] * PROFILES[s["kind"]](d.hour.values)
          * np.where(off, WEEKEND[s["kind"]], 1.0)
          * (1 + 0.04*np.minimum(d.rain, 10))
          * (1 + 0.05*(d.temp > 38))
          * np.where(d.event == 1, 1.5, 1.0))
    d["entries"] = (mu * rng.lognormal(0, 0.08, len(d))).round().astype(int)
    out.append(d)

df = pd.concat(out).drop(columns="date")
os.makedirs("data", exist_ok=True)
df.to_csv("data/entries.csv", index=False)
print("rows:", len(df))
