# Apple Style Weather App - Streamlit Cloud Edition
# --------------------------------------------------
# Ultra iOS-inspired visual design implemented in pure Python.
# This version removes all React/TSX code and uses valid
# Streamlit syntax only.

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Apple Style Weather", layout="centered")

# -----------------------------
# City Selection
# -----------------------------
CITIES = {
    "New York": (40.7128, -74.0060, "America/New_York"),
    "Arlington": (38.8500, -77.0400, "America/New_York"),
    "Dorset": (43.2548, -73.0973, "America/New_York"),
}

city = st.selectbox("Select City", list(CITIES.keys()))
lat, lon, tz_name = CITIES[city]

# -----------------------------
# Cached Weather Fetch
# -----------------------------
@st.cache_data(ttl=600)
def fetch_weather(lat, lon, tz):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,apparent_temperature,precipitation_probability,windspeed_10m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "temperature_unit": "fahrenheit",
        "windspeed_unit": "mph",
        "timezone": tz,
        "forecast_days": 7,
    }
    try:
        r = requests.get(url, params=params, timeout=6)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

raw = fetch_weather(lat, lon, tz_name)

if raw is None:
    st.error("Unable to fetch live weather data.")
    st.stop()

# -----------------------------
# Time and Day/Night
# -----------------------------
tz = pytz.timezone(tz_name)
now = datetime.now(tz)
now_hour = now.strftime("%Y-%m-%dT%H:00")
times = raw["hourly"]["time"]
index = times.index(now_hour) if now_hour in times else 0

is_day = 6 <= now.hour < 18

# -----------------------------
# Current Conditions
# -----------------------------
current_temp = round(raw["hourly"]["temperature_2m"][index])
feels_like = round(raw["hourly"]["apparent_temperature"][index])
precip = raw["hourly"]["precipitation_probability"][index]
wind = round(raw["hourly"]["windspeed_10m"][index])

# -----------------------------
# iOS Style Background
# -----------------------------
background = (
    "radial-gradient(circle at 50% 0%, #89CFF0 0%, #4facfe 40%, #1e3c72 100%)"
    if is_day
    else "radial-gradient(circle at 50% 0%, #3a4a63 0%, #141E30 50%, #0f2027 100%)"
)

st.markdown(
    f"""
    <style>
    .stApp {{ background: {background}; color: white; }}
    .city {{ font-size: 34px; text-align: center; margin-top: 20px; }}
    .big-temp {{ font-size: 110px; font-weight: 200; text-align: center; line-height: 1; }}
    .glass {{
        background: rgba(255,255,255,0.12);
        backdrop-filter: blur(25px);
        border-radius: 32px;
        padding: 20px;
        margin-top: 20px;
        border: 1px solid rgba(255,255,255,0.15);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Header
# -----------------------------
st.markdown(f"<div class='city'>{city}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='big-temp'>{current_temp}°</div>", unsafe_allow_html=True)
st.caption(f"Feels like {feels_like}° | Wind {wind} mph")

# -----------------------------
# Hourly Forecast with Precip Bars
# -----------------------------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.subheader("Next 12 Hours")

hourly_df = pd.DataFrame({
    "Time": pd.to_datetime(raw["hourly"]["time"][:12]),
    "Temp": raw["hourly"]["temperature_2m"][:12],
    "Precip": raw["hourly"]["precipitation_probability"][:12],
})

for i, row in hourly_df.iterrows():
    label = "Now" if i == 0 else row["Time"].strftime("%I %p")
    st.write(f"{label}  |  {round(row['Temp'])}°")
    st.progress(int(row["Precip"]))

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 7 Day Forecast with Range Bars
# -----------------------------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.subheader("7 Day Forecast")

highs = raw["daily"]["temperature_2m_max"]
lows = raw["daily"]["temperature_2m_min"]

min_temp = min(lows)
max_temp = max(highs)
range_temp = max_temp - min_temp

for i, date_str in enumerate(raw["daily"]["time"]):
    day = "Today" if i == 0 else datetime.fromisoformat(date_str).strftime("%a")
    high = round(highs[i])
    low = round(lows[i])

    low_percent = int(((low - min_temp) / range_temp) * 100) if range_temp else 0
    width_percent = int(((high - low) / range_temp) * 100) if range_temp else 0

    st.write(f"{day}  {low}° / {high}°")
    st.markdown(
        f"""
        <div style='background:rgba(255,255,255,0.25); height:4px; border-radius:4px;'>
            <div style='margin-left:{low_percent}%; width:{width_percent}%; height:4px; background:white; border-radius:4px;'></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Basic Validation Test
# -----------------------------
if __name__ == "__main__":
    sample = {
        "hourly": {
            "time": ["2024-01-01T00:00:00"],
            "temperature_2m": [70],
            "apparent_temperature": [68],
            "precipitation_probability": [20],
            "windspeed_10m": [5],
        },
        "daily": {
            "time": ["2024-01-01"],
            "temperature_2m_max": [75],
            "temperature_2m_min": [60],
        },
    }
    assert sample["hourly"]["temperature_2m"][0] == 70

















































