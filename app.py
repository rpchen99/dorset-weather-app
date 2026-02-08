import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- CONFIG ---
LOCATIONS = {
    "Dorset, VT": {"lat": 43.2548, "lon": -73.0973, "tz": "America/New_York"},
    "Arlington, VA (22202)": {"lat": 38.8500, "lon": -77.0400, "tz": "America/New_York"},
    "Maywood, NJ (07607)": {"lat": 40.9029, "lon": -74.0635, "tz": "America/New_York"}
}

WMO_CODES = {
    0: "☀️ Sunny", 1: "🌤 Mainly Clear", 2: "⛅ Partly Cloudy", 3: "☁️ Overcast",
    45: "🌫 Foggy", 48: "🌫 Rime Fog", 51: "🌦 Light Drizzle", 53: "🌦 Moderate Drizzle",
    55: "🌦 Dense Drizzle", 61: "🌧 Slight Rain", 63: "🌧 Moderate Rain", 65: "🌧 Heavy Rain",
    71: "❄️ Slight Snow", 73: "❄️ Moderate Snow", 75: "❄️ Heavy Snow",
    77: "❄️ Snow Grains", 80: "🌦 Slight Rain Showers", 81: "🌧 Moderate Rain Showers",
    82: "⛈ Violent Rain Showers", 85: "❄️ Slight Snow Showers",
    86: "❄️ Heavy Snow Showers", 95: "🌩 Thunderstorm"
}

st.set_page_config(page_title="Weather Dashboard", page_icon="❄️", layout="wide")

# --- UI ---
selected_loc_name = st.sidebar.selectbox("Select Location", list(LOCATIONS.keys()))
loc = LOCATIONS[selected_loc_name]

# --- API SETUP ---
base = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": loc["lat"],
    "longitude": loc["lon"],
    "hourly": (
        "temperature_2m,"
        "apparent_temperature,"
        "precipitation_probability,"
        "weathercode,"
        "windgusts_10m"
    ),
    "daily": "weathercode,temperature_2m_max,temperature_2m_min",
    "temperature_unit": "fahrenheit",
    "windspeed_unit": "mph",
    "timezone": loc["tz"],
    "forecast_days": 10
}

try:
    response = requests.get(base, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # --- CURRENT CONDITIONS ---
    tz = pytz.timezone(loc["tz"])
    now_hour = datetime.now(tz).strftime("%Y-%m-%dT%H:00")

    hourly_times = data["hourly"]["time"]
    idx = hourly_times.index(now_hour) if now_hour in hourly_times else 0

    current_temp = data["hourly"]["temperature_2m"][idx]
    feels_like = data["hourly"]["apparent_temperature"][idx]
    precip = data["hourly"]["precipitation_probability"][idx]
    gusts = data["hourly"]["windgusts_10m"][idx]
    condition = WMO_CODES.get(data["hourly"]["weathercode"][idx], "Unknown")

    st.markdown(f"# **{current_temp}°F**")
    st.markdown(f"### Feels like {feels_like}°F · {selected_loc_name}")
    st.write(
        f"**{condition}** · 🌧 {precip}% · 💨 Gusts {gusts} mph"
    )
    st.write(f"Updated at {datetime.now(tz).strftime('%I:%M %p')}")
    st.divider()

    # --- NEXT 36 HOURS ---
    st.subheader("Next 36 Hours")
    h_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°F)": data["hourly"]["temperature_2m"],
        "Feels Like (°F)": data["hourly"]["apparent_temperature"],
        "Rain %": data["hourly"]["precipitation_probability"],
        "Wind Gusts (mph)": data["hourly"]["windgusts_10m"],
        "Condition": [
            WMO_CODES.get(c, "Unknown")
            for c in data["hourly"]["weathercode"]
        ]
    }).head(36)

    st.line_chart(




























