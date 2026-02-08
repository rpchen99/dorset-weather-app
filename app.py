import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIG ---
LOCATIONS = {
    "Dorset, VT": {"lat": "43.2548", "lon": "-73.0973", "tz": "America/New_York"},
    "Arlington, VA (22202)": {"lat": "38.8500", "lon": "-77.0400", "tz": "America/New_York"},
    "Maywood, NJ (07607)": {"lat": "40.9029", "lon": "-74.0635", "tz": "America/New_York"}

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
base = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": loc["lat"],
    "longitude": loc["lon"],
    "hourly": "temperature_2m,weathercode",
    "daily": "weathercode,temperature_2m_max,temperature_2m_min",
    "temperature_unit": "fahrenheit",
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

    st.markdown(f"# **{current_temp}°F**")
    st.markdown(f"### {selected_loc_name}: {current_condition}")
    st.write(f"Updated at {datetime.now().strftime('%I:%M %p')}")
    st.divider()

    # --- VISUALS ---
    st.subheader("Next 36 Hours")
    h_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°F)": data["hourly"]["temperature_2m"],
        "Condition": [WMO_CODES.get(c, "Unknown") for c in data["hourly"]["weathercode"]]
    }).head(36)

    st.line_chart(h_df.set_index("Time")["Temp (°F)"])

    with st.expander("View Detailed Hourly Table"):
        table_df = h_df.copy()
        table_df["Time"] = table_df["Time"].dt.strftime('%I:%M %p')
        st.table(table_df)

    st.divider()
    st.subheader("10-Day Summary")
    d_df = pd.DataFrame({
        "Date": data["daily"]["time"],
        "Condition": [WMO_CODES.get(c, "Unknown") for c in data["daily"]["weathercode"]],
        "High (°F)": data["daily"]["temperature_2m_max"],
        "Low (°F)": data["daily"]["temperature_2m_min"]
    })
    st.table(d_df)

except Exception as e:
    st.error(f"Error: {e}")



























