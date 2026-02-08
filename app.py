import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import altair as alt

# ---------- CONFIG ----------
LOCATIONS = {
    "Dorset, VT": {"lat": 43.2548, "lon": -73.0973, "tz": "America/New_York"},
    "Arlington, VA (22202)": {"lat": 38.8500, "lon": -77.0400, "tz": "America/New_York"},
    "Maywood, NJ (07607)": {"lat": 40.9029, "lon": -74.0635, "tz": "America/New_York"}
}

# Base weather icons
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

# ---------- ICON FUNCTION (DAY/NIGHT + RAIN) ----------
def get_hourly_icon(code, dt, rain_prob):
    """Return icon for weather code, using moon for night clear skies and rain icon for heavy rain."""
    hour = dt.hour
    if rain_prob >= 30:
        return "🌧"
    if code == 0:  # Clear sky
        return "☀️" if 6 <= hour < 18 else "🌙"
    elif code == 1:  # Mainly clear
        return "🌤" if 6 <= hour < 18 else "🌙"
    else:
        return WMO_CODES.get(code, "❓")

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
temp = round(data["hourly"]["temperature_2m"][index], 1)
feels = round(data["hourly"]["apparent_temperature"][index], 1)
rain = round(data["hourly"]["precipitation_probability"][index], 1)
gusts = round(data["hourly"]["windgusts_10m"][index], 1)
dt_current = pd.to_datetime(data["hourly"]["time"][index])
condition_icon = get_hourly_icon(data["hourly"]["weathercode"][index], dt_current, rain)

st.markdown(f"# **{temp:.1f}°F**")
st.markdown(f"### Feels like {feels:.1f}°F · {location_name}")
st.write(f"{condition_icon} · Rain {rain:.1f}% · Gusts {gusts:.1f} mph")
st.write(f"Updated {datetime.now(tz).strftime('%I:%M %p')}")
st.divider()

# ---------- NEXT 36 HOURS ----------
df_hourly = pd.DataFrame({
    "DateTime": pd.to_datetime(data["hourly"]["time"]),
    "Temp (°F)": data["hourly"]["temperature_2m"],
    "Feels Like (°F)": data["hourly"]["apparent_temperature"],
    "Rain %": data["hourly"]["precipitation_probability"],
    "Wind Gusts (mph)": data["hourly"]["windgusts_10m"],
    "WeatherCode": data["hourly"]["weathercode"]
}).head(36)

# Round temperatures and gusts to 1 decimal place
df_hourly["Temp (°F)"] = df_hourly["Temp (°F)"].round(1)
df_hourly["Feels Like (°F)"] = df_hourly["Feels Like (°F)"].round(1)
df_hourly["Wind Gusts (mph)"] = df_hourly["Wind Gusts (mph)"].round(1)
df_hourly["Rain %"] = df_hourly["Rain %"].round(1)

# Add day/night/rain aware condition icons
df_hourly["Condition"] = [
    get_hourly_icon(c, dt, rain) 
    for c, dt, rain in zip(df_hourly["WeatherCode"], df_hourly["DateTime"], df_hourly["Rain %"])
]

# Day & Time column for table
df_hourly["Day & Time"] = df_hourly["DateTime"].dt.strftime("%a %I:%M %p")

# ---------- ALTAR CHART WITH ICONS ----------
st.subheader("Next 36 Hours · Temperature with Weather Icons")

line = alt.Chart(df_hourly).mark_line(point=False).encode(
    x=alt.X('DateTime:T', title='Time'),
    y=alt.Y('Temp (°F):Q', title='Temperature (°F)')
)

icons = alt.Chart(df_hourly).mark_text(
    baseline='bottom',
    fontSize=20
).encode(
    x='DateTime:T',
    y='Temp (°F):Q',
    text='Condition:N'
)

st.altair_chart(line + icons, use_container_width=True)

# ---------- WIND GUST COLORING ----------
def color_wind_gusts(val):
    if val >= 40:
        return "background-color: #ff6666"
    elif val >= 25:
        return "background-color: #ffcc80"
    else:
        return "background-color: #99ff99"

# ---------- HOURLY DETAILS TABLE ----------
with st.expander("Hourly Details"):
    df_hourly_table = df_hourly.copy()
    df_hourly_table = df_hourly_table[["Day & Time", "Temp (°F)", "Feels Like (°F)", "Rain %", "Wind Gusts (mph)", "Condition"]]
    st.dataframe(df_hourly_table.style.applymap(
        color_wind_gusts, subset=["Wind Gusts (mph)"]
    ), use_container_width=True)

# ---------- 10-DAY SUMMARY ----------
st.divider()
st.subheader("10-Day Summary")

today_str = datetime.now(tz).strftime("%Y-%m-%d")
daily_df = pd.DataFrame({
    "Date": data["daily"]["time"],
    "Condition": [
        get_hourly_icon(c, pd.to_datetime(d), 0)  # daily rain not included; assume 0%
        for c, d in zip(data["daily"]["weathercode"], data["daily"]["time"])
    ],
    "High (°F)": [round(x, 1) for x in data["daily"]["temperature_2m_max"]],
    "Low (°F)": [round(x, 1) for x in data["daily"]["temperature_2m_min"]]
})

# ---------- DARK-THEME-FRIENDLY STYLING ----------
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












































