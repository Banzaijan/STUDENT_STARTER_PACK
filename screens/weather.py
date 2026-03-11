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

from utils.colors import CARD, CARD2, ACCENT, TEXT, MUTED, BLACK, DIM
from widgets.buttons import lbl, section_label
from widgets.cards import BaseScreen, CardLayout

WMO_ICONS = {
    0:"☀",1:"🌤",2:"⛅",3:"☁",45:"◌",48:"◌",
    51:"🌦",53:"🌦",55:"🌧",61:"🌧",63:"🌧",65:"🌧",
    80:"🌦",81:"🌧",82:"⛈",95:"⛈",96:"⛈",99:"⛈",
}
WMO_DESC = {
    0:"CLEAR",1:"MAINLY CLEAR",2:"PARTLY CLOUDY",3:"OVERCAST",
    45:"FOGGY",51:"LIGHT DRIZZLE",61:"LIGHT RAIN",63:"MODERATE RAIN",
    65:"HEAVY RAIN",80:"RAIN SHOWERS",95:"THUNDERSTORM",
}


class WeatherScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=0)

        hdr = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(16), dp(6)])
        hdr.add_widget(lbl("WEATHER  ·  MANILA", size=11, bold=True, color=TEXT))
        root.add_widget(hdr)

        self.weather_card = CardLayout(bg=CARD, radius=10,
                                        size_hint_y=None, height=dp(80),
                                        padding=[dp(16), dp(12)])
        self.weather_card.add_widget(lbl("Fetching...", color=MUTED, halign="center"))
        root.add_widget(self.weather_card)

        # calendar header
        cal_hdr = BoxLayout(size_hint_y=None, height=dp(34), padding=[dp(16), dp(6)])
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
        self.weather_card.height = dp(210)
        c    = data["current"]
        d    = data["daily"]
        temp = round(c["temperature_2m"])
        hum  = c["relative_humidity_2m"]
        wind = c["wind_speed_10m"]
        code = c["weather_code"]
        icon = WMO_ICONS.get(code, "—")
        desc = WMO_DESC.get(code, "UNKNOWN")

        main_row = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(12))
        main_row.add_widget(lbl(icon, size=40, halign="center",
                                size_hint_x=None, width=dp(64)))
        info = BoxLayout(orientation="vertical", spacing=dp(2))
        info.add_widget(lbl(f"{temp}°C", size=34, bold=True, color=TEXT,
                            size_hint_y=None, height=dp(46)))
        info.add_widget(lbl(desc, size=8, bold=True, color=MUTED,
                            size_hint_y=None, height=dp(16)))
        main_row.add_widget(info)
        detail = BoxLayout(orientation="vertical", spacing=dp(4))
        detail.add_widget(lbl(f"HUM  {hum}%", size=9, bold=True, color=MUTED,
                              halign="right", size_hint_y=None, height=dp(18)))
        detail.add_widget(lbl(f"WIND  {wind} km/h", size=9, bold=True, color=MUTED,
                              halign="right", size_hint_y=None, height=dp(18)))
        main_row.add_widget(detail)
        self.weather_card.add_widget(main_row)

        day_labels = ["TODAY","D+1","D+2","D+3","D+4"]
        fc_row = BoxLayout(size_hint_y=None, height=dp(88), spacing=dp(6))
        for i in range(min(5, len(d["temperature_2m_max"]))):
            fc = CardLayout(bg=CARD2, radius=8, size_hint_x=1, padding=[dp(4), dp(6)])
            fc.add_widget(lbl(day_labels[i], size=7, bold=True, color=MUTED,
                              halign="center", size_hint_y=None, height=dp(14)))
            fc.add_widget(lbl(WMO_ICONS.get(d["weather_code"][i], "—"),
                              size=16, halign="center", size_hint_y=None, height=dp(26)))
            fc.add_widget(lbl(f"{round(d['temperature_2m_max'][i])}°",
                              size=11, bold=True, color=ACCENT, halign="center",
                              size_hint_y=None, height=dp(20)))
            fc.add_widget(lbl(f"{round(d['temperature_2m_min'][i])}°",
                              size=9, color=MUTED, halign="center",
                              size_hint_y=None, height=dp(16)))
            fc_row.add_widget(fc)
        self.weather_card.add_widget(fc_row)

    def _render_fallback(self):
        self.weather_card.clear_widgets()
        self.weather_card.add_widget(
            lbl("No internet connection", color=MUTED, halign="center"))

    def _build_calendar(self):
        now   = datetime.now()
        frame = CardLayout(bg=CARD, radius=10,
                           size_hint_y=None, height=dp(260),
                           padding=[dp(14), dp(10)])
        frame.add_widget(lbl(now.strftime("%B %Y").upper(), size=10, bold=True,
                             color=TEXT, size_hint_y=None, height=dp(24)))
        day_row = BoxLayout(size_hint_y=None, height=dp(22))
        for d in ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]:
            day_row.add_widget(lbl(d, size=8, bold=True, color=MUTED, halign="center"))
        frame.add_widget(day_row)

        for week in calendar.monthcalendar(now.year, now.month):
            week_row = BoxLayout(size_hint_y=None, height=dp(32))
            for day in week:
                is_today = (day == now.day)
                if is_today:
                    bg_col  = ACCENT
                    txt_col = BLACK
                elif day:
                    bg_col  = (0, 0, 0, 0)
                    txt_col = TEXT
                else:
                    bg_col  = (0, 0, 0, 0)
                    txt_col = (0, 0, 0, 0)
                cell = Button(
                    text=str(day) if day else "",
                    font_size=dp(10), bold=is_today,
                    background_normal="",
                    background_color=bg_col,
                    color=txt_col)
                week_row.add_widget(cell)
            frame.add_widget(week_row)
        return frame