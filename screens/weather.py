import json
import calendar
import threading

try:
    import urllib.request
    HAS_URLLIB = True
except Exception:
    HAS_URLLIB = False

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import datetime

from utils.colors import CARD, CARD2, ACCENT, ACCENT_DIM, TEXT, MUTED, BLACK, DIM, BORDER
from widgets.buttons import lbl
from widgets.cards import BaseScreen, CardLayout

WMO_ICONS = {
    0:"☀️", 1:"🌤", 2:"⛅", 3:"☁️", 45:"🌫", 48:"🌫",
    51:"🌦", 53:"🌦", 55:"🌧", 61:"🌧", 63:"🌧", 65:"🌧",
    80:"🌦", 81:"🌧", 82:"⛈", 95:"⛈", 96:"⛈", 99:"⛈",
}
WMO_DESC = {
    0:"Clear", 1:"Mainly Clear", 2:"Partly Cloudy", 3:"Overcast",
    45:"Foggy", 51:"Light Drizzle", 61:"Light Rain", 63:"Moderate Rain",
    65:"Heavy Rain", 80:"Rain Showers", 95:"Thunderstorm",
}


class WeatherScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=0)

        hdr = BoxLayout(size_hint_y=None, height=dp(64), padding=[dp(20), dp(10)])
        hdr.add_widget(lbl("Weather  ·  Manila", size=22, bold=True, color=TEXT,
                           size_hint_y=None, height=dp(44)))
        root.add_widget(hdr)

        self.weather_card = CardLayout(bg=CARD, radius=18,
                                       size_hint_y=None, height=dp(80),
                                       padding=[dp(20), dp(16)])
        self.weather_card.add_widget(lbl("Fetching weather…", size=14,
                                         color=MUTED, halign="center"))
        root.add_widget(self.weather_card)

        cal_hdr = BoxLayout(size_hint_y=None, height=dp(42), padding=[dp(20), dp(8)])
        cal_hdr.add_widget(lbl("CALENDAR", size=11, bold=True, color=MUTED))
        root.add_widget(cal_hdr)
        root.add_widget(self._build_calendar())
        self.add_widget(root)

        if HAS_URLLIB:
            threading.Thread(target=self._fetch_weather, daemon=True).start()
        else:
            self._render_fallback()

    def _fetch_weather(self):
        try:
            url = ("https://api.open-meteo.com/v1/forecast"
                   "?latitude=14.5995&longitude=120.9842"
                   "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
                   "&daily=temperature_2m_max,temperature_2m_min,weather_code"
                   "&timezone=Asia/Manila&forecast_days=5")
            with urllib.request.urlopen(url, timeout=8) as r:
                data = json.loads(r.read().decode())
            Clock.schedule_once(lambda dt: self._render_weather(data))
        except Exception as e:
            print(f"[WEATHER] {e}")
            Clock.schedule_once(lambda dt: self._render_fallback())

    def _render_weather(self, data):
        self.weather_card.clear_widgets()
        self.weather_card.height = dp(240)
        c    = data["current"]
        d    = data["daily"]
        temp = round(c["temperature_2m"])
        hum  = c["relative_humidity_2m"]
        wind = c["wind_speed_10m"]
        code = c["weather_code"]
        icon = WMO_ICONS.get(code, "—")
        desc = WMO_DESC.get(code, "Unknown")

        main_row = BoxLayout(size_hint_y=None, height=dp(96), spacing=dp(16))
        main_row.add_widget(lbl(icon, size=52, halign="center",
                                size_hint_x=None, width=dp(80)))
        info = BoxLayout(orientation="vertical", spacing=dp(4))
        info.add_widget(lbl(f"{temp}°C", size=44, bold=True, color=TEXT,
                            size_hint_y=None, height=dp(60)))
        info.add_widget(lbl(desc, size=12, color=MUTED,
                            size_hint_y=None, height=dp(22)))
        main_row.add_widget(info)
        detail = BoxLayout(orientation="vertical", spacing=dp(6))
        detail.add_widget(lbl(f"Humidity  {hum}%", size=11, color=MUTED,
                              halign="right", size_hint_y=None, height=dp(22)))
        detail.add_widget(lbl(f"Wind  {wind} km/h", size=11, color=MUTED,
                              halign="right", size_hint_y=None, height=dp(22)))
        main_row.add_widget(detail)
        self.weather_card.add_widget(main_row)

        day_labels = ["Today", "D+1", "D+2", "D+3", "D+4"]
        fc_row = BoxLayout(size_hint_y=None, height=dp(106), spacing=dp(8))
        for i in range(min(5, len(d["temperature_2m_max"]))):
            fc = CardLayout(bg=CARD2, radius=12, size_hint_x=1, padding=[dp(6), dp(8)])
            fc.add_widget(lbl(day_labels[i], size=9, bold=True, color=MUTED,
                              halign="center", size_hint_y=None, height=dp(18)))
            fc.add_widget(lbl(WMO_ICONS.get(d["weather_code"][i], "—"),
                              size=20, halign="center", size_hint_y=None, height=dp(30)))
            fc.add_widget(lbl(f"{round(d['temperature_2m_max'][i])}°",
                              size=13, bold=True, color=ACCENT, halign="center",
                              size_hint_y=None, height=dp(24)))
            fc.add_widget(lbl(f"{round(d['temperature_2m_min'][i])}°",
                              size=11, color=MUTED, halign="center",
                              size_hint_y=None, height=dp(20)))
            fc_row.add_widget(fc)
        self.weather_card.add_widget(fc_row)

    def _render_fallback(self):
        self.weather_card.clear_widgets()
        self.weather_card.add_widget(
            lbl("No internet connection", size=14, color=MUTED, halign="center"))

    def _build_calendar(self):
        now   = datetime.now()
        frame = CardLayout(bg=CARD, radius=18,
                           size_hint_y=None, height=dp(300),
                           padding=[dp(18), dp(14)])
        frame.add_widget(lbl(now.strftime("%B %Y"), size=15, bold=True,
                             color=TEXT, size_hint_y=None, height=dp(30)))
        day_row = BoxLayout(size_hint_y=None, height=dp(28))
        for d in ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]:
            day_row.add_widget(lbl(d, size=11, bold=True, color=MUTED, halign="center"))
        frame.add_widget(day_row)

        for week in calendar.monthcalendar(now.year, now.month):
            week_row = BoxLayout(size_hint_y=None, height=dp(38))
            for day in week:
                is_today = (day == now.day)
                cell = Button(
                    text=str(day) if day else "",
                    font_size=dp(13), bold=is_today,
                    background_normal="",
                    background_color=ACCENT if is_today else (0,0,0,0),
                    color=BLACK if is_today else (TEXT if day else (0,0,0,0)))
                week_row.add_widget(cell)
            frame.add_widget(week_row)
        return frame