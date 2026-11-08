import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from dotenv import load_dotenv
from supabase import create_client

from register_student import register_student
from attendance import take_attendance
from attendance_report import build_report_page

from ui_helpers import (
    setup_ttk_styles, center_window, try_set_icon, add_bhutan_pattern,
    make_top_bar, make_card, make_hero, rounded_button, empty_state_label,
    bhutan_now, format_check_in_time, BG, CARD, WHITE, NAVY, NAVY_DARK,
    GOLD, GOLD_LIGHT, WOOD, SLATE, TEXT, MUTED, BORDER, GREEN, RED, BLUE, HOVER
)

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials are blank!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

CLASS_OPTIONS = ["B.Ed IT", "B.Ed Geo/Eng", "B.Ed His/Eng", "B.Ed Bio/Chem", "B.Ed Phy/Math"]
YEAR_OPTIONS = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
CAMERA_OPTIONS = {"Camera 0": 0, "Camera 1": 1, "Camera 2": 2}

root = tk.Tk()
root.title("FaceAttend | Bhutan Digital Attendance System")
root.minsize(1050, 680)
root.configure(bg=BG)
try_set_icon(root)
center_window(root, 1280, 760)
setup_ttk_styles()

main_area = tk.Frame(root, bg=BG)
main_area.pack(side="right", fill="both", expand=True)
make_top_bar(main_area)

content_frame = tk.Frame(main_area, bg=BG)
content_frame.pack(fill="both", expand=True)


def clear_content():
    for widget in content_frame.winfo_children():
        try: widget.destroy()
        except tk.TclError: pass


