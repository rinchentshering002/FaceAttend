"""
FaceAttend — Shared UI helpers.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from zoneinfo import ZoneInfo

BHUTAN_TZ = ZoneInfo("Asia/Thimphu")

# ============================================================
# COLORS & FONTS
# ============================================================

BG = "#F4F7FB"
CARD = "#FFFFFF"
WHITE = "#FFFFFF"

NAVY = "#2C4A6E"
NAVY_DARK = "#1E3652"
NAVY_MID = "#4A6D96"

GOLD = "#C99A2E"
GOLD_LIGHT = "#E7C76A"

WOOD = "#3A4A5C"
SLATE = "#6B7A88"

TEXT = "#1A202C"
MUTED = "#6B7280"

GREEN = "#23824B"
RED = "#B93636"
BLUE = "#315A78"

BORDER = "#D6E0EC"
HOVER = "#E8EFF7"

TITLE_FONT = ("Segoe UI", 22, "bold")
SUBTITLE_FONT = ("Segoe UI", 9)
BODY_FONT = ("Segoe UI", 10)

# ============================================================
# TTK STYLES
# ============================================================

def setup_ttk_styles():
    style = ttk.Style()
    try: style.theme_use("clam")
    except tk.TclError: pass

    style.configure("Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=42, borderwidth=0, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", background=NAVY, foreground=WHITE, font=("Segoe UI", 10, "bold"), relief="flat", padding=(10, 9))
    style.map("Treeview", background=[("selected", "#D6E4F0")], foreground=[("selected", TEXT)])

    style.configure("Report.Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=34, borderwidth=0, font=("Segoe UI", 9))
    style.configure("Report.Treeview.Heading", background=NAVY, foreground=WHITE, font=("Segoe UI", 9, "bold"), relief="flat", padding=8)
    style.map("Report.Treeview", background=[("selected", "#D6E4F0")], foreground=[("selected", TEXT)])

    style.configure("Modern.TCombobox", fieldbackground=WHITE, background=WHITE, foreground=TEXT, padding=8, font=("Segoe UI", 10))
    style.map("Modern.TCombobox", fieldbackground=[("readonly", WHITE)], foreground=[("readonly", TEXT)])

# ============================================================
# TIME & WINDOW HELPERS
# ============================================================

def center_window(win, width, height):
    win.update_idletasks()
    x = (win.winfo_screenwidth() - width) // 2
    y = (win.winfo_screenheight() - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

def try_set_icon(win):
    try: win.iconbitmap("faceattend.ico")
    except Exception: pass

def bhutan_now():
    return datetime.now(BHUTAN_TZ)

def format_check_in_time(value):
    if not value: return "-"
    value = str(value).strip()
    try: return datetime.strptime(value, "%H:%M:%S.%f").strftime("%I:%M:%S %p")
    except ValueError: pass
    try: return datetime.strptime(value, "%H:%M:%S").strftime("%I:%M:%S %p")
    except ValueError: pass
    try:
        utc_time = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if utc_time.tzinfo is None: utc_time = utc_time.replace(tzinfo=ZoneInfo("UTC"))
        return utc_time.astimezone(BHUTAN_TZ).strftime("%I:%M:%S %p")
    except Exception: return value

def format_time_short(value):
    if not value: return ""
    try: return datetime.strptime(str(value).split(".")[0], "%H:%M:%S").strftime("%I:%M:%S %p")
    except Exception: return str(value)

# ============================================================
# UI ELEMENTS
# ============================================================

def add_bhutan_pattern(parent, bg=NAVY):
    pattern = tk.Frame(parent, bg=bg, height=7)
    pattern.pack(fill="x")
    pattern.pack_propagate(False)
    for i in range(24):
        tk.Label(pattern, text="◆", bg=bg, fg=(GOLD_LIGHT if i % 2 == 0 else GOLD), font=("Segoe UI", 6)).pack(side="left", expand=True)

def make_hero(parent, title, subtitle=None, on_back=None):
    """Hero header with optional Back button."""
    hero = tk.Frame(parent, bg=NAVY)
    hero.pack(fill="x")
    add_bhutan_pattern(hero, NAVY)

    hero_body = tk.Frame(hero, bg=NAVY)
    hero_body.pack(fill="x", padx=25, pady=15)

    if on_back:
        tk.Button(
            hero_body, text="←  Back to Dashboard", command=on_back,
            font=("Segoe UI", 10, "bold"), bg=NAVY, fg=GOLD_LIGHT,
            activebackground=NAVY_DARK, activeforeground=GOLD_LIGHT,
            relief="flat", bd=0, cursor="hand2"
        ).pack(side="right", anchor="n")

    text_frame = tk.Frame(hero_body, bg=NAVY)
    text_frame.pack(side="left", anchor="w")

    tk.Label(text_frame, text=title, bg=NAVY, fg=WHITE, font=TITLE_FONT).pack(anchor="w")
    if subtitle:
        tk.Label(text_frame, text=subtitle, bg=NAVY, fg="#DCE6F0", font=SUBTITLE_FONT).pack(anchor="w", pady=(3, 0))

    return hero

def make_top_bar(parent):
    bar = tk.Frame(parent, bg=CARD, height=55)
    bar.pack(fill="x")
    bar.pack_propagate(False)

    label = tk.Label(bar, text="", bg=CARD, fg=NAVY, font=("Segoe UI", 10, "bold"))
    label.pack(side="right", padx=30)

    def tick():
        try:
            if not label.winfo_exists(): return
            now = bhutan_now()
            label.configure(text=f"BHUTAN TIME  •  {now.strftime('%d %b %Y  |  %I:%M:%S %p')}")
            parent.after(1000, tick)
        except tk.TclError: pass
    tick()
    return bar

def make_card(parent):
    return tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1, bd=0)

def empty_state_label(parent, message="No records yet."):
    return tk.Label(parent, text=message, bg=CARD, fg=MUTED, font=("Segoe UI", 10, "italic"))

_HOVER_MAP = {NAVY: NAVY_DARK, BLUE: "#264B66", WOOD: "#2A3845", RED: "#8E2828", GREEN: "#1B6D2D", SLATE: "#566472"}

def rounded_button(parent, text, command, width=22, bg=NAVY, fg=WHITE, height=2):
    hover_bg = _HOVER_MAP.get(bg, HOVER)
    button = tk.Button(parent, text=text, command=command, width=width, height=height, bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg, font=("Segoe UI", 10, "bold"), relief="flat", bd=0, cursor="hand2")

    def enter(_):
        try:
            if button["state"] != "disabled": button.configure(bg=hover_bg)
        except tk.TclError: pass
    def leave(_):
        try:
            if button["state"] != "disabled": button.configure(bg=bg)
        except tk.TclError: pass

    button.bind("<Enter>", enter)
    button.bind("<Leave>", leave)
    return button