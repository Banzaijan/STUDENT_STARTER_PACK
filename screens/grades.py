from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

from utils.colors import CARD, CARD2, ACCENT, TEXT, MUTED, BLACK, DIM
from utils.helpers import compute_gwa, grade_remark
from utils.data import save_data
from widgets.buttons import lbl, accent_btn, muted_btn, vstack, safe_popup
from widgets.cards import BaseScreen, CardLayout


class GradesScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=0)
        hdr  = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(16), dp(6)])
        hdr.add_widget(lbl("GRADES", size=11, bold=True, color=TEXT))
        add_btn = Button(
            text="+ ADD", font_size=dp(10), bold=True,
            size_hint=(None, None), size=(dp(72), dp(32)),
            background_normal="", background_color=ACCENT, color=BLACK)
        add_btn.bind(on_press=self._add_grade_popup)
        hdr.add_widget(add_btn)
        root.add_widget(hdr)
        self.grades_scroll = ScrollView(do_scroll_x=False)
        self.grades_stack  = vstack(spacing=6)
        self.grades_scroll.add_widget(self.grades_stack)
        root.add_widget(self.grades_scroll)
        self._render_grades()
        self.add_widget(root)

    def _render_grades(self):
        self.grades_stack.clear_widgets()
        grades = self.app.data.get("grades", [])

        if grades:
            avg = sum(compute_gwa(g["written"], g["performance"], g["exam"])
                      for g in grades) / len(grades)
            remark, rcol = grade_remark(avg)
            summary = CardLayout(bg=CARD2, radius=10, size_hint_y=None, height=dp(76),
                                 padding=[dp(16), dp(12)])
            top = BoxLayout(size_hint_y=None, height=dp(38))
            top.add_widget(lbl(f"{avg:.1f}", size=30, bold=True, color=ACCENT,
                               size_hint_x=None, width=dp(90)))
            info = BoxLayout(orientation="vertical")
            info.add_widget(lbl("OVERALL GWA", size=8, bold=True, color=MUTED,
                                size_hint_y=None, height=dp(16)))
            info.add_widget(lbl(remark.upper(), size=10, bold=True, color=rcol,
                                size_hint_y=None, height=dp(20)))
            top.add_widget(info)
            summary.add_widget(top)
            self.grades_stack.add_widget(summary)

        # column header
        hdr = BoxLayout(size_hint_y=None, height=dp(22), padding=[dp(14), 0])
        hdr.add_widget(lbl("SUBJECT", size=8, bold=True, color=MUTED,
                           size_hint_x=1, halign="left"))
        for t in ["WW", "PT", "QE", "FINAL"]:
            hdr.add_widget(lbl(t, size=8, bold=True, color=MUTED,
                               size_hint_x=None, width=dp(46), halign="center"))
        self.grades_stack.add_widget(hdr)

        for g in grades:
            self.grades_stack.add_widget(self._grade_card(g))

    def _grade_card(self, g):
        final_val  = compute_gwa(g["written"], g["performance"], g["exam"])
        remark, rc = grade_remark(final_val)
        card = CardLayout(bg=CARD, radius=8, padding=[dp(14), dp(8)],
                          size_hint_y=None, height=dp(62),
                          orientation="vertical", spacing=dp(4))

        row1 = BoxLayout(size_hint_y=None, height=dp(22))
        row1.add_widget(lbl(g["subject"].upper(), size=11, bold=True, color=TEXT))
        for val in [g["written"], g["performance"], g["exam"]]:
            row1.add_widget(lbl(str(val), size=11, color=MUTED,
                                halign="center", size_hint_x=None, width=dp(46)))
        row1.add_widget(lbl(f"{final_val:.1f}", size=11, bold=True, color=ACCENT,
                            halign="center", size_hint_x=None, width=dp(46)))
        card.add_widget(row1)

        # progress bar row
        pb_row = BoxLayout(size_hint_y=None, height=dp(16), spacing=dp(8))
        pb_row.add_widget(lbl(remark.upper(), size=7, bold=True, color=rc,
                              size_hint_x=None, width=dp(110)))
        pb_bg = Widget()
        with pb_bg.canvas:
            Color(*CARD2)
            pb_bg._bg_rect = RoundedRectangle(pos=pb_bg.pos, size=pb_bg.size, radius=[dp(2)])
            Color(*rc)
            pb_bg._fill = RoundedRectangle(
                pos=pb_bg.pos,
                size=(pb_bg.width * min(final_val / 100.0, 1.0), pb_bg.height),
                radius=[dp(2)])
        def _upd_pb(inst, *a, fv=final_val):
            inst._bg_rect.pos  = inst.pos
            inst._bg_rect.size = inst.size
            inst._fill.pos     = inst.pos
            inst._fill.size    = (inst.width * min(fv / 100.0, 1.0), inst.height)
        pb_bg.bind(pos=_upd_pb, size=_upd_pb)
        pb_row.add_widget(pb_bg)

        del_btn = Button(
            text="✕", font_size=dp(13),
            size_hint=(None, None), size=(dp(28), dp(28)),
            background_normal="", background_color=(0,0,0,0), color=MUTED)
        del_btn.bind(on_press=lambda b, gid=g["id"]: self._delete_grade(gid))
        pb_row.add_widget(del_btn)
        card.add_widget(pb_row)
        return card

    def _delete_grade(self, gid):
        self.app.data["grades"] = [g for g in self.app.data["grades"] if g["id"] != gid]
        save_data(self.app.data)
        Clock.schedule_once(lambda dt: self._render_grades(), 0)

    def _add_grade_popup(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=[dp(18), dp(14)])
        with content.canvas.before:
            Color(*CARD)
            content._bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(12)])
        content.bind(pos=lambda i,v: setattr(i._bg,"pos",v),
                     size=lambda i,v: setattr(i._bg,"size",v))
        content.add_widget(lbl("ADD GRADES", size=11, bold=True, color=ACCENT,
                               halign="left", size_hint_y=None, height=dp(28)))
        content.add_widget(lbl("WW 25%  +  PT 50%  +  QE 25%", size=8, color=MUTED,
                               size_hint_y=None, height=dp(16)))
        fields = {}
        for label, key, ph in [("SUBJECT","subject","Mathematics"),
                                ("WRITTEN WORKS (25%)","written","88"),
                                ("PERFORMANCE TASKS (50%)","performance","90"),
                                ("QUARTERLY EXAM (25%)","exam","85")]:
            content.add_widget(lbl(label, size=8, bold=True, color=MUTED,
                                   size_hint_y=None, height=dp(18)))
            ti = TextInput(hint_text=ph, multiline=False, font_size=dp(13),
                           background_color=CARD2, foreground_color=TEXT,
                           hint_text_color=MUTED, cursor_color=ACCENT,
                           input_filter="float" if key != "subject" else None,
                           size_hint_y=None, height=dp(40))
            content.add_widget(ti)
            fields[key] = ti
        popup = safe_popup(content, height=dp(450))

        def save(*a):
            subj = fields["subject"].text.strip()
            if not subj:
                return
            try:
                w = float(fields["written"].text or 0)
                p = float(fields["performance"].text or 0)
                e = float(fields["exam"].text or 0)
            except Exception:
                return
            self.app.data["grades"].append({
                "id":          max((g["id"] for g in self.app.data["grades"]), default=0) + 1,
                "subject":     subj,
                "written":     w,
                "performance": p,
                "exam":        e,
            })
            save_data(self.app.data)
            popup.dismiss()
            Clock.schedule_once(lambda dt: self._render_grades(), 0.1)

        content.add_widget(accent_btn("SAVE", save, height=dp(44)))
        content.add_widget(muted_btn("CANCEL", lambda *a: popup.dismiss(), width=dp(110), height=dp(38)))
        popup.open()