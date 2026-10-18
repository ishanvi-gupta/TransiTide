# TransiTide: Metro Station Congestion Forecaster

Predicts hourly station congestion from calendar, weather and event signals,
then recommends entrance rebalancing and quieter travel times.

## Run
```bash
pip install -r requirements.txt
python data_gen.py      # synthetic data (or plug in real data, below)
python train.py         # trains LightGBM, prints metrics vs. baseline
streamlit run app.py
```

## Structure
- `config.py`    stations, capacities, simulated entrance split, features
- `data_gen.py`  synthetic hourly entries (2023-2024)
- `train.py`     time-based split, seasonal baseline, LightGBM, metrics
- `predict.py`   what-if forecasting for all stations
- `recommend.py` entrance rebalancing + time-shift suggestion
- `app.py`       Streamlit map, heatmap and recommendation panel

## Use real data
Replace `data_gen.py` output with a CSV having columns:
`ts, station, station_id, hour, dow, month, is_weekend, is_holiday, event, rain, temp, entries`
- Ridership: NYC MTA hourly ridership (data.ny.gov), Hong Kong MTR, or Delhi Metro station data
- Weather: Open-Meteo (free, no key, hourly history)
- Holidays: the `holidays` Python package
- Update `config.py` with your stations and coordinates

## Honest limitations
- Entrance/platform splits are simulated; public data is station-level
- "Congestion" = entries / assumed capacity, not measured crowd density
- Shift behaviour (`max_shift`) is an assumption; validate with surveys if possible

## Upgrade ideas
Lag features and nowcasting, quantile forecasts (prediction intervals),
graph neural net across the line network, SHAP explanations, Docker + deploy to
Hugging Face Spaces / Render, MLflow experiment tracking.
