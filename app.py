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
    "temperature_unit": "fahrenheit",
    "windspeed_unit": "mph",
    "timezone": loc["tz"],
    "forecast_days": 2
}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()
data = response.json()

# ---------- CURRENT CONDITIONS ----------
tz = pytz.timezone(loc["tz"])
now_hour = datetime.now(tz).strftime("%Y-%m-%dT%H:00")
times = data["hourly"]["time"]

index = times.index(now_hour) if now_hour in times else 0

temp = data["hourly"]["temperature_2m"][index]
feels = data["hourly"]["apparent_temperature"][index]
rain = data["hourly"]["precipitation_probability"][index]
gusts = data["hourly"]["windgusts_10m"][index]
condition = WMO_CODES.get(
    data["hourly"]["weathercode"][index],
    "Unknown"
)

st.markdown(f"# **{temp}°F**")
st.markdown(f"### Feels like {feels}°F · {location_name}")
st.write(f"{condition} · Rain {rain}% · Gusts {gusts} mph")
st.write(f"Updated {datetime.now(tz).strftime('%I:%M %p')}")
st.divider()

# ---------- NEXT 36 HOURS ----------
df = pd.DataFrame({
    "Time": pd.to_datetime(data["hourly"]["time"]),
    "Temp (°F)": data["hourly"]["temperature_2m"],
    "Feels Like (°F)": data["hourly"]["apparent_temperature"],
    "Rain %": data["hourly"]["precipitation_probability"],
    "Wind Gusts (mph)": data["hourly"]["windgusts_10m"]
}).head(36)

st.subheader("Next 36 Hours · Temperature")
st.line_chart(df.set_index("Time")[["Temp (°F)", "Feels Like (°F)"]])

st.subheader("Next 36 Hours · Precipitation Probability")
st.line_chart(df.set_index("Time")[["Rain %"]])

with st.expander("Hourly Details"):
    st.dataframe(df, use_container_width=True)
































