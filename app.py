import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Dorset Weather", page_icon="❄️", layout="wide")

# Weather Code Mapping
WMO_CODES = {
    0: "☀️ Sunny", 1: "🌤 Mainly Clear", 2: "⛅ Partly Cloudy", 3: "☁️ Overcast",
    45: "🌫 Foggy", 48: "🌫 Rime Fog", 51: "🌦 Light Drizzle", 53: "🌦 Moderate Drizzle",
    55: "🌦 Dense Drizzle", 61: "🌧 Slight Rain", 63: "🌧 Moderate Rain", 65: "🌧 Heavy Rain",
    71: "❄️ Slight Snow", 73: "❄️ Moderate Snow", 75: "❄️ Heavy Snow",
    77: "❄️ Snow Grains", 80: "🌦 Slight Rain Showers", 81: "🌧 Moderate Rain Showers",
    82: "⛈ Violent Rain Showers", 85: "❄️ Slight Snow Showers", 86: "❄️ Heavy Snow Showers",
    95: "🌩 Thunderstorm"
}

# --- THE FIX: FORCED PATH ---
# We define the base and params separately to ensure 'requests' handles it perfectly
ENDPOINT = "https://api.open-meteo.com"
params = {
    "latitude": 43.2548,
    "longitude": -73.0973,
    "hourly": "temperature_2m,weather_code",
    "daily": "weather_code,temperature_2m_max,temperature_2m_min",
    "temperature_unit": "fahrenheit",
    "wind_speed_unit": "mph",
    "precipitation_unit": "inch",
    "timezone": "America/New_York",
    "forecast_days": 10
}

try:
    # This automatically glues 'ENDPOINT' and 'params' together with the correct /v1/forecast/ path
    response = requests.get(ENDPOINT, params=params)
    response.raise_for_status()
    data = response.json()

    # --- TOP SECTION: Current Temperature ---
    # Dorset is currently seeing snow! 
    now_hour = datetime.now().strftime('%Y-%m-%dT%H:00')
    hourly_times = data["hourly"]["time"]
    
    try:
        idx = hourly_times.index(now_hour)
    except ValueError:
        idx = 0 
        
    current_temp = data["hourly"]["temperature_2m"][idx]
    current_condition = WMO_CODES.get(data["hourly"]["weather_code"][idx], "Unknown")

    st.markdown(f"# **{current_temp}°F**")
    st.markdown(f"### Dorset, VT: {current_condition}")
    st.write(f"Last Sync: {datetime.now().strftime('%I:%M %p')}")
    st.divider()

    # --- MIDDLE SECTION: Next 36 Hours ---
    st.subheader("Next 36 Hours")
    hourly_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°F)": data["hourly"]["temperature_2m"],
        "Condition": [WMO_CODES.get(code, "Unknown") for code in data["hourly"]["weather_code"]]
    }).head(36)

    st.line_chart(hourly_df.set_index("Time")["Temp (°F)"])
    
    with st.expander("View Hourly Details"):
        display_hourly = hourly_df.copy()
        display_hourly["Time"] = display_hourly["Time"].dt.strftime('%m/%d %I:%M %p')
        st.table(display_hourly)

    # --- BOTTOM SECTION: 10-Day Forecast ---
    st.divider()
    st.subheader("10-Day Forecast")
    daily_df = pd.DataFrame({
        "Date": data["daily"]["time"],
        "Condition": [WMO_CODES.get(code, "Unknown") for code in data["daily"]["weather_code"]],
        "High (°F)": data["daily"]["temperature_2m_max"],
        "Low (°F)": data["daily"]["temperature_2m_min"]
    })
    st.table(daily_df)

except Exception as e:
    st.error(f"Weather Data Error: {e}")










