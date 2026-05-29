"use strict";

const $ = (id) => document.getElementById(id);
const els = {
  form: $("search-form"),
  city: $("city"),
  days: $("days"),
  status: $("status"),
  current: $("current"),
  forecast: $("forecast"),
};

els.form.addEventListener("submit", (e) => {
  e.preventDefault();
  const city = els.city.value.trim();
  if (city) load(city, parseInt(els.days.value, 10));
});

async function load(city, days) {
  setStatus("Loading…");
  els.current.hidden = true;
  els.forecast.hidden = true;
  try {
    const params = new URLSearchParams({ city, days });
    const res = await fetch(`/api/weather?${params}`);
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || `Request failed (${res.status}).`);
    }
    render(await res.json());
    setStatus(null);
  } catch (err) {
    setStatus(err.message, true);
  }
}

function setStatus(msg, isError = false) {
  els.status.hidden = !msg;
  els.status.textContent = msg || "";
  els.status.classList.toggle("error", isError);
}

function render(report) {
  const c = report.current;
  els.current.innerHTML = `
    <div class="place">${escapeHtml(locationLabel(report.location))}</div>
    <div class="icon">${emoji(c.weather_code)}</div>
    <div class="temp">${Math.round(c.temperature)}${report.temp_symbol}</div>
    <div class="desc">${describe(c.weather_code)}</div>
    <div class="details">
      <span>Feels like <b>${Math.round(c.apparent_temperature)}${report.temp_symbol}</b></span>
      <span>Humidity <b>${c.humidity}%</b></span>
      <span>Wind <b>${Math.round(c.wind_speed)} ${report.wind_symbol}</b></span>
    </div>`;
  els.current.hidden = false;

  els.forecast.innerHTML = report.daily
    .map((d) => {
      const rain = d.precipitation_probability == null ? "" :
        `<div class="rain">💧 ${d.precipitation_probability}%</div>`;
      return `<div class="day">
        <div class="dow">${dayOfWeek(d.date)}</div>
        <div class="date">${shortDate(d.date)}</div>
        <div class="icon">${emoji(d.weather_code)}</div>
        <div class="hl"><span class="hi">${Math.round(d.temp_max)}°</span>
          <span class="lo">${Math.round(d.temp_min)}°</span></div>
        ${rain}
      </div>`;
    })
    .join("");
  els.forecast.hidden = false;
}

// --- WMO weather code mapping (mirrors the Python side) --------------------
const WMO = {
  0: ["Clear sky", "☀️"], 1: ["Mainly clear", "🌤️"], 2: ["Partly cloudy", "⛅"],
  3: ["Overcast", "☁️"], 45: ["Fog", "🌫️"], 48: ["Rime fog", "🌫️"],
  51: ["Light drizzle", "🌦️"], 53: ["Drizzle", "🌦️"], 55: ["Dense drizzle", "🌧️"],
  56: ["Freezing drizzle", "🌧️"], 57: ["Freezing drizzle", "🌧️"],
  61: ["Slight rain", "🌦️"], 63: ["Rain", "🌧️"], 65: ["Heavy rain", "🌧️"],
  66: ["Freezing rain", "🌧️"], 67: ["Freezing rain", "🌧️"],
  71: ["Slight snow", "🌨️"], 73: ["Snow", "🌨️"], 75: ["Heavy snow", "❄️"],
  77: ["Snow grains", "🌨️"], 80: ["Rain showers", "🌦️"], 81: ["Rain showers", "🌧️"],
  82: ["Violent showers", "⛈️"], 85: ["Snow showers", "🌨️"], 86: ["Snow showers", "❄️"],
  95: ["Thunderstorm", "⛈️"], 96: ["Thunderstorm", "⛈️"], 99: ["Thunderstorm", "⛈️"],
};
const describe = (code) => (WMO[code] || ["Unknown", "❓"])[0];
const emoji = (code) => (WMO[code] || ["Unknown", "❓"])[1];

// --- small helpers ---------------------------------------------------------
function locationLabel(loc) {
  return [loc.name, loc.admin1, loc.country].filter(Boolean).join(", ");
}
function dayOfWeek(iso) {
  return new Date(iso + "T00:00:00").toLocaleDateString(undefined, { weekday: "short" });
}
function shortDate(iso) {
  return new Date(iso + "T00:00:00").toLocaleDateString(undefined, { month: "short", day: "numeric" });
}
function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}
