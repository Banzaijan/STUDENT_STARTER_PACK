from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.animation import Animation
from datetime import datetime

from utils.colors import (BG, CARD, CARD2, ACCENT, ACCENT_DIM,
                           TEXT, MUTED, NAV_BG, TOPBAR, BLACK, DIM, BORDER)
from utils.helpers import subject_color


class CardLayout(BoxLayout):
    def __init__(self, bg=None, radius=16, padding=None, **kw):
        kw.setdefault("orientation", "vertical")
        super().__init__(**kw)
        bg = bg if bg is not None else CARD
        self.padding = padding or [dp(18), dp(14)]
        self.spacing = dp(6)
        with self.canvas.before:
            Color(*BORDER)
            self._shadow = RoundedRectangle(
                pos=(self.x - dp(0.5), self.y - dp(0.5)),
                size=(self.width + dp(1), self.height + dp(1)),
                radius=[dp(radius + 1)])
            Color(*bg)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(radius)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._shadow.pos  = (self.x - dp(0.5), self.y - dp(0.5))
        self._shadow.size = (self.width + dp(1), self.height + dp(1))
        self._rect.pos    = self.pos
        self._rect.size   = self.size


# ── Nav Tab Button — tap-only, ignores scroll ─────────────────────────────────
class NavTabButton(Button):
    def __init__(self, tab_id, switch_cb, label, **kw):
        self._tab_id      = tab_id
        self._switch      = switch_cb
        self._tstart      = None
        super().__init__(
            text=label,
            font_size=dp(11),
            bold=False,
            background_normal="",
            background_color=NAV_BG,
            color=MUTED,
            halign="center",
            **kw)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._tstart = (touch.x, touch.y)
            Animation.cancel_all(self, "opacity")
            Animation(opacity=0.5, duration=0.07, t="out_quad").start(self)
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and self._tstart:
            dx = abs(touch.x - self._tstart[0])
            dy = abs(touch.y - self._tstart[1])
            if dx > dp(10) or dy > dp(10):
                Animation.cancel_all(self, "opacity")
                Animation(opacity=1.0, duration=0.15).start(self)
                touch.ungrab(self)
                self._tstart = None
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            Animation.cancel_all(self, "opacity")
            Animation(opacity=1.0, duration=0.18, t="out_cubic").start(self)
            if self._tstart is not None:
                self._tstart = None
                self._switch(self._tab_id)
            return True
        return super().on_touch_up(touch)


# ── NavBar ────────────────────────────────────────────────────────────────────
class NavBar(BoxLayout):
    TABS = [
        ("home",     "HOME"),
        ("schedule", "SCHED"),
        ("exams",    "EXAMS"),
        ("tasks",    "TASKS"),
        ("grades",   "GRADES"),
        ("timer",    "TIMER"),
        ("weather",  "WEATHER"),
    ]

    def __init__(self, switch_cb, **kw):
        super().__init__(orientation="horizontal",
                         size_hint_y=None, height=dp(56),
                         spacing=0, **kw)
        self.switch_cb = switch_cb
        self._btns     = {}

        with self.canvas.before:
            Color(*NAV_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(*BORDER)
            self._line = Rectangle(pos=(self.x, self.top - dp(1)),
                                   size=(self.width, dp(1)))
        self.bind(pos=self._upd, size=self._upd)

        for tid, label in self.TABS:
            btn = NavTabButton(tab_id=tid, switch_cb=switch_cb, label=label)
            self._btns[tid] = btn
            self.add_widget(btn)

    def _upd(self, *a):
        self._bg.pos    = self.pos
        self._bg.size   = self.size
        self._line.pos  = (self.x, self.top - dp(1))
        self._line.size = (self.width, dp(1))

    def set_active(self, tab):
        for tid, btn in self._btns.items():
            if tid == tab:
                btn.color            = ACCENT
                btn.background_color = ACCENT_DIM
                btn.bold             = True
            else:
                btn.color            = MUTED
                btn.background_color = NAV_BG
                btn.bold             = False


# ── TopBar ────────────────────────────────────────────────────────────────────
class TopBar(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", size_hint_y=None,
                         height=dp(88), padding=[dp(22), dp(12)],
                         spacing=dp(2), **kw)
        with self.canvas.before:
            Color(*TOPBAR)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(*BORDER)
            self._line = Rectangle(pos=(self.x, self.y), size=(self.width, dp(1)))
        self.bind(pos=self._upd, size=self._upd)

        now   = datetime.now()
        h     = now.hour
        greet = "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"

        from widgets.buttons import lbl
        self._greet_lbl = lbl(greet, size=11, color=MUTED,
                               size_hint_y=None, height=dp(18))
        self._name_lbl  = lbl("Student Pack", size=24, bold=True, color=TEXT,
                               size_hint_y=None, height=dp(34))
        self._date_lbl  = lbl(now.strftime("%A, %B %d").upper(),
                               size=9, color=DIM, size_hint_y=None, height=dp(16))
        self.add_widget(self._greet_lbl)
        self.add_widget(self._name_lbl)
        self.add_widget(self._date_lbl)

    def update_user(self, name):
        """Called after login to personalise the TopBar."""
        now   = datetime.now()
        h     = now.hour
        greet = "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"
        if name:
            self._greet_lbl.text = greet + ","
            self._name_lbl.text  = name
        else:
            self._greet_lbl.text = greet
            self._name_lbl.text  = "Student Pack"

    def _upd(self, *a):
        self._bg.pos    = self.pos
        self._bg.size   = self.size
        self._line.pos  = (self.x, self.y)
        self._line.size = (self.width, dp(1))


# ── BaseScreen ────────────────────────────────────────────────────────────────
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
        card = CardLayout(bg=CARD, radius=14, padding=[dp(16), dp(12)],
                          size_hint_y=None, height=dp(82),
                          orientation="vertical", spacing=dp(4))
        row = BoxLayout(size_hint_y=None, height=dp(28))
        row.add_widget(lbl(time_, size=11, color=MUTED,
                           size_hint_x=None, width=dp(82)))
        row.add_widget(lbl(subj, size=14, bold=True, color=TEXT))
        with card.canvas.after:
            Color(*col)
            card._bar = RoundedRectangle(
                pos=(card.x + dp(2), card.y + dp(8)),
                size=(dp(4), card.height - dp(16)),
                radius=[dp(2)])
        def _upd_bar(inst, *a):
            inst._bar.pos  = (inst.x + dp(2), inst.y + dp(8))
            inst._bar.size = (dp(4), inst.height - dp(16))
        card.bind(pos=_upd_bar, size=_upd_bar)
        card.add_widget(row)
        card.add_widget(lbl(f"  {room}", size=11, color=MUTED,
                            size_hint_y=None, height=dp(20)))
        return card