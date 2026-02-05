import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Dorset Weather", layout="wide")
st.title("Dorset, VT 10-Day Forecast")

# --- NWS Alerts Section ---
# --- Fixed NWS Alerts Section ---
# Bennington County, VT (NWS County Code: VTC003)
ALERTS_URL = "https://api.weather.gov"

# 1. Use a unique User-Agent string (NWS requirement)
headers = {
    'User-Agent': '(myweatherapp.com, contact@email.com)', 
    'Accept': 'application/geo+json'
}

try:
    alerts_response = requests.get(ALERTS_URL, headers=headers)
    
    # 2. Check if the request was actually successful (Status 200)
    if alerts_response.status_code == 200:
        alerts_data = alerts_response.json()
        active_alerts = alerts_data.get('features', [])

        if active_alerts:
            with st.container(border=True): 
                with st.expander(f"⚠️ **ACTIVE NWS ALERTS ({len(active_alerts)})** ⚠️"):
                    for alert in active_alerts:
                        props = alert.get('properties', {})
                        st.markdown(f"### {props.get('event', 'Weather Alert')}")
                        st.warning(f"**{props.get('headline')}**")
                        st.write(props.get('description'))
                        st.divider()
        else:
            st.success("✅ No active NWS weather alerts for Dorset, VT.")
    else:
        # If not 200, the API might be down or blocking the request
        st.info(f"NWS Alert service currently unavailable (Status: {alerts_response.status_code})")

except Exception as e:
    # This prevents the whole app from crashing if the alert service fails
    st.info("Note: Could not load weather alerts at this time.")


# --- Main Weather Forecast Section (The original code) ---
BASE_URL = "https://api.open-meteo.com"
params = {
    "latitude": 43.2548,
    "longitude": -73.0973,
    "hourly": ["temperature_2m", "precipitation_probability", "snowfall"],
    "daily": ["temperature_2m_max", "temperature_2m_min"],
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

    # Hourly Data Visualization
    hourly_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°F)": data["hourly"]["temperature_2m"]
    })
    st.subheader("Hourly Temperature Outlook")
    st.line_chart(hourly_df.set_index("Time"))

    # Daily Data Table
    daily_df = pd.DataFrame({
        "Date": data["daily"]["time"],
        "Max Temp (°F)": data["daily"]["temperature_2m_max"],
        "Min Temp (°F)": data["daily"]["temperature_2m_min"]
    })
    st.subheader("10-Day Highs/Lows")
    st.table(daily_df)

except Exception as e:
    st.error(f"Failed to fetch weather data: {e}")




