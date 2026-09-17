import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from supabase import create_client

from register_student import register_student
from attendance import take_attendance


# ============================================================
# FACEATTEND — BHUTANESE PROFESSIONAL DASHBOARD
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials are missing!")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

BHUTAN_TZ = ZoneInfo("Asia/Thimphu")


# ============================================================
# THEME
# Subtle Bhutanese-inspired palette
# ============================================================

BG = "#F7F3EA"
CARD = "#FFFDF8"
WHITE = "#FFFFFF"

MAROON = "#7A1F2B"
MAROON_DARK = "#54131D"
MAROON_LIGHT = "#A6404D"

GOLD = "#C99A2E"
GOLD_LIGHT = "#E7C76A"

WOOD = "#3E2B25"

TEXT = "#29211E"
MUTED = "#786F68"

GREEN = "#23824B"
GREEN_LIGHT = "#E6F4EA"

RED = "#B93636"
RED_LIGHT = "#FBE8E8"

BLUE = "#315A78"

BORDER = "#E5DCCB"
HOVER = "#F0E6D5"


# ============================================================
# WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "FaceAttend | Bhutan Digital Attendance System"
)

root.geometry("1280x760")
root.minsize(1050, 680)
root.configure(bg=BG)


# ============================================================
# STYLE
# ============================================================

style = ttk.Style()

try:
    style.theme_use("clam")
except tk.TclError:
    pass


style.configure(
    "Treeview",
    background=CARD,
    foreground=TEXT,
    fieldbackground=CARD,
    rowheight=42,
    borderwidth=0,
    font=("Segoe UI", 10)
)


style.configure(
    "Treeview.Heading",
    background=MAROON,
    foreground=WHITE,
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    padding=(10, 9)
)


style.map(
    "Treeview",
    background=[
        ("selected", "#F1DFC0")
    ],
    foreground=[
        ("selected", TEXT)
    ]
)


style.configure(
    "Modern.TCombobox",
    fieldbackground=WHITE,
    background=WHITE,
    foreground=TEXT,
    padding=8,
    font=("Segoe UI", 10)
)


style.map(
    "Modern.TCombobox",
    fieldbackground=[
        ("readonly", WHITE)
    ],
    foreground=[
        ("readonly", TEXT)
    ]
)


# ============================================================
# MAIN AREA
# ============================================================

main_area = tk.Frame(
    root,
    bg=BG
)

main_area.pack(
    side="right",
    fill="both",
    expand=True
)


# ============================================================
# TOP BAR
# IMPORTANT:
# top_bar is outside content_frame.
# Therefore clear_content() will never destroy it.
# ============================================================

top_bar = tk.Frame(
    main_area,
    bg=CARD,
    height=55
)

top_bar.pack(
    fill="x"
)

top_bar.pack_propagate(False)


live_clock = tk.Label(
    top_bar,
    text="",
    bg=CARD,
    fg=MAROON,
    font=("Segoe UI", 10, "bold")
)

live_clock.pack(
    side="right",
    padx=30
)


# ============================================================
# PAGE CONTENT
# ============================================================

content_frame = tk.Frame(
    main_area,
    bg=BG
)

content_frame.pack(
    fill="both",
    expand=True
)


# ============================================================
# HELPERS
# ============================================================

def bhutan_now():
    return datetime.now(BHUTAN_TZ)


def clear_content():
    """
    Remove only the current page content.

    IMPORTANT:
    This does NOT destroy top_bar or live_clock.
    """

    for widget in content_frame.winfo_children():
        try:
            widget.destroy()
        except tk.TclError:
            pass


def format_check_in_time(value):
    if not value:
        return "-"

    try:
        utc_time = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )

        if utc_time.tzinfo is None:
            utc_time = utc_time.replace(
                tzinfo=ZoneInfo("UTC")
            )

        return utc_time.astimezone(
            BHUTAN_TZ
        ).strftime("%I:%M:%S %p")

    except Exception:
        return str(value)


def rounded_button(
    parent,
    text,
    command,
    width=20,
    bg=MAROON,
    fg=WHITE
):

    button = tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        height=2,
        bg=bg,
        fg=fg,
        activebackground=(
            MAROON_DARK
            if bg == MAROON
            else HOVER
        ),
        activeforeground=(
            WHITE
            if bg == MAROON
            else TEXT
        ),
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2"
    )

    def enter(_):
        try:
            if button["state"] != "disabled":
                button.configure(
                    bg=(
                        MAROON_DARK
                        if bg == MAROON
                        else HOVER
                    )
                )
        except tk.TclError:
            pass

    def leave(_):
        try:
            if button["state"] != "disabled":
                button.configure(bg=bg)
        except tk.TclError:
            pass

    button.bind(
        "<Enter>",
        enter
    )

    button.bind(
        "<Leave>",
        leave
    )

    return button


def section_title(
    parent,
    title,
    subtitle=None
):

    frame = tk.Frame(
        parent,
        bg=BG
    )

    tk.Label(
        frame,
        text=title,
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 23, "bold")
    ).pack(
        anchor="w"
    )

    if subtitle:
        tk.Label(
            frame,
            text=subtitle,
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            pady=(3, 0)
        )

    return frame


def make_card(parent):

    return tk.Frame(
        parent,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1,
        bd=0
    )


