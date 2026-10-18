import streamlit as st, plotly.express as px, pandas as pd
from config import HOURS, STATIONS, STATION
from predict import load, forecast
from recommend import entrance_plan, best_shift

st.set_page_config(page_title="TransiTide", page_icon="🌊", layout="wide")
st.title("TransiTide: Metro Congestion Forecaster")

@st.cache_resource
def get_model():
    return load()
model, how = get_model()

with st.sidebar:
    date = st.date_input("Date", pd.Timestamp("2025-01-15"))
    hour = st.slider("Hour", HOURS[0], HOURS[-1], 9)
    rain = st.slider("Rain (mm/h)", 0.0, 15.0, 0.0)
    temp = st.slider("Temperature (C)", 5, 45, 30)
    holiday = st.checkbox("Public holiday")
    ev = st.selectbox("Event nearby", [None] + [s["code"] for s in STATIONS],
                      format_func=lambda c: "None" if c is None else STATION[c]["name"])

day = forecast(model, how, date, HOURS, rain, temp, holiday, ev)
now = day[day.hour == hour]

c1, c2 = st.columns([3, 2])
with c1:
    fig = px.scatter_map(now, lat="lat", lon="lon", color="congestion",
                         size="pred", hover_name="name", zoom=9.5,
                         range_color=(0, 1.3), color_continuous_scale="RdYlGn_r",
                         height=450)
    st.plotly_chart(fig, width="stretch")
with c2:
    pivot = day.pivot(index="name", columns="hour", values="congestion")
    st.plotly_chart(px.imshow(pivot, color_continuous_scale="RdYlGn_r",
                              zmin=0, zmax=1.3, aspect="auto", height=450),
                    width="stretch")

st.subheader("Recommendations")
code = st.selectbox("Station", [s["code"] for s in STATIONS],
                    format_func=lambda c: STATION[c]["name"])
sd = day[day.station == code].set_index("hour")
row = sd.loc[hour]
st.metric("Predicted entries", int(row.pred), f"congestion {row.congestion:.0%}")
plan = entrance_plan(code, row.pred)
st.dataframe(plan, hide_index=True)
bh, cur, new = best_shift(sd.congestion.to_dict(), hour)
if cur > 0.9 and bh != hour:
    st.info(f"Travelling at {bh}:00 instead of {hour}:00 cuts congestion "
            f"from {cur:.0%} to {new:.0%}.")
else:
    st.success("Congestion is manageable at this time.")
