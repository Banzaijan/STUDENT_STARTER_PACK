from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import datetime

from utils.colors import CARD, CARD2, ACCENT, ACCENT_DIM, TEXT, MUTED, DIM, BORDER, BLACK
from utils.data import DEFAULT_SCHEDULE, save_data
from widgets.buttons import (lbl, section_label, accent_btn, muted_btn,
                              add_btn, icon_btn, day_pill, vstack, safe_popup)
from widgets.cards import BaseScreen, CardLayout


class ScheduleScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.current_day = datetime.now().strftime("%A")
        root = BoxLayout(orientation="vertical", spacing=0)

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(64),
                        padding=[dp(20), dp(10)], spacing=dp(10))
        hdr.add_widget(lbl("Schedule", size=22, bold=True, color=TEXT,
                           size_hint_y=None, height=dp(44)))
        hdr.add_widget(add_btn(self._add_class_popup))
        root.add_widget(hdr)

        # Day selector
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_sv  = ScrollView(size_hint_y=None, height=dp(58), do_scroll_y=False)
        day_row = BoxLayout(size_hint_x=None, height=dp(58),
                            spacing=dp(8), padding=[dp(20), dp(8)])
        day_row.bind(minimum_width=day_row.setter("width"))
        self._day_btns = {}
        for d in days:
            is_cur = (d == self.current_day)
            # day_pill(text, active, on_press)
            btn = day_pill(d[:3], is_cur,
                           lambda b, day=d: self._load_day(day))
            self._day_btns[d] = btn
            day_row.add_widget(btn)
        day_sv.add_widget(day_row)
        root.add_widget(day_sv)

        # Classes list
        self.sched_scroll = ScrollView(do_scroll_x=False)
        self.sched_stack  = vstack(spacing=10)
        self.sched_scroll.add_widget(self.sched_stack)
        root.add_widget(self.sched_scroll)

        self._load_day(self.current_day)
        self.add_widget(root)

    def _load_day(self, day):
        self.current_day = day
        for d, btn in self._day_btns.items():
            is_cur = (d == day)
            btn.background_color = ACCENT if is_cur else DIM
            btn.color            = BLACK  if is_cur else MUTED
            btn.bold             = is_cur

        self.sched_stack.clear_widgets()
        schedule = self.app.data.get("schedule",
                   {k: [list(i) for i in v] for k, v in DEFAULT_SCHEDULE.items()})
        classes  = schedule.get(day, [])

        if not classes:
            c = CardLayout(bg=CARD, radius=16, size_hint_y=None, height=dp(72))
            c.add_widget(lbl("No classes today", color=MUTED,
                             halign="center", size_hint_y=None, height=dp(36)))
            self.sched_stack.add_widget(c)
        else:
            for i, item in enumerate(classes):
                self.sched_stack.add_widget(self._class_row(item, i))

    def _class_row(self, item, idx):
        row  = BoxLayout(size_hint_y=None, height=dp(88), spacing=dp(6))
        card = self.class_card(item[0], item[1], item[2])
        card.size_hint_x = 1
        del_btn = icon_btn("✕", lambda b, i=idx: self._delete_class(i),
                           size=dp(44), font_size=18)
        row.add_widget(card)
        row.add_widget(del_btn)
        return row

    def _delete_class(self, idx):
        sched   = self.app.data.get("schedule", {})
        classes = sched.get(self.current_day, [])
        if 0 <= idx < len(classes):
            classes.pop(idx)
            sched[self.current_day]   = classes
            self.app.data["schedule"] = sched
            save_data(self.app.data)
            Clock.schedule_once(lambda dt: self._load_day(self.current_day), 0)

    def _add_class_popup(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(12),
                            padding=[dp(24), dp(20)])
        with content.canvas.before:
            Color(*CARD)
            content._bg = RoundedRectangle(pos=content.pos, size=content.size,
                                           radius=[dp(20)])
        content.bind(pos=lambda i, v: setattr(i._bg, "pos",  v),
                     size=lambda i, v: setattr(i._bg, "size", v))
        content.add_widget(lbl("New Class", size=20, bold=True, color=TEXT,
                               halign="left", size_hint_y=None, height=dp(38)))
        fields = {}
        for label, key, ph in [("Time",    "time",    "7:00 AM"),
                                ("Subject", "subject", "Mathematics"),
                                ("Room",    "room",    "Room 204")]:
            content.add_widget(lbl(label, size=12, bold=True, color=MUTED,
                                   size_hint_y=None, height=dp(24)))
            ti = TextInput(hint_text=ph, multiline=False, font_size=dp(16),
                           background_color=CARD2, foreground_color=TEXT,
                           hint_text_color=DIM, cursor_color=ACCENT,
                           padding=[dp(14), dp(12)],
                           size_hint_y=None, height=dp(52))
            content.add_widget(ti)
            fields[key] = ti
        popup = safe_popup(content, height=dp(460))

        def save(*a):
            t = fields["time"].text.strip()
            s = fields["subject"].text.strip()
            r = fields["room"].text.strip()
            if not t or not s or not r:
                return
            sched = self.app.data.get("schedule",
                    {k: [list(i) for i in v] for k, v in DEFAULT_SCHEDULE.items()})
            sched.setdefault(self.current_day, []).append([t, s, r])
            self.app.data["schedule"] = sched
            save_data(self.app.data)
            popup.dismiss()
            Clock.schedule_once(lambda dt: self._load_day(self.current_day), 0.1)

        content.add_widget(accent_btn("Save", save, height=dp(54)))
        content.add_widget(muted_btn("Cancel", lambda *a: popup.dismiss(),
                                     width=dp(140), height=dp(46)))
        popup.open()