def add_bhutan_pattern(
    parent,
    bg=MAROON
):

    pattern = tk.Frame(
        parent,
        bg=bg,
        height=7
    )

    pattern.pack(
        fill="x"
    )

    pattern.pack_propagate(False)

    for i in range(24):

        tk.Label(
            pattern,
            text="◆",
            bg=bg,
            fg=(
                GOLD_LIGHT
                if i % 2 == 0
                else GOLD
            ),
            font=("Segoe UI", 6)
        ).pack(
            side="left",
            expand=True
        )


# ============================================================
# LIVE CLOCK
# ============================================================

clock_job = None


def update_clock():

    global clock_job

    try:

        if not root.winfo_exists():
            clock_job = None
            return

        if not live_clock.winfo_exists():
            clock_job = None
            return

        now = bhutan_now()

        live_clock.configure(
            text=(
                f"BHUTAN TIME  •  "
                f"{now.strftime('%d %b %Y  |  %I:%M:%S %p')}"
            )
        )

        clock_job = root.after(
            1000,
            update_clock
        )

    except tk.TclError:

        clock_job = None


# Start clock
update_clock()


# ============================================================
# SIDEBAR
# ============================================================

sidebar = tk.Frame(
    root,
    bg=MAROON_DARK,
    width=245
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(False)


# ============================================================
# BRAND
# ============================================================

brand = tk.Frame(
    sidebar,
    bg=MAROON_DARK
)

brand.pack(
    fill="x",
    padx=22,
    pady=(26, 15)
)


tk.Label(
    brand,
    text="༺  FACEATTEND  ༻",
    bg=MAROON_DARK,
    fg=GOLD_LIGHT,
    font=("Segoe UI", 18, "bold")
).pack()


tk.Label(
    brand,
    text="DIGITAL ATTENDANCE SYSTEM",
    bg=MAROON_DARK,
    fg="#E9DCCF",
    font=("Segoe UI", 8, "bold")
).pack(
    pady=(5, 0)
)


tk.Label(
    brand,
    text="འབྲུག • BHUTAN",
    bg=MAROON_DARK,
    fg=GOLD_LIGHT,
    font=("Segoe UI", 9, "bold")
).pack(
    pady=(8, 0)
)


add_bhutan_pattern(
    sidebar,
    MAROON_DARK
)


# ============================================================
# NAVIGATION
# ============================================================

nav_buttons = []


def set_active(active_button):

    for button in nav_buttons:

        try:
            button.configure(
                bg=MAROON_DARK,
                fg="#E9DCCF"
            )
        except tk.TclError:
            pass

    try:
        active_button.configure(
            bg=MAROON,
            fg=WHITE
        )
    except tk.TclError:
        pass


def navigation_button(
    text,
    command
):

    button = tk.Button(
        sidebar,
        text=text,
        command=command,
        anchor="w",
        padx=25,
        bg=MAROON_DARK,
        fg="#E9DCCF",
        activebackground=MAROON,
        activeforeground=WHITE,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        height=2
    )

    button.pack(
        fill="x",
        pady=2
    )

    def enter(_):

        try:
            if button["bg"] != MAROON:
                button.configure(
                    bg=MAROON
                )
        except tk.TclError:
            pass

    def leave(_):

        try:
            if button["bg"] != MAROON:
                button.configure(
                    bg=MAROON_DARK
                )
        except tk.TclError:
            pass

    button.bind(
        "<Enter>",
        enter
    )

    button.bind(
        "<Leave>",
        leave
    )

    nav_buttons.append(button)

    return button


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    clear_content()

    set_active(
        dashboard_nav
    )

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    hero = tk.Frame(
        content_frame,
        bg=MAROON
    )

    hero.pack(
        fill="x",
        padx=28,
        pady=(25, 0)
    )

    add_bhutan_pattern(
        hero,
        MAROON
    )

    hero_body = tk.Frame(
        hero,
        bg=MAROON
    )

    hero_body.pack(
        fill="x",
        padx=28,
        pady=22
    )

    left = tk.Frame(
        hero_body,
        bg=MAROON
    )

    left.pack(
        side="left"
    )


    tk.Label(
        left,
        text="Kuzuzangpo La! 👋",
        bg=MAROON,
        fg=GOLD_LIGHT,
        font=("Segoe UI", 11, "bold")
    ).pack(
        anchor="w"
    )


    tk.Label(
        left,
        text="Attendance Dashboard",
        bg=MAROON,
        fg=WHITE,
        font=("Segoe UI", 26, "bold")
    ).pack(
        anchor="w",
        pady=(2, 2)
    )


    tk.Label(
        left,
        text=(
            "A smarter and more reliable way "
            "to manage student attendance."
        ),
        bg=MAROON,
        fg="#F1E4DA",
        font=("Segoe UI", 10)
    ).pack(
        anchor="w"
    )


    now = bhutan_now()


    tk.Label(
        hero_body,
        text=now.strftime(
            "%A\n%d %B %Y"
        ),
        bg=MAROON,
        fg=GOLD_LIGHT,
        justify="right",
        font=("Segoe UI", 11, "bold")
    ).pack(
        side="right",
        padx=10
    )


    # --------------------------------------------------------
    # DATABASE STATISTICS
    # --------------------------------------------------------

    try:

        students_response = (
            supabase
            .table("students")
            .select("student_id")
            .execute()
        )

        students = (
            students_response.data
            or []
        )

    except Exception:

        students = []


    today = bhutan_now().date().isoformat()


    try:

        attendance_response = (
            supabase
            .table("attendance")
            .select(
                "student_id, status"
            )
            .eq(
                "attendance_date",
                today
            )
            .execute()
        )

        attendance_records = (
            attendance_response.data
            or []
        )

    except Exception:

        attendance_records = []


    unique_present_ids = {
        record.get("student_id")
        for record in attendance_records
        if record.get("status") == "Present"
    }


    present = len(
        unique_present_ids
    )

    total_students = len(
        students
    )

    absent = max(
        total_students - present,
        0
    )

    percentage = (
        present / total_students * 100
        if total_students
        else 0
    )


    # --------------------------------------------------------
    # STATISTICS CARDS
    # --------------------------------------------------------

    stats = tk.Frame(
        content_frame,
        bg=BG
    )

    stats.pack(
        fill="x",
        padx=28,
        pady=20
    )


    def stat_card(
        parent,
        title,
        value,
        subtitle,
        symbol,
        accent
    ):

        card = make_card(
            parent
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )


        top = tk.Frame(
            card,
            bg=CARD
        )

        top.pack(
            fill="x",
            padx=18,
            pady=(17, 5)
        )


        icon = tk.Label(
            top,
            text=symbol,
            bg=accent,
            fg=WHITE,
            width=3,
            height=1,
            font=("Segoe UI", 11, "bold")
        )

        icon.pack(
            side="left"
        )


        tk.Label(
            top,
            text=title,
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(
            side="left",
            padx=10
        )


        tk.Label(
            card,
            text=value,
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 24, "bold")
        ).pack(
            anchor="w",
            padx=18
        )


        tk.Label(
            card,
            text=subtitle,
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 17)
        )


        return card


    stat_card(
        stats,
        "TOTAL STUDENTS",
        str(total_students),
        "Registered students",
        "●",
        MAROON
    )


    stat_card(
        stats,
        "PRESENT TODAY",
        str(present),
        "Face attendance recorded",
        "✓",
        GREEN
    )


    stat_card(
        stats,
        "ABSENT TODAY",
        str(absent),
        "No attendance record",
        "×",
        RED
    )


    stat_card(
        stats,
        "ATTENDANCE RATE",
        f"{percentage:.1f}%",
        "Today's attendance",
        "%",
        GOLD
    )


    # --------------------------------------------------------
    # MIDDLE SECTION
    # --------------------------------------------------------

    middle = tk.Frame(
        content_frame,
        bg=BG
    )

    middle.pack(
        fill="x",
        padx=28
    )


    # --------------------------------------------------------
    # ATTENDANCE OVERVIEW
    # --------------------------------------------------------

    overview = make_card(
        middle
    )

    overview.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 7)
    )


    tk.Label(
        overview,
        text="Today's Attendance",
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 14, "bold")
    ).pack(
        anchor="w",
        padx=22,
        pady=(20, 2)
    )


    tk.Label(
        overview,
        text=(
            f"{present} of "
            f"{total_students} "
            f"students present"
        ),
        bg=CARD,
        fg=MUTED,
        font=("Segoe UI", 9)
    ).pack(
        anchor="w",
        padx=22
    )


    progress_bg = tk.Frame(
        overview,
        bg="#E8DED0",
        height=14
    )

    progress_bg.pack(
        fill="x",
        padx=22,
        pady=(16, 8)
    )

    progress_bg.pack_propagate(
        False
    )


    progress_width = max(
        int(
            min(
                percentage,
                100
            ) * 2.7
        ),
        1
    )


    progress = tk.Frame(
        progress_bg,
        bg=MAROON,
        height=14
    )

    progress.place(
        x=0,
        y=0,
        width=progress_width
    )


    if percentage >= 85:

        attendance_message = (
            "Excellent attendance today."
        )

        attendance_color = GREEN

    elif percentage >= 60:

        attendance_message = (
            "Attendance could use some attention."
        )

        attendance_color = GOLD

    else:

        attendance_message = (
            "Attendance is currently low."
        )

        attendance_color = RED


    tk.Label(
        overview,
        text=attendance_message,
        bg=CARD,
        fg=attendance_color,
        font=("Segoe UI", 9, "bold")
    ).pack(
        anchor="w",
        padx=22,
        pady=(2, 20)
    )


    # --------------------------------------------------------
    # QUICK ACTIONS
    # --------------------------------------------------------

    actions = make_card(
        middle
    )

    actions.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(7, 0)
    )


    tk.Label(
        actions,
        text="Quick Actions",
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 14, "bold")
    ).pack(
        anchor="w",
        padx=22,
        pady=(20, 12)
    )


    action_row = tk.Frame(
        actions,
        bg=CARD
    )

    action_row.pack(
        fill="x",
        padx=18
    )


    rounded_button(
        action_row,
        "📷  Take Attendance",
        open_attendance,
        width=20
    ).pack(
        side="left",
        padx=4
    )


    rounded_button(
        action_row,
        "＋  Register Student",
        open_registration,
        width=20,
        bg=WOOD
    ).pack(
        side="left",
        padx=4
    )


    rounded_button(
        actions,
        "▣  Open Reports",
        view_attendance,
        width=20,
        bg=BLUE
    ).pack(
        anchor="w",
        padx=22,
        pady=12
    )


    # --------------------------------------------------------
    # RECENT ATTENDANCE
    # --------------------------------------------------------

    recent = make_card(
        content_frame
    )

    recent.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=(15, 25)
    )


    header = tk.Frame(
        recent,
        bg=CARD
    )

    header.pack(
        fill="x",
        padx=20,
        pady=(15, 8)
    )


    tk.Label(
        header,
        text="Recent Attendance",
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 14, "bold")
    ).pack(
        side="left"
    )


    tk.Label(
        header,
        text="Latest check-ins",
        bg=CARD,
        fg=MUTED,
        font=("Segoe UI", 9)
    ).pack(
        side="left",
        padx=10
    )


    columns = (
        "student_id",
        "name",
        "course",
        "date",
        "time",
        "status"
    )


    tree = ttk.Treeview(
        recent,
        columns=columns,
        show="headings",
        height=6
    )


    headings = {
        "student_id": "Student ID",
        "name": "Student",
        "course": "Course",
        "date": "Date",
        "time": "Check-in",
        "status": "Status"
    }


    widths = {
        "student_id": 100,
        "name": 190,
        "course": 110,
        "date": 105,
        "time": 125,
        "status": 90
    }


    for column in columns:

        tree.heading(
            column,
            text=headings[column]
        )

        tree.column(
            column,
            width=widths[column],
            anchor="center"
        )


    try:

        recent_response = (
            supabase
            .table("attendance")
            .select(
                "student_id, attendance_date, "
                "status, check_in_time, "
                "courses(course_code)"
            )
            .order(
                "check_in_time",
                desc=True
            )
            .limit(8)
            .execute()
        )

        recent_records = (
            recent_response.data
            or []
        )


        student_map = {
            student["student_id"]:
                student.get("name", "-")
            for student in students
        }


        for record in recent_records:

            student_id = (
                record.get(
                    "student_id",
                    "-"
                )
            )


            course_data = record.get(
                "courses"
            )


            if isinstance(
                course_data,
                list
            ):

                course_data = (
                    course_data[0]
                    if course_data
                    else None
                )


            course_code = (
                course_data.get(
                    "course_code",
                    "-"
                )
                if isinstance(
                    course_data,
                    dict
                )
                else "-"
            )


            tree.insert(
                "",
                "end",
                values=(
                    student_id,
                    student_map.get(
                        student_id,
                        "-"
                    ),
                    course_code,
                    record.get(
                        "attendance_date",
                        "-"
                    ),
                    format_check_in_time(
                        record.get(
                            "check_in_time"
                        )
                    ),
                    record.get(
                        "status",
                        "-"
                    )
                )
            )


    except Exception:
        pass


    tree.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=(0, 15)
    )


