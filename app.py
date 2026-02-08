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

# --- UI: SIDEBAR ---
st.sidebar.header("Settings")
selected_loc_name = st.sidebar.selectbox("Select Location", list(LOCATIONS.keys()))
loc = LOCATIONS[selected_loc_name]

# --- API SETUP ---
# Added: apparent_temp, precip_prob, visibility, uv_index, and wind_gusts
base = "https://api.open-meteo.com"
params = {
    "latitude": loc["lat"],
    "longitude": loc["lon"],
    "hourly": "temperature_2m,apparent_temperature,weathercode,precipitation_probability,visibility",
    "daily": "weathercode,temperature_2m_max,temperature_2m_min,uv_index_max,windgusts_10m_max",
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
    current_feels = data["hourly"]["apparent_temperature"][idx]
    current_condition = WMO_CODES.get(data["hourly"]["weathercode"][idx], "Unknown")
    current_precip = data["hourly"]["precipitation_probability"][idx]
    # Convert visibility from meters to miles
    current_viz = data["hourly"]["visibility"][idx] / 1609.34

    st.title(f"Weather for {selected_loc_name}")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Temperature", f"{current_temp}°F", f"Feels {current_feels}°F")
    col2.metric("Condition", current_condition)
    col3.metric("Rain Chance", f"{current_precip}%")
    col4.metric("Visibility", f"{current_viz:.1f} mi")
    
    st.write(f"Last updated: {datetime.now().strftime('%I:%M %p')}")
    st.markdown("---")

    # --- VISUALS ---
    st.subheader("Next 36 Hours")
    h_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°F)": data["hourly"]["temperature_2m"],
        "Feels Like (°F)": data["hourly"]["apparent_temperature"],
        "Rain %": data["hourly"]["precipitation_probability"],
        "Condition": [WMO_CODES.get(c, "Unknown") for c in data["hourly"]["weathercode"]]
    }).head(36)

    # Line chart showing Temp and Feels Like
    st.line_chart(h_df.set_index("Time")[["Temp (°F)", "Feels Like (°F)"]])

    with st.expander("View Detailed Hourly Table"):
        table_df = h_df.copy()
        table_df["Time"] = table_df["Time"].dt.strftime('%a %I:%M %p')
        st.dataframe(table_df, use_container_width=True)

    # --- 10-DAY SUMMARY ---
    st.markdown("---")
    st.subheader("10-Day Forecast")
    
    d_df = pd.DataFrame({
        "Date": data["daily"]["time"],
        "Condition": [WMO_CODES.get(c, "Unknown") for c in data["daily"]["weathercode"]],
        "High (°F)": data["daily"]["temperature_2m_max"],
        "Low (°F)": data["daily"]["temperature_2m_min"],
        "Max UV": data["daily"]["uv_index_max"],
        "Wind Gusts (mph)": data["daily"]["windgusts_10m_max"]
    })

    # Display as a clean interactive dataframe
    st.dataframe(d_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error fetching weather data: {e}")
    st.info("Check your internet connection or the API endpoint.")

























