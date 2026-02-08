import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import pytz

# ---------- CONFIG ----------
LOCATIONS = {
    "Dorset, VT": {"lat": 43.2548, "lon": -73.0973, "tz": "America/New_York"},
    "Arlington, VA (22202)": {"lat": 38.8500, "lon": -77.0400, "tz": "America/New_York"},
    "Maywood, NJ (07607)": {"lat": 40.9029, "lon": -74.0635, "tz": "America/New_York"}
}

# Map weather codes to icons
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
@st.cache_data(ttl=600)  # Cache for 10 minutes
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
    "Wind Gusts (mph)": data["hourly"]["windgusts_10m"]
}).head(36)

st.subheader("Next 36 Hours · Temperature")
st.line_chart(df_hourly.set_index("Time")[["Temp (°F)", "Feels Like (°F)"]])

st.subheader("Next 36 Hours · Precipitation Probability")
st.line_chart(df_hourly.set_index("Time")[["Rain %"]])

# Wind gust coloring
def color_wind_gusts(val):
    if val >= 40:
        return "background-color: #ffcccc"   # strong
    elif val >= 25:
        return "background-color: #fff2cc"   # breezy
    else:
        return "background-color: #e8f5e9"   # calm

with st.expander("Hourly Details"):
    styled_df = df_hourly.style.applymap(
        color_wind_gusts, subset=["Wind Gusts (mph)"]
    )
    st.dataframe(styled_df, use_container_width=True)

st.divider()

# ---------- 10-DAY SUMMARY ----------
st.subheader("10-Day Summary")

today_str = datetime.now(tz).strftime("%Y-%m-%d")
daily_df = pd.DataFrame({
    "Date": data["daily"]["time"],
    "Condition": [WMO_CODES.get(code, "❓") for code in data["daily"]["weathercode"]],
    "High (°F)": data["daily"]["temperature_2m_max"],
    "Low (°F)": data["daily"]["temperature_2m_min"]
})

# Color high/low temperatures and highlight today
def style_daily(row):
    styles = []
    # Highlight today
    if row["Date"] == today_str:
        styles.append("background-color: #d0f0fd")  # light blue
    else:
        styles.append("")  
    # High temp coloring
    if row["High (°F)"] >= 85:
        styles.append("color: red; font-weight: bold")
    elif row["High (°F)"] <= 50:
        styles.append("color: blue; font-weight: bold")
    else:
        styles.append("")
    # Low temp coloring
    if row["Low (°F)"] <= 32:
        styles.append("color: darkblue")
    elif row["Low (°F)"] >= 75:
        styles.append("color: darkred")
    else:
        styles.append("")
    return styles

styled_daily = daily_df.style.apply(
    lambda row: style_daily(row),
    axis=1
)
st.dataframe(styled_daily, use_container_width=True)





































