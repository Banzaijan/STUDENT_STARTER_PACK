from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from datetime import datetime

from utils.colors import CARD, CARD2, ACCENT, ACCENT_DIM, TEXT, MUTED, RED, DIM, BORDER
from utils.helpers import days_left
from utils.data import DEFAULT_SCHEDULE
from widgets.buttons import lbl, section_label, scrollable, vstack
from widgets.cards import BaseScreen, CardLayout


class HomeScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root  = BoxLayout(orientation="vertical")
        stack = vstack(spacing=10)
        data  = self.app.data

        pending_exams = sum(1 for e in data["exams"] if not e["done"])
        pending_tasks = sum(1 for t in data["todos"]  if not t["done"])

        # ── stat cards ──
        stat_row = BoxLayout(size_hint_y=None, height=dp(88), spacing=dp(10))
        for num, label, is_primary in [
            (pending_exams, "EXAMS DUE", True),
            (pending_tasks, "TASKS LEFT", False)
        ]:
            c = CardLayout(
                bg=ACCENT_DIM if is_primary else CARD,
                radius=10, size_hint_x=1,
                padding=[dp(14), dp(12)])
            c.add_widget(lbl(str(num), size=32, bold=True,
                             color=ACCENT if is_primary else TEXT,
                             halign="left", size_hint_y=None, height=dp(42)))
            c.add_widget(lbl(label, size=8, bold=True, color=MUTED,
                             halign="left", size_hint_y=None, height=dp(18)))
            stat_row.add_widget(c)
        stack.add_widget(stat_row)

        # ── today classes ──
        today_name = datetime.now().strftime("%A")
        classes    = data.get("schedule", DEFAULT_SCHEDULE).get(today_name, [])
        stack.add_widget(section_label(f"TODAY  ·  {today_name.upper()}"))
        if not classes:
            c = CardLayout(bg=CARD, radius=10, size_hint_y=None, height=dp(52))
            c.add_widget(lbl("No classes today", color=MUTED,
                             halign="center", size_hint_y=None, height=dp(30)))
            stack.add_widget(c)
        else:
            for item in classes:
                stack.add_widget(self.class_card(item[0], item[1], item[2]))

        # ── next exam ──
        upcoming = [e for e in data["exams"] if not e["done"] and days_left(e["date"]) != "Past"]
        upcoming.sort(key=lambda x: x["date"])
        stack.add_widget(section_label("NEXT EXAM"))
        if upcoming:
            e  = upcoming[0]
            dl = days_left(e["date"])
            c  = CardLayout(bg=CARD, radius=10, size_hint_y=None, height=dp(78),
                            padding=[dp(14), dp(12)])
            top_row = BoxLayout(size_hint_y=None, height=dp(26))
            top_row.add_widget(lbl(e['subject'].upper(), size=12, bold=True, color=TEXT))
            top_row.add_widget(lbl(dl, size=11, bold=True,
                                   color=RED if dl == "Today!" else ACCENT,
                                   halign="right"))
            c.add_widget(top_row)
            c.add_widget(lbl(e['type'], size=10, color=MUTED,
                             size_hint_y=None, height=dp(18)))
            c.add_widget(lbl(f"{e['date']}   {e['notes']}", size=9, color=DIM,
                             size_hint_y=None, height=dp(16)))
            stack.add_widget(c)

        root.add_widget(scrollable(stack))
        self.add_widget(root)