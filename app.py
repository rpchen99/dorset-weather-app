import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# ---------- CONFIG ----------
LOCATIONS = {
    "Dorset, VT": {"lat": 43.2548, "lon": -73.0973, "tz": "America/New_York"},
    "Arlington, VA (22202)": {"lat": 38.8500, "lon": -77.0400, "tz": "America/New_York"},
    "Maywood, NJ (07607)": {"lat": 40.9029, "lon": -74.0635, "tz": "America/New_York"}
}

WMO_CODES = {
    0: "Sunny",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Slight Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    77: "Snow Grains",
    80: "Rain Showers",
    81: "Rain Showers",
    82: "Violent Rain Showers",
    85: "Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm"
}

st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="❄️",
    layout="wide"
)

# ---------- UI ----------
location_name = st.sidebar.selectbox(
    "Select Location",
    list(LOCATIONS.keys())
)
loc = LOCATIONS[location_name]

# ---------- API ----------
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": loc["lat"],
    "longitude": loc["lon"],
    "hourly": (
        "temperature_2m,"
        "apparent_temperature,"
        "precipitation_probability,"
        "weathercode,"
        "windgusts_10m"
    ),
    "daily": (
        "weathercode,"
        "temperature_2m_max,"
        "temperature_2m_min"
    ),
    "temperature_unit": "fahrenheit",
    "windspeed_unit": "mph",
    "timezone": loc["tz"],
    "forecast_days": 10
}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()
data = response.json()

# ---------- CURRENT CONDITIONS



