# ============================================================
# REGISTER STUDENT
# ============================================================

def open_registration():

    set_active(
        student_nav
    )


    window = tk.Toplevel(
        root
    )

    window.title(
        "Register Student | FaceAttend"
    )

    window.geometry(
        "560x650"
    )

    window.configure(
        bg=BG
    )

    window.resizable(
        False,
        False
    )

    window.transient(
        root
    )


    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    hero = tk.Frame(
        window,
        bg=MAROON
    )

    hero.pack(
        fill="x"
    )


    add_bhutan_pattern(
        hero,
        MAROON
    )


    tk.Label(
        hero,
        text="Register Student",
        bg=MAROON,
        fg=WHITE,
        font=("Segoe UI", 23, "bold")
    ).pack(
        pady=(20, 3)
    )


    tk.Label(
        hero,
        text=(
            "Create a student profile "
            "and capture their face"
        ),
        bg=MAROON,
        fg="#F1E4DA",
        font=("Segoe UI", 9)
    ).pack(
        pady=(0, 20)
    )


    # --------------------------------------------------------
    # FORM
    # --------------------------------------------------------

    form = make_card(
        window
    )

    form.pack(
        fill="x",
        padx=45,
        pady=22
    )


    def field(
        label,
        placeholder=""
    ):

        tk.Label(
            form,
            text=label,
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(14, 5)
        )


        entry = tk.Entry(
            form,
            font=("Segoe UI", 11),
            bg=WHITE,
            fg=TEXT,
            relief="solid",
            bd=1,
            insertbackground=MAROON
        )


        entry.pack(
            fill="x",
            padx=25,
            ipady=7
        )


        return entry


    student_id_entry = field(
        "Student ID"
    )

    name_entry = field(
        "Student Name"
    )

    class_entry = field(
        "Class"
    )

    section_entry = field(
        "Section"
    )


    status_label = tk.Label(
        window,
        text="Ready to capture face",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 9)
    )

    status_label.pack()


    # --------------------------------------------------------
    # REGISTER FUNCTION
    # --------------------------------------------------------

    def register():

        student_id = (
            student_id_entry
            .get()
            .strip()
        )

        name = (
            name_entry
            .get()
            .strip()
        )

        student_class = (
            class_entry
            .get()
            .strip()
        )

        section = (
            section_entry
            .get()
            .strip()
        )


        if not student_id or not name:

            messagebox.showwarning(
                "Missing Information",
                "Student ID and name are required.",
                parent=window
            )

            return


        status_label.configure(
            text=(
                "Opening camera and "
                "registering student..."
            ),
            fg=MAROON
        )


        window.update_idletasks()

        window.withdraw()


        try:

            success, message = register_student(
                student_id,
                name,
                student_class,
                section
            )

        except Exception as e:

            success = False
            message = str(e)


        try:
            window.deiconify()
        except tk.TclError:
            return


        if success:

            messagebox.showinfo(
                "Registration Successful",
                message,
                parent=window
            )


            window.destroy()

            show_dashboard()


        else:

            status_label.configure(
                text=(
                    "Registration failed. "
                    "Please try again."
                ),
                fg=RED
            )


            messagebox.showerror(
                "Registration Error",
                message,
                parent=window
            )


    # --------------------------------------------------------
    # BUTTONS
    # --------------------------------------------------------

    rounded_button(
        window,
        "📷  Capture Face & Register",
        register,
        width=31
    ).pack(
        pady=(5, 8)
    )


    tk.Button(
        window,
        text="Cancel",
        command=window.destroy,
        bg=BG,
        fg=MUTED,
        activebackground=HOVER,
        activeforeground=TEXT,
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2"
    ).pack(
        pady=(0, 15)
    )