def show_loading(message="Loading..."):
    loading = tk.Toplevel(root)
    loading.title("Please Wait")
    loading.geometry("350x120")
    loading.configure(bg=BG)
    loading.transient(root)
    loading.grab_set()

    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - 175
    y = root.winfo_y() + (root.winfo_height() // 2) - 60
    loading.geometry(f"+{x}+{y}")

    tk.Label(loading, text=message, bg=BG, fg=NAVY,
             font=("Segoe UI", 11, "bold"), justify="center").pack(expand=True)
    root.update()
    return loading


def preview_camera(index):
    """Opens a small 4-second preview window for the chosen camera index."""
    def _run():
        try:
            import cv2
            import time
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if not cap.isOpened():
                root.after(0, lambda: messagebox.showerror(
                    "Camera", f"Camera {index} is not available.", parent=root))
                return
            for _ in range(10): cap.read()
            start = time.time()
            try:
                while time.time() - start < 4:
                    ret, frame = cap.read()
                    if not ret: break
                    if frame.shape[1] > 960:
                        scale = 960 / frame.shape[1]
                        frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
                    cv2.putText(frame, f"Camera {index} | Close window to stop", (20, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow(f"Camera {index} Preview", frame)
                    if cv2.waitKey(1) & 0xFF != 255: break
            finally:
                cap.release()
                cv2.destroyAllWindows()
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Camera", str(e), parent=root))
    threading.Thread(target=_run, daemon=True).start()


# ---------------- SIDEBAR ----------------
sidebar = tk.Frame(root, bg=NAVY_DARK, width=245)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

brand = tk.Frame(sidebar, bg=NAVY_DARK)
brand.pack(fill="x", padx=22, pady=(26, 15))
tk.Label(brand, text="༺  FACEATTEND  ༻", bg=NAVY_DARK, fg=GOLD_LIGHT,
         font=("Segoe UI", 18, "bold")).pack()
tk.Label(brand, text="DIGITAL ATTENDANCE SYSTEM", bg=NAVY_DARK, fg="#DCE6F0",
         font=("Segoe UI", 8, "bold")).pack(pady=(5, 0))
tk.Label(brand, text="འབྲུག • BHUTAN", bg=NAVY_DARK, fg=GOLD_LIGHT,
         font=("Segoe UI", 9, "bold")).pack(pady=(8, 0))
add_bhutan_pattern(sidebar, NAVY_DARK)

nav_buttons = []
active_nav = None


def set_active(active_button):
    global active_nav
    active_nav = active_button
    for button in nav_buttons:
        try: button.configure(bg=NAVY_DARK, fg="#DCE6F0")
        except tk.TclError: pass
    try: active_button.configure(bg=NAVY, fg=WHITE)
    except tk.TclError: pass


def navigation_button(text, command):
    button = tk.Button(sidebar, text=text, command=command, anchor="w", padx=25,
                       bg=NAVY_DARK, fg="#DCE6F0", activebackground=NAVY,
                       activeforeground=WHITE, font=("Segoe UI", 10, "bold"),
                       relief="flat", bd=0, cursor="hand2", height=2)
    button.pack(fill="x", pady=2)

    def enter(_):
        if button is not active_nav:
            try: button.configure(bg=NAVY)
            except tk.TclError: pass

    def leave(_):
        if button is not active_nav:
            try: button.configure(bg=NAVY_DARK)
            except tk.TclError: pass

    button.bind("<Enter>", enter)
    button.bind("<Leave>", leave)
    nav_buttons.append(button)
    return button


# ---------------- PAGE: DASHBOARD ----------------
def show_dashboard():
    clear_content()
    set_active(dashboard_nav)

    # HERO (fast, no queries)
    hero = tk.Frame(content_frame, bg=NAVY)
    hero.pack(fill="x", padx=28, pady=(25, 0))
    add_bhutan_pattern(hero, NAVY)
    hero_body = tk.Frame(hero, bg=NAVY)
    hero_body.pack(fill="x", padx=28, pady=22)
    left = tk.Frame(hero_body, bg=NAVY); left.pack(side="left")
    tk.Label(left, text="Kuzuzangpo La! 👋", bg=NAVY, fg=GOLD_LIGHT,
             font=("Segoe UI", 11, "bold")).pack(anchor="w")
    tk.Label(left, text="Attendance Dashboard", bg=NAVY, fg=WHITE,
             font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(2, 2))
    tk.Label(left, text="A smarter and more reliable way to manage student attendance.",
             bg=NAVY, fg="#DCE6F0", font=("Segoe UI", 10)).pack(anchor="w")
    now = bhutan_now()
    tk.Label(hero_body, text=now.strftime("%A\n%d %B %Y"), bg=NAVY, fg=GOLD_LIGHT,
             justify="right", font=("Segoe UI", 11, "bold")).pack(side="right", padx=10)

    # STAT CARDS (placeholders, filled in by async fetch)
    total_var   = tk.StringVar(value="…")
    present_var = tk.StringVar(value="…")
    absent_var  = tk.StringVar(value="…")
    rate_var    = tk.StringVar(value="…")

    stats = tk.Frame(content_frame, bg=BG)
    stats.pack(fill="x", padx=28, pady=20)

    def stat_card(parent, title, value_var, subtitle, symbol, accent):
        card = make_card(parent)
        card.pack(side="left", fill="both", expand=True, padx=5)
        top = tk.Frame(card, bg=CARD)
        top.pack(fill="x", padx=18, pady=(17, 5))
        tk.Label(top, text=symbol, bg=accent, fg=WHITE, width=3, height=1,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(top, text=title, bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=10)
        tk.Label(card, textvariable=value_var, bg=CARD, fg=TEXT,
                 font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=18)
        tk.Label(card, text=subtitle, bg=CARD, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=18, pady=(0, 17))

    stat_card(stats, "TOTAL STUDENTS",  total_var,   "Registered students",      "●", NAVY)
    stat_card(stats, "PRESENT TODAY",   present_var, "Face attendance recorded", "✓", GREEN)
    stat_card(stats, "ABSENT TODAY",    absent_var,  "No attendance record",     "×", RED)
    stat_card(stats, "ATTENDANCE RATE", rate_var,    "Today's attendance",       "%", GOLD)

    # MIDDLE ROW
    middle = tk.Frame(content_frame, bg=BG)
    middle.pack(fill="x", padx=28)

    overview = make_card(middle)
    overview.pack(side="left", fill="both", expand=True, padx=(0, 7))
    tk.Label(overview, text="Today's Attendance", bg=CARD, fg=TEXT,
             font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=22, pady=(20, 2))
    progress_text = tk.StringVar(value="Loading…")
    tk.Label(overview, textvariable=progress_text, bg=CARD, fg=MUTED,
             font=("Segoe UI", 9)).pack(anchor="w", padx=22)
    progress_bg = tk.Frame(overview, bg="#DCE6F0", height=14)
    progress_bg.pack(fill="x", padx=22, pady=(16, 8))
    progress_bg.pack_propagate(False)
    progress_fill = tk.Frame(progress_bg, bg=NAVY, height=14)
    progress_fill.place(x=0, y=0, relwidth=0)
    msg_var = tk.StringVar(value="")
    msg_label = tk.Label(overview, textvariable=msg_var, bg=CARD, fg=GOLD,
                         font=("Segoe UI", 9, "bold"))
    msg_label.pack(anchor="w", padx=22, pady=(2, 20))

    actions = make_card(middle)
    actions.pack(side="left", fill="both", expand=True, padx=(7, 0))
    tk.Label(actions, text="Quick Actions", bg=CARD, fg=TEXT,
             font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=22, pady=(20, 12))
    row = tk.Frame(actions, bg=CARD)
    row.pack(fill="x", padx=18)
    rounded_button(row, "📷  Take Attendance",  show_attendance_page,   width=20).pack(side="left", padx=4)
    rounded_button(row, "＋  Register Student", show_registration_page, width=20, bg=WOOD).pack(side="left", padx=4)
    rounded_button(actions, "◫  Open Reports", show_report_page, width=20, bg=BLUE).pack(anchor="w", padx=22, pady=12)

    # RECENT TABLE
    recent = make_card(content_frame)
    recent.pack(fill="both", expand=True, padx=28, pady=(15, 25))
    header = tk.Frame(recent, bg=CARD)
    header.pack(fill="x", padx=20, pady=(15, 8))
    tk.Label(header, text="Recent Attendance", bg=CARD, fg=TEXT,
             font=("Segoe UI", 14, "bold")).pack(side="left")
    tk.Label(header, text="Latest check-ins", bg=CARD, fg=MUTED,
             font=("Segoe UI", 9)).pack(side="left", padx=10)
    table_frame = tk.Frame(recent, bg=CARD)
    table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    columns = ("student_id", "name", "course", "date", "time", "status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
    headings = {"student_id": "Student ID", "name": "Student", "course": "Course",
                "date": "Date", "time": "Check-in", "status": "Status"}
    widths = {"student_id": 100, "name": 190, "course": 110,
              "date": 105, "time": 125, "status": 90}
    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, width=widths[col], anchor="center")
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    empty = empty_state_label(table_frame, "Loading…")
    empty.place(relx=0.5, rely=0.5, anchor="center")

    # ASYNC DATA FETCH
    def apply(data):
        try:
            if not content_frame.winfo_exists():
                return
            if data.get("error"):
                total_var.set("—"); present_var.set("—")
                absent_var.set("—"); rate_var.set("—")
                progress_text.set(f"Could not load data: {data['error']}")
                return

            students = data["students"]
            records = data["attendance"]
            recent_records = data["recent"]
            course_map = data["courses"]
            student_map = {str(s["student_id"]): s.get("name", "-") for s in students}

            present_ids = {r.get("student_id") for r in records if r.get("status") == "Present"}
            present = len(present_ids)
            total = len(students)
            absent = max(total - present, 0)
            pct = (present / total * 100) if total else 0

            total_var.set(str(total))
            present_var.set(str(present))
            absent_var.set(str(absent))
            rate_var.set(f"{pct:.1f}%")
            progress_text.set(f"{present} of {total} students present")
            progress_fill.place(x=0, y=0, relwidth=max(min(pct, 100), 0) / 100)

            if pct >= 85:
                msg_var.set("Excellent attendance today.");        msg_label.configure(fg=GREEN)
            elif pct >= 60:
                msg_var.set("Attendance could use some attention."); msg_label.configure(fg=GOLD)
            else:
                msg_var.set("Attendance is currently low.");       msg_label.configure(fg=RED)

            for i in tree.get_children(): tree.delete(i)
            if recent_records:
                empty.place_forget()
                for r in recent_records:
                    sid = str(r.get("student_id", "-"))
                    cid = r.get("course_id")
                    tree.insert("", "end", values=(
                        sid,
                        student_map.get(sid, "-"),
                        course_map.get(str(cid), "-"),
                        r.get("attendance_date", "-"),
                        format_check_in_time(r.get("attendance_time")),
                        r.get("status", "-"),
                    ))
            else:
                empty.configure(text="No attendance yet.")
        except tk.TclError:
            pass  # widgets already destroyed (user navigated away)

    def fetch():
        try:
            students = supabase.table("students").select("student_id, name").execute().data or []
            today = bhutan_now().date().isoformat()
            att = (supabase.table("attendance")
                   .select("student_id, status")
                   .eq("attendance_date", today)
                   .execute().data or [])
            recent_q = (supabase.table("attendance")
                        .select("student_id, attendance_date, attendance_time, status, course_id")
                        .order("attendance_date", desc=True)
                        .order("attendance_time", desc=True)
                        .limit(8).execute().data or [])
            courses = {str(c["course_id"]): c.get("course_code", "-")
                       for c in (supabase.table("courses")
                                 .select("course_id, course_code")
                                 .execute().data or [])}
            data = {"students": students, "attendance": att,
                    "recent": recent_q, "courses": courses}
        except Exception as e:
            data = {"error": str(e)}
        root.after(0, lambda: apply(data))

    threading.Thread(target=fetch, daemon=True).start()


# ---------------- PAGE: REGISTER ----------------
def show_registration_page():
    clear_content()
    set_active(student_nav)
    make_hero(content_frame, "Register Student",
              "Create a student profile and capture their face", on_back=show_dashboard)
    form = make_card(content_frame)
    form.pack(fill="x", padx=80, pady=20)

    def field(label, values=None):
        tk.Label(form, text=label, bg=CARD, fg=TEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=30, pady=(12, 5))
        if values is not None:
            w = ttk.Combobox(form, values=values, state="readonly",
                             font=("Segoe UI", 10), style="Modern.TCombobox")
            w.pack(fill="x", padx=30)
        else:
            w = tk.Entry(form, font=("Segoe UI", 11), bg=WHITE, fg=TEXT,
                         relief="solid", bd=1, insertbackground=NAVY)
            w.pack(fill="x", padx=30, ipady=7)
        return w

    student_id_entry = field("Student ID")
    name_entry = field("Student Name")
    class_entry = field("Class", values=CLASS_OPTIONS)
    year_entry = field("Year", values=YEAR_OPTIONS)
    section_entry = field("Section")

    cam_frame = tk.Frame(content_frame, bg=BG)
    cam_frame.pack(pady=8)
    tk.Label(cam_frame, text="Camera:", bg=BG, fg=MUTED,
             font=("Segoe UI", 9)).pack(side="left", padx=5)
    cam_var = tk.StringVar(value="Camera 0")
    cam_combo = ttk.Combobox(cam_frame, textvariable=cam_var, state="readonly",
                             width=18, style="Modern.TCombobox")
    cam_combo["values"] = list(CAMERA_OPTIONS.keys())
    cam_combo.pack(side="left", padx=8)
    tk.Button(cam_frame, text="Preview",
              command=lambda: preview_camera(CAMERA_OPTIONS.get(cam_var.get(), 0)),
              bg=NAVY, fg=WHITE, activebackground=NAVY_DARK, activeforeground=WHITE,
              relief="flat", padx=14, pady=5, cursor="hand2",
              font=("Segoe UI", 9, "bold")).pack(side="left")

    status_label = tk.Label(content_frame, text="Ready to capture face", bg=BG,
                            fg=MUTED, font=("Segoe UI", 9))
    status_label.pack(pady=4)

    def register():
        sid = student_id_entry.get().strip()
        name = name_entry.get().strip()
        cls = class_entry.get().strip()
        yr = year_entry.get().strip()
        sec = section_entry.get().strip()
        if not all([sid, name, cls, yr, sec]):
            messagebox.showwarning("Missing Information",
                                   "Please fill in all fields.", parent=root)
            return
        cam_index = CAMERA_OPTIONS.get(cam_var.get(), 0)
        loading = show_loading("Opening camera...\nPlease wait.")
        root.withdraw()
        try:
            success, message = register_student(sid, name, cls, sec, yr, cam_index)
        except Exception as e:
            success, message = False, str(e)
        loading.destroy()
        root.deiconify()
        if success:
            messagebox.showinfo("Success", message, parent=root)
            show_dashboard()
        else:
            status_label.configure(text="Failed.", fg=RED)
            messagebox.showerror("Error", message, parent=root)

    btn_frame = tk.Frame(content_frame, bg=BG)
    btn_frame.pack(pady=10)
    rounded_button(btn_frame, "📷  Capture Face & Register", register, width=26).pack()
    tk.Button(btn_frame, text="Cancel", command=show_dashboard,
              bg=BG, fg=MUTED, activebackground=HOVER,
              font=("Segoe UI", 9, "bold"), relief="flat",
              cursor="hand2").pack(pady=8)


# ---------------- PAGE: ATTENDANCE ----------------
def show_attendance_page():
    clear_content()
    set_active(attendance_nav)
    make_hero(content_frame, "Face Recognition Attendance",
              "Select a course and start the camera", on_back=show_dashboard)
    try:
        courses = (supabase.table("courses")
                   .select("course_id, course_code, course_name, teacher")
                   .order("course_id").execute().data or [])
    except Exception as e:
        messagebox.showerror("Error", f"Could not load courses.\n\n{e}", parent=root)
        return
    if not courses:
        messagebox.showwarning("No Courses", "Please add a course first.", parent=root)
        show_dashboard()
        return

    card = make_card(content_frame)
    card.pack(fill="x", padx=120, pady=20)

    tk.Label(card, text="COURSE", bg=CARD, fg=MUTED,
             font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=30, pady=(25, 8))
    course_values = [f"{c.get('course_code')} — {c.get('course_name')}" for c in courses]
    combo = ttk.Combobox(card, values=course_values, state="readonly",
                         width=50, style="Modern.TCombobox")
    combo.pack(fill="x", padx=30)
    combo.current(0)

    teacher_label = tk.Label(card, text="", bg=CARD, fg=MUTED, font=("Segoe UI", 9))
    teacher_label.pack(pady=(10, 5))
    tk.Label(card, text="● Camera Ready", bg=CARD, fg=GREEN,
             font=("Segoe UI", 9, "bold")).pack(pady=(0, 15))

    def update_info(_=None):
        idx = combo.current()
        if idx >= 0:
            teacher_label.configure(
                text=f"Instructor: {courses[idx].get('teacher') or 'Not specified'}")
    combo.bind("<<ComboboxSelected>>", update_info)
    update_info()

    cam_frame = tk.Frame(card, bg=CARD)
    cam_frame.pack(fill="x", padx=30, pady=(0, 20))
    tk.Label(cam_frame, text="Camera:", bg=CARD, fg=MUTED,
             font=("Segoe UI", 9)).pack(side="left")
    cam_var = tk.StringVar(value="Camera 0")
    cam_combo = ttk.Combobox(cam_frame, textvariable=cam_var, state="readonly",
                             width=18, style="Modern.TCombobox")
    cam_combo["values"] = list(CAMERA_OPTIONS.keys())
    cam_combo.pack(side="left", padx=8)
    tk.Button(cam_frame, text="Preview",
              command=lambda: preview_camera(CAMERA_OPTIONS.get(cam_var.get(), 0)),
              bg=NAVY, fg=WHITE, activebackground=NAVY_DARK, activeforeground=WHITE,
              relief="flat", padx=14, pady=5, cursor="hand2",
              font=("Segoe UI", 9, "bold")).pack(side="left")

    def start():
        idx = combo.current()
        if idx == -1: return
        c = courses[idx]
        cam_index = CAMERA_OPTIONS.get(cam_var.get(), 0)
        loading = show_loading("Loading students & opening camera...\nPlease wait.")
        root.withdraw()
        try:
            success, message = take_attendance(
                c["course_id"], c["course_code"], c["course_name"], cam_index)
        except Exception as e:
            success, message = False, str(e)
        loading.destroy()
        root.deiconify()
        if success:
            messagebox.showinfo("Attendance Complete", message, parent=root)
            show_dashboard()
        else:
            messagebox.showerror("Error", message, parent=root)

    btn_frame = tk.Frame(content_frame, bg=BG)
    btn_frame.pack(pady=10)
    rounded_button(btn_frame, "◎  Start Face Recognition", start, width=26).pack()
    tk.Label(btn_frame, text="A camera window will open. Press Q on it to finish.",
             bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(pady=6)
    tk.Button(btn_frame, text="Cancel", command=show_dashboard,
              bg=BG, fg=MUTED, activebackground=HOVER,
              font=("Segoe UI", 9, "bold"), relief="flat",
              cursor="hand2").pack()


# ---------------- PAGE: COURSES ----------------
def show_courses_page():
    clear_content()
    set_active(courses_nav)
    make_hero(content_frame, "Manage Courses",
              "Add, update and remove courses", on_back=show_dashboard)
    form = make_card(content_frame)
    form.pack(fill="x", padx=40, pady=20)
    entries = []
    for i, label in enumerate(["Course Code", "Course Name", "Teacher"]):
        tk.Label(form, text=label.upper(), bg=CARD, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).grid(
                     row=0, column=i*2, columnspan=2,
                     padx=(20 if i == 0 else 10, 5), pady=(15, 5), sticky="w")
        e = tk.Entry(form, font=("Segoe UI", 10), relief="solid", bd=1,
                     width=(20 if i != 1 else 35))
        e.grid(row=1, column=i*2, columnspan=2,
               padx=(20 if i == 0 else 10, 5), pady=(0, 15),
               ipady=6, sticky="ew")
        entries.append(e)
    code_e, name_e, teacher_e = entries
    for c in range(6): form.grid_columnconfigure(c, weight=1)

    btn_frame = tk.Frame(content_frame, bg=BG)
    btn_frame.pack(side="bottom", fill="x", padx=40, pady=15)
    table_card = make_card(content_frame)
    table_card.pack(fill="both", expand=True, padx=40, pady=(0, 5))
    table_frame = tk.Frame(table_card, bg=CARD)
    table_frame.pack(fill="both", expand=True, padx=15, pady=15)
    tree = ttk.Treeview(table_frame, columns=("id", "code", "name", "teacher"),
                        show="headings")
    for col, txt, w, anc in [("id", "ID", 70, "center"),
                             ("code", "Course Code", 180, "center"),
                             ("name", "Course Name", 400, "w"),
                             ("teacher", "Teacher", 250, "w")]:
        tree.heading(col, text=txt)
        tree.column(col, width=w, anchor=anc)
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    empty = empty_state_label(table_frame, "No courses yet.")

    def clear_form():
        for e in entries: e.delete(0, tk.END)
        tree.selection_remove(tree.selection())

    def load_courses():
        for item in tree.get_children(): tree.delete(item)
        try:
            data = (supabase.table("courses")
                    .select("*").order("course_id").execute().data or [])
            if not data:
                empty.place(relx=0.5, rely=0.5, anchor="center")
            else:
                empty.place_forget()
                for c in data:
                    tree.insert("", "end", values=(
                        c.get("course_id"), c.get("course_code"),
                        c.get("course_name"), c.get("teacher") or "-"))
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=root)

    def select_course(_=None):
        sel = tree.selection()
        if not sel: return
        vals = tree.item(sel[0], "values")
        for e in entries: e.delete(0, tk.END)
        code_e.insert(0, vals[1]); name_e.insert(0, vals[2])
        if vals[3] != "-": teacher_e.insert(0, vals[3])
    tree.bind("<<TreeviewSelect>>", select_course)

    def add_course():
        code, name = code_e.get().strip(), name_e.get().strip()
        if not code or not name:
            return messagebox.showwarning("Missing", "Enter code and name", parent=root)
        try:
            if supabase.table("courses").select("course_id").eq("course_code", code).execute().data:
                return messagebox.showwarning("Duplicate", "Code exists", parent=root)
            supabase.table("courses").insert({
                "course_code": code, "course_name": name,
                "teacher": teacher_e.get().strip(),
            }).execute()
            clear_form(); load_courses()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=root)

    def update_course():
        sel = tree.selection()
        if not sel:
            return messagebox.showwarning("Select", "Select a course", parent=root)
        cid = tree.item(sel[0], "values")[0]
        try:
            supabase.table("courses").update({
                "course_code": code_e.get().strip(),
                "course_name": name_e.get().strip(),
                "teacher": teacher_e.get().strip(),
            }).eq("course_id", cid).execute()
            clear_form(); load_courses()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=root)

    def delete_course():
        sel = tree.selection()
        if not sel: return
        vals = tree.item(sel[0], "values")
        if messagebox.askyesno("Delete", f"Delete {vals[1]}?", parent=root):
            try:
                supabase.table("courses").delete().eq("course_id", vals[0]).execute()
                clear_form(); load_courses()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=root)

    rounded_button(btn_frame, "＋ Add",     add_course,    width=12).pack(side="left", padx=5)
    rounded_button(btn_frame, "✎ Update",  update_course, width=12, bg=WOOD).pack(side="left", padx=5)
    rounded_button(btn_frame, "× Delete",  delete_course, width=12, bg=RED).pack(side="left", padx=5)
    rounded_button(btn_frame, "↻ Refresh", load_courses,  width=12, bg=SLATE).pack(side="left", padx=5)
    load_courses()


# ---------------- PAGE: REPORTS ----------------
def show_report_page():
    clear_content()
    set_active(reports_nav)
    build_report_page(content_frame, on_back=show_dashboard)


# ---------------- NAVIGATION ----------------
dashboard_nav  = navigation_button("  ◈   Dashboard",  show_dashboard)
student_nav    = navigation_button("  ◉   Students",   show_registration_page)
attendance_nav = navigation_button("  ◎   Attendance", show_attendance_page)
courses_nav    = navigation_button("  ▣   Courses",    show_courses_page)
reports_nav    = navigation_button("  ◫   Reports",    show_report_page)

tk.Frame(sidebar, bg=NAVY_DARK).pack(fill="both", expand=True)

settings_nav = navigation_button(
    "  ⚙   Settings",
    lambda: messagebox.showinfo("Settings", "Coming soon", parent=root))


def close_app():
    try: root.destroy()
    except: pass


logout_nav = navigation_button("  ⇥   Exit", close_app)
root.protocol("WM_DELETE_WINDOW", close_app)

show_dashboard()
root.mainloop()