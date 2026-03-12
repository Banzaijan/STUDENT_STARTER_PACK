from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.metrics import dp
from kivy.clock import Clock

from utils.colors import CARD, CARD2, ACCENT, TEXT, MUTED, BLACK, DIM, PRIORITY_COLORS
from utils.data import save_data
from widgets.buttons import lbl, vstack, icon_btn, check_btn, accent_btn, safe_popup
from widgets.cards import BaseScreen, CardLayout


class TasksScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=0)

        hdr = BoxLayout(size_hint_y=None, height=dp(64), padding=[dp(20), dp(10)])
        hdr.add_widget(lbl("To-Do", size=22, bold=True, color=TEXT,
                           size_hint_y=None, height=dp(44)))
        root.add_widget(hdr)

        # Add task row
        add_card = CardLayout(bg=CARD, radius=16, size_hint_y=None, height=dp(72),
                              padding=[dp(14), dp(10)], orientation="horizontal",
                              spacing=dp(10))
        self.task_entry = TextInput(
            hint_text="Add a new task…", multiline=False,
            font_size=dp(15), background_color=(0, 0, 0, 0),
            foreground_color=TEXT, hint_text_color=DIM,
            cursor_color=ACCENT)
        self.priority_spinner = Spinner(
            text="high", values=["high", "medium", "low"],
            font_size=dp(12), bold=True,
            size_hint_x=None, width=dp(82),
            background_normal="", background_color=CARD2, color=ACCENT)

        from kivy.uix.button import Button
        from kivy.animation import Animation

        add_plus = Button(
            text="+", font_size=dp(26), bold=True,
            size_hint=(None, None), size=(dp(52), dp(52)),
            background_normal="", background_color=ACCENT, color=BLACK)

        def _down(inst, touch):
            if inst.collide_point(*touch.pos):
                Animation.cancel_all(inst, "opacity")
                Animation(opacity=0.45, duration=0.07).start(inst)
        def _up(inst, touch):
            Animation.cancel_all(inst, "opacity")
            Animation(opacity=1.0, duration=0.20, t="out_cubic").start(inst)

        add_plus.bind(on_touch_down=_down, on_touch_up=_up)
        add_plus.bind(on_press=lambda b: self._add_todo())

        add_card.add_widget(self.task_entry)
        add_card.add_widget(self.priority_spinner)
        add_card.add_widget(add_plus)
        root.add_widget(add_card)

        self.todos_scroll = ScrollView(do_scroll_x=False)
        self.todos_stack  = vstack(spacing=10)
        self.todos_scroll.add_widget(self.todos_stack)
        root.add_widget(self.todos_scroll)
        self._render_todos()
        self.add_widget(root)

    def _render_todos(self):
        self.todos_stack.clear_widgets()
        high   = [t for t in self.app.data["todos"] if t["priority"] == "high"   and not t["done"]]
        medium = [t for t in self.app.data["todos"] if t["priority"] == "medium" and not t["done"]]
        low    = [t for t in self.app.data["todos"] if t["priority"] == "low"    and not t["done"]]
        done   = [t for t in self.app.data["todos"] if t["done"]]

        if high + medium + low:
            self.todos_stack.add_widget(
                lbl("PENDING", size=11, bold=True, color=MUTED,
                    size_hint_y=None, height=dp(30)))
            for todo in high + medium + low:
                self.todos_stack.add_widget(self._todo_card(todo))

        if done:
            self.todos_stack.add_widget(
                lbl("COMPLETED", size=11, bold=True, color=MUTED,
                    size_hint_y=None, height=dp(30)))
            for todo in done:
                self.todos_stack.add_widget(self._todo_card(todo))

        total_done = len(done)
        total      = len(self.app.data["todos"])
        self.todos_stack.add_widget(
            lbl(f"{total_done} of {total} completed", size=11, color=DIM,
                halign="center", size_hint_y=None, height=dp(34)))

    def _todo_card(self, todo):
        pcol    = PRIORITY_COLORS.get(todo["priority"], (0.4, 0.4, 0.4, 1.0))
        is_done = todo["done"]
        card = CardLayout(bg=CARD, radius=14, padding=[dp(16), dp(12)],
                          size_hint_y=None, height=dp(64),
                          orientation="horizontal", spacing=dp(12))

        dot = Widget(size_hint=(None, None), size=(dp(10), dp(10)))
        with dot.canvas:
            Color(*(DIM if is_done else pcol))
            dot._circ = Ellipse(pos=dot.pos, size=dot.size)
        dot.bind(pos=lambda i, v: setattr(i._circ, "pos", v))
        card.add_widget(dot)

        card.add_widget(check_btn(is_done,
                                  lambda b, tid=todo["id"]: self._toggle_todo(tid),
                                  size=dp(36)))
        card.add_widget(lbl(todo["text"], size=14,
                            color=DIM if is_done else TEXT))
        card.add_widget(icon_btn("✕",
                                 lambda b, tid=todo["id"]: self._remove_todo(tid),
                                 size=dp(36), font_size=16))
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