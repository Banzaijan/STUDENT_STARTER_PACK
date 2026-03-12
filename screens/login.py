from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse, Line
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.clock import Clock
import json, os, random, string

from utils.colors import ACCENT, TEXT, MUTED, DIM, BLACK, RED, GREEN

# ── Customize these ───────────────────────────────────────────────────────────
SCHOOL_DOMAIN  = "@asiatech.edu.ph"   # e.g. "@sti.edu.ph"
SCHOOL_NAME    = "Student Starter Pack"
COPYRIGHT_TEXT = "© 2026 ASIATECH — ALL RIGHTS RESERVED"

# ── Colors ────────────────────────────────────────────────────────────────────
PAGE_BG    = (0.878, 0.957, 0.906, 1.0)   # soft green background
CARD_BG    = (1.000, 1.000, 1.000, 1.0)   # white card
AVATAR_BG  = (0.200, 0.780, 0.420, 1.0)   # green avatar circle
ACCENT_G   = (0.200, 0.780, 0.420, 1.0)   # green accent
NOTICE_BG  = (0.878, 0.957, 0.906, 1.0)   # light green notice
NOTICE_BD  = (0.200, 0.780, 0.420, 1.0)   # green border
FIELD_BG   = (0.972, 0.972, 0.972, 1.0)   # light grey input
FIELD_BD   = (0.878, 0.878, 0.878, 1.0)
BTN_GREEN  = (0.200, 0.780, 0.420, 1.0)
TEXT_DARK  = (0.133, 0.133, 0.133, 1.0)
TEXT_MID   = (0.400, 0.400, 0.400, 1.0)
TEXT_LIGHT = (0.650, 0.650, 0.650, 1.0)
WHITE      = (1.000, 1.000, 1.000, 1.0)
ERROR_RED  = (0.900, 0.200, 0.200, 1.0)
SUCCESS_G  = (0.200, 0.700, 0.380, 1.0)

LOGIN_FILE = "login_data.json"


def load_accounts():
    if os.path.exists(LOGIN_FILE):
        try:
            with open(LOGIN_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_accounts(data):
    try:
        with open(LOGIN_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[LOGIN] {e}")


def generate_code(length=6):
    return "".join(random.choices(string.digits, k=length))


# ── Tap-safe button ───────────────────────────────────────────────────────────
def make_btn(text, callback, bg=None, fg=WHITE, height=dp(54), font_size=14, bold=True):
    bg = bg or BTN_GREEN
    btn = Button(
        text=text, font_size=dp(font_size), bold=bold,
        size_hint_y=None, height=height,
        background_normal="", background_color=bg, color=fg)

    def _down(inst, touch):
        if inst.collide_point(*touch.pos):
            inst._ts = (touch.x, touch.y)
            Animation.cancel_all(inst, "opacity")
            Animation(opacity=0.6, duration=0.07).start(inst)
            touch.grab(inst)
            return True
    def _move(inst, touch):
        if touch.grab_current is inst and hasattr(inst, "_ts"):
            if abs(touch.x-inst._ts[0]) > dp(10) or abs(touch.y-inst._ts[1]) > dp(10):
                Animation(opacity=1.0, duration=0.15).start(inst)
                touch.ungrab(inst); inst._ts = None
    def _up(inst, touch):
        if touch.grab_current is inst:
            touch.ungrab(inst)
            Animation(opacity=1.0, duration=0.18, t="out_cubic").start(inst)
            if getattr(inst, "_ts", None) is not None:
                inst._ts = None; inst.dispatch("on_press")
            return True
    btn.bind(on_touch_down=_down, on_touch_move=_move, on_touch_up=_up)
    btn.bind(on_press=callback)
    return btn


def lbl(text, size=13, color=None, bold=False, halign="left", **kw):
    color = color or TEXT_DARK
    l = Label(text=text, font_size=dp(size), color=color,
              bold=bold, halign=halign, **kw)
    l.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
    return l


def field_input(hint, password=False):
    return TextInput(
        hint_text=hint, password=password,
        multiline=False, font_size=dp(15),
        background_color=(0, 0, 0, 0),
        foreground_color=TEXT_DARK,
        hint_text_color=TEXT_LIGHT,
        cursor_color=ACCENT_G,
        padding=[dp(14), dp(14)],
        size_hint_y=None, height=dp(48))


def rounded_box(bg, radius=12, **kw):
    kw.setdefault("orientation", "vertical")
    box = BoxLayout(**kw)
    with box.canvas.before:
        Color(*bg)
        box._r = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(radius)])
    box.bind(pos=lambda i, v: setattr(i._r, "pos",  v),
             size=lambda i, v: setattr(i._r, "size", v))
    return box


