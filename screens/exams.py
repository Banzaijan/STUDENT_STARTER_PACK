from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

from utils.colors import CARD, CARD2, ACCENT, ACCENT_DIM, TEXT, MUTED, RED, BLACK, DIM
from utils.helpers import days_left
from utils.data import save_data
from widgets.buttons import lbl, accent_btn, muted_btn, vstack, safe_popup
from widgets.cards import BaseScreen, CardLayout


class ExamsScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=0)
        hdr  = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(16), dp(6)])
        hdr.add_widget(lbl("EXAMS & QUIZZES", size=11, bold=True, color=TEXT))
        add_btn = Button(
            text="+ ADD", font_size=dp(10), bold=True,
            size_hint=(None, None), size=(dp(72), dp(32)),
            background_normal="", background_color=ACCENT, color=BLACK)
        add_btn.bind(on_press=self._add_exam_popup)
        hdr.add_widget(add_btn)
        root.add_widget(hdr)
        self.exams_scroll = ScrollView(do_scroll_x=False)
        self.exams_stack  = vstack(spacing=6)
        self.exams_scroll.add_widget(self.exams_stack)
        root.add_widget(self.exams_scroll)
        self._render_exams()
        self.add_widget(root)

    def _render_exams(self):
        self.exams_stack.clear_widgets()
        for exam in sorted(self.app.data["exams"], key=lambda x: x["date"]):
            self.exams_stack.add_widget(self._exam_card(exam))

    def _exam_card(self, exam):
        dl       = days_left(exam["date"])
        dl_color = RED if dl == "Today!" else MUTED if dl == "Past" else ACCENT
        is_done  = exam["done"]

        card = CardLayout(
            bg=CARD, radius=8,
            padding=[dp(14), dp(10)],
            size_hint_y=None, height=dp(76),
            orientation="vertical", spacing=dp(4))

        row1 = BoxLayout(size_hint_y=None, height=dp(28))
        done_btn = Button(
            text="●" if is_done else "○",
            font_size=dp(16),
            size_hint=(None, None), size=(dp(32), dp(32)),
            background_normal="", background_color=(0,0,0,0),
            color=ACCENT if is_done else DIM)
        done_btn.bind(on_press=lambda b, eid=exam["id"]: self._toggle_exam(eid))
        row1.add_widget(done_btn)
        row1.add_widget(lbl(exam["subject"].upper(), size=12, bold=True,
                            color=MUTED if is_done else TEXT))
        row1.add_widget(lbl(dl, size=10, bold=True, color=dl_color,
                            halign="right", size_hint_x=None, width=dp(76)))
        card.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(20))
        row2.add_widget(lbl(f"  {exam['type']}", size=9, color=MUTED))
        row2.add_widget(lbl(exam["date"], size=9, color=DIM, halign="right"))
        card.add_widget(row2)

        card.add_widget(lbl(f"  {exam['notes']}", size=9, color=DIM,
                            size_hint_y=None, height=dp(16)))
        return card

    def _toggle_exam(self, eid):
        for e in self.app.data["exams"]:
            if e["id"] == eid:
                e["done"] = not e["done"]
        save_data(self.app.data)
        Clock.schedule_once(lambda dt: self._render_exams(), 0)

    def _add_exam_popup(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=[dp(18), dp(14)])
        with content.canvas.before:
            Color(*CARD)
            content._bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(12)])
        content.bind(pos=lambda i,v: setattr(i._bg,"pos",v),
                     size=lambda i,v: setattr(i._bg,"size",v))
        content.add_widget(lbl("NEW EXAM", size=11, bold=True, color=ACCENT,
                               halign="left", size_hint_y=None, height=dp(28)))
        fields = {}
        for label, key, ph in [("SUBJECT","subject","Mathematics"),
                                ("TYPE","type","Long Quiz"),
                                ("DATE","date","2026-03-20"),
                                ("NOTES","notes","Chapters 1-5")]:
            content.add_widget(lbl(label, size=8, bold=True, color=MUTED,
                                   size_hint_y=None, height=dp(18)))
            ti = TextInput(hint_text=ph, multiline=False, font_size=dp(13),
                           background_color=CARD2, foreground_color=TEXT,
                           hint_text_color=MUTED, cursor_color=ACCENT,
                           size_hint_y=None, height=dp(40))
            content.add_widget(ti)
            fields[key] = ti
        popup = safe_popup(content, height=dp(430))

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

        content.add_widget(accent_btn("SAVE", save, height=dp(44)))
        content.add_widget(muted_btn("CANCEL", lambda *a: popup.dismiss(), width=dp(110), height=dp(38)))
        popup.open()