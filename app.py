import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Dorset Weather", page_icon="☁️", layout="wide")

# Dictionary to translate WMO Weather Codes
WMO_CODES = {
    0: "☀️ Sunny", 1: "🌤 Mainly Clear", 2: "⛅ Partly Cloudy", 3: "☁️ Overcast",
    45: "🌫 Foggy", 48: "🌫 Rime Fog", 51: "🌦 Light Drizzle", 53: "🌦 Moderate Drizzle",
    55: "🌦 Dense Drizzle", 61: "🌧 Slight Rain", 63: "🌧 Moderate Rain", 65: "🌧 Heavy Rain",
    71: "❄️ Slight Snow", 73: "❄️ Moderate Snow", 75: "❄️ Heavy Snow",
    77: "❄️ Snow Grains", 80: "🌦 Slight Rain Showers", 81: "🌧 Moderate Rain Showers",
    82: "⛈ Violent Rain Showers", 85: "❄️ Slight Snow Showers", 86: "❄️ Heavy Snow Showers",
    95: "🌩 Thunderstorm"
}

BASE_URL = "https://api.open-meteo.com"
params = {
    "latitude": 43.2548,
    "longitude": -73.0973,
    "hourly": "temperature_2m,weather_code",
    "daily": "weather_code,temperature_2m_max,temperature_2m_min",
    "temperature_unit": "fahrenheit",
    "wind_speed_unit": "mph",
    "precipitation_unit": "inch",
    "timezone": "auto",
    "forecast_days": 10
}

try:
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    # --- CURRENT CONDITIONS (New Feature) ---
    current_time_str = datetime.now().strftime('%Y-%m-%dT%H:00')
    hourly_times = pd.to_datetime(data["hourly"]["time"])
    
    # Find the index that matches the current hour
    current_index = hourly_times.get_indexer([current_time_str], method='nearest')[0]
    
    current_temp = data["hourly"]["temperature_2m"][current_index]
    current_code = data["hourly"]["weather_code"][current_index]
    current_condition = WMO_CODES.get(current_code, "Unknown")

    st.markdown(f"# **{current_temp}°F**")
    st.markdown(f"**Dorset, VT:** {current_condition} | *As of {datetime.now().strftime('%I:%M %p')}*")
    st.divider()


    # --- Next 36 Hours Forecast ---
    st.subheader("Next 36 Hours")
    
    hourly_data = {
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°F)": data["hourly"]["temperature_2m"],
        "Condition": [WMO_CODES.get(code, "Unknown") for code in data["hourly"]["weather_code"]]
    }
    hourly_df = pd.DataFrame(hourly_data).head(36)

    st.line_chart(hourly_df.set_index("Time")["Temp (°F)"])
    
    with st.expander("View Hourly Details"):
        st.dataframe(hourly_df, use_container_width=True)
    st.divider()

    # --- 10-Day Summary Table ---
    st.subheader("10-Day Forecast")
    
    daily_df = pd.DataFrame({
        "Date": data["daily"]["time"],
        "Condition": [WMO_CODES.get(code, "Unknown") for code in data["daily"]["weather_code"]],
        "High Temp (°F)": data["daily"]["temperature_2m_max"],
        "Low Temp (°F)": data["daily"]["temperature_2m_min"]
    })
    
    st.table(daily_df)

except Exception as e:
    st.error(f"App Error: {e}")






