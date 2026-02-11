# -*- coding: utf-8 -*-
# Apple Style Weather App - Streamlit Cloud Version

import streamlit as st
import requests
from datetime import datetime
import pytz

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(page_title="Apple Style Weather", layout="centered")

# -------------------------------------------------
# Weather Icons
# -------------------------------------------------
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

# -------------------------------------------------
# Cities (Dorset Default)
# -------------------------------------------------
CITIES = {
    "Dorset": (43.2548, -73.0973, "America/New_York"),
    "New York": (40.7128, -74.0060, "America/New_York"),
    "Arlington": (38.8500, -77.0400, "America/New_York"),
}

city = st.selectbox("Select City", list(CITIES.keys()), index=0)
lat, lon, tz_name = CITIES[city]

# -------------------------------------------------
# Fetch Weather
# -------------------------------------------------
@st.cache_data(ttl=600)
def fetch_weather(lat, lon, tz):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,apparent_temperature,weathercode",
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
        "temperature_unit": "fahrenheit",
        "timezone": tz,
        "forecast_days": 10,
    }
    r = requests.get(url, params=params, timeout=6)
    r.raise_for_status()
    return r.json()

raw = fetch_weather(lat, lon, tz_name)

# -------------------------------------------------
# Current Conditions
# -------------------------------------------------
tz = pytz.timezone(tz_name)
now = datetime.now(tz)
now_hour = now.strftime("%Y-%m-%dT%H:00")
hourly_times = raw["hourly"]["time"]

index = hourly_times.index(now_hour) if now_hour in hourly_times else 0

current_temp = round(raw["hourly"]["temperature_2m"][index])
feels_like = round(raw["hourly"]["apparent_temperature"][index])
current_icon = get_icon(raw["hourly"]["weathercode"][index])

# -------------------------------------------------
# Background Styling
# -------------------------------------------------
is_day = 6 <= now.hour < 18
background = (
    "radial-gradient(circle at 50% 0%, #8EC5FC 0%, #4facfe 40%, #1e3c72 100%)"
    if is_day
    else "radial-gradient(circle at 50% 0%, #2C3E50 0%, #141E30 60%, #0f2027 100%)"
)

st.markdown(f"""
<style>
.stApp {{
    background: {background};
    color: white;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}}
.city {{
    font-size: 32px;
    text-align: center;
    margin-top: 20px;
    font-weight: 500;
}}
.big-icon {{
    font-size: 60px;
    text-align: center;
}}
.big-temp {{
    font-size: 100px;
    font-weight: 200;
    text-align: center;
}}
.glass {{
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(20px);
    border-radius: 30px;
    padding: 20px;
    margin-top: 25px;
    border: 1px solid rgba(255,255,255,0.2);
}}
.hour-scroll {{
    display: flex;
    overflow-x: auto;
    gap: 20px;
    padding-bottom: 10px;
}}
.hour-item {{
    min-width: 70px;
    text-align: center;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown(f"<div class='city'>{city}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='big-icon'>{current_icon}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='big-temp'>{current_temp}°F</div>", unsafe_allow_html=True)
st.markdown(
    f"<div style='text-align:center; opacity:0.8;'>Feels like {feels_like}°F</div>",
    unsafe_allow_html=True
)

# -------------------------------------------------
# 24 Hour Horizontal Scroll
# -------------------------------------------------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.subheader("Next 24 Hours")

hour_html = "<div class='hour-scroll'>"
...
st.write(hour_html)

for i in range(24):
    time_obj = datetime.fromisoformat(hourly_times[i])
    label = "Now" if i == 0 else time_obj.strftime("%I %p")
    temp = round(raw["hourly"]["temperature_2m"][i])
    feels = round(raw["hourly"]["apparent_temperature"][i])
    icon = get_icon(raw["hourly"]["weathercode"][i])

    hour_html += f"""
    <div class='hour-item'>
        <div style='font-size:12px; opacity:0.7;'>{label}</div>
        <div style='font-size:24px'>{icon}</div>
        <div>{temp}°F</div>
        <div style='font-size:11px; opacity:0.6;'>FL {feels}°F</div>
    </div>
    """

hour_html += "</div>"

# ✅ THIS IS THE IMPORTANT LINE
st.markdown(hour_html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 10 Day Forecast with Range Bars
# -------------------------------------------------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.subheader("10 Day Forecast")

highs = raw["daily"]["temperature_2m_max"]
lows = raw["daily"]["temperature_2m_min"]

min_temp = min(lows)
max_temp = max(highs)
range_temp = max_temp - min_temp

for i, date_str in enumerate(raw["daily"]["time"]):
    day = "Today" if i == 0 else datetime.fromisoformat(date_str).strftime("%a")
    high = round(highs[i])
    low = round(lows[i])
    icon = get_icon(raw["daily"]["weathercode"][i])

    low_pct = ((low - min_temp) / range_temp) * 100 if range_temp else 0
    width_pct = ((high - low) / range_temp) * 100 if range_temp else 0

    st.markdown(f"""
    <div style='display:flex; align-items:center; justify-content:space-between; margin:8px 0;'>
        <div style='width:70px'>{day}</div>
        <div>{icon}</div>
        <div style='width:35px; text-align:right; opacity:0.6'>{low}°</div>
        <div style='flex:1; margin:0 10px; background:rgba(255,255,255,0.25); height:4px; border-radius:4px; position:relative;'>
            <div style='position:absolute; left:{low_pct}%; width:{width_pct}%; height:4px; background:white; border-radius:4px;'></div>
        </div>
        <div style='width:35px; text-align:right; font-weight:500'>{high}°</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
