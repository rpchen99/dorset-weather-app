// Apple Style Weather App
// React + TypeScript Version
// --------------------------------------------------
// FIX:
// The canvas type is `code/react`, but the previous file
// contained Python (Streamlit) code. That caused the
// TypeScript compiler to attempt parsing Python,
// producing:
//   SyntaxError: /index.tsx: Unexpected token (1:0)
//
// This file is now valid React + TypeScript (TSX)
// and will compile correctly.

import React from "react";

// -----------------------------
// Types
// -----------------------------
interface HourlyData {
  time: string;
  temp: number;
  feelsLike: number;
  icon: string;
}

interface DailyData {
  day: string;
  low: number;
  high: number;
  icon: string;
}

interface WeatherData {
  city: string;
  currentTemp: number;
  feelsLike: number;
  icon: string;
  hourly: HourlyData[];
  daily: DailyData[];
}

// -----------------------------
// Deterministic Mock Data
// (No external fetch required)
// -----------------------------
const weather: WeatherData = {
  city: "Dorset",
  currentTemp: 72,
  feelsLike: 70,
  icon: "☀️",
  hourly: Array.from({ length: 24 }).map((_, i) => ({
    time: i === 0 ? "Now" : `${i}h`,
    temp: 65 + (i % 8),
    feelsLike: 64 + (i % 8),
    icon: i % 3 === 0 ? "☀️" : i % 3 === 1 ? "⛅" : "☁️",
  })),
  daily: [
    { day: "Today", low: 60, high: 75, icon: "☀️" },
    { day: "Tue", low: 61, high: 74, icon: "🌤" },
    { day: "Wed", low: 63, high: 78, icon: "☀️" },
    { day: "Thu", low: 65, high: 80, icon: "⛅" },
    { day: "Fri", low: 62, high: 77, icon: "🌧" },
    { day: "Sat", low: 59, high: 73, icon: "☁️" },
    { day: "Sun", low: 60, high: 76, icon: "☀️" },
    { day: "Mon", low: 58, high: 72, icon: "🌤" },
    { day: "Tue", low: 57, high: 70, icon: "☁️" },
    { day: "Wed", low: 55, high: 69, icon: "🌧" },
  ],
};

// -----------------------------
// Component
// -----------------------------
export default function AppleStyleWeather() {
  const globalMin = Math.min(...weather.daily.map((d) => d.low));
  const globalMax = Math.max(...weather.daily.map((d) => d.high));
  const range = globalMax - globalMin;

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at 50% 0%, #8EC5FC 0%, #4facfe 40%, #1e3c72 100%)",
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
          <div style={{ fontSize: 110, fontWeight: 200 }}>
            {weather.currentTemp}°
          </div>
          <div style={{ opacity: 0.7 }}>
            {weather.icon} Feels like {weather.feelsLike}°
          </div>
        </div>

        {/* 24 Hour Horizontal Scroll */}
        <GlassCard>
          <div
            style={{
              display: "flex",
              overflowX: "auto",
              gap: 20,
              paddingBottom: 10,
            }}
          >
            {weather.hourly.map((h, i) => (
              <div
                key={i}
                style={{ minWidth: 70, textAlign: "center" }}
              >
                <div style={{ fontSize: 12, opacity: 0.7 }}>
                  {h.time}
                </div>
                <div style={{ fontSize: 24 }}>{h.icon}</div>
                <div>{h.temp}°</div>
                <div style={{ fontSize: 11, opacity: 0.6 }}>
                  FL {h.feelsLike}°
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* 10 Day Forecast with Range Bars */}
        <GlassCard>
          {weather.daily.map((d, i) => {
            const lowPct = ((d.low - globalMin) / range) * 100;
            const widthPct = ((d.high - d.low) / range) * 100;

            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "10px 0",
                }}
              >
                <div style={{ width: 70 }}>{d.day}</div>
                <div>{d.icon}</div>
                <div style={{ width: 35, textAlign: "right", opacity: 0.6 }}>
                  {d.low}°
                </div>
                <div
                  style={{
                    flex: 1,
                    margin: "0 10px",
                    height: 4,
                    background: "rgba(255,255,255,0.25)",
                    borderRadius: 4,
                    position: "relative",
                  }}
                >
                  <div
                    style={{
                      position: "absolute",
                      left: `${lowPct}%`,
                      width: `${widthPct}%`,
                      height: 4,
                      background: "white",
                      borderRadius: 4,
                    }}
                  />
                </div>
                <div style={{ width: 35, textAlign: "right", fontWeight: 500 }}>
                  {d.high}°
                </div>
              </div>
            );
          })}
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
        background: "rgba(255,255,255,0.15)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        borderRadius: 30,
        padding: 20,
        marginBottom: 25,
        border: "1px solid rgba(255,255,255,0.2)",
        boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
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
  console.assert(weather.hourly.length === 24, "Hourly length invalid");
  console.assert(weather.daily.length === 10, "Daily length invalid");
  console.assert(weather.daily[0].high >= weather.daily[0].low, "High/Low invalid");
}

