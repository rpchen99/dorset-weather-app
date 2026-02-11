# -*- coding: utf-8 -*-
# Apple Style Weather App - Streamlit Cloud Version
# 24 Hour + 10 Day Forecast Edition

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
        "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max,windspeed_10m_max",
        "temperature_unit": "fahrenheit",
        "windspeed_unit": "mph",
        "timezone": tz,
        "forecast_days": 10,
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
current_code = raw["hourly"]["weathercode"][index]
current_icon = get_icon(current_code)

# -----------------------------
# Dynamic Gradient Background
# -----------------------------
is_day = 6 <= now.hour < 18
background = (
    "radial-gradient(circle at 50% 0%, #8EC5FC 0%, #4facfe 40%, #1e3c72 100%)"
    if is_day
    else "radial-gradient(circle at 50% 0%, #2C3E50 0%, #141E30 60%, #0f2027 100%)"
)

st.markdown(
    f"""
    <style>
    .stApp {{ background: {background}; color: white; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }}
    .city {{ font-size: 32px; text-align: center; margin-top: 20px; font-weight: 500; }}
    .big-icon {{ font-size: 60px; text-align: center; }}
    .big-temp {{ font-size: 100px; font-weight: 200; text-align: center; line-height: 1; margin-bottom: 10px; }}
    .glass {{
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 20px;
        margin-top: 25px;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Header Section
# -----------------------------
st.markdown(f"<div class='city'>{city}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='big-icon'>{current_icon}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='big-temp'>{current_temp}°F</div>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; opacity:0.85;'>Feels like {feels_like}°F</div>", unsafe_allow_html=True)

# -----------------------------
# 24 Hour Forecast
# -----------------------------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.subheader("Next 24 Hours")

for i in range(24):
    time_obj = datetime.fromisoformat(raw["hourly"]["time"][i])
    label = "Now" if i == 0 else time_obj.strftime("%I %p")
    temp = round(raw["hourly"]["temperature_2m"][i])
    icon = get_icon(raw["hourly"]["weathercode"][i])
    wind = round(raw["hourly"]["windspeed_10m"][i])
    precip = int(raw["hourly"]["precipitation_probability"][i])

    st.markdown(
        f"<div style='display:flex; justify-content:space-between;'>"
        f"<span>{label} {icon}</span>"
        f"<span>{temp}°F | 💨 {wind} mph | 🌧 {precip}%</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 10 Day Forecast
# -----------------------------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.subheader("10 Day Forecast")

for i, date_str in enumerate(raw["daily"]["time"]):
    day = "Today" if i == 0 else datetime.fromisoformat(date_str).strftime("%a")
    high = round(raw["daily"]["temperature_2m_max"][i])
    low = round(raw["daily"]["temperature_2m_min"][i])
    icon = get_icon(raw["daily"]["weathercode"][i])
    wind = round(raw["daily"]["windspeed_10m_max"][i])
    precip = int(raw["daily"]["precipitation_probability_max"][i])

    st.markdown(
        f"<div style='display:flex; justify-content:space-between;'>"
        f"<span>{icon} {day}</span>"
        f"<span>{low}°F / <b>{high}°F</b> | 💨 {wind} mph | 🌧 {precip}%</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Validation Tests
# -----------------------------
if __name__ == "__main__":
    assert get_icon(0) == "☀️"
    assert get_icon(71) == "❄️"
    assert get_icon(999) == "❔"
    assert len(raw["hourly"]["time"]) >= 24
    assert len(raw["daily"]["time"]) >= 7
