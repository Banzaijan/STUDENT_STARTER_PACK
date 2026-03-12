from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from datetime import datetime

from utils.colors import (CARD, CARD2, ACCENT, ACCENT_DIM,
                           TEXT, MUTED, RED, GREEN, DIM, BORDER)
from utils.helpers import days_left
from utils.data import DEFAULT_SCHEDULE
from widgets.buttons import lbl, section_label, scrollable, vstack
from widgets.cards import BaseScreen, CardLayout


class HomeScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root  = BoxLayout(orientation="vertical")
        stack = vstack(spacing=14)
        data  = self.app.data

        pending_exams = sum(1 for e in data["exams"] if not e["done"])
        pending_tasks = sum(1 for t in data["todos"]  if not t["done"])
        done_tasks    = sum(1 for t in data["todos"]  if t["done"])
        total_tasks   = len(data["todos"])

        # ── stat row ──────────────────────────────────────────────────────────
        stat_row = BoxLayout(size_hint_y=None, height=dp(108), spacing=dp(12))

        ec = CardLayout(bg=ACCENT_DIM, radius=16, size_hint_x=1,
                        padding=[dp(18), dp(16)])
        ec.add_widget(lbl(str(pending_exams), size=42, bold=True, color=ACCENT,
                          halign="left", size_hint_y=None, height=dp(54)))
        ec.add_widget(lbl("Exams due", size=12, color=ACCENT,
                          halign="left", size_hint_y=None, height=dp(20)))
        stat_row.add_widget(ec)

        tc = CardLayout(bg=CARD, radius=16, size_hint_x=1,
                        padding=[dp(18), dp(16)])
        tc.add_widget(lbl(str(pending_tasks), size=42, bold=True, color=TEXT,
                          halign="left", size_hint_y=None, height=dp(54)))
        tc.add_widget(lbl("Tasks left", size=12, color=MUTED,
                          halign="left", size_hint_y=None, height=dp(20)))
        stat_row.add_widget(tc)
        stack.add_widget(stat_row)

        # ── progress bar ──────────────────────────────────────────────────────
        if total_tasks > 0:
            ratio = done_tasks / total_tasks
            prog_card = CardLayout(bg=CARD, radius=16, size_hint_y=None,
                                   height=dp(72), padding=[dp(18), dp(14)])
            top_row = BoxLayout(size_hint_y=None, height=dp(22))
            top_row.add_widget(lbl("Today's Progress", size=12, color=MUTED))
            top_row.add_widget(lbl(f"{int(ratio*100)}%", size=12, bold=True,
                                   color=ACCENT, halign="right"))
            prog_card.add_widget(top_row)
            pb_bg = Widget(size_hint_y=None, height=dp(8))
            with pb_bg.canvas:
                Color(*CARD2)
                pb_bg._bg   = RoundedRectangle(pos=pb_bg.pos, size=pb_bg.size, radius=[dp(4)])
                Color(*ACCENT)
                pb_bg._fill = RoundedRectangle(
                    pos=pb_bg.pos,
                    size=(pb_bg.width * ratio, pb_bg.height),
                    radius=[dp(4)])
            def _upd(inst, *a, r=ratio):
                inst._bg.pos    = inst.pos
                inst._bg.size   = inst.size
                inst._fill.pos  = inst.pos
                inst._fill.size = (inst.width * r, inst.height)
            pb_bg.bind(pos=_upd, size=_upd)
            prog_card.add_widget(pb_bg)
            stack.add_widget(prog_card)

        # ── today's classes ───────────────────────────────────────────────────
        today_name = datetime.now().strftime("%A")
        classes    = data.get("schedule", DEFAULT_SCHEDULE).get(today_name, [])
        stack.add_widget(section_label(f"TODAY  ·  {today_name.upper()}"))

        if not classes:
            c = CardLayout(bg=CARD, radius=16, size_hint_y=None, height=dp(64))
            c.add_widget(lbl("No classes today 🎉", color=MUTED,
                             halign="center", size_hint_y=None, height=dp(36)))
            stack.add_widget(c)
        else:
            for item in classes:
                stack.add_widget(self.class_card(item[0], item[1], item[2]))

        # ── next exam ─────────────────────────────────────────────────────────
        upcoming = [e for e in data["exams"]
                    if not e["done"] and days_left(e["date"]) != "Past"]
        upcoming.sort(key=lambda x: x["date"])
        stack.add_widget(section_label("NEXT EXAM"))

        if upcoming:
            e  = upcoming[0]
            dl = days_left(e["date"])
            c  = CardLayout(bg=CARD, radius=16, size_hint_y=None, height=dp(96),
                            padding=[dp(18), dp(14)])
            top_row = BoxLayout(size_hint_y=None, height=dp(30))
            top_row.add_widget(lbl(e["subject"], size=15, bold=True, color=TEXT))
            top_row.add_widget(lbl(dl, size=13, bold=True,
                                   color=RED if dl == "Today!" else ACCENT,
                                   halign="right"))
            c.add_widget(top_row)
            c.add_widget(lbl(e["type"], size=12, color=MUTED,
                             size_hint_y=None, height=dp(22)))
            c.add_widget(lbl(f"{e['date']}   {e['notes']}", size=11, color=DIM,
                             size_hint_y=None, height=dp(20)))
            stack.add_widget(c)
        else:
            c = CardLayout(bg=CARD, radius=16, size_hint_y=None, height=dp(64))
            c.add_widget(lbl("No upcoming exams", color=MUTED,
                             halign="center", size_hint_y=None, height=dp(36)))
            stack.add_widget(c)

        root.add_widget(scrollable(stack))
        self.add_widget(root)