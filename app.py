import streamlit as st
import pandas as pd
import requests

st.title("Dorset, VT 10-Day Forecast")

# 1. Define the base URL and the parameters separately
BASE_URL = "https://api.open-meteo.com/v1/forecast"
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

# 2. Use 'params' in the get request so 'requests' builds the URL correctly
try:
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status() # Check for HTTP errors
    data = response.json()

    # 3. Hourly Data Visualization
    hourly_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°F)": data["hourly"]["temperature_2m"]
    })
    st.subheader("Hourly Temperature")
    st.line_chart(hourly_df.set_index("Time"))

    # 4. Daily Data Table
    daily_df = pd.DataFrame({
        "Date": data["daily"]["time"],
        "Max Temp (°F)": data["daily"]["temperature_2m_max"],
        "Min Temp (°F)": data["daily"]["temperature_2m_min"]
    })
    st.subheader("10-Day Highs/Lows")
    st.table(daily_df)

except Exception as e:
    st.error(f"Failed to fetch weather data: {e}")



