from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

from utils.colors import CARD, CARD2, ACCENT, ACCENT_DIM, TEXT, MUTED, GREEN, BLACK, DIM
from widgets.buttons import lbl, AnimatedButton
from widgets.cards import BaseScreen, CardLayout


class TimerScreen(BaseScreen):
    WORK_MINS  = 25
    BREAK_MINS = 5

    def on_enter(self):
        self.clear_widgets()
        self._timer_event = None
        self._seconds     = self.WORK_MINS * 60
        self._running     = False
        self._is_break    = False
        self._sessions    = 0

        root = BoxLayout(orientation="vertical", spacing=0)

        hdr = BoxLayout(size_hint_y=None, height=dp(64), padding=[dp(20), dp(10)])
        hdr.add_widget(lbl("Pomodoro Timer", size=22, bold=True, color=TEXT,
                           size_hint_y=None, height=dp(44)))
        root.add_widget(hdr)

        mode_row = BoxLayout(size_hint_y=None, height=dp(38),
                             padding=[dp(20), dp(4)], spacing=dp(12))
        self._mode_lbl = lbl("FOCUS", size=13, bold=True, color=ACCENT,
                              halign="left", size_hint_y=None, height=dp(28))
        self._session_lbl = lbl("0 sessions", size=12, color=MUTED,
                                 halign="right", size_hint_y=None, height=dp(28))
        mode_row.add_widget(self._mode_lbl)
        mode_row.add_widget(self._session_lbl)
        root.add_widget(mode_row)

        # ── big timer card ────────────────────────────────────────────────────
        timer_card = CardLayout(bg=CARD, radius=22,
                                size_hint_y=None, height=dp(210),
                                padding=[dp(20), dp(28)],
                                orientation="vertical", spacing=dp(14))
        self._timer_lbl = lbl("25:00", size=72, bold=True, color=TEXT,
                               halign="center", size_hint_y=None, height=dp(100))
        timer_card.add_widget(self._timer_lbl)

        self._pb_total  = self.WORK_MINS * 60
        self._pb_widget = Widget(size_hint_y=None, height=dp(8))
        with self._pb_widget.canvas:
            Color(*CARD2)
            self._pb_widget._bg   = RoundedRectangle(
                pos=self._pb_widget.pos, size=self._pb_widget.size, radius=[dp(4)])
            Color(*ACCENT)
            self._pb_widget._fill = RoundedRectangle(
                pos=self._pb_widget.pos, size=self._pb_widget.size, radius=[dp(4)])
        self._pb_widget.bind(pos=self._update_pb, size=self._update_pb)
        timer_card.add_widget(self._pb_widget)
        root.add_widget(timer_card)

        # ── buttons ───────────────────────────────────────────────────────────
        btn_row = BoxLayout(size_hint_y=None, height=dp(68),
                            spacing=dp(12), padding=[dp(20), dp(10)])
        self._start_btn = AnimatedButton(
            text="Start", font_size=dp(16), bold=True,
            background_normal="", background_color=ACCENT, color=BLACK,
            scale=0.95, darken=0.82)
        self._start_btn.bind(on_press=self._toggle_timer)
        btn_row.add_widget(self._start_btn)
        reset_btn = AnimatedButton(
            text="Reset", font_size=dp(14),
            size_hint_x=None, width=dp(110),
            background_normal="", background_color=CARD2, color=MUTED,
            scale=0.93, darken=0.90)
        reset_btn.bind(on_press=self._reset_timer)
        btn_row.add_widget(reset_btn)
        root.add_widget(btn_row)

        # ── duration config ───────────────────────────────────────────────────
        dur_card = CardLayout(bg=CARD, radius=16, size_hint_y=None, height=dp(70),
                              padding=[dp(20), dp(12)], orientation="horizontal",
                              spacing=dp(12))
        dur_card.add_widget(lbl("Work", size=12, bold=True, color=MUTED,
                                size_hint_x=None, width=dp(46)))
        self._work_input = TextInput(
            text=str(self.WORK_MINS), multiline=False,
            font_size=dp(16), input_filter="int",
            background_color=CARD2, foreground_color=TEXT,
            cursor_color=ACCENT, size_hint_x=None, width=dp(62),
            padding=[dp(12), dp(10)])
        dur_card.add_widget(self._work_input)
        dur_card.add_widget(lbl("Break", size=12, bold=True, color=MUTED,
                                size_hint_x=None, width=dp(52)))
        self._break_input = TextInput(
            text=str(self.BREAK_MINS), multiline=False,
            font_size=dp(16), input_filter="int",
            background_color=CARD2, foreground_color=TEXT,
            cursor_color=ACCENT, size_hint_x=None, width=dp(62),
            padding=[dp(12), dp(10)])
        dur_card.add_widget(self._break_input)
        set_btn = AnimatedButton(
            text="Set", font_size=dp(13), bold=True,
            size_hint_x=None, width=dp(60),
            background_normal="", background_color=ACCENT_DIM, color=ACCENT,
            scale=0.90, darken=0.88)
        set_btn.bind(on_press=self._reset_timer)
        dur_card.add_widget(set_btn)
        root.add_widget(dur_card)

        tip = CardLayout(bg=CARD, radius=16, size_hint_y=None, height=dp(72),
                         padding=[dp(20), dp(14)])
        tip.add_widget(lbl("25 min focus  →  5 min break  →  repeat",
                           size=12, color=MUTED, halign="center",
                           size_hint_y=None, height=dp(24)))
        tip.add_widget(lbl("After 4 sessions, take a long 15–30 min break.",
                           size=11, color=DIM, halign="center",
                           size_hint_y=None, height=dp(22)))
        root.add_widget(tip)
        self.add_widget(root)

    def _update_pb(self, inst=None, *a):
        w     = self._pb_widget
        ratio = self._seconds / self._pb_total if self._pb_total else 1.0
        w._bg.pos    = w.pos;   w._bg.size   = w.size
        w._fill.pos  = w.pos;   w._fill.size = (w.width * ratio, w.height)

    def _toggle_timer(self, *a):
        if self._running:
            self._running = False
            if self._timer_event:
                self._timer_event.cancel(); self._timer_event = None
            self._start_btn.text             = "Resume"
            self._start_btn.background_color = ACCENT
            self._start_btn.color            = BLACK
        else:
            self._running = True
            self._start_btn.text             = "Pause"
            self._start_btn.background_color = CARD2
            self._start_btn.color            = ACCENT
            self._timer_event = Clock.schedule_interval(self._tick, 1)

    def _tick(self, dt):
        if self._seconds > 0:
            self._seconds -= 1
            self._update_display()
        else:
            if self._timer_event:
                self._timer_event.cancel(); self._timer_event = None
            self._running = False
            if not self._is_break:
                self._sessions += 1
                self._session_lbl.text = f"{self._sessions} session{'s' if self._sessions != 1 else ''}"
                self._is_break         = True
                self._seconds          = int(self._break_input.text or 5) * 60
                self._pb_total         = self._seconds
                self._mode_lbl.text    = "BREAK"
                self._mode_lbl.color   = GREEN
            else:
                self._is_break         = False
                self._seconds          = int(self._work_input.text or 25) * 60
                self._pb_total         = self._seconds
                self._mode_lbl.text    = "FOCUS"
                self._mode_lbl.color   = ACCENT
            self._start_btn.text             = "Start"
            self._start_btn.background_color = ACCENT
            self._start_btn.color            = BLACK
            self._update_display()

    def _update_display(self):
        m, s = divmod(self._seconds, 60)
        self._timer_lbl.text = f"{m:02d}:{s:02d}"
        self._update_pb()

    def _reset_timer(self, *a):
        if self._timer_event:
            self._timer_event.cancel(); self._timer_event = None
        self._running          = False
        self._is_break         = False
        self._seconds          = int(self._work_input.text or 25) * 60
        self._pb_total         = self._seconds
        self._mode_lbl.text    = "FOCUS"
        self._mode_lbl.color   = ACCENT
        self._start_btn.text             = "Start"
        self._start_btn.background_color = ACCENT
        self._start_btn.color            = BLACK
        self._update_display()

    def on_leave(self):
        if self._timer_event:
            self._timer_event.cancel(); self._timer_event = None
        self._running = False