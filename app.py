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

# Weather icons
WMO_CODES = {
    0: "☀️", 1: "🌤", 2: "⛅", 3: "☁️",
    45: "🌫", 48: "🌫", 51: "🌦", 53: "🌦",
    55: "🌦", 61: "🌧", 63: "🌧", 65: "🌧",
    71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️",
    80: "🌦", 81: "🌧", 82: "⛈", 85: "❄️",
    86: "❄️", 95: "🌩"
}

st.set_page_config(page_title="Weather Dashboard", page_icon="❄️", layout="wide")

# ---------- API CALL (CACHED) ----------
@st.cache_data(ttl=600)
def fetch_weather(lat, lon, tz):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
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
        "timezone": tz,
        "forecast_days": 10
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

# ---------- UI ----------
location_name = st.sidebar.selectbox("Select Location", list(LOCATIONS.keys()))
loc = LOCATIONS[location_name]

try:
    data = fetch_weather(loc["lat"], loc["lon"], loc["tz"])
except Exception as e:
    st.error(f"Error fetching weather: {e}")
    st.stop()

tz = pytz.timezone(loc["tz"])
now_hour = datetime.now(tz).strftime("%Y-%m-%dT%H:00")
times = data["hourly"]["time"]
index = times.index(now_hour) if now_hour in times else 0

# ---------- CURRENT CONDITIONS ----------
temp = data["hourly"]["temperature_2m"][index]
feels = data["hourly"]["apparent_temperature"][index]
rain = data["hourly"]["precipitation_probability"][index]
gusts = data["hourly"]["windgusts_10m"][index]
condition_icon = WMO_CODES.get(data["hourly"]["weathercode"][index], "❓")

st.markdown(f"# **{temp}°F**")
st.markdown(f"### Feels like {feels}°F · {location_name}")
st.write(f"{condition_icon} · Rain {rain}% · Gusts {gusts} mph")
st.write(f"Updated {datetime.now(tz).strftime('%I:%M %p')}")
st.divider()

# ---------- NEXT 36 HOURS ----------
df_hourly = pd.DataFrame({
    "Time": pd.to_datetime(data["hourly"]["time"]),
    "Temp (°F)": data["hourly"]["temperature_2m"],
    "Feels Like (°F)": data["hourly"]["apparent_temperature"],
    "Rain %": data["hourly"]["precipitation_probability"],
    "Wind Gusts (mph)": data["hourly"]["windgusts_10m"],
    "Condition": [WMO_CODES.get(c, "❓") for c in data["hourly"]["weathercode"]]
}).head(36)

st.subheader("Next 36 Hours · Temperature / Feels Like")
st.line_chart(df_hourly.set_index("Time")[["Temp (°F)", "Feels Like (°F)"]])

st.subheader("Next 36 Hours · Precipitation Probability")
st.line_chart(df_hourly.set_index("Time")[["Rain %"]])

# ---------- WIND GUST COLORING ----------
def color_wind_gusts(val):
    if val >= 40:
        return "background-color: #ff6666"   # strong gust
    elif val >= 25:
        return "background-color: #ffcc80"   # moderate
    else:
        return "background-color: #99ff99"   # calm

with st.expander("Hourly Details"):
    styled_df = df_hourly.copy()
    # Add icons in the table
    styled_df["Condition"] = df_hourly["Condition"]
    st.dataframe(styled_df.style.applymap(
        color_wind_gusts, subset=["Wind Gusts (mph)"]
    ), use_container_width=True)

# ---------- 10-DAY SUMMARY ----------
st.divider()
st.subheader("10-Day Summary")

today_str = datetime.now(tz).strftime("%Y-%m-%d")
daily_df = pd.DataFrame({
    "Date": data["daily"]["time"],
    "Condition": [WMO_CODES.get(c, "❓") for c in data["daily"]["weathercode"]],
    "High (°F)": data["daily"]["temperature_2m_max"],
    "Low (°F)": data["daily"]["temperature_2m_min"]
})

# Dark-theme-friendly styling
def highlight_today(val):
    return "background-color: #ffcc80; font-weight: bold" if val == today_str else ""

def style_high(val):
    if val >= 85:
        return "color: #ff6666; font-weight: bold"
    elif val <= 50:
        return "color: #66ffff; font-weight: bold"
    return ""

def style_low(val):
    if val <= 32:
        return "color: #3399ff; font-weight: bold"
    elif val >= 75:
        return "color: #ff9933; font-weight: bold"
    return ""

styled_daily = daily_df.style.applymap(highlight_today, subset=["Date"]) \
                             .applymap(style_high, subset=["High (°F)"]) \
                             .applymap(style_low, subset=["Low (°F)"])

st.dataframe(styled_daily, use_container_width=True)








































