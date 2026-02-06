import streamlit as st
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime

st.set_page_config(page_title="Dorset Weather", page_icon="☁️", layout="wide")

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

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

# Dorset, VT Coordinates
params = {
	"latitude": 43.2548,
	"longitude": -73.0973,
	"hourly": ["temperature_2m", "weather_code"],
	"daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
	"temperature_unit": "fahrenheit",
	"wind_speed_unit": "mph",
	"precipitation_unit": "inch",
	"timezone": "auto",
	"forecast_days": 10
}

try:
    # Fetch Data using the SDK
    responses = openmeteo.weather_api("https://api.open-meteo.com", params=params)
    res = responses[0]

    # --- PROCESS HOURLY ---
    hourly = res.Hourly()
    hourly_temp = hourly.Variables(0).ValuesAsNumpy()
    hourly_code = hourly.Variables(1).ValuesAsNumpy()
    
    # Create Hourly DataFrame
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["Temp (°F)"] = hourly_temp
    hourly_data["Condition"] = [WMO_CODES.get(int(c), "Unknown") for c in hourly_code]
    hourly_df = pd.DataFrame(data = hourly_data).head(36)

    # --- TOP SECTION: Current Temp ---
    current_temp = round(hourly_df.iloc[0]["Temp (°F)"], 1)
    current_cond = hourly_df.iloc[0]["Condition"]
    
    st.markdown(f"# **{current_temp}°F**")
    st.markdown(f"### Dorset, VT: {current_cond}")
    st.write(f"Refreshed: {datetime.now().strftime('%I:%M %p')}")
    st.divider()

    # --- MIDDLE SECTION: 36 Hours ---
    st.subheader("Next 36 Hours")
    st.line_chart(hourly_df.set_index("date")["Temp (°F)"])
    with st.expander("View Hourly Table"):
        st.table(hourly_df.assign(date=hourly_df['date'].dt.strftime('%m/%d %I:%M %p')))

    # --- BOTTOM SECTION: 10-Day ---
    st.divider()
    st.subheader("10-Day Forecast")
    daily = res.Daily()
    daily_df = pd.DataFrame({
        "Date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        ).strftime('%Y-%m-%d'),
        "Condition": [WMO_CODES.get(int(c), "Unknown") for c in daily.Variables(0).ValuesAsNumpy()],
        "High (°F)": daily.Variables(1).ValuesAsNumpy(),
        "Low (°F)": daily.Variables(2).ValuesAsNumpy()
    })
    st.table(daily_df)

except Exception as e:
    st.error(f"SDK Error: {e}")









