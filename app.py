import streamlit as st
import pandas as pd
import requests

st.title("Dorset, VT 10-Day Forecast")

# Dorset, VT Coordinates
LAT, LON = 43.2548, -73.0973
URL = f"https://api.open-meteo.com{LAT}&longitude={LON}&hourly=temperature_2m&daily=temperature_2m_max,temperature_2m_min&forecast_days=10&timezone=auto"

if st.button("Get Forecast"):
    data = requests.get(URL).json()
    
    # Hourly Data
    hourly_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "Temp (°C)": data["hourly"]["temperature_2m"]
    })
    st.subheader("Hourly Outlook")
    st.line_chart(hourly_df.set_index("Time"))

    # Daily Data
    daily_df = pd.DataFrame({
        "Date": data["daily"]["time"],
        "Max Temp": data["daily"]["temperature_2m_max"],
        "Min Temp": data["daily"]["temperature_2m_min"]
    })
    st.subheader("Daily Highs/Lows")
    st.table(daily_df)

