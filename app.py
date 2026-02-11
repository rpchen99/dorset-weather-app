# Apple-Style Weather App (Streamlit Cloud Compatible)
# --------------------------------------------------
# FIX:
# Streamlit Cloud may restrict or intermittently block
# outbound requests, causing: TypeError: Failed to fetch
#
# This version:
# - Uses safe local mock data by default
# - Optionally attempts live API fetch with timeout
# - Falls back gracefully if network fails
# - Contains simple testable transformation logic

import streamlit as st
import requests
from datetime import datetime
from typing import Dict, Any

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Apple Weather", layout="centered")

# -----------------------------
# Pure Transformation Function
# -----------------------------
def transform_weather_data(data: Dict[str, Any]) -> Dict[str, Any]:
    if not data.get("hourly") or not data["hourly"].get("temperature_2m"):
        raise ValueError("Invalid hourly data")

    current = round(data["hourly"]["temperature_2m"][0])

    hourly = []
    for i, t in enumerate(data["hourly"]["time"][:12]):
        label = "Now" if i == 0 else datetime.fromisoformat(t).strftime("%-I %p")
        hourly.append({
            "time": label,
            "temp": round(data["hourly"]["temperature_2m"][i]),
        })

    daily = []
    for i, d in enumerate(data["daily"]["time"]):
        label = "Today" if i == 0 else datetime.fromisoformat(d).strftime("%a")
        daily.append({
            "day": label,
            "high": round(data["daily"]["temperature_2m_max"][i]),
            "low": round(data["daily"]["temperature_2m_min"][i]),
        })

    return {"current": current, "hourly": hourly, "daily": daily}


# -----------------------------
# Deterministic Mock Data
# -----------------------------
def get_mock_weather():
    return {
        "current": 72,
        "hourly": [
            {"time": "Now", "temp": 72},
            {"time": "1 PM", "temp": 73},
            {"time": "2 PM", "temp": 74},
            {"time": "3 PM", "temp": 75},
        ],
        "daily": [
            {"day": "Today", "high": 75, "low": 60},
            {"day": "Tue", "high": 74, "low": 61},
            {"day": "Wed", "high": 78, "low": 63},
            {"day": "Thu", "high": 80, "low": 65},
            {"day": "Fri", "high": 77, "low": 62},
            {"day": "Sat", "high": 73, "low": 59},
            {"day": "Sun", "high": 76, "low": 60},
        ],
    }


# -----------------------------
# Optional Live Fetch
# -----------------------------
def fetch_live_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=40.7128"
        "&longitude=-74.0060"
        "&hourly=temperature_2m"
        "&daily=temperature_2m_max,temperature_2m_min"
        "&temperature_unit=fahrenheit"
        "&timezone=America/New_York"
        "&forecast_days=7"
    )

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return transform_weather_data(response.json())
    except Exception:
        return None


# -----------------------------
# Load Weather Data
# -----------------------------
weather = fetch_live_weather()
if weather is None:
    weather = get_mock_weather()
    st.info("Live weather unavailable. Showing sample data.")


# -----------------------------
# Apple-Style UI
# -----------------------------
st.markdown(
    """
    <style>
    .big-temp { font-size: 80px; font-weight: 200; text-align:center; }
    .city { font-size: 28px; text-align:center; }
    .card { background: rgba(255,255,255,0.15); padding:20px; border-radius:20px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="city">New York</div>', unsafe_allow_html=True)
st.markdown(f'<div class="big-temp">{weather["current"]}°</div>', unsafe_allow_html=True)

st.markdown("### Hourly Forecast")
with st.container():
    cols = st.columns(len(weather["hourly"]))
    for col, hour in zip(cols, weather["hourly"]):
        col.metric(hour["time"], f"{hour['temp']}°")

st.markdown("### 7-Day Forecast")
for day in weather["daily"]:
    st.write(f"{day['day']}  |  Low: {day['low']}°  |  High: {day['high']}°")


# -----------------------------
# Basic Tests
# -----------------------------
if __name__ == "__main__":
    sample = {
        "hourly": {
            "time": ["2024-01-01T00:00:00"],
            "temperature_2m": [70.4],
        },
        "daily": {
            "time": ["2024-01-01"],
            "temperature_2m_max": [75.2],
            "temperature_2m_min": [60.1],
        },
    }

    result = transform_weather_data(sample)
    assert result["current"] == 70
    assert result["daily"][0]["high"] == 75
    assert result["daily"][0]["low"] == 60















































