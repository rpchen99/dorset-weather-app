import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Dorset Weather", layout="wide")
st.title("Dorset, VT 10-Day Forecast")

# --- NWS Alerts Section ---
# Bennington County, VT (NWS County Code: VTC003)
ALERTS_URL = "https://api.weather.gov"

try:
    alerts_response = requests.get(ALERTS_URL, headers={'User-Agent': 'Dorset-Weather-App/1.0 (contact@example.com)'})
    alerts_response.raise_for_status()
    alerts_data = alerts_response.json()
    
    active_alerts = alerts_data.get('features', [])

    if active_alerts:
        # Use a red box (container) for visibility
        with st.container(border=True): 
            # Use st.expander for a clickable, collapsable box
            with st.expander(f"⚠️ **ACTIVE NWS ALERTS ({len(active_alerts)})** ⚠️"):
                for alert in active_alerts:
                    props = alert.get('properties', {})
                    headline = props.get('headline', 'No Headline')
                    description = props.get('description', 'No description provided.')
                    severity = props.get('severity', 'minor').capitalize()
                    event = props.get('event', 'Weather Alert')
                    
                    st.markdown(f"### {event} ({severity})")
                    st.warning(f"**{headline}**")
                    st.markdown(description)
                    st.divider()
    else:
        # Green box if no alerts
        with st.container(border=True):
            st.success("✅ No active NWS weather alerts for Bennington County, VT.")

except requests.exceptions.RequestException as e:
    st.error(f"Error fetching NWS alerts: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred with alerts: {e}")

st.divider() # Separates the alerts from the main weather data

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




