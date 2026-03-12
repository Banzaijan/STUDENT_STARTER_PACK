from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.animation import Animation

from utils.colors import CARD, CARD2, ACCENT, TEXT, MUTED, BLACK, DIM, BORDER


# ── Label helper ──────────────────────────────────────────────────────────────
def lbl(text, size=14, color=None, bold=False, halign="left", **kw):
    color = color if color is not None else TEXT
    l = Label(text=text, font_size=dp(size), color=color,
              bold=bold, halign=halign, **kw)
    l.bind(size=lambda inst, v: setattr(inst, "text_size", (v[0], None)))
    return l


# ── Tap-safe animation — won't fire on scroll ─────────────────────────────────
class _TapButton(Button):
    """Button that only fires on_press if it was a real tap, not a scroll."""
    _floor = 0.5

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._tstart = (touch.x, touch.y)
            Animation.cancel_all(self, "opacity")
            Animation(opacity=self._floor, duration=0.07, t="out_quad").start(self)
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and hasattr(self, "_tstart"):
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
            if getattr(self, "_tstart", None) is not None:
                self._tstart = None
                # dispatch on_press manually
                self.dispatch("on_press")
            return True
        return super().on_touch_up(touch)


# ── AnimatedButton (drop-in, strips invalid kwargs) ───────────────────────────
class AnimatedButton(_TapButton):
    _floor = 0.45

    def __init__(self, callback=None, **kwargs):
        kwargs.pop("scale",  None)
        kwargs.pop("darken", None)
        super().__init__(**kwargs)
        if callback:
            self.bind(on_press=callback)


# ── Button factories ──────────────────────────────────────────────────────────
def accent_btn(text, on_press, height=dp(54), font_size=15):
    btn = _TapButton(
        text=text, font_size=dp(font_size), bold=True,
        size_hint_y=None, height=height,
        background_normal="", background_color=ACCENT,
        color=BLACK)
    btn.bind(on_press=on_press)
    return btn


def muted_btn(text, on_press, width=dp(120), height=dp(46)):
    btn = _TapButton(
        text=text, font_size=dp(13),
        size_hint=(None, None), size=(width, height),
        background_normal="", background_color=DIM,
        color=MUTED)
    btn.bind(on_press=on_press)
    return btn


def add_btn(on_press, height=dp(42), width=dp(100)):
    btn = _TapButton(
        text="+ Add", font_size=dp(14), bold=True,
        size_hint=(None, None), size=(width, height),
        background_normal="", background_color=ACCENT,
        color=BLACK)
    btn.bind(on_press=on_press)
    return btn


def icon_btn(text, on_press, color=MUTED, bg=DIM, size=dp(40), font_size=16):
    btn = _TapButton(
        text=text, font_size=dp(font_size),
        size_hint=(None, None), size=(size, size),
        background_normal="", background_color=bg,
        color=color)
    btn._floor = 0.35
    btn.bind(on_press=on_press)
    return btn


def check_btn(done, on_press, size=dp(36)):
    bg   = ACCENT if done else DIM
    text = "✓"    if done else ""
    btn  = _TapButton(
        text=text, font_size=dp(18), bold=True,
        size_hint=(None, None), size=(size, size),
        background_normal="", background_color=bg,
        color=BLACK if done else MUTED)
    btn._floor = 0.4
    btn.bind(on_press=on_press)
    return btn


def day_pill(text, active, on_press, width=dp(52), height=dp(38)):
    bg = ACCENT if active else DIM
    fg = BLACK  if active else MUTED
    btn = _TapButton(
        text=text, font_size=dp(13), bold=active,
        size_hint=(None, None), size=(width, height),
        background_normal="", background_color=bg,
        color=fg)
    btn.bind(on_press=on_press)
    return btn


def section_label(text):
    return lbl(text, size=11, bold=True, color=MUTED,
               size_hint_y=None, height=dp(34))


def scrollable(content_widget):
    sv = ScrollView(size_hint=(1, 1), do_scroll_x=False)
    sv.add_widget(content_widget)
    return sv


def vstack(spacing=8, padding=None):
    bl = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(spacing))
    bl.padding = [dp(x) for x in (padding or [16, 8, 16, 20])]
    bl.bind(minimum_height=bl.setter("height"))
    return bl


def safe_popup(content, height=dp(460)):
    return Popup(
        title="", content=content,
        size_hint=(0.95, None), height=height,
        background="", background_color=(0, 0, 0, 0),
        separator_height=0, auto_dismiss=True)