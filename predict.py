import joblib, pandas as pd
from config import STATIONS, FEATURES


def load():
    return joblib.load("models/lgbm.pkl"), pd.read_csv("models/how_mean.csv")


def forecast(model, how, date, hours, rain=0.0, temp=30.0,
             holiday=False, event_station=None):
    """Predict entries + congestion index for every station/hour (what-if)."""
    date = pd.Timestamp(date)
    rows = []
    for s in STATIONS:
        for h in hours:
            rows.append(dict(
                station=s["code"], station_id=s["id"], name=s["name"],
                lat=s["lat"], lon=s["lon"], capacity=s["capacity"],
                hour=h, dow=date.dayofweek, month=date.month,
                is_weekend=int(date.dayofweek >= 5), is_holiday=int(holiday),
                event=int(event_station == s["code"] and 16 <= h <= 22),
                rain=rain, temp=temp))
    df = pd.DataFrame(rows).merge(how, on=["station", "dow", "hour"], how="left")
    df["pred"] = model.predict(df[FEATURES]).clip(min=0)
    df["congestion"] = df.pred / df.capacity
    return df
