import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Dorset Weather", page_icon="☁️", layout="wide")

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

# 1. HARDCODED CORRECT ENDPOINT
# This ensures /v1/forecast is always included
FULL_URL = "https://api.open-meteo.com"

try:
    response = requests.get(FULL_URL)
    response.raise_for_status()
    data = response.json()

    # --- CURRENT CONDITIONS ---
    # Find the hour that matches right now
    current_time_str = datetime.now().strftime('%Y-%m-%dT%H:00')
    hourly_times = data["hourly"]["time"]
    
    try:
        idx = hourly_times.index(current_time_str)
    except ValueError:
        idx = 0 
        
    current_temp = data["hourly"]["temperature_2m"][idx]
    current_condition = WMO_CODES.get(data["hourly"]["weather_code"][idx], "Unknown")

    st.markdown(f"# **{current_temp}°F**")
    st.markdown(f"### Dorset, VT: {current_condition}")
    st.write(f"Last Updated: {datetime.now().strftime('%I:%M %p')}")
    st.divider()

    # --- NEXT 36 HOURS ---
    st.subheader("Next 36 Hours")
    hourly_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°F)": data["hourly"]["temperature_2m"],
        "Condition": [WMO_CODES.get(code, "Unknown") for code in data["hourly"]["weather_code"]]
    }).head(36)

    # Line chart of temp
    st.line_chart(hourly_df.set_index("Time")["Temp (°F)"])
    
    with st.expander("View Hourly Details"):
        # Format the time for the table
        hourly_df["Time"] = hourly_df["Time"].dt.strftime('%m/%d %I:%M %p')
        st.table(hourly_df)

    st.divider()

    # --- 10-DAY FORECAST ---
    st.subheader("10-Day Forecast")
    daily_df = pd.DataFrame({
        "Date": data["daily"]["time"],
        "Condition": [WMO_CODES.get(code, "Unknown") for code in data["daily"]["weather_code"]],
        "High (°F)": data["daily"]["temperature_2m_max"],
        "Low (°F)": data["daily"]["temperature_2m_min"]
    })
    st.table(daily_df)

except Exception as e:
    st.error(f"App Error: {e}")







