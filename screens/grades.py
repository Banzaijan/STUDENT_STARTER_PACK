from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

from utils.colors import CARD, CARD2, ACCENT, ACCENT_DIM, TEXT, MUTED, BLACK, DIM
from utils.helpers import compute_gwa, grade_remark
from utils.data import save_data
from widgets.buttons import lbl, accent_btn, muted_btn, add_btn, icon_btn, vstack, safe_popup
from widgets.cards import BaseScreen, CardLayout


class GradesScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=0)
        hdr  = BoxLayout(size_hint_y=None, height=dp(64),
                         padding=[dp(20), dp(10)], spacing=dp(10))
        hdr.add_widget(lbl("Grades", size=22, bold=True, color=TEXT,
                           size_hint_y=None, height=dp(44)))
        hdr.add_widget(add_btn(self._add_grade_popup))
        root.add_widget(hdr)
        self.grades_scroll = ScrollView(do_scroll_x=False)
        self.grades_stack  = vstack(spacing=10)
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
            summary = CardLayout(bg=ACCENT_DIM, radius=18,
                                 size_hint_y=None, height=dp(100),
                                 padding=[dp(22), dp(18)])
            top = BoxLayout(size_hint_y=None, height=dp(56))
            top.add_widget(lbl(f"{avg:.1f}", size=42, bold=True, color=ACCENT,
                               size_hint_x=None, width=dp(120)))
            info = BoxLayout(orientation="vertical", spacing=dp(4))
            info.add_widget(lbl("Overall GWA", size=12, color=MUTED,
                                size_hint_y=None, height=dp(22)))
            info.add_widget(lbl(remark, size=14, bold=True, color=rcol,
                                size_hint_y=None, height=dp(26)))
            top.add_widget(info)
            summary.add_widget(top)
            self.grades_stack.add_widget(summary)

        hdr = BoxLayout(size_hint_y=None, height=dp(28), padding=[dp(18), 0])
        hdr.add_widget(lbl("SUBJECT", size=10, bold=True, color=MUTED,
                           size_hint_x=1, halign="left"))
        for t in ["WW","PT","QE","FINAL"]:
            hdr.add_widget(lbl(t, size=10, bold=True, color=MUTED,
                               size_hint_x=None, width=dp(52), halign="center"))
        self.grades_stack.add_widget(hdr)

        for g in grades:
            self.grades_stack.add_widget(self._grade_card(g))

    def _grade_card(self, g):
        final_val  = compute_gwa(g["written"], g["performance"], g["exam"])
        remark, rc = grade_remark(final_val)
        card = CardLayout(bg=CARD, radius=14, padding=[dp(18), dp(12)],
                          size_hint_y=None, height=dp(78),
                          orientation="vertical", spacing=dp(8))

        row1 = BoxLayout(size_hint_y=None, height=dp(28))
        row1.add_widget(lbl(g["subject"], size=14, bold=True, color=TEXT))
        for val in [g["written"], g["performance"], g["exam"]]:
            row1.add_widget(lbl(str(val), size=13, color=MUTED,
                                halign="center", size_hint_x=None, width=dp(52)))
        row1.add_widget(lbl(f"{final_val:.1f}", size=14, bold=True, color=ACCENT,
                            halign="center", size_hint_x=None, width=dp(52)))
        card.add_widget(row1)

        pb_row = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(10))
        pb_row.add_widget(lbl(remark, size=9, bold=True, color=rc,
                              size_hint_x=None, width=dp(130)))
        pb_bg = Widget()
        with pb_bg.canvas:
            Color(*CARD2)
            pb_bg._bg_rect = RoundedRectangle(pos=pb_bg.pos, size=pb_bg.size, radius=[dp(3)])
            Color(*rc)
            pb_bg._fill = RoundedRectangle(
                pos=pb_bg.pos,
                size=(pb_bg.width * min(final_val/100.0, 1.0), pb_bg.height),
                radius=[dp(3)])
        def _upd_pb(inst, *a, fv=final_val):
            inst._bg_rect.pos  = inst.pos; inst._bg_rect.size = inst.size
            inst._fill.pos     = inst.pos
            inst._fill.size    = (inst.width * min(fv/100.0, 1.0), inst.height)
        pb_bg.bind(pos=_upd_pb, size=_upd_pb)
        pb_row.add_widget(pb_bg)
        pb_row.add_widget(icon_btn("✕",
                                   lambda b, gid=g["id"]: self._delete_grade(gid),
                                   size=dp(30), font_size=14))
        card.add_widget(pb_row)
        return card

    def _delete_grade(self, gid):
        self.app.data["grades"] = [g for g in self.app.data["grades"] if g["id"] != gid]
        save_data(self.app.data)
        Clock.schedule_once(lambda dt: self._render_grades(), 0)

    def _add_grade_popup(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(12),
                            padding=[dp(24), dp(20)])
        with content.canvas.before:
            Color(*CARD)
            content._bg = RoundedRectangle(pos=content.pos, size=content.size,
                                           radius=[dp(20)])
        content.bind(pos=lambda i,v: setattr(i._bg,"pos",v),
                     size=lambda i,v: setattr(i._bg,"size",v))
        content.add_widget(lbl("Add Grades", size=20, bold=True, color=TEXT,
                               halign="left", size_hint_y=None, height=dp(38)))
        content.add_widget(lbl("WW 25%  ·  PT 50%  ·  QE 25%", size=11,
                               color=MUTED, size_hint_y=None, height=dp(22)))
        fields = {}
        for label, key, ph in [("Subject","subject","Mathematics"),
                                ("Written Works (25%)","written","88"),
                                ("Performance Tasks (50%)","performance","90"),
                                ("Quarterly Exam (25%)","exam","85")]:
            content.add_widget(lbl(label, size=12, bold=True, color=MUTED,
                                   size_hint_y=None, height=dp(24)))
            ti = TextInput(hint_text=ph, multiline=False, font_size=dp(16),
                           background_color=CARD2, foreground_color=TEXT,
                           hint_text_color=DIM, cursor_color=ACCENT,
                           input_filter="float" if key != "subject" else None,
                           padding=[dp(14), dp(12)],
                           size_hint_y=None, height=dp(52))
            content.add_widget(ti)
            fields[key] = ti
        popup = safe_popup(content, height=dp(540))

        def save(*a):
            subj = fields["subject"].text.strip()
            if not subj: return
            try:
                w = float(fields["written"].text or 0)
                p = float(fields["performance"].text or 0)
                e = float(fields["exam"].text or 0)
            except Exception:
                return
            self.app.data["grades"].append({
                "id":          max((g["id"] for g in self.app.data["grades"]), default=0)+1,
                "subject":     subj, "written": w, "performance": p, "exam": e,
            })
            save_data(self.app.data)
            popup.dismiss()
            Clock.schedule_once(lambda dt: self._render_grades(), 0.1)

        content.add_widget(accent_btn("Save", save, height=dp(54)))
        content.add_widget(muted_btn("Cancel", lambda *a: popup.dismiss(),
                                     width=dp(140), height=dp(46)))
        popup.open()