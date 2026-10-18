"""Train LightGBM forecaster, compare to seasonal baseline, save artifacts."""
import json, joblib, pandas as pd, lightgbm as lgb
from sklearn.metrics import mean_absolute_error
from config import FEATURES

import os; os.makedirs("models", exist_ok=True)
df = pd.read_csv("data/entries.csv", parse_dates=["ts"])
df["date"] = df.ts.dt.normalize()
test_start = df.date.max() - pd.Timedelta(days=60)
val_start = test_start - pd.Timedelta(days=30)
train = df[df.date <= val_start]
val = df[(df.date > val_start) & (df.date <= test_start)]
test = df[df.date > test_start]

# Seasonal baseline feature: avg entries per station / weekday / hour (train only)
how = (train.groupby(["station", "dow", "hour"]).entries.mean()
       .rename("how_mean").reset_index())
add = lambda x: x.merge(how, on=["station", "dow", "hour"], how="left")
train, val, test = add(train), add(val), add(test)

model = lgb.LGBMRegressor(n_estimators=1000, learning_rate=0.05,
                          num_leaves=63, subsample=0.8, colsample_bytree=0.8,
                          verbose=-1)
model.fit(train[FEATURES], train.entries,
          eval_set=[(val[FEATURES], val.entries)],
          callbacks=[lgb.early_stopping(50, verbose=False)])

pred = model.predict(test[FEATURES]).clip(0)
mae = mean_absolute_error(test.entries, pred)
base = mean_absolute_error(test.entries, test.how_mean)
wape = abs(test.entries - pred).sum() / test.entries.sum()
metrics = dict(model_mae=round(mae, 1), baseline_mae=round(base, 1),
               improvement_pct=round(100*(base-mae)/base, 1),
               wape_pct=round(100*wape, 2))
print(metrics)

# Refit on train+val for the final model
full = pd.concat([train, val])
model.set_params(n_estimators=model.best_iteration_ or 300)
model.fit(full[FEATURES], full.entries)
joblib.dump(model, "models/lgbm.pkl")
how.to_csv("models/how_mean.csv", index=False)
json.dump(metrics, open("models/metrics.json", "w"), indent=2)
