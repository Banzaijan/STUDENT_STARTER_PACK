from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import datetime

from utils.colors import CARD, CARD2, ACCENT, TEXT, MUTED, RED, BLACK, DIM, BORDER
from utils.data import DEFAULT_SCHEDULE, save_data
from widgets.buttons import lbl, section_label, accent_btn, muted_btn, vstack, safe_popup
from widgets.cards import BaseScreen, CardLayout


class ScheduleScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.current_day = datetime.now().strftime("%A")
        root = BoxLayout(orientation="vertical", spacing=0)

        hdr = BoxLayout(size_hint_y=None, height=dp(48),
                        padding=[dp(16), dp(6)], spacing=dp(8))
        hdr.add_widget(lbl("SCHEDULE", size=11, bold=True, color=TEXT,
                           size_hint_y=None, height=dp(36)))
        add_btn = Button(
            text="+ ADD", font_size=dp(10), bold=True,
            size_hint=(None, None), size=(dp(72), dp(32)),
            background_normal="", background_color=ACCENT, color=BLACK)
        add_btn.bind(on_press=self._add_class_popup)
        hdr.add_widget(add_btn)
        root.add_widget(hdr)

        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_row = BoxLayout(size_hint_y=None, height=dp(38),
                            spacing=dp(4), padding=[dp(16), dp(2)])
        self._day_btns = {}
        for d in days:
            is_cur = (d == self.current_day)
            btn = Button(
                text=d[:3].upper(), font_size=dp(9), bold=True,
                size_hint_x=None, width=dp(42),
                background_normal="",
                background_color=ACCENT if is_cur else CARD2,
                color=BLACK if is_cur else MUTED)
            btn.bind(on_press=lambda b, day=d: self._load_day(day))
            self._day_btns[d] = btn
            day_row.add_widget(btn)
        root.add_widget(day_row)

        self.sched_scroll = ScrollView(do_scroll_x=False)
        self.sched_stack  = vstack(spacing=6)
        self.sched_scroll.add_widget(self.sched_stack)
        root.add_widget(self.sched_scroll)
        self._load_day(self.current_day)
        self.add_widget(root)

    def _load_day(self, day):
        self.current_day = day
        for d, btn in self._day_btns.items():
            is_cur = (d == day)
            btn.background_color = ACCENT if is_cur else CARD2
            btn.color            = BLACK  if is_cur else MUTED
        self.sched_stack.clear_widgets()
        schedule = self.app.data.get("schedule", {k: [list(i) for i in v] for k, v in DEFAULT_SCHEDULE.items()})
        classes  = schedule.get(day, [])
        if not classes:
            c = CardLayout(bg=CARD, radius=8, size_hint_y=None, height=dp(52))
            c.add_widget(lbl("No classes", color=MUTED, halign="center",
                             size_hint_y=None, height=dp(30)))
            self.sched_stack.add_widget(c)
        else:
            for i, item in enumerate(classes):
                self.sched_stack.add_widget(self._class_row(item, i))

    def _class_row(self, item, idx):
        row  = BoxLayout(size_hint_y=None, height=dp(66), spacing=dp(6))
        card = self.class_card(item[0], item[1], item[2])
        card.size_hint_x = 1
        del_btn = Button(
            text="✕", font_size=dp(14),
            size_hint=(None, None), size=(dp(40), dp(66)),
            background_normal="", background_color=CARD2, color=MUTED)
        del_btn.bind(on_press=lambda b, i=idx: self._delete_class(i))
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
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=[dp(18), dp(16)])
        with content.canvas.before:
            Color(*CARD)
            content._bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(12)])
        content.bind(pos=lambda i,v: setattr(i._bg,"pos",v),
                     size=lambda i,v: setattr(i._bg,"size",v))
        content.add_widget(lbl("NEW CLASS", size=11, bold=True, color=ACCENT,
                               halign="left", size_hint_y=None, height=dp(28)))
        fields = {}
        for label, key, ph in [("TIME","time","7:00 AM"),
                                ("SUBJECT","subject","Mathematics"),
                                ("ROOM","room","Room 204")]:
            content.add_widget(lbl(label, size=8, bold=True, color=MUTED,
                                   size_hint_y=None, height=dp(18)))
            ti = TextInput(hint_text=ph, multiline=False, font_size=dp(13),
                           background_color=CARD2, foreground_color=TEXT,
                           hint_text_color=MUTED, cursor_color=ACCENT,
                           size_hint_y=None, height=dp(40))
            content.add_widget(ti)
            fields[key] = ti
        popup = safe_popup(content, height=dp(370))

        def save(*a):
            t = fields["time"].text.strip()
            s = fields["subject"].text.strip()
            r = fields["room"].text.strip()
            if not t or not s or not r:
                return
            sched = self.app.data.get("schedule", {k: [list(i) for i in v] for k, v in DEFAULT_SCHEDULE.items()})
            sched.setdefault(self.current_day, []).append([t, s, r])
            self.app.data["schedule"] = sched
            save_data(self.app.data)
            popup.dismiss()
            Clock.schedule_once(lambda dt: self._load_day(self.current_day), 0.1)

        content.add_widget(accent_btn("SAVE", save, height=dp(44)))
        content.add_widget(muted_btn("CANCEL", lambda *a: popup.dismiss(), width=dp(110), height=dp(38)))
        popup.open()