from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.metrics import dp
from kivy.clock import Clock

from utils.colors import CARD, CARD2, ACCENT, ACCENT2, TEXT, MUTED, GREEN, BLACK, DIM
from widgets.buttons import lbl, section_label
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

        hdr = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(16), dp(6)])
        hdr.add_widget(lbl("POMODORO", size=11, bold=True, color=TEXT))
        root.add_widget(hdr)

        self._session_lbl = lbl("0 sessions", size=9, bold=True, color=MUTED,
                                 halign="center", size_hint_y=None, height=dp(22))
        root.add_widget(self._session_lbl)

        self._mode_lbl = lbl("FOCUS", size=10, bold=True, color=ACCENT,
                              halign="center", size_hint_y=None, height=dp(22))
        root.add_widget(self._mode_lbl)

        # big timer display
        timer_card = CardLayout(bg=CARD, radius=10,
                                size_hint_y=None, height=dp(160),
                                padding=[dp(10), dp(20)])
        self._timer_lbl = lbl("25:00", size=56, bold=True, color=TEXT,
                               halign="center", size_hint_y=None, height=dp(80))
        timer_card.add_widget(self._timer_lbl)

        self._pb_total  = self.WORK_MINS * 60
        self._pb_widget = Widget(size_hint_y=None, height=dp(4))
        with self._pb_widget.canvas:
            Color(*CARD2)
            self._pb_widget._bg   = RoundedRectangle(
                pos=self._pb_widget.pos, size=self._pb_widget.size, radius=[dp(2)])
            Color(*ACCENT)
            self._pb_widget._fill = RoundedRectangle(
                pos=self._pb_widget.pos, size=self._pb_widget.size, radius=[dp(2)])
        self._pb_widget.bind(pos=self._update_pb, size=self._update_pb)
        timer_card.add_widget(self._pb_widget)
        root.add_widget(timer_card)

        # buttons
        btn_row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8),
                            padding=[dp(16), dp(6)])
        self._start_btn = Button(
            text="START", font_size=dp(13), bold=True,
            background_normal="", background_color=ACCENT, color=BLACK)
        self._start_btn.bind(on_press=self._toggle_timer)
        btn_row.add_widget(self._start_btn)
        reset_btn = Button(
            text="RESET", font_size=dp(12), bold=True,
            size_hint_x=None, width=dp(90),
            background_normal="", background_color=CARD2, color=MUTED)
        reset_btn.bind(on_press=self._reset_timer)
        btn_row.add_widget(reset_btn)
        root.add_widget(btn_row)

        # duration config
        dur_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8),
                            padding=[dp(16), dp(2)])
        dur_row.add_widget(lbl("WORK", size=8, bold=True, color=MUTED,
                               size_hint_x=None, width=dp(46)))
        self._work_input = TextInput(
            text=str(self.WORK_MINS), multiline=False,
            font_size=dp(13), input_filter="int",
            background_color=CARD2, foreground_color=TEXT,
            cursor_color=ACCENT, size_hint_x=None, width=dp(52))
        dur_row.add_widget(self._work_input)
        dur_row.add_widget(lbl("BREAK", size=8, bold=True, color=MUTED,
                               size_hint_x=None, width=dp(46)))
        self._break_input = TextInput(
            text=str(self.BREAK_MINS), multiline=False,
            font_size=dp(13), input_filter="int",
            background_color=CARD2, foreground_color=TEXT,
            cursor_color=ACCENT, size_hint_x=None, width=dp(52))
        dur_row.add_widget(self._break_input)
        set_btn = Button(
            text="SET", font_size=dp(10), bold=True,
            size_hint_x=None, width=dp(52),
            background_normal="", background_color=CARD2, color=ACCENT)
        set_btn.bind(on_press=self._reset_timer)
        dur_row.add_widget(set_btn)
        root.add_widget(dur_row)

        tip = CardLayout(bg=CARD, radius=8, size_hint_y=None, height=dp(70),
                         padding=[dp(16), dp(10)])
        tip.add_widget(lbl("25 min focus  →  5 min break  →  repeat",
                           size=10, color=MUTED, halign="center",
                           size_hint_y=None, height=dp(22)))
        tip.add_widget(lbl("After 4 sessions, take a 15–30 min long break.",
                           size=9, color=DIM, halign="center",
                           size_hint_y=None, height=dp(18)))
        root.add_widget(tip)
        self.add_widget(root)

    def _update_pb(self, inst=None, *a):
        w     = self._pb_widget
        ratio = self._seconds / self._pb_total if self._pb_total else 1.0
        w._bg.pos    = w.pos
        w._bg.size   = w.size
        w._fill.pos  = w.pos
        w._fill.size = (w.width * ratio, w.height)

    def _toggle_timer(self, *a):
        if self._running:
            self._running = False
            if self._timer_event:
                self._timer_event.cancel()
                self._timer_event = None
            self._start_btn.text             = "RESUME"
            self._start_btn.background_color = ACCENT
        else:
            self._running = True
            self._start_btn.text             = "PAUSE"
            self._start_btn.background_color = CARD2
            self._start_btn.color            = ACCENT
            self._timer_event = Clock.schedule_interval(self._tick, 1)

    def _tick(self, dt):
        if self._seconds > 0:
            self._seconds -= 1
            self._update_display()
        else:
            if self._timer_event:
                self._timer_event.cancel()
                self._timer_event = None
            self._running = False
            if not self._is_break:
                self._sessions += 1
                self._session_lbl.text  = f"{self._sessions} sessions"
                self._is_break          = True
                self._seconds           = int(self._break_input.text or 5) * 60
                self._pb_total          = self._seconds
                self._mode_lbl.text     = "BREAK"
                self._mode_lbl.color    = GREEN
            else:
                self._is_break          = False
                self._seconds           = int(self._work_input.text or 25) * 60
                self._pb_total          = self._seconds
                self._mode_lbl.text     = "FOCUS"
                self._mode_lbl.color    = ACCENT
            self._start_btn.text             = "START"
            self._start_btn.background_color = ACCENT
            self._start_btn.color            = BLACK
            self._update_display()

    def _update_display(self):
        m, s = divmod(self._seconds, 60)
        self._timer_lbl.text = f"{m:02d}:{s:02d}"
        self._update_pb()

    def _reset_timer(self, *a):
        if self._timer_event:
            self._timer_event.cancel()
            self._timer_event = None
        self._running           = False
        self._is_break          = False
        self._seconds           = int(self._work_input.text or 25) * 60
        self._pb_total          = self._seconds
        self._mode_lbl.text     = "FOCUS"
        self._mode_lbl.color    = ACCENT
        self._start_btn.text             = "START"
        self._start_btn.background_color = ACCENT
        self._start_btn.color            = BLACK
        self._update_display()

    def on_leave(self):
        if self._timer_event:
            self._timer_event.cancel()
            self._timer_event = None
        self._running = False