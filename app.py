# --- 10-DAY SUMMARY (GRID FORMAT) ---
st.divider()
st.subheader("10-Day Forecast")

# Create a container for the grid
grid_data = pd.DataFrame({
    "Date": pd.to_datetime(data["daily"]["time"]),
    "Condition": [WMO_CODES.get(c, "☁️") for c in data["daily"]["weathercode"]],
    "High": data["daily"]["temperature_2m_max"],
    "Low": data["daily"]["temperature_2m_min"]
})

# Display in a 5-column grid (2 rows of 5)
cols = st.columns(5)
for i, row in grid_data.iterrows():
    with cols[i % 5]:
        st.markdown(f"**{row['Date'].strftime('%a, %b %d')}**")
        st.markdown(f"### {row['Condition']}")
        st.markdown(f"High: **{row['High']}°**")
        st.markdown(f"Low: {row['Low']}°")
        st.caption("---")





