# ============================================================
# TAKE ATTENDANCE
# ============================================================

def open_attendance():

    set_active(
        attendance_nav
    )


    window = tk.Toplevel(
        root
    )

    window.title(
        "Take Attendance | FaceAttend"
    )

    window.geometry(
        "650x520"
    )

    window.configure(
        bg=BG
    )

    window.resizable(
        False,
        False
    )

    window.transient(
        root
    )


    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    hero = tk.Frame(
        window,
        bg=MAROON
    )

    hero.pack(
        fill="x"
    )


    add_bhutan_pattern(
        hero,
        MAROON
    )


    tk.Label(
        hero,
        text="Face Recognition Attendance",
        bg=MAROON,
        fg=WHITE,
        font=("Segoe UI", 22, "bold")
    ).pack(
        pady=(20, 3)
    )


    tk.Label(
        hero,
        text=(
            "Select a course and start "
            "the external camera"
        ),
        bg=MAROON,
        fg="#F1E4DA",
        font=("Segoe UI", 9)
    ).pack(
        pady=(0, 20)
    )


    # --------------------------------------------------------
    # COURSE CARD
    # --------------------------------------------------------

    card = make_card(
        window
    )

    card.pack(
        fill="x",
        padx=55,
        pady=25
    )


    tk.Label(
        card,
        text="COURSE",
        bg=CARD,
        fg=MUTED,
        font=("Segoe UI", 9, "bold")
    ).pack(
        anchor="w",
        padx=28,
        pady=(22, 7)
    )


    try:

        response = (
            supabase
            .table("courses")
            .select(
                "course_id, "
                "course_code, "
                "course_name, "
                "teacher"
            )
            .order("course_id")
            .execute()
        )

        courses = (
            response.data
            or []
        )


    except Exception as e:

        window.destroy()

        messagebox.showerror(
            "Database Error",
            f"Could not load courses.\n\n{e}",
            parent=root
        )

        return


    if not courses:

        window.destroy()

        messagebox.showwarning(
            "No Courses",
            (
                "Please add a course "
                "before taking attendance."
            ),
            parent=root
        )

        return


    course_values = [
        (
            f"{course['course_code']} "
            f"— {course['course_name']}"
        )
        for course in courses
    ]


    combo = ttk.Combobox(
        card,
        values=course_values,
        state="readonly",
        width=54,
        style="Modern.TCombobox"
    )

    combo.pack(
        fill="x",
        padx=28
    )

    combo.current(0)


    teacher_label = tk.Label(
        card,
        text="",
        bg=CARD,
        fg=MUTED,
        font=("Segoe UI", 9)
    )

    teacher_label.pack(
        pady=(9, 5)
    )


    camera_status = tk.Label(
        card,
        text="● External camera ready",
        bg=CARD,
        fg=GREEN,
        font=("Segoe UI", 9, "bold")
    )

    camera_status.pack(
        pady=(2, 20)
    )


    def update_course_info(
        _=None
    ):

        index = combo.current()

        if index >= 0:

            teacher = (
                courses[index].get(
                    "teacher"
                )
                or "Teacher not specified"
            )

            teacher_label.configure(
                text=f"Instructor: {teacher}"
            )


    combo.bind(
        "<<ComboboxSelected>>",
        update_course_info
    )

    update_course_info()


    # --------------------------------------------------------
    # START ATTENDANCE
    # --------------------------------------------------------

    def start():

        index = combo.current()


        if index == -1:

            messagebox.showwarning(
                "Select Course",
                "Please select a course.",
                parent=window
            )

            return


        course = courses[index]


        window.withdraw()


        try:

            success, message = take_attendance(
                course["course_id"],
                course["course_code"],
                course["course_name"]
            )

        except Exception as e:

            success = False
            message = str(e)


        try:
            window.deiconify()
        except tk.TclError:
            return


        if success:

            messagebox.showinfo(
                "Attendance Complete",
                message,
                parent=window
            )


            window.destroy()

            show_dashboard()


        else:

            messagebox.showerror(
                "Attendance Error",
                message,
                parent=window
            )


    rounded_button(
        window,
        "◎  Start Face Recognition",
        start,
        width=31
    ).pack(
        pady=(0, 10)
    )


    tk.Button(
        window,
        text="Cancel",
        command=window.destroy,
        bg=BG,
        fg=MUTED,
        activebackground=HOVER,
        activeforeground=TEXT,
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2"
    ).pack()


