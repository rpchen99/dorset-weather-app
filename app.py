# -*- coding: utf-8 -*-
# Apple Style Weather App - Streamlit Cloud Version
# Pure Python implementation with emoji weather icons

import streamlit as st
import requests
from datetime import datetime
import pytz

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Apple Style Weather", layout="centered")

# -----------------------------
# Weather Code -> Emoji Mapping
# -----------------------------
WMO_ICONS = {
    0: "☀️", 1: "🌤", 2: "⛅", 3: "☁️",
    45: "🌫", 48: "🌫",
    51: "🌦", 53: "🌦", 55: "🌧",
    61: "🌧", 63: "🌧", 65: "🌧",
    71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️",
    80: "🌦", 81: "🌧", 82: "⛈",
    85: "❄️", 86: "❄️",
    95: "⛈",
}

def get_icon(code):
    return WMO_ICONS.get(code, "❔")

# -----------------------------
# City Selection (Dorset default)
# -----------------------------
CITIES = {
    "Dorset": (43.2548, -73.0973, "America/New_York"),
    "New York": (40.7128, -74.0060, "America/New_York"),
    "Arlington": (38.8500, -77.0400, "America/New_York"),
}

city_names = list(CITIES.keys())
city = st.selectbox("Select City", city_names, index=0)
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
        "hourly": "temperature_2m,apparent_temperature,precipitation_probability,weathercode,windspeed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
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
# Current Conditions
# -----------------------------
tz = pytz.timezone(tz_name)
now = datetime.now(tz)
now_hour = now.strftime("%Y-%m-%dT%H:00")
times = raw["hourly"]["time"]
index = times.index(now_hour) if now_hour in times else 0

current_temp = round(raw["hourly"]["temperature_2m"][index])
feels_like = round(raw["hourly"]["apparent_temperature"][index])
wind = round(raw["hourly"]["windspeed_10m"][index])
current_code = raw["hourly"]["weathercode"][index]
current_icon = get_icon(current_code)

# -----------------------------
# Header
# -----------------------------
st.title(city)
st.markdown(f"## {current_icon}  {current_temp}°F")
st.caption(f"Feels like {feels_like}°F | Wind {wind} mph")

# -----------------------------
# Hourly Forecast
# -----------------------------
st.markdown("---")
st.subheader("Next 12 Hours")

for i in range(12):
    time_obj = datetime.fromisoformat(raw["hourly"]["time"][i])
    label = "Now" if i == 0 else time_obj.strftime("%I %p")
    temp = round(raw["hourly"]["temperature_2m"][i])
    icon = get_icon(raw["hourly"]["weathercode"][i])
    st.write(f"{label}  |  {icon}  |  {temp}°F")

# -----------------------------
# 7 Day Forecast
# -----------------------------
st.markdown("---")
st.subheader("7 Day Forecast")

for i, date_str in enumerate(raw["daily"]["time"]):
    day = "Today" if i == 0 else datetime.fromisoformat(date_str).strftime("%a")
    high = round(raw["daily"]["temperature_2m_max"][i])
    low = round(raw["daily"]["temperature_2m_min"][i])
    icon = get_icon(raw["daily"]["weathercode"][i])
    st.write(f"{icon}  {day}  {low}°F / {high}°F")

# -----------------------------
# Basic Validation Tests
# -----------------------------
if __name__ == "__main__":
    assert get_icon(0) == "☀️"
    assert get_icon(71) == "❄️"
    assert get_icon(999) == "❔"
