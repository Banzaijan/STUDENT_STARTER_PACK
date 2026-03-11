from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp

from utils.colors import CARD, CARD2, ACCENT, TEXT, MUTED, BLACK, DIM


def lbl(text, size=13, color=None, bold=False, halign="left", **kw):
    color = color if color is not None else TEXT
    l = Label(text=text, font_size=dp(size), color=color,
              bold=bold, halign=halign, **kw)
    l.bind(size=lambda inst, v: setattr(inst, "text_size", (v[0], None)))
    return l


def accent_btn(text, on_press, height=dp(46), font_size=13):
    btn = Button(
        text=text, font_size=dp(font_size), bold=True,
        size_hint_y=None, height=height,
        background_normal="", background_color=ACCENT,
        color=BLACK)
    btn.bind(on_press=on_press)
    return btn


def muted_btn(text, on_press, width=dp(90), height=dp(38)):
    btn = Button(
        text=text, font_size=dp(11),
        size_hint=(None, None), size=(width, height),
        background_normal="", background_color=DIM,
        color=MUTED)
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


def safe_popup(content, height=dp(420)):
    return Popup(
        title="", content=content,
        size_hint=(0.95, None), height=height,
        background="", background_color=(0, 0, 0, 0),
        separator_height=0, auto_dismiss=True)