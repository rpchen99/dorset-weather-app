import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIG ---
LOCATIONS = {
    "Dorset, VT": {"lat": "43.2548", "lon": "-73.0973", "tz": "America/New_York"},
    "Arlington, VA (22202)": {"lat": "38.8500", "lon": "-77.0400", "tz": "America/New_York"}
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

# --- UI: LOCATION SELECTOR ---
selected_loc_name = st.sidebar.selectbox("Select Location", list(LOCATIONS.keys()))
loc = LOCATIONS[selected_loc_name]

# --- API SETUP ---
base = "https://api.open-meteo.com" # FIXED ENDPOINT
params = {
    "latitude": loc["lat"],
    "longitude": loc["lon"],
    "hourly": "temperature_2m,weathercode,precipitation_probability,windspeed_10m",
    "daily": "weathercode,temperature_2m_max,temperature_2m_min,windspeed_10m_max",
    "temperature_unit": "fahrenheit",
    "windspeed_unit": "mph",
    "timezone": loc["tz"],
    "forecast_days": 10
}

try:
    response = requests.get(base, params=params)
    response.raise_for_status()
    data = response.json()

    # --- CURRENT CONDITIONS ---
    now_hour = datetime.now().strftime('%Y-%m-%dT%H:00')
    hourly_times = data["hourly"]["time"]
    idx = hourly_times.index(now_hour) if now_hour in hourly_times else 0

    current_temp = data["hourly"]["temperature_2m"][idx]
    current_condition = WMO_CODES.get(data["hourly"]["weathercode"][idx], "Unknown")
    current_precip = data["hourly"]["precipitation_probability"][idx]
    current_wind = data["hourly"]["windspeed_10m"][idx]

    st.markdown(f"## {selected_loc_name}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", f"{current_temp}°F")
    col2.metric("Precip Chance", f"{current_precip}%")
    col3.metric("Wind Speed", f"{current_wind} mph")
    
    st.write(f"Condition: **{current_condition}** | Updated at {datetime.now().strftime('%I:%M %p')}")
    st.divider()

    # --- VISUALS ---
    st.subheader("Next 36 Hours: Temperature & Rain %")
    h_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°F)": data["hourly"]["temperature_2m"],
        "Rain %": data["hourly"]["precipitation_probability"]
    }).head(36)

    st.line_chart(h_df.set_index("Time")[["Temp (°F)", "Rain %"]])

    # --- 10-DAY SUMMARY ---
    st.subheader("10-Day Forecast")
    d_df = pd.DataFrame({
        "Date": data["daily"]["time"],
        "Condition": [WMO_CODES.get(c, "Unknown") for c in data["daily"]["weathercode"]],
        "High (°F)": data["daily"]["temperature_2m_max"],
        "Low (°F)": data["daily"]["temperature_2m_min"],
        "Max Wind (mph)": data["daily"]["windspeed_10m_max"]
    })
    st.dataframe(d_df, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")

















