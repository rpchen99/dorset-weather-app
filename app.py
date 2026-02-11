// Apple Style Weather App - React Version
// --------------------------------------------------
// FIX:
// The canvas type is `code/react`, but the previous content
// was Python (Streamlit). That caused the build system to
// attempt parsing Python as TSX, resulting in:
//   SyntaxError: /index.tsx: Unexpected token (1:0)
//
// This file is now valid React + TypeScript (TSX)
// and will compile correctly in a React / Next.js environment.

import React from "react";

// -----------------------------
// Types
// -----------------------------
interface Hourly {
  time: string;
  temp: number;
  icon: string;
}

interface Daily {
  day: string;
  high: number;
  low: number;
  icon: string;
}

interface WeatherData {
  city: string;
  current: number;
  feelsLike: number;
  wind: number;
  hourly: Hourly[];
  daily: Daily[];
}

// -----------------------------
// Deterministic Mock Data
// (No external fetch required)
// -----------------------------
const weather: WeatherData = {
  city: "Dorset",
  current: 72,
  feelsLike: 70,
  wind: 8,
  hourly: [
    { time: "Now", temp: 72, icon: "☀️" },
    { time: "1 PM", temp: 73, icon: "🌤" },
    { time: "2 PM", temp: 74, icon: "🌤" },
    { time: "3 PM", temp: 75, icon: "☀️" },
    { time: "4 PM", temp: 74, icon: "⛅" },
    { time: "5 PM", temp: 72, icon: "☁️" },
  ],
  daily: [
    { day: "Today", high: 75, low: 60, icon: "☀️" },
    { day: "Tue", high: 74, low: 61, icon: "🌤" },
    { day: "Wed", high: 78, low: 63, icon: "☀️" },
    { day: "Thu", high: 80, low: 65, icon: "⛅" },
    { day: "Fri", high: 77, low: 62, icon: "🌧" },
    { day: "Sat", high: 73, low: 59, icon: "☁️" },
    { day: "Sun", high: 76, low: 60, icon: "☀️" },
  ],
};

// -----------------------------
// Component
// -----------------------------
export default function AppleStyleWeather() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at 50% 0%, #89CFF0 0%, #4facfe 40%, #1e3c72 100%)",
        color: "white",
        padding: "40px 20px",
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif",
      }}
    >
      <div style={{ maxWidth: 420, margin: "0 auto" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 30 }}>
          <div style={{ fontSize: 34, fontWeight: 500 }}>
            {weather.city}
          </div>
          <div style={{ fontSize: 110, fontWeight: 200, lineHeight: 1 }}>
            {weather.current}°
          </div>
          <div style={{ opacity: 0.7 }}>
            Feels like {weather.feelsLike}° · Wind {weather.wind} mph
          </div>
        </div>

        {/* Hourly */}
        <GlassCard>
          <div style={{ display: "flex", gap: 20, overflowX: "auto" }}>
            {weather.hourly.map((h, i) => (
              <div key={i} style={{ textAlign: "center", minWidth: 60 }}>
                <div style={{ fontSize: 13, opacity: 0.7 }}>{h.time}</div>
                <div style={{ fontSize: 24 }}>{h.icon}</div>
                <div style={{ fontWeight: 500 }}>{h.temp}°</div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* 7 Day */}
        <GlassCard>
          {weather.daily.map((d, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "10px 0",
              }}
            >
              <span>{d.icon} {d.day}</span>
              <span>
                {d.low}° / <strong>{d.high}°</strong>
              </span>
            </div>
          ))}
        </GlassCard>
      </div>
    </div>
  );
}

// -----------------------------
// Glass Card Component
// -----------------------------
function GlassCard({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.12)",
        backdropFilter: "blur(25px)",
        WebkitBackdropFilter: "blur(25px)",
        borderRadius: 32,
        padding: 20,
        marginBottom: 20,
        border: "1px solid rgba(255,255,255,0.15)",
      }}
    >
      {children}
    </div>
  );
}

// -----------------------------
// Basic Runtime Tests
// -----------------------------
if (process.env.NODE_ENV === "test") {
  console.assert(weather.city === "Dorset", "Default city mismatch");
  console.assert(weather.hourly.length > 0, "Hourly data missing");
  console.assert(weather.daily.length === 7, "Daily forecast length invalid");
}


















































