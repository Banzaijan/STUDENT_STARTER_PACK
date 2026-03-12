from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

from utils.colors import CARD, CARD2, ACCENT, ACCENT_DIM, TEXT, MUTED, BLACK, DIM, RED, GREEN
from utils.helpers import days_left
from utils.data import save_data
from widgets.buttons import lbl, accent_btn, muted_btn, add_btn, icon_btn, check_btn, vstack, safe_popup
from widgets.cards import BaseScreen, CardLayout


class ExamsScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=0)

        hdr = BoxLayout(size_hint_y=None, height=dp(64),
                        padding=[dp(20), dp(10)], spacing=dp(10))
        hdr.add_widget(lbl("Exams & Quizzes", size=22, bold=True, color=TEXT,
                           size_hint_y=None, height=dp(44)))
        hdr.add_widget(add_btn(self._add_exam_popup))
        root.add_widget(hdr)

        self.exams_scroll = ScrollView(do_scroll_x=False)
        self.exams_stack  = vstack(spacing=10)
        self.exams_scroll.add_widget(self.exams_stack)
        root.add_widget(self.exams_scroll)
        self._render_exams()
        self.add_widget(root)

    def _render_exams(self):
        self.exams_stack.clear_widgets()
        exams   = sorted(self.app.data["exams"], key=lambda x: x["date"])
        pending = [e for e in exams if not e["done"]]
        done    = [e for e in exams if e["done"]]

        if pending:
            self.exams_stack.add_widget(
                lbl("UPCOMING", size=11, bold=True, color=MUTED,
                    size_hint_y=None, height=dp(32)))
            for exam in pending:
                self.exams_stack.add_widget(self._exam_card(exam))
        if done:
            self.exams_stack.add_widget(
                lbl("COMPLETED", size=11, bold=True, color=MUTED,
                    size_hint_y=None, height=dp(32)))
            for exam in done:
                self.exams_stack.add_widget(self._exam_card(exam))

    def _exam_card(self, exam):
        dl       = days_left(exam["date"])
        is_done  = exam["done"]
        dl_color = GREEN if is_done else (RED if dl == "Today!" else (DIM if dl == "Past" else ACCENT))

        card = CardLayout(bg=CARD, radius=16, padding=[dp(18), dp(14)],
                          size_hint_y=None, height=dp(96),
                          orientation="vertical", spacing=dp(8))

        row1 = BoxLayout(size_hint_y=None, height=dp(34))
        row1.add_widget(check_btn(is_done,
                                  lambda b, eid=exam["id"]: self._toggle_exam(eid),
                                  size=dp(32)))
        row1.add_widget(BoxLayout(size_hint_x=None, width=dp(10)))
        row1.add_widget(lbl(exam["subject"], size=15, bold=True,
                            color=DIM if is_done else TEXT))
        row1.add_widget(lbl(dl, size=12, bold=True, color=dl_color,
                            halign="right", size_hint_x=None, width=dp(90)))
        card.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(22))
        row2.add_widget(lbl(f"  {exam['type']}", size=12, color=MUTED))
        row2.add_widget(lbl(exam["date"], size=11, color=DIM, halign="right"))
        card.add_widget(row2)

        if exam.get("notes"):
            card.add_widget(lbl(f"  {exam['notes']}", size=11, color=DIM,
                                size_hint_y=None, height=dp(20)))
        return card

    def _toggle_exam(self, eid):
        for e in self.app.data["exams"]:
            if e["id"] == eid:
                e["done"] = not e["done"]
        save_data(self.app.data)
        Clock.schedule_once(lambda dt: self._render_exams(), 0)

    def _add_exam_popup(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(12),
                            padding=[dp(24), dp(20)])
        with content.canvas.before:
            Color(*CARD)
            content._bg = RoundedRectangle(pos=content.pos, size=content.size,
                                           radius=[dp(20)])
        content.bind(pos=lambda i,v: setattr(i._bg,"pos",v),
                     size=lambda i,v: setattr(i._bg,"size",v))
        content.add_widget(lbl("New Exam", size=20, bold=True, color=TEXT,
                               halign="left", size_hint_y=None, height=dp(38)))
        fields = {}
        for label, key, ph in [("Subject","subject","Mathematics"),
                                ("Type","type","Long Quiz"),
                                ("Date (YYYY-MM-DD)","date","2026-03-20"),
                                ("Notes","notes","Chapters 1–5")]:
            content.add_widget(lbl(label, size=12, bold=True, color=MUTED,
                                   size_hint_y=None, height=dp(24)))
            ti = TextInput(hint_text=ph, multiline=False, font_size=dp(16),
                           background_color=CARD2, foreground_color=TEXT,
                           hint_text_color=DIM, cursor_color=ACCENT,
                           padding=[dp(14), dp(12)],
                           size_hint_y=None, height=dp(52))
            content.add_widget(ti)
            fields[key] = ti
        popup = safe_popup(content, height=dp(520))

        def save(*a):
            new = {k: fields[k].text.strip() for k in fields}
            if not new["subject"] or not new["date"]:
                return
            new["id"]   = max((e["id"] for e in self.app.data["exams"]), default=0) + 1
            new["done"] = False
            self.app.data["exams"].append(new)
            save_data(self.app.data)
            popup.dismiss()
            Clock.schedule_once(lambda dt: self._render_exams(), 0.1)

        content.add_widget(accent_btn("Save", save, height=dp(54)))
        content.add_widget(muted_btn("Cancel", lambda *a: popup.dismiss(),
                                     width=dp(140), height=dp(46)))
        popup.open()