# ============================================================
# REPORTS
# ============================================================

def view_attendance():

    set_active(
        reports_nav
    )


    window = tk.Toplevel(
        root
    )

    window.title(
        "Attendance Reports | FaceAttend"
    )

    window.geometry(
        "1150x690"
    )

    window.configure(
        bg=BG
    )

    window.minsize(
        1000,
        600
    )


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title = section_title(
        window,
        "Attendance Reports",
        "Review attendance by course and date"
    )

    title.pack(
        anchor="w",
        padx=30,
        pady=(25, 15)
    )


    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    filter_frame = make_card(
        window
    )

    filter_frame.pack(
        fill="x",
        padx=30,
        pady=(0, 15)
    )


    tk.Label(
        filter_frame,
        text="COURSE",
        bg=CARD,
        fg=MUTED,
        font=("Segoe UI", 8, "bold")
    ).grid(
        row=0,
        column=0,
        padx=(20, 7),
        pady=18
    )


    try:

        course_response = (
            supabase
            .table("courses")
            .select(
                "course_id, "
                "course_code, "
                "course_name"
            )
            .order("course_id")
            .execute()
        )

        courses = (
            course_response.data
            or []
        )


    except Exception as e:

        messagebox.showerror(
            "Error",
            f"Could not load courses.\n\n{e}",
            parent=window
        )

        window.destroy()

        return


    course_values = [
        (
            f"{course['course_code']} "
            f"— {course['course_name']}"
        )
        for course in courses
    ]


    course_combo = ttk.Combobox(
        filter_frame,
        values=course_values,
        state="readonly",
        width=35,
        style="Modern.TCombobox"
    )

    course_combo.grid(
        row=0,
        column=1,
        padx=5
    )


    if courses:
        course_combo.current(0)


    tk.Label(
        filter_frame,
        text="DATE",
        bg=CARD,
        fg=MUTED,
        font=("Segoe UI", 8, "bold")
    ).grid(
        row=0,
        column=2,
        padx=(25, 7)
    )


    date_entry = tk.Entry(
        filter_frame,
        width=14,
        font=("Segoe UI", 10),
        relief="solid",
        bd=1
    )

    date_entry.grid(
        row=0,
        column=3,
        padx=5,
        ipady=5
    )

    date_entry.insert(
        0,
        bhutan_now().date().isoformat()
    )


    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    table_card = make_card(
        window
    )

    table_card.pack(
        fill="both",
        expand=True,
        padx=30
    )


    columns = (
        "student_id",
        "name",
        "class",
        "section",
        "status",
        "check_in_time"
    )


    tree = ttk.Treeview(
        table_card,
        columns=columns,
        show="headings"
    )


    headings = {
        "student_id": "Student ID",
        "name": "Name",
        "class": "Class",
        "section": "Section",
        "status": "Status",
        "check_in_time": "Check-in Time"
    }


    widths = {
        "student_id": 120,
        "name": 240,
        "class": 100,
        "section": 100,
        "status": 120,
        "check_in_time": 160
    }


    for column in columns:

        tree.heading(
            column,
            text=headings[column]
        )

        tree.column(
            column,
            width=widths[column],
            anchor="center"
        )


    scrollbar = ttk.Scrollbar(
        table_card,
        orient="vertical",
        command=tree.yview
    )


    tree.configure(
        yscrollcommand=scrollbar.set
    )


    tree.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(12, 0),
        pady=12
    )


    scrollbar.pack(
        side="right",
        fill="y",
        padx=(0, 12),
        pady=12
    )


    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    footer = tk.Frame(
        window,
        bg=BG
    )

    footer.pack(
        fill="x",
        padx=30,
        pady=15
    )


    summary = tk.Label(
        footer,
        text=(
            "Present: 0    "
            "Absent: 0    "
            "Total: 0"
        ),
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    )

    summary.pack(
        side="left"
    )


    # --------------------------------------------------------
    # LOAD ATTENDANCE
    # --------------------------------------------------------

    def load():

        if not courses:
            return


        selected_index = (
            course_combo.current()
        )


        if selected_index == -1:

            messagebox.showwarning(
                "Select Course",
                "Please select a course.",
                parent=window
            )

            return


        selected_date = (
            date_entry
            .get()
            .strip()
        )


        try:

            datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            )

        except ValueError:

            messagebox.showerror(
                "Invalid Date",
                "Please use YYYY-MM-DD.",
                parent=window
            )

            return


        course_id = (
            courses[selected_index]
            ["course_id"]
        )


        for item in tree.get_children():

            tree.delete(item)


        # ----------------------------------------------------
        # LOAD STUDENTS
        # ----------------------------------------------------

        try:

            student_response = (
                supabase
                .table("students")
                .select(
                    "student_id, "
                    "name, "
                    "class, "
                    "section"
                )
                .order("student_id")
                .execute()
            )

            students = (
                student_response.data
                or []
            )


        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Could not load students.\n\n{e}",
                parent=window
            )

            return


        # ----------------------------------------------------
        # LOAD ATTENDANCE
        # ----------------------------------------------------

        try:

            attendance_response = (
                supabase
                .table("attendance")
                .select(
                    "student_id, "
                    "status, "
                    "check_in_time"
                )
                .eq(
                    "course_id",
                    course_id
                )
                .eq(
                    "attendance_date",
                    selected_date
                )
                .execute()
            )

            attendance_records = (
                attendance_response.data
                or []
            )


        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Could not load attendance.\n\n{e}",
                parent=window
            )

            return


        # ----------------------------------------------------
        # CREATE ATTENDANCE LOOKUP
        # ----------------------------------------------------

        attendance_lookup = {
            record["student_id"]: {
                "status": record.get(
                    "status",
                    "Absent"
                ),
                "check_in_time": record.get(
                    "check_in_time"
                )
            }
            for record in attendance_records
        }


        present_count = 0
        absent_count = 0


        # ----------------------------------------------------
        # DISPLAY STUDENTS
        # ----------------------------------------------------

        for student in students:

            student_id = (
                student["student_id"]
            )


            info = attendance_lookup.get(
                student_id
            )


            if info:

                status = info["status"]

                check_in_time = (
                    format_check_in_time(
                        info.get(
                            "check_in_time"
                        )
                    )
                )

            else:

                status = "Absent"

                check_in_time = "-"


            if status == "Present":

                present_count += 1

            else:

                absent_count += 1


            tree.insert(
                "",
                "end",
                values=(
                    student_id,
                    student.get(
                        "name",
                        "-"
                    ),
                    student.get(
                        "class",
                        "-"
                    ),
                    student.get(
                        "section",
                        "-"
                    ),
                    status,
                    check_in_time
                )
            )


        total = len(
            students
        )


        rate = (
            present_count /
            total *
            100
            if total
            else 0
        )


        summary.configure(
            text=(
                f"Present: {present_count}    "
                f"Absent: {absent_count}    "
                f"Total: {total}    "
                f"Attendance Rate: {rate:.1f}%"
            )
        )


    rounded_button(
        footer,
        "↻  Load Attendance",
        load,
        width=18
    ).pack(
        side="right"
    )


    if courses:
        load()


