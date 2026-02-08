import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIG ---
LOCATIONS = {
    "Dorset, VT": {"lat": 43.2548, "lon": -73.0973, "tz": "America/New_York"},
    "Arlington, VA (22202)": {"lat": 38.8500, "lon": -77.0400, "tz": "America/New_York"}
}

WMO_CODES = {0: "☀️ Sunny", 1: "🌤 Clear", 2: "⛅ Partly Cloudy", 3: "☁️ Overcast", 45: "🌫 Fog", 51: "🌦 Drizzle", 61: "🌧 Rain", 71: "❄️ Snow", 80: "🌦 Showers", 95: "🌩 Thunderstorm"}

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤", layout="wide")

# --- UI ---
selected_loc_name = st.sidebar.selectbox("Select Location", list(LOCATIONS.keys()))
loc = LOCATIONS[selected_loc_name]

# --- API DATA ---
base_url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": loc["lat"],
    "longitude": loc["lon"],
    "hourly": ["temperature_2m", "weathercode", "precipitation_probability", "windspeed_10m"],
    "daily": ["weathercode", "temperature_2m_max", "temperature_2m_min", "windspeed_10m_max"],
    "temperature_unit": "fahrenheit",
    "windspeed_unit": "mph",
    "timezone": loc["tz"],
    "forecast_days": 10
}

try:
    # Use params=params to let 'requests' handle URL encoding (commas vs %2C)
    response = requests.get(base_url, params=params)
    data = response.json()

    # Check for API-side errors before accessing keys
    if "error" in data:
        st.error(f"API Error: {data.get('reason', 'Unknown error')}")
        st.stop()

    # --- CURRENT CONDITIONS ---
    # Lookup the current hour's data
    now_str = datetime.now().strftime('%Y-%m-%dT%H:00')
    times = data["hourly"]["time"]
    
    # Fallback to index 0 if exact hour match fails
    idx = times.index(now_str) if now_str in times else 0
    
    st.title(f"Weather for {selected_loc_name}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature", f"{data['hourly']['temperature_2m'][idx]}°F")
    c2.metric("Rain Chance", f"{data['hourly']['precipitation_probability'][idx]}%")
    c3.metric("Wind Speed", f"{data['hourly']['windspeed_10m'][idx]} mph")

    # --- 36-HOUR CHART ---
    st.subheader("Next 36 Hours")
    h_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°F)": data["hourly"]["temperature_2m"],
        "Rain %": data["hourly"]["precipitation_probability"]
    }).head(36).set_index("Time")
    
    st.line_chart(h_df)

    # --- 10-DAY FORECAST ---
    st.subheader("10-Day Forecast")
    d_df = pd.DataFrame({
        "Date": data["daily"]["time"],
        "Condition": [WMO_CODES.get(c, "☁️") for c in data["daily"]["weathercode"]],
        "High": data["daily"]["temperature_2m_max"],
        "Low": data["daily"]["temperature_2m_min"],
        "Max Wind": data["daily"]["windspeed_10m_max"]
    })
    st.dataframe(d_df, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load data: {e}")
    if 'data' in locals():
        st.write("Full API Response for debugging:")
        st.json(data)




