def bordered_box(bg, border_color, radius=12, **kw):
    kw.setdefault("orientation", "vertical")
    box = BoxLayout(**kw)
    with box.canvas.before:
        Color(*border_color)
        box._bd = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(radius)])
        Color(*bg)
        box._bg = RoundedRectangle(
            pos=(box.x + dp(1.5), box.y + dp(1.5)),
            size=(box.width - dp(3), box.height - dp(3)),
            radius=[dp(radius - 1)])
    def _upd(i, *a):
        i._bd.pos  = i.pos;  i._bd.size = i.size
        i._bg.pos  = (i.x + dp(1.5), i.y + dp(1.5))
        i._bg.size = (i.width - dp(3), i.height - dp(3))
    box.bind(pos=_upd, size=_upd)
    return box


# ══════════════════════════════════════════════════════════════════════════════
class LoginScreen(Screen):
    def __init__(self, on_success, **kw):
        super().__init__(name="login", **kw)
        self.on_success        = on_success
        self.accounts          = load_accounts()
        self._step             = "login"
        self._pending_email    = None
        self._pending_code     = None
        self._show_pass        = False
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build(self):
        self.clear_widgets()

        root = FloatLayout()

        # Dotted green background
        with root.canvas.before:
            Color(*PAGE_BG)
            root._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: setattr(i._bg, "pos",  v),
                  size=lambda i, v: setattr(i._bg, "size", v))

        # White card
        card_h = {"login": dp(560), "register": dp(540), "verify": dp(480)}
        card = rounded_box(CARD_BG, radius=20,
                           size_hint=(0.88, None),
                           height=card_h.get(self._step, dp(560)),
                           pos_hint={"center_x": 0.5, "center_y": 0.52},
                           padding=[dp(28), dp(24)],
                           spacing=dp(10))

        if self._step == "login":
            self._build_login(card)
        elif self._step == "register":
            self._build_register(card)
        elif self._step == "verify":
            self._build_verify(card)

        root.add_widget(card)

        # Copyright footer
        foot = lbl(COPYRIGHT_TEXT, size=9, color=TEXT_LIGHT,
                   halign="center",
                   size_hint=(1, None), height=dp(28),
                   pos_hint={"center_x": 0.5, "y": 0.01})
        root.add_widget(foot)

        self.add_widget(root)

    # ── Login step ────────────────────────────────────────────────────────────
    def _build_login(self, card):
        # Avatar circle
        av_wrap = BoxLayout(size_hint_y=None, height=dp(90),
                            orientation="vertical")
        av = Widget(size_hint_x=None, width=dp(72),
                               size_hint_y=None, height=dp(72),
                    pos_hint={"center_x": 0.5})
        with av.canvas:
            # Dashed ring
            Color(*NOTICE_BD)
            av._ring = Ellipse(pos=(av.x - dp(6), av.y - dp(6)),
                               size=(dp(84), dp(84)))
            Color(*CARD_BG)
            av._ring2 = Ellipse(pos=(av.x - dp(3), av.y - dp(3)),
                                size=(dp(78), dp(78)))
            # Filled circle
            Color(*AVATAR_BG)
            av._circ = Ellipse(pos=av.pos, size=av.size)
        def _upd_av(i, *a):
            i._ring.pos   = (i.x - dp(6), i.y - dp(6))
            i._ring.size  = (dp(84), dp(84))
            i._ring2.pos  = (i.x - dp(3), i.y - dp(3))
            i._ring2.size = (dp(78), dp(78))
            i._circ.pos   = i.pos; i._circ.size = i.size
        av.bind(pos=_upd_av, size=_upd_av)

        av_lbl = Label(text="[b]i[/b]", markup=True, font_size=dp(28),
                       color=WHITE, size_hint=(None, None),
                       size=(dp(72), dp(72)), pos_hint={"center_x": 0.5})
        av_fl = FloatLayout(size_hint_y=None, height=dp(90))
        av_fl.add_widget(av)
        av_fl.add_widget(av_lbl)
        card.add_widget(av_fl)

        # Title
        card.add_widget(lbl("Student Portal", size=22, bold=True,
                             color=TEXT_DARK, halign="center",
                             size_hint_y=None, height=dp(32)))
        card.add_widget(lbl("Login to access your student dashboard",
                             size=11, color=TEXT_MID, halign="center",
                             size_hint_y=None, height=dp(20)))

        # Notice banner
        notice = bordered_box(NOTICE_BG, NOTICE_BD, radius=10,
                               orientation="horizontal",
                               size_hint_y=None, height=dp(52),
                               padding=[dp(12), dp(8)], spacing=dp(8))
        notice.add_widget(lbl("i", size=14, bold=True, color=ACCENT_G,
                               size_hint_x=None, width=dp(22),
                               size_hint_y=None, height=dp(22)))
        notice.add_widget(lbl(f"STUDENT ACCESS ONLY — Use your school-issued email",
                               size=11, bold=True, color=ACCENT_G,
                               size_hint_y=None, height=dp(36)))
        card.add_widget(notice)

        # Email field
        card.add_widget(lbl("Student Email", size=12, bold=True,
                             color=TEXT_DARK, size_hint_y=None, height=dp(22)))
        email_wrap = bordered_box(FIELD_BG, FIELD_BD, radius=10,
                                   orientation="horizontal",
                                   size_hint_y=None, height=dp(52),
                                   padding=[dp(12), dp(4)], spacing=dp(6))
        email_wrap.add_widget(lbl("@", size=16, color=TEXT_LIGHT,
                                   size_hint_x=None, width=dp(22),
                               size_hint_y=None, height=dp(44)))
        self.email_in = field_input(f"student{SCHOOL_DOMAIN}")
        email_wrap.add_widget(self.email_in)
        card.add_widget(email_wrap)

        # Password field
        card.add_widget(lbl("Access Code / Password", size=12, bold=True,
                             color=TEXT_DARK, size_hint_y=None, height=dp(22)))
        pass_wrap = bordered_box(FIELD_BG, FIELD_BD, radius=10,
                                  orientation="horizontal",
                                  size_hint_y=None, height=dp(52),
                                  padding=[dp(12), dp(4)], spacing=dp(6))
        pass_wrap.add_widget(lbl("#", size=16, color=TEXT_LIGHT,
                                  size_hint_x=None, width=dp(22),
                               size_hint_y=None, height=dp(44)))
        self.code_in = field_input("Enter your 6-digit code", password=True)
        pass_wrap.add_widget(self.code_in)

        # Show/hide toggle
        show_btn = Button(text="Show", font_size=dp(11), bold=True,
                          size_hint_x=None, width=dp(52),
                               size_hint_y=None, height=dp(36),
                          background_normal="", background_color=(0,0,0,0),
                          color=ACCENT_G)
        def _toggle_pass(b):
            self._show_pass = not self._show_pass
            self.code_in.password = not self._show_pass
            show_btn.text = "Hide" if self._show_pass else "Show"
        show_btn.bind(on_press=_toggle_pass)
        pass_wrap.add_widget(show_btn)
        card.add_widget(pass_wrap)

        # Status
        self.status_lbl = lbl("", size=11, color=ERROR_RED,
                               halign="center", size_hint_y=None, height=dp(20))
        card.add_widget(self.status_lbl)

        # Login button
        login_btn = make_btn(f"LOGIN AS STUDENT  →", self._do_login,
                              bg=BTN_GREEN, height=dp(54), font_size=14)
        card.add_widget(login_btn)

        # Create account link
        card.add_widget(make_btn("Don't have an account? Create one",
                                  self._go_register,
                                  bg=(0,0,0,0), fg=ACCENT_G,
                                  height=dp(36), font_size=12, bold=False))

    # ── Register step ─────────────────────────────────────────────────────────
    def _build_register(self, card):
        card.add_widget(lbl("← Back to Sign In", size=12, color=ACCENT_G,
                             size_hint_y=None, height=dp(28)))
        back_btn = make_btn("← Back", self._go_login,
                             bg=(0,0,0,0), fg=ACCENT_G,
                             height=dp(32), font_size=12, bold=False)
        card.add_widget(back_btn)

        card.add_widget(lbl("Create Account", size=22, bold=True,
                             color=TEXT_DARK, size_hint_y=None, height=dp(32)))
        card.add_widget(lbl(f"Must use your school email  ({SCHOOL_DOMAIN})",
                             size=11, color=TEXT_MID,
                             size_hint_y=None, height=dp(20)))

        notice = bordered_box(NOTICE_BG, NOTICE_BD, radius=10,
                               size_hint_y=None, height=dp(44),
                               padding=[dp(12), dp(8)])
        notice.add_widget(lbl(f"STUDENT ACCESS ONLY — School email required",
                               size=11, bold=True, color=ACCENT_G,
                               size_hint_y=None, height=dp(28)))
        card.add_widget(notice)

        card.add_widget(lbl("Full Name", size=12, bold=True,
                             color=TEXT_DARK, size_hint_y=None, height=dp(22)))
        name_wrap = bordered_box(FIELD_BG, FIELD_BD, radius=10,
                                  size_hint_y=None, height=dp(52),
                                  padding=[dp(12), dp(4)])
        self.reg_name = field_input("e.g. Joshua Copias Luci")
        name_wrap.add_widget(self.reg_name)
        card.add_widget(name_wrap)

        card.add_widget(lbl("School Email", size=12, bold=True,
                             color=TEXT_DARK, size_hint_y=None, height=dp(22)))
        email_wrap = bordered_box(FIELD_BG, FIELD_BD, radius=10,
                                   orientation="horizontal",
                                   size_hint_y=None, height=dp(52),
                                   padding=[dp(12), dp(4)], spacing=dp(6))
        email_wrap.add_widget(lbl("@", size=16, color=TEXT_LIGHT,
                                   size_hint_x=None, width=dp(22),
                               size_hint_y=None, height=dp(44)))
        self.reg_email = field_input(f"1200000F{SCHOOL_DOMAIN}", )
        email_wrap.add_widget(self.reg_email)
        card.add_widget(email_wrap)

        self.reg_status = lbl("", size=11, color=ERROR_RED,
                               halign="center", size_hint_y=None, height=dp(20))
        card.add_widget(self.reg_status)

        card.add_widget(make_btn("SEND CODE  →", self._do_register,
                                  bg=BTN_GREEN, height=dp(54)))
        card.add_widget(make_btn("Already have an account? Sign in",
                                  self._go_login,
                                  bg=(0,0,0,0), fg=ACCENT_G,
                                  height=dp(36), font_size=12, bold=False))

    # ── Verify step ───────────────────────────────────────────────────────────
    def _build_verify(self, card):
        card.add_widget(make_btn("← Back", self._go_register,
                                  bg=(0,0,0,0), fg=ACCENT_G,
                                  height=dp(32), font_size=12, bold=False))

        card.add_widget(lbl("Enter Your Code", size=22, bold=True,
                             color=TEXT_DARK, size_hint_y=None, height=dp(32)))
        card.add_widget(lbl(f"A 6-digit code was generated for\n{self._pending_email}",
                             size=11, color=TEXT_MID,
                             size_hint_y=None, height=dp(36)))

        # Demo code display
        code_box = bordered_box(NOTICE_BG, NOTICE_BD, radius=12,
                                 size_hint_y=None, height=dp(62),
                                 padding=[dp(16), dp(10)])
        code_box.add_widget(lbl(f"Your code:   {self._pending_code}",
                                 size=22, bold=True, color=ACCENT_G,
                                 halign="center", size_hint_y=None, height=dp(38)))
        card.add_widget(code_box)

        card.add_widget(lbl("In a real school system this code would be\n"
                             "sent to your school email inbox.",
                             size=10, color=TEXT_LIGHT,
                             size_hint_y=None, height=dp(30)))

        card.add_widget(lbl("6-Digit Code", size=12, bold=True,
                             color=TEXT_DARK, size_hint_y=None, height=dp(22)))
        code_wrap = bordered_box(FIELD_BG, FIELD_BD, radius=10,
                                  size_hint_y=None, height=dp(52),
                                  padding=[dp(12), dp(4)])
        self.verify_in = field_input("Enter the 6-digit code above")
        code_wrap.add_widget(self.verify_in)
        card.add_widget(code_wrap)

        self.verify_status = lbl("", size=11, color=ERROR_RED,
                                  halign="center", size_hint_y=None, height=dp(20))
        card.add_widget(self.verify_status)
        card.add_widget(make_btn("VERIFY & SIGN IN  →", self._do_verify,
                                  bg=BTN_GREEN, height=dp(54)))

    # ── Actions ───────────────────────────────────────────────────────────────
    def _do_login(self, *a):
        email = self.email_in.text.strip().lower()
        code  = self.code_in.text.strip()
        if not email or not code:
            self._err(self.status_lbl, "Please fill in all fields.")
            return
        if not email.endswith(SCHOOL_DOMAIN):
            self._err(self.status_lbl, f"Must end with {SCHOOL_DOMAIN}")
            return
        acc = self.accounts.get(email)
        if not acc:
            self._err(self.status_lbl, "Account not found. Create one first.")
            return
        if acc.get("code") != code:
            self._err(self.status_lbl, "Wrong code. Try again.")
            return
        self._ok(self.status_lbl, "Welcome back! Signing in…")
        Clock.schedule_once(
            lambda dt: self.on_success(email, acc.get("name", "")), 0.8)

    def _do_register(self, *a):
        name  = self.reg_name.text.strip()
        email = self.reg_email.text.strip().lower()
        if not name or not email:
            self._err(self.reg_status, "Please fill in all fields.")
            return
        if not email.endswith(SCHOOL_DOMAIN):
            self._err(self.reg_status, f"Must end with {SCHOOL_DOMAIN}")
            return
        if email in self.accounts:
            self._err(self.reg_status, "Account exists. Sign in instead.")
            return
        code = generate_code()
        self.accounts[email] = {"name": name, "code": code, "verified": False}
        save_accounts(self.accounts)
        self._pending_email = email
        self._pending_code  = code
        self._step = "verify"
        self._build()

    def _do_verify(self, *a):
        if self.verify_in.text.strip() == self._pending_code:
            self.accounts[self._pending_email]["verified"] = True
            save_accounts(self.accounts)
            self._ok(self.verify_status, "Verified! Signing in…")
            Clock.schedule_once(
                lambda dt: self.on_success(
                    self._pending_email,
                    self.accounts[self._pending_email].get("name", "")), 0.8)
        else:
            self._err(self.verify_status, "Wrong code. Try again.")

    def _go_login(self,    *a): self._step = "login";    self._build()
    def _go_register(self, *a): self._step = "register"; self._build()

    @staticmethod
    def _err(lbl_w, msg):
        lbl_w.text  = msg
        lbl_w.color = ERROR_RED

    @staticmethod
    def _ok(lbl_w, msg):
        lbl_w.text  = msg
        lbl_w.color = SUCCESS_G