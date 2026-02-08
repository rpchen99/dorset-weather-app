import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIG ---
LOCATIONS = {
    "Dorset, VT": {"lat": "43.2548", "lon": "-73.0973", "tz": "America/New_York"},
    "Arlington, VA (22202)": {"lat": "38.8500", "lon": "-77.0400", "tz": "America/New_York"}
}

WMO_CODES = {0: "☀️ Sunny", 1: "🌤 Clear", 2: "⛅ Partly Cloudy", 3: "☁️ Overcast", 45: "🌫 Fog", 51: "🌦 Drizzle", 61: "🌧 Rain", 71: "❄️ Snow", 80: "🌦 Showers", 95: "🌩 Thunderstorm"}

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤", layout="wide")

# --- UI ---
selected_loc_name = st.sidebar.selectbox("Select Location", list(LOCATIONS.keys()))
loc = LOCATIONS[selected_loc_name]

# --- API DATA ---
base_url = "https://api.open-meteo.com" # Path corrected
params = {
    "latitude": loc["lat"], "longitude": loc["lon"],
    "hourly": "temperature_2m,weathercode,precipitation_probability,windspeed_10m",
    "daily": "weathercode,temperature_2m_max,temperature_2m_min,windspeed_10m_max",
    "temperature_unit": "fahrenheit", "windspeed_unit": "mph",
    "timezone": loc["tz"], "forecast_days": 10
}

try:
    data = requests.get(base_url, params=params).json()

    # Current Stats
    idx = data["hourly"]["time"].index(datetime.now().strftime('%Y-%m-%dT%H:00'))
    
    st.title(f"Weather for {selected_loc_name}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Temp", f"{data['hourly']['temperature_2m'][idx]}°F")
    c2.metric("Rain Chance", f"{data['hourly']['precipitation_probability'][idx]}%")
    c3.metric("Wind", f"{data['hourly']['windspeed_10m'][idx]} mph")

    # Chart
    h_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp": data["hourly"]["temperature_2m"],
        "Rain %": data["hourly"]["precipitation_probability"]
    }).head(36).set_index("Time")
    
    st.subheader("Next 36 Hours")
    st.line_chart(h_df)

    # Table
    st.subheader("10-Day Forecast")
    st.table(pd.DataFrame({
        "Date": data["daily"]["time"],
        "Condition": [WMO_CODES.get(c, "☁️") for c in data["daily"]["weathercode"]],
        "High": data["daily"]["temperature_2m_max"],
        "Low": data["daily"]["temperature_2m_min"],
        "Max Wind": data["daily"]["windspeed_10m_max"]
    }))

except Exception as e:
    st.error(f"Error fetching data: {e}")



