# ============================================================
# COURSE MANAGEMENT
# ============================================================

def manage_courses():

    set_active(
        courses_nav
    )


    window = tk.Toplevel(
        root
    )

    window.title(
        "Manage Courses | FaceAttend"
    )

    window.geometry(
        "1080x700"
    )

    window.configure(
        bg=BG
    )

    window.minsize(
        950,
        620
    )


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title = section_title(
        window,
        "Manage Courses",
        "Add, update and remove courses"
    )

    title.pack(
        anchor="w",
        padx=30,
        pady=(25, 15)
    )


    # --------------------------------------------------------
    # FORM
    # --------------------------------------------------------

    form = make_card(
        window
    )

    form.pack(
        fill="x",
        padx=30,
        pady=(0, 18)
    )


    labels = [
        "Course Code",
        "Course Name",
        "Teacher"
    ]


    entries = []


    for index, label in enumerate(labels):

        tk.Label(
            form,
            text=label.upper(),
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).grid(
            row=0,
            column=index * 2,
            padx=(
                18 if index == 0 else 12,
                6
            ),
            pady=(17, 5),
            sticky="w"
        )


        entry = tk.Entry(
            form,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=(
                20
                if index != 1
                else 30
            )
        )


        entry.grid(
            row=1,
            column=index * 2,
            columnspan=2,
            padx=(
                18 if index == 0 else 12,
                6
            ),
            pady=(0, 17),
            ipady=6,
            sticky="ew"
        )


        entries.append(entry)


    code_entry, name_entry, teacher_entry = (
        entries
    )


    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    table_card = make_card(
        window
    )

    table_card.pack(
        fill="both",
        expand=True,
        padx=30
    )


    columns = (
        "course_id",
        "course_code",
        "course_name",
        "teacher"
    )


    tree = ttk.Treeview(
        table_card,
        columns=columns,
        show="headings"
    )


    tree.heading(
        "course_id",
        text="ID"
    )

    tree.heading(
        "course_code",
        text="Course Code"
    )

    tree.heading(
        "course_name",
        text="Course Name"
    )

    tree.heading(
        "teacher",
        text="Teacher"
    )


    tree.column(
        "course_id",
        width=70,
        anchor="center"
    )

    tree.column(
        "course_code",
        width=170,
        anchor="center"
    )

    tree.column(
        "course_name",
        width=420
    )

    tree.column(
        "teacher",
        width=260
    )


    tree.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=12
    )


    # --------------------------------------------------------
    # FORM HELPERS
    # --------------------------------------------------------

    def clear_form():

        for entry in entries:

            entry.delete(
                0,
                tk.END
            )


    # --------------------------------------------------------
    # LOAD COURSES
    # --------------------------------------------------------

    def load_courses():

        for item in tree.get_children():

            tree.delete(item)


        try:

            response = (
                supabase
                .table("courses")
                .select(
                    "course_id, "
                    "course_code, "
                    "course_name, "
                    "teacher"
                )
                .order("course_id")
                .execute()
            )


            for course in (
                response.data
                or []
            ):

                tree.insert(
                    "",
                    "end",
                    values=(
                        course.get(
                            "course_id"
                        ),
                        course.get(
                            "course_code"
                        ),
                        course.get(
                            "course_name"
                        ),
                        course.get(
                            "teacher"
                        ) or "-"
                    )
                )


        except Exception as e:

            messagebox.showerror(
                "Database Error",
                f"Could not load courses.\n\n{e}",
                parent=window
            )


    # --------------------------------------------------------
    # SELECT COURSE
    # --------------------------------------------------------

    def select_course(
        _=None
    ):

        selected = tree.selection()


        if not selected:
            return


        values = tree.item(
            selected[0],
            "values"
        )


        clear_form()


        code_entry.insert(
            0,
            values[1]
        )

        name_entry.insert(
            0,
            values[2]
        )

        teacher_entry.insert(
            0,
            values[3]
        )


    tree.bind(
        "<<TreeviewSelect>>",
        select_course
    )


    # --------------------------------------------------------
    # ADD COURSE
    # --------------------------------------------------------

    def add_course():

        code = (
            code_entry
            .get()
            .strip()
        )

        name = (
            name_entry
            .get()
            .strip()
        )

        teacher = (
            teacher_entry
            .get()
            .strip()
        )


        if not code or not name:

            messagebox.showwarning(
                "Missing Information",
                (
                    "Course code and "
                    "course name are required."
                ),
                parent=window
            )

            return


        try:

            supabase.table(
                "courses"
            ).insert({
                "course_code": code,
                "course_name": name,
                "teacher": teacher
            }).execute()


            messagebox.showinfo(
                "Success",
                "Course added successfully.",
                parent=window
            )


            clear_form()

            load_courses()


        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Could not add course.\n\n{e}",
                parent=window
            )


    # --------------------------------------------------------
    # UPDATE COURSE
    # --------------------------------------------------------

    def update_course():

        selected = tree.selection()


        if not selected:

            messagebox.showwarning(
                "Select Course",
                (
                    "Please select a course "
                    "to update."
                ),
                parent=window
            )

            return


        values = tree.item(
            selected[0],
            "values"
        )


        course_id = values[0]


        code = (
            code_entry
            .get()
            .strip()
        )

        name = (
            name_entry
            .get()
            .strip()
        )

        teacher = (
            teacher_entry
            .get()
            .strip()
        )


        if not code or not name:

            messagebox.showwarning(
                "Missing Information",
                (
                    "Course code and "
                    "course name are required."
                ),
                parent=window
            )

            return


        try:

            supabase.table(
                "courses"
            ).update({
                "course_code": code,
                "course_name": name,
                "teacher": teacher
            }).eq(
                "course_id",
                course_id
            ).execute()


            messagebox.showinfo(
                "Success",
                "Course updated successfully.",
                parent=window
            )


            clear_form()

            load_courses()


        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Could not update course.\n\n{e}",
                parent=window
            )


    # --------------------------------------------------------
    # DELETE COURSE
    # --------------------------------------------------------

    def delete_course():

        selected = tree.selection()


        if not selected:

            messagebox.showwarning(
                "Select Course",
                (
                    "Please select a course "
                    "to delete."
                ),
                parent=window
            )

            return


        values = tree.item(
            selected[0],
            "values"
        )


        course_id = values[0]

        course_code = values[1]


        confirm = messagebox.askyesno(
            "Delete Course",
            (
                f"Are you sure you want "
                f"to delete {course_code}?"
            ),
            parent=window
        )


        if not confirm:
            return


        try:

            supabase.table(
                "courses"
            ).delete().eq(
                "course_id",
                course_id
            ).execute()


            messagebox.showinfo(
                "Deleted",
                "Course deleted successfully.",
                parent=window
            )


            clear_form()

            load_courses()


        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Could not delete course.\n\n{e}",
                parent=window
            )


    # --------------------------------------------------------
    # BUTTONS
    # --------------------------------------------------------

    button_frame = tk.Frame(
        window,
        bg=BG
    )

    button_frame.pack(
        pady=17
    )


    rounded_button(
        button_frame,
        "＋ Add Course",
        add_course,
        width=16
    ).pack(
        side="left",
        padx=5
    )


    rounded_button(
        button_frame,
        "✎ Update",
        update_course,
        width=16,
        bg=WOOD
    ).pack(
        side="left",
        padx=5
    )


    rounded_button(
        button_frame,
        "× Delete",
        delete_course,
        width=16,
        bg=RED
    ).pack(
        side="left",
        padx=5
    )


    rounded_button(
        button_frame,
        "↻ Refresh",
        load_courses,
        width=16,
        bg=BLUE
    ).pack(
        side="left",
        padx=5
    )


    load_courses()


