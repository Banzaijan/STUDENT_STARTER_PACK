from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.metrics import dp
from datetime import datetime

from utils.colors import BG, CARD, CARD2, ACCENT, ACCENT2, TEXT, MUTED, NAV_BG, TOPBAR, BLACK, DIM, BORDER
from utils.helpers import subject_color


class CardLayout(BoxLayout):
    def __init__(self, bg=None, radius=10, padding=None, **kw):
        kw.setdefault("orientation", "vertical")
        super().__init__(**kw)
        bg = bg if bg is not None else CARD
        self.padding = padding or [dp(14), dp(10)]
        self.spacing = dp(4)
        with self.canvas.before:
            Color(*bg)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._rect.pos  = self.pos
        self._rect.size = self.size


class NavBar(BoxLayout):
    TABS = [
        ("home",     "⌂",  "Home"),
        ("schedule", "◷",  "Sched"),
        ("exams",    "✎",  "Exams"),
        ("tasks",    "✓",  "Tasks"),
        ("grades",   "◈",  "Grades"),
        ("timer",    "◉",  "Timer"),
        ("weather",  "◌",  "Weather"),
    ]

    def __init__(self, switch_cb, **kw):
        super().__init__(orientation="horizontal",
                         size_hint_y=None, height=dp(58), spacing=0, **kw)
        self.switch_cb = switch_cb
        self._btns = {}
        with self.canvas.before:
            Color(*NAV_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            # top border line
            Color(*BORDER)
            self._line = Rectangle(pos=(self.x, self.top - dp(1)), size=(self.width, dp(1)))
        self.bind(pos=self._upd, size=self._upd)
        for tid, icon, label in self.TABS:
            btn = Button(
                text=f"{icon}\n{label}",
                font_size=dp(8),
                background_normal="",
                background_color=NAV_BG,
                color=MUTED,
                halign="center")
            btn.bind(on_press=lambda b, t=tid: self.switch_cb(t))
            self._btns[tid] = btn
            self.add_widget(btn)

    def _upd(self, *a):
        self._bg.pos   = self.pos
        self._bg.size  = self.size
        self._line.pos  = (self.x, self.top - dp(1))
        self._line.size = (self.width, dp(1))

    def set_active(self, tab):
        for tid, btn in self._btns.items():
            if tid == tab:
                btn.color            = ACCENT
                btn.background_color = CARD
            else:
                btn.color            = MUTED
                btn.background_color = NAV_BG


class TopBar(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", size_hint_y=None,
                         height=dp(72), padding=[dp(18), dp(10)], spacing=dp(0), **kw)
        with self.canvas.before:
            Color(*TOPBAR)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            # bottom accent line
            Color(*ACCENT)
            self._line = Rectangle(pos=(self.x, self.y), size=(self.width, dp(1)))
        self.bind(pos=self._upd, size=self._upd)
        now   = datetime.now()
        h     = now.hour
        greet = "GOOD MORNING" if h < 12 else "GOOD AFTERNOON" if h < 18 else "GOOD EVENING"
        from widgets.buttons import lbl
        self.add_widget(lbl(greet, size=8, bold=True, color=ACCENT,
                            size_hint_y=None, height=dp(14)))
        self.add_widget(lbl("Student Pack", size=22, bold=True, color=TEXT,
                            size_hint_y=None, height=dp(32)))
        self.add_widget(lbl(now.strftime("%A  ·  %B %d, %Y").upper(),
                            size=8, color=MUTED, size_hint_y=None, height=dp(14)))

    def _upd(self, *a):
        self._bg.pos   = self.pos
        self._bg.size  = self.size
        self._line.pos  = (self.x, self.y)
        self._line.size = (self.width, dp(1))


class BaseScreen(Screen):
    def __init__(self, app_ref, **kw):
        super().__init__(**kw)
        self.app = app_ref
        with self.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def class_card(self, time_, subj, room):
        from widgets.buttons import lbl
        col  = subject_color(subj)
        card = CardLayout(
            bg=CARD, radius=8, padding=[dp(14), dp(10)],
            size_hint_y=None, height=dp(66),
            orientation="vertical", spacing=dp(2))
        row = BoxLayout(size_hint_y=None, height=dp(22))
        row.add_widget(lbl(time_, size=9, color=MUTED, size_hint_x=None, width=dp(68)))
        row.add_widget(lbl(subj.upper(), size=11, bold=True, color=TEXT))
        with card.canvas.after:
            Color(*col)
            card._bar = RoundedRectangle(
                pos=(card.x, card.y),
                size=(dp(3), card.height),
                radius=[dp(2)])
        def _upd_bar(inst, *a):
            inst._bar.pos  = (inst.x, inst.y)
            inst._bar.size = (dp(3), inst.height)
        card.bind(pos=_upd_bar, size=_upd_bar)
        card.add_widget(row)
        card.add_widget(lbl(f"  {room}", size=9, color=MUTED,
                            size_hint_y=None, height=dp(16)))
        return card