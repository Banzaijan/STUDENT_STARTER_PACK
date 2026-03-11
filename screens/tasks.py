from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

from utils.colors import CARD, CARD2, ACCENT, TEXT, MUTED, BLACK, DIM, PRIORITY_COLORS
from utils.data import save_data
from widgets.buttons import lbl, section_label, vstack
from widgets.cards import BaseScreen, CardLayout


class TasksScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=0)

        hdr = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(16), dp(6)])
        hdr.add_widget(lbl("TO-DO", size=11, bold=True, color=TEXT))
        root.add_widget(hdr)

        add_row = BoxLayout(size_hint_y=None, height=dp(50),
                            spacing=dp(6), padding=[dp(16), dp(4)])
        self.task_entry = TextInput(
            hint_text="New task...", multiline=False,
            font_size=dp(13), background_color=CARD2,
            foreground_color=TEXT, hint_text_color=MUTED,
            cursor_color=ACCENT)
        self.priority_spinner = Spinner(
            text="high", values=["high", "medium", "low"],
            font_size=dp(10), bold=True,
            size_hint_x=None, width=dp(80),
            background_normal="", background_color=CARD2, color=ACCENT)
        add_btn = Button(
            text="+", font_size=dp(24), bold=True,
            size_hint=(None, None), size=(dp(46), dp(46)),
            background_normal="", background_color=ACCENT, color=BLACK)
        add_btn.bind(on_press=lambda b: self._add_todo())
        add_row.add_widget(self.task_entry)
        add_row.add_widget(self.priority_spinner)
        add_row.add_widget(add_btn)
        root.add_widget(add_row)

        self.todos_scroll = ScrollView(do_scroll_x=False)
        self.todos_stack  = vstack(spacing=6)
        self.todos_scroll.add_widget(self.todos_stack)
        root.add_widget(self.todos_scroll)
        self._render_todos()
        self.add_widget(root)

    def _render_todos(self):
        self.todos_stack.clear_widgets()
        high   = [t for t in self.app.data["todos"] if t["priority"]=="high"   and not t["done"]]
        medium = [t for t in self.app.data["todos"] if t["priority"]=="medium" and not t["done"]]
        low    = [t for t in self.app.data["todos"] if t["priority"]=="low"    and not t["done"]]
        done   = [t for t in self.app.data["todos"] if t["done"]]
        for todo in high + medium + low + done:
            self.todos_stack.add_widget(self._todo_card(todo))
        total_done = len(done)
        total      = len(self.app.data["todos"])
        self.todos_stack.add_widget(
            lbl(f"{total_done} of {total} completed", size=9, color=MUTED,
                halign="center", size_hint_y=None, height=dp(28)))

    def _todo_card(self, todo):
        pcol    = PRIORITY_COLORS.get(todo["priority"], (0.4, 0.4, 0.4, 1.0))
        is_done = todo["done"]
        card = CardLayout(
            bg=CARD, radius=8, padding=[dp(12), dp(8)],
            size_hint_y=None, height=dp(50),
            orientation="horizontal", spacing=dp(10))

        # priority dot
        dot = Widget(size_hint=(None, None), size=(dp(6), dp(6)))
        with dot.canvas:
            Color(*(MUTED if is_done else pcol))
            dot._circ = Ellipse(pos=dot.pos, size=dot.size)
        dot.bind(pos=lambda i,v: setattr(i._circ, "pos", v))
        card.add_widget(dot)

        done_btn = Button(
            text="●" if is_done else "○",
            font_size=dp(16),
            size_hint=(None, None), size=(dp(32), dp(32)),
            background_normal="", background_color=(0,0,0,0),
            color=ACCENT if is_done else DIM)
        done_btn.bind(on_press=lambda b, tid=todo["id"]: self._toggle_todo(tid))
        card.add_widget(done_btn)

        card.add_widget(lbl(todo["text"], size=12,
                            color=MUTED if is_done else TEXT))

        del_btn = Button(
            text="✕", font_size=dp(14),
            size_hint=(None, None), size=(dp(32), dp(32)),
            background_normal="", background_color=(0,0,0,0), color=MUTED)
        del_btn.bind(on_press=lambda b, tid=todo["id"]: self._remove_todo(tid))
        card.add_widget(del_btn)
        return card

    def _toggle_todo(self, tid):
        for t in self.app.data["todos"]:
            if t["id"] == tid:
                t["done"] = not t["done"]
        save_data(self.app.data)
        Clock.schedule_once(lambda dt: self._render_todos(), 0)

    def _remove_todo(self, tid):
        self.app.data["todos"] = [t for t in self.app.data["todos"] if t["id"] != tid]
        save_data(self.app.data)
        Clock.schedule_once(lambda dt: self._render_todos(), 0)

    def _add_todo(self):
        text = self.task_entry.text.strip()
        if not text:
            return
        self.app.data["todos"].append({
            "id":       max((t["id"] for t in self.app.data["todos"]), default=0) + 1,
            "text":     text,
            "done":     False,
            "priority": self.priority_spinner.text,
        })
        save_data(self.app.data)
        self.task_entry.text = ""
        Clock.schedule_once(lambda dt: self._render_todos(), 0)