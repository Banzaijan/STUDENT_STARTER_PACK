"""
╔══════════════════════════════════════╗
║     STUDENT STARTER PACK 🎒          ║
║  Kivy version — Android APK Ready    ║
║  v4 — With Student Login             ║
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
from kivy.uix.screenmanager import ScreenManager, NoTransition, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp

from utils.data import load_data
from utils.colors import BG, ACCENT, TEXT, MUTED
from widgets.cards import NavBar, TopBar
from screens.home     import HomeScreen
from screens.schedule import ScheduleScreen
from screens.exams    import ExamsScreen
from screens.tasks    import TasksScreen
from screens.grades   import GradesScreen
from screens.timer    import TimerScreen
from screens.weather  import WeatherScreen
from screens.login    import LoginScreen

# ─── OTA ─────────────────────────────────────────────────────────────────────
APP_VERSION     = 4
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
            with open(os.path.abspath(__file__), "wb") as f:
                f.write(new_code)
            print(f"[OTA] Updated to v{latest} — restart to apply.")
    except Exception as e:
        print(f"[OTA] Check failed: {e}")


class StudentApp(App):
    def build(self):
        self.data         = load_data()
        self.title        = "Student Starter Pack"
        self.current_user = {"email": "", "name": ""}
        threading.Thread(target=check_ota_update, daemon=True).start()

        # Root screen manager — switches between login and main app
        self.root_sm = ScreenManager(transition=FadeTransition(duration=0.25))

        # ── Login screen ──────────────────────────────────────────────────────
        login = LoginScreen(on_success=self._on_login)
        self.root_sm.add_widget(login)

        # ── Main app screen (wraps TopBar + NavBar + content) ─────────────────
        from kivy.uix.screenmanager import Screen
        main_screen = Screen(name="main")
        main_layout = BoxLayout(orientation="vertical")

        self.topbar = TopBar()
        main_layout.add_widget(self.topbar)

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
        main_layout.add_widget(self.sm)

        self.nav = NavBar(switch_cb=self.switch_tab)
        main_layout.add_widget(self.nav)

        main_screen.add_widget(main_layout)
        self.root_sm.add_widget(main_screen)

        return self.root_sm

    def _on_login(self, email, name):
        self.current_user = {"email": email, "name": name}
        # Update TopBar greeting with student name
        self.topbar.update_user(name)
        self.switch_tab("home")
        self.root_sm.current = "main"

    def switch_tab(self, tab):
        self.sm.current = tab
        self.nav.set_active(tab)


if __name__ == "__main__":
    StudentApp().run()