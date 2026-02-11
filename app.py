# -*- coding: utf-8 -*-
# Apple Style Weather App - Streamlit Cloud Version
# Pure Python implementation (NO React / NO TypeScript)
# All characters are ASCII-safe to avoid encoding errors

import streamlit as st
import requests
from datetime import datetime
import pytz

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Apple Style Weather", layout="centered")

# -----------------------------
# Weather Code -> Text Icon Mapping (ASCII Safe)
# -----------------------------
WMO_ICONS = {
    0: "SUN",
    1: "PARTLY",
    2: "PARTLY",
    3: "CLOUD",
    45: "FOG",
    48: "FOG",
    51: "DRIZZLE",
    53: "DRIZZLE",
    55: "RAIN",
    61: "RAIN",
    63: "RAIN",
    65: "RAIN",
    71: "SNOW",
    73: "SNOW",
    75: "SNOW",
    77: "SNOW",
    80: "RAIN",
    81: "RAIN",
    82: "STORM",
    85: "SNOW",
    86: "SNOW",
    95: "STORM",
}

def get_icon(code):
    return WMO_ICONS.get(code, "UNKNOWN")

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
st.subheader(current_icon)
st.markdown("## " + str(current_temp) + " F")
st.caption("Feels like " + str(feels_like) + " F | Wind " + str(wind) + " mph")

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
    st.write(label + "  |  " + icon + "  |  " + str(temp) + " F")

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
    st.write(icon + "  " + day + "  " + str(low) + " F / " + str(high) + " F")

# -----------------------------
# Basic Validation Tests
# -----------------------------
if __name__ == "__main__":
    assert get_icon(0) == "SUN"
    assert get_icon(71) == "SNOW"
    assert get_icon(999) == "UNKNOWN"



















