# ============================================================
# NAVIGATION BUTTONS
# IMPORTANT:
# These are created AFTER all page functions exist.
# ============================================================

dashboard_nav = navigation_button(
    "  ◈   Dashboard",
    show_dashboard
)


student_nav = navigation_button(
    "  ◉   Students",
    open_registration
)


attendance_nav = navigation_button(
    "  ◎   Attendance",
    open_attendance
)


courses_nav = navigation_button(
    "  ▣   Courses",
    manage_courses
)


reports_nav = navigation_button(
    "  ◫   Reports",
    view_attendance
)


# ============================================================
# SIDEBAR SPACER
# ============================================================

tk.Frame(
    sidebar,
    bg=MAROON_DARK
).pack(
    fill="both",
    expand=True
)


# ============================================================
# SETTINGS
# ============================================================

settings_nav = navigation_button(
    "  ⚙   Settings",
    lambda: messagebox.showinfo(
        "Settings",
        (
            "Settings module is reserved "
            "for future configuration."
        ),
        parent=root
    )
)


# ============================================================
# SAFE APPLICATION EXIT
# ============================================================

def close_application():

    global clock_job

    # Cancel the repeating clock callback
    if clock_job is not None:

        try:

            root.after_cancel(
                clock_job
            )

        except tk.TclError:
            pass

        clock_job = None


    # Close application
    try:
        root.destroy()
    except tk.TclError:
        pass


# ============================================================
# EXIT
# ============================================================

logout_nav = navigation_button(
    "  ⇥   Exit",
    close_application
)


# ============================================================
# WINDOW CLOSE BUTTON
# ============================================================

root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# ============================================================
# START DASHBOARD
# ============================================================

show_dashboard()


# ============================================================
# MAIN LOOP
# ============================================================

root.mainloop()