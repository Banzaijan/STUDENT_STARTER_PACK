"""
╔══════════════════════════════════════╗
║     STUDENT STARTER PACK 🎒          ║
║  Kivy version — Android APK Ready    ║
║  v3 — Modular Entry Point            ║
╚══════════════════════════════════════╝
"""

import json
import os
import threading

try:
    import urllib.request
    HAS_URLLIB = True
except Exception:
    HAS_URLLIB = False

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.boxlayout import BoxLayout

from utils.data import load_data
from widgets.cards import NavBar, TopBar
from screens.home     import HomeScreen
from screens.schedule import ScheduleScreen
from screens.exams    import ExamsScreen
from screens.tasks    import TasksScreen
from screens.grades   import GradesScreen
from screens.timer    import TimerScreen
from screens.weather  import WeatherScreen

# ─── OTA Update ──────────────────────────────────────────────────────────────
APP_VERSION     = 3
OTA_UPDATE_URL  = "https://raw.githubusercontent.com/Banzaijan/STUDENT-STARTER-PACK/refs/heads/main/Main.py"
OTA_VERSION_URL = "https://raw.githubusercontent.com/Banzaijan/STUDENT-STARTER-PACK/refs/heads/main/version.json"

def check_ota_update():
    if not HAS_URLLIB:
        return
    try:
        with urllib.request.urlopen(OTA_VERSION_URL, timeout=5) as r:
            info = json.loads(r.read().decode())
        latest = info.get("version", 1)
        if latest > APP_VERSION:
            with urllib.request.urlopen(OTA_UPDATE_URL, timeout=10) as r:
                new_code = r.read()
            script_path = os.path.abspath(__file__)
            with open(script_path, "wb") as f:
                f.write(new_code)
            print(f"[OTA] Updated to v{latest} — restart to apply.")
    except Exception as e:
        print(f"[OTA] Check failed: {e}")


class StudentApp(App):
    def build(self):
        self.data  = load_data()
        self.title = "Student Starter Pack"
        threading.Thread(target=check_ota_update, daemon=True).start()

        root = BoxLayout(orientation="vertical")
        root.add_widget(TopBar())

        self.sm = ScreenManager(transition=NoTransition(), size_hint_y=1)
        for name, cls in [
            ("home",     HomeScreen),
            ("schedule", ScheduleScreen),
            ("exams",    ExamsScreen),
            ("tasks",    TasksScreen),
            ("grades",   GradesScreen),
            ("timer",    TimerScreen),
            ("weather",  WeatherScreen),
        ]:
            self.sm.add_widget(cls(app_ref=self, name=name))
        root.add_widget(self.sm)

        self.nav = NavBar(switch_cb=self.switch_tab)
        root.add_widget(self.nav)
        self.switch_tab("home")
        return root

    def switch_tab(self, tab):
        self.sm.current = tab
        self.nav.set_active(tab)


if __name__ == "__main__":
    StudentApp().run()