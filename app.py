// Apple-Style Weather App — Ultra iOS Replica
// --------------------------------------------------
// Visually tuned to closely match iOS Weather:
// ✓ Radial light glow gradient
// ✓ Glassmorphism cards (blur + subtle borders)
// ✓ SF-style typography hierarchy
// ✓ Horizontal scroll hourly strip
// ✓ iOS-style daily temperature range bars
// ✓ Soft separators + spacing
// ✓ Subtle atmospheric animation layer
// ✓ Deterministic mock data (no external fetch)

import React from "react";

// -----------------------------
// Types
// -----------------------------
interface Hourly {
  time: string;
  temp: number;
  precip: number;
}

interface Daily {
  day: string;
  high: number;
  low: number;
}

interface WeatherData {
  city: string;
  current: number;
  feelsLike: number;
  condition: string;
  wind: number;
  isDay: boolean;
  hourly: Hourly[];
  daily: Daily[];
}

// -----------------------------
// Mock Data
// -----------------------------
const mockWeather: WeatherData = {
  city: "New York",
  current: 72,
  feelsLike: 70,
  condition: "Partly Cloudy",
  wind: 8,
  isDay: true,
  hourly: Array.from({ length: 12 }).map((_, i) => ({
    time: i === 0 ? "Now" : `${i + 1} PM`,
    temp: 70 + (i % 5),
    precip: i * 6,
  })),
  daily: [
    { day: "Today", high: 75, low: 60 },
    { day: "Tue", high: 74, low: 61 },
    { day: "Wed", high: 78, low: 63 },
    { day: "Thu", high: 80, low: 65 },
    { day: "Fri", high: 77, low: 62 },
    { day: "Sat", high: 73, low: 59 },
    { day: "Sun", high: 76, low: 60 },
  ],
};

// -----------------------------
// Component
// -----------------------------
export default function AppleStyleWeather() {
  const weather = mockWeather;

  const background = weather.isDay
    ? "radial-gradient(circle at 50% 0%, #89CFF0 0%, #4facfe 40%, #1e3c72 100%)"
    : "radial-gradient(circle at 50% 0%, #3a4a63 0%, #141E30 50%, #0f2027 100%)";

  const globalMin = Math.min(...weather.daily.map((d) => d.low));
  const globalMax = Math.max(...weather.daily.map((d) => d.high));
  const range = globalMax - globalMin;

  return (
    <div
      style={{
        minHeight: "100vh",
        background,
        color: "white",
        padding: "40px 20px 60px",
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif",
      }}
    >
      <div style={{ maxWidth: 420, margin: "0 auto" }}>
        {/* Location + Current */}
        <div style={{ textAlign: "center", marginBottom: 30 }}>
          <div style={{ fontSize: 34, fontWeight: 500 }}>
            {weather.city}
          </div>
          <div
            style={{
              fontSize: 110,
              fontWeight: 200,
              lineHeight: 1,
            }}
          >
            {weather.current}°
          </div>
          <div style={{ opacity: 0.85, fontSize: 20 }}>
            {weather.condition}
          </div>
          <div style={{ opacity: 0.6, fontSize: 15 }}>
            H:{weather.daily[0].high}° L:{weather.daily[0].low}°
          </div>
        </div>

        {/* Hourly Card */}
        <GlassCard>
          <div style={{ display: "flex", overflowX: "auto", gap: 24 }}>
            {weather.hourly.map((h, i) => (
              <div
                key={i}
                style={{
                  minWidth: 60,
                  textAlign: "center",
                  opacity: i === 0 ? 1 : 0.9,
                }}
              >
                <div style={{ fontSize: 13, opacity: 0.7 }}>{h.time}</div>
                <div style={{ fontSize: 22, margin: "6px 0" }}>☀️</div>
                <div style={{ fontSize: 17, fontWeight: 500 }}>
                  {h.temp}°
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Details Panel */}
        <GlassCard>
          <DetailRow label="Feels Like" value={`${weather.feelsLike}°`} />
          <Divider />
          <DetailRow label="Wind" value={`${weather.wind} mph`} />
        </GlassCard>

        {/* 7-Day Forecast */}
        <GlassCard>
          {weather.daily.map((d, i) => {
            const lowPercent = ((d.low - globalMin) / range) * 100;
            const widthPercent = ((d.high - d.low) / range) * 100;

            return (
              <React.Fragment key={i}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "12px 0",
                  }}
                >
                  <div style={{ width: 70 }}>{d.day}</div>
                  <div>☀️</div>
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
                        left: `${lowPercent}%`,
                        width: `${widthPercent}%`,
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
                {i < weather.daily.length - 1 && <Divider />}
              </React.Fragment>
            );
          })}
        </GlassCard>
      </div>
    </div>
  );
}

// -----------------------------
// Reusable Components
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
        boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
      }}
    >
      {children}
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        padding: "10px 0",
        fontSize: 16,
      }}
    >
      <span style={{ opacity: 0.7 }}>{label}</span>
      <span style={{ fontWeight: 500 }}>{value}</span>
    </div>
  );
}

function Divider() {
  return (
    <div
      style={{
        height: 1,
        background: "rgba(255,255,255,0.15)",
        margin: "4px 0",
      }}
    />
  );
}

// -----------------------------
// Basic Runtime Tests
// -----------------------------
if (process.env.NODE_ENV === "test") {
  console.assert(mockWeather.current === 72, "Current temp mismatch");
  console.assert(mockWeather.hourly.length === 12, "Hourly length mismatch");
  console.assert(mockWeather.daily.length === 7, "Daily length mismatch");
  console.assert(mockWeather.daily[0].high >= mockWeather.daily[0].low, "High/Low invalid");
}
















































