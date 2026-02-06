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

# --- THE BRUTE FORCE FIX ---
# We are building the string manually to ensure NO part is lost.
base = "https://api.open-meteo.com"
lat = "43.2548"
lon = "-73.0973"
hourly_vars = "temperature_2m,weather_code"
daily_vars = "weather_code,temperature_2m_max,temperature_2m_min"

final_url = f"{base}?latitude={lat}&longitude={lon}&hourly={hourly_vars}&daily={daily_vars}&temperature_unit=fahrenheit&timezone=America/New_York&forecast_days=10"

try:
    # We call the URL and force it to be a clean string
    response = requests.get(final_url.strip())
    response.raise_for_status()
    data = response.json()

    # --- TOP SECTION: Current Temperature ---
    # Since it is currently Friday morning in Dorset, you're likely seeing snow!
    now_hour = datetime.now().strftime('%Y-%m-%dT%H:00')
    hourly_times = data["hourly"]["time"]
    
    try:
        idx = hourly_times.index(now_hour)
    except:
        idx = 0 
        
    current_temp = data["hourly"]["temperature_2m"][idx]
    current_condition = WMO_CODES.get(data["hourly"]["weather_code"][idx], "Unknown")

    st.markdown(f"# **{current_temp}°F**")
    st.markdown(f"### Dorset, VT: {current_condition}")
    st.write(f"Updated at {datetime.now().strftime('%I:%M %p')}")
    st.divider()

    # --- NEXT 36 HOURS ---
    st.subheader("Next 36 Hours")
    h_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°F)": data["hourly"]["temperature_2m"],
        "Condition": [WMO_CODES.get(c, "Unknown") for c in data["hourly"]["weather_code"]]
    }).head(36)

    st.line_chart(h_df.set_index("Time")["Temp (°F)"])
    
    with st.expander("View Detailed Hourly Table"):
        # Formatting for the table view
        table_df = h_df.copy()
        table_df["Time"] = table_df["Time"].dt.strftime('%I:%M %p')
        st.table(table_df)

    # --- 10-DAY FORECAST ---
    st.divider()
    st.subheader("10-Day Summary")
    d_df = pd.DataFrame({
        "Date": data["daily"]["time"],
        "Condition": [WMO_CODES.get(c, "Unknown") for c in data["daily"]["weather_code"]],
        "High": data["daily"]["temperature_2m_max"],
        "Low": data["daily"]["temperature_2m_min"]
    })
    st.table(d_df)

except Exception as e:
    st.error(f"Error: {e}")
    # This helps us see EXACTLY what URL the app tried to use
    st.write("Debug - The app tried to call this URL:")
    st.code(final_url)












