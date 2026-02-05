import streamlit as st
import pandas as pd
import requests

st.title("Dorset, VT 10-Day Forecast")

# Dorset, VT Coordinates (Cleaned URL)
LAT, LON = 43.2548, -73.0973
URL = f"https://api.open-meteo.com{LAT}&longitude={LON}&hourly=temperature_2m,precipitation_probability,snowfall&daily=temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=auto&forecast_days=10"

# No more 'if st.button' here—just run the request immediately
with requests.Session() as s:
    response = s.get(URL.strip())
    data = response.json()

# Hourly Data Visualization
hourly_df = pd.DataFrame({
    "Time": pd.to_datetime(data["hourly"]["time"]),
    "Temp (°F)": data["hourly"]["temperature_2m"]
})
st.subheader("Hourly Temperature")
st.line_chart(hourly_df.set_index("Time"))

# Daily Data Table
daily_df = pd.DataFrame({
    "Date": data["daily"]["time"],
    "Max Temp (°F)": data["daily"]["temperature_2m_max"],
    "Min Temp (°F)": data["daily"]["temperature_2m_min"]
})
st.subheader("10-Day Highs/Lows")
st.table(daily_df)


