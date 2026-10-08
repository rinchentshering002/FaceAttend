# ============================================================
# FACEATTEND - ATTENDANCE REPORT
# ============================================================

import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# TIMEZONE
# ============================================================

BHUTAN_TZ = ZoneInfo("Asia/Thimphu")


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials are missing!")


# ============================================================
# SUPABASE
# ============================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# COLORS
# ============================================================

BG = "#f5f6fa"
CARD = "#ffffff"
DARK = "#541d29"
GOLD = "#e7c76a"
TEXT = "#242424"
MUTED = "#6b7280"
BORDER = "#dddddd"
GREEN = "#238636"
RED = "#b42318"


# ============================================================
# ATTENDANCE REPORT
# ============================================================

class AttendanceReport:

    def __init__(self, parent=None):

        self.parent = parent

        self.window = tk.Toplevel(parent) if parent else tk.Tk()

        self.window.title("FaceAttend | Attendance Report")

        self.window.geometry("1150x700")

        self.window.minsize(950, 600)

        self.window.configure(
            bg=BG
        )

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        # ----------------------------------------------------
        # DATA
        # ----------------------------------------------------

        self.all_records = []

        self.filtered_records = []

        self.students = {}

        self.courses = {}

        # ----------------------------------------------------
        # VARIABLES
        # ----------------------------------------------------

        self.date_var = tk.StringVar()

        self.course_var = tk.StringVar(
            value="All Courses"
        )

        self.search_var = tk.StringVar()

        self.total_var = tk.StringVar(
            value="Total Records: 0"
        )

        self.present_var = tk.StringVar(
            value="Present: 0"
        )

        self.absent_var = tk.StringVar(
            value="Absent: 0"
        )

        # ----------------------------------------------------
        # BUILD UI
        # ----------------------------------------------------

        self.build_ui()

        # ----------------------------------------------------
        # LOAD DATA
        # ----------------------------------------------------

        self.load_data()


    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        # ====================================================
        # HEADER
        # ====================================================

        header = tk.Frame(
            self.window,
            bg=DARK,
            height=85
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)


        title_frame = tk.Frame(
            header,
            bg=DARK
        )

        title_frame.pack(
            side="left",
            padx=25,
            pady=12
        )


        tk.Label(
            title_frame,
            text="FACEATTEND",
            font=(
                "Segoe UI",
                18,
                "bold"
            ),
            fg=GOLD,
            bg=DARK
        ).pack(
            anchor="w"
        )


        tk.Label(
            title_frame,
            text="Attendance Report",
            font=(
                "Segoe UI",
                10
            ),
            fg="white",
            bg=DARK
        ).pack(
            anchor="w"
        )


        # ====================================================
        # CLOSE BUTTON
        # ====================================================

        tk.Button(
            header,
            text="✕  Close",
            command=self.close,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            bg=DARK,
            fg="white",
            activebackground=DARK,
            activeforeground=GOLD,
            relief="flat",
            bd=0,
            cursor="hand2"
        ).pack(
            side="right",
            padx=25
        )


        # ====================================================
        # FILTER CARD
        # ====================================================

        filter_card = tk.Frame(
            self.window,
            bg=CARD,
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        filter_card.pack(
            fill="x",
            padx=20,
            pady=(20, 10)
        )


        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        tk.Label(
            filter_card,
            text="Date",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            fg=TEXT,
            bg=CARD
        ).grid(
            row=0,
            column=0,
            padx=(15, 5),
            pady=(12, 4),
            sticky="w"
        )


        today = datetime.now(
            BHUTAN_TZ
        ).date().isoformat()

        self.date_var.set(today)


        date_entry = ttk.Entry(
            filter_card,
            textvariable=self.date_var,
            width=15
        )

        date_entry.grid(
            row=1,
            column=0,
            padx=(15, 10),
            pady=(0, 12),
            sticky="w"
        )


        # ----------------------------------------------------
        # COURSE
        # ----------------------------------------------------

        tk.Label(
            filter_card,
            text="Course",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            fg=TEXT,
            bg=CARD
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=(12, 4),
            sticky="w"
        )


        self.course_combo = ttk.Combobox(
            filter_card,
            textvariable=self.course_var,
            state="readonly",
            width=22
        )

        self.course_combo.grid(
            row=1,
            column=1,
            padx=5,
            pady=(0, 12),
            sticky="w"
        )

        self.course_combo["values"] = [
            "All Courses"
        ]


        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        tk.Label(
            filter_card,
            text="Search Student",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            fg=TEXT,
            bg=CARD
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=(12, 4),
            sticky="w"
        )


        search_entry = ttk.Entry(
            filter_card,
            textvariable=self.search_var,
            width=28
        )

        search_entry.grid(
            row=1,
            column=2,
            padx=5,
            pady=(0, 12),
            sticky="w"
        )


        self.search_var.trace_add(
            "write",
            lambda *_: self.apply_filters()
        )


        # ----------------------------------------------------
        # REFRESH
        # ----------------------------------------------------

        tk.Button(
            filter_card,
            text="⟳  Refresh",
            command=self.load_data,
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            bg=DARK,
            fg="white",
            activebackground="#6d2938",
            activeforeground="white",
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        ).grid(
            row=1,
            column=3,
            padx=(10, 5),
            pady=(0, 12)
        )


        # ----------------------------------------------------
        # EXPORT
        # ----------------------------------------------------

        tk.Button(
            filter_card,
            text="↓  Export CSV",
            command=self.export_csv,
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            bg=GREEN,
            fg="white",
            activebackground="#1b6d2d",
            activeforeground="white",
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        ).grid(
            row=1,
            column=4,
            padx=(5, 15),
            pady=(0, 12)
        )


        self.course_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self.apply_filters()
        )


        # ====================================================
        # TABLE CARD
        # ====================================================

        table_card = tk.Frame(
            self.window,
            bg=CARD,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        table_card.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )


        # ====================================================
        # TREEVIEW STYLE
        # ====================================================

        style = ttk.Style()

        try:
            style.theme_use(
                "clam"
            )
        except Exception:
            pass


        style.configure(
            "Treeview",
            background="white",
            foreground=TEXT,
            rowheight=34,
            fieldbackground="white",
            font=(
                "Segoe UI",
                9
            )
        )


        style.configure(
            "Treeview.Heading",
            background=DARK,
            foreground="white",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            padding=8
        )


        style.map(
            "Treeview",
            background=[
                ("selected", "#ead9a0")
            ],
            foreground=[
                ("selected", TEXT)
            ]
        )


        # ====================================================
        # SCROLLBARS
        # ====================================================

        vertical_scroll = ttk.Scrollbar(
            table_card,
            orient="vertical"
        )

        horizontal_scroll = ttk.Scrollbar(
            table_card,
            orient="horizontal"
        )


        # ====================================================
        # TABLE
        # ====================================================

        columns = (
            "attendance_id",
            "student_id",
            "student_name",
            "course",
            "date",
            "time",
            "status"
        )


        self.tree = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings",
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )


        vertical_scroll.config(
            command=self.tree.yview
        )

        horizontal_scroll.config(
            command=self.tree.xview
        )


        # ====================================================
        # HEADINGS
        # ====================================================

        self.tree.heading(
            "attendance_id",
            text="Attendance ID"
        )

        self.tree.heading(
            "student_id",
            text="Student ID"
        )

        self.tree.heading(
            "student_name",
            text="Student Name"
        )

        self.tree.heading(
            "course",
            text="Course"
        )

        self.tree.heading(
            "date",
            text="Date"
        )

        self.tree.heading(
            "time",
            text="Time"
        )

        self.tree.heading(
            "status",
            text="Status"
        )


        # ====================================================
        # COLUMN WIDTHS
        # ====================================================

        self.tree.column(
            "attendance_id",
            width=110,
            anchor="center"
        )

        self.tree.column(
            "student_id",
            width=120,
            anchor="center"
        )

        self.tree.column(
            "student_name",
            width=210,
            anchor="w"
        )

        self.tree.column(
            "course",
            width=180,
            anchor="w"
        )

        self.tree.column(
            "date",
            width=120,
            anchor="center"
        )

        self.tree.column(
            "time",
            width=120,
            anchor="center"
        )

        self.tree.column(
            "status",
            width=100,
            anchor="center"
        )


        # ====================================================
        # PACK TABLE
        # ====================================================

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        vertical_scroll.pack(
            side="right",
            fill="y"
        )

        horizontal_scroll.pack(
            side="bottom",
            fill="x"
        )


        # ====================================================
        # STATUS COLORS
        # ====================================================

        self.tree.tag_configure(
            "present",
            foreground=GREEN
        )

        self.tree.tag_configure(
            "absent",
            foreground=RED
        )


        # ====================================================
        # SUMMARY
        # ====================================================

        summary = tk.Frame(
            self.window,
            bg=BG
        )

        summary.pack(
            fill="x",
            padx=20,
            pady=(5, 20)
        )


        tk.Label(
            summary,
            textvariable=self.total_var,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            fg=TEXT,
            bg=BG
        ).pack(
            side="left"
        )


        tk.Label(
            summary,
            textvariable=self.present_var,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            fg=GREEN,
            bg=BG
        ).pack(
            side="left",
            padx=25
        )


        tk.Label(
            summary,
            textvariable=self.absent_var,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            fg=RED,
            bg=BG
        ).pack(
            side="left"
        )


    # ========================================================
    # LOAD DATA FROM SUPABASE
    # ========================================================

    def load_data(self):

        try:

            # ------------------------------------------------
            # LOAD STUDENTS
            # ------------------------------------------------

            student_response = (
                supabase
                .table("students")
                .select(
                    "student_id, name"
                )
                .execute()
            )


            self.students = {}

            for student in student_response.data:

                student_id = str(
                    student.get("student_id")
                )

                self.students[student_id] = (
                    student.get("name")
                    or "Unknown Student"
                )


            # ------------------------------------------------
            # LOAD ATTENDANCE
            # ------------------------------------------------

            attendance_response = (
                supabase
                .table("attendance")
                .select("*")
                .order(
                    "attendance_date",
                    desc=True
                )
                .order(
                    "attendance_time",
                    desc=True
                )
                .execute()
            )


            self.all_records = (
                attendance_response.data
                or []
            )


            # ------------------------------------------------
            # LOAD COURSE NAMES
            # ------------------------------------------------

            self.load_courses()


            # ------------------------------------------------
            # UPDATE COURSE DROPDOWN
            # ------------------------------------------------

            course_names = [
                "All Courses"
            ]

            for course_id, course_name in self.courses.items():

                if course_name not in course_names:

                    course_names.append(
                        course_name
                    )


            self.course_combo["values"] = (
                course_names
            )


            if self.course_var.get() not in course_names:

                self.course_var.set(
                    "All Courses"
                )


            # ------------------------------------------------
            # APPLY FILTER
            # ------------------------------------------------

            self.apply_filters()


        except Exception as e:

            messagebox.showerror(
                "Database Error",
                "Could not load attendance records.\n\n"
                f"{e}",
                parent=self.window
            )


    # ========================================================
    # LOAD COURSES
    # ========================================================

    def load_courses(self):

        self.courses = {}


        try:

            response = (
                supabase
                .table("courses")
                .select("*")
                .execute()
            )


            for row in response.data:

                course_id = row.get(
                    "course_id"
                )

                if course_id is None:
                    continue


                course_name = (
                    row.get("course_name")
                    or row.get("name")
                    or row.get("course_code")
                    or str(course_id)
                )


                self.courses[
                    str(course_id)
                ] = str(course_name)


        except Exception:

            # ------------------------------------------------
            # If a courses table does not exist, the report
            # will still work.
            # ------------------------------------------------

            self.courses = {}


    # ========================================================
    # APPLY FILTERS
    # ========================================================

    def apply_filters(self):

        selected_date = (
            self.date_var
            .get()
            .strip()
        )

        selected_course = (
            self.course_var
            .get()
            .strip()
        )

        search_text = (
            self.search_var
            .get()
            .strip()
            .lower()
        )


        filtered = []


        for record in self.all_records:

            # ------------------------------------------------
            # DATE FILTER
            # ------------------------------------------------

            record_date = str(
                record.get(
                    "attendance_date",
                    ""
                )
            )


            if selected_date:

                if record_date != selected_date:

                    continue


            # ------------------------------------------------
            # STUDENT INFORMATION
            # ------------------------------------------------

            student_id = str(
                record.get(
                    "student_id",
                    ""
                )
            )


            student_name = self.students.get(
                student_id,
                "Unknown Student"
            )


            # ------------------------------------------------
            # COURSE INFORMATION
            # ------------------------------------------------

            course_id = record.get(
                "course_id"
            )


            course_name = "No Course"


            if course_id is not None:

                course_name = self.courses.get(
                    str(course_id),
                    str(course_id)
                )


            # ------------------------------------------------
            # COURSE FILTER
            # ------------------------------------------------

            if selected_course:

                if selected_course != "All Courses":

                    if course_name != selected_course:

                        continue


            # ------------------------------------------------
            # SEARCH FILTER
            # ------------------------------------------------

            if search_text:

                combined_text = (
                    f"{student_id} "
                    f"{student_name} "
                    f"{course_name}"
                ).lower()


                if search_text not in combined_text:

                    continue


            filtered.append({
                "attendance_id": record.get(
                    "attendance_id",
                    ""
                ),

                "student_id": student_id,

                "student_name": student_name,

                "course": course_name,

                "date": record_date,

                "time": self.format_time(
                    record.get(
                        "attendance_time",
                        ""
                    )
                ),

                "status": record.get(
                    "status",
                    ""
                )
            })


        self.filtered_records = filtered


        self.update_table()

        self.update_summary()


    # ========================================================
    # FORMAT TIME
    # ========================================================

    def format_time(self, time_value):

        if not time_value:

            return ""


        try:

            # Example:
            # 09:32:15.123456

            time_part = str(
                time_value
            ).split(".")[0]


            parsed = datetime.strptime(
                time_part,
                "%H:%M:%S"
            )


            return parsed.strftime(
                "%I:%M:%S %p"
            )


        except Exception:

            return str(
                time_value
            )


    # ========================================================
    # UPDATE TABLE
    # ========================================================

    def update_table(self):

        # ----------------------------------------------------
        # CLEAR OLD DATA
        # ----------------------------------------------------

        for item in self.tree.get_children():

            self.tree.delete(
                item
            )


        # ----------------------------------------------------
        # INSERT NEW DATA
        # ----------------------------------------------------

        for record in self.filtered_records:

            status = str(
                record["status"]
            )


            tag = (
                "present"
                if status.lower() == "present"
                else "absent"
            )


            self.tree.insert(
                "",
                "end",
                values=(
                    record["attendance_id"],
                    record["student_id"],
                    record["student_name"],
                    record["course"],
                    record["date"],
                    record["time"],
                    record["status"]
                ),
                tags=(tag,)
            )


    # ========================================================
    # UPDATE SUMMARY
    # ========================================================

    def update_summary(self):

        total = len(
            self.filtered_records
        )


        present = sum(
            1
            for record in self.filtered_records
            if str(
                record["status"]
            ).lower() == "present"
        )


        absent = sum(
            1
            for record in self.filtered_records
            if str(
                record["status"]
            ).lower() == "absent"
        )


        self.total_var.set(
            f"Total Records: {total}"
        )


        self.present_var.set(
            f"Present: {present}"
        )


        self.absent_var.set(
            f"Absent: {absent}"
        )


    # ========================================================
    # EXPORT CSV
    # ========================================================

    def export_csv(self):

        if not self.filtered_records:

            messagebox.showinfo(
                "Nothing to Export",
                "There are no attendance records "
                "to export.",
                parent=self.window
            )

            return


        today = datetime.now(
            BHUTAN_TZ
        ).strftime(
            "%Y%m%d"
        )


        filename = (
            f"attendance_report_{today}.csv"
        )


        filepath = filedialog.asksaveasfilename(
            parent=self.window,
            title="Save Attendance Report",
            defaultextension=".csv",
            initialfile=filename,
            filetypes=[
                (
                    "CSV files",
                    "*.csv"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )


        if not filepath:

            return


        try:

            with open(
                filepath,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(
                    file
                )


                writer.writerow([
                    "Attendance ID",
                    "Student ID",
                    "Student Name",
                    "Course",
                    "Date",
                    "Time",
                    "Status"
                ])


                for record in self.filtered_records:

                    writer.writerow([
                        record["attendance_id"],
                        record["student_id"],
                        record["student_name"],
                        record["course"],
                        record["date"],
                        record["time"],
                        record["status"]
                    ])


            messagebox.showinfo(
                "Export Complete",
                "Attendance report exported successfully.",
                parent=self.window
            )


        except Exception as e:

            messagebox.showerror(
                "Export Error",
                f"Could not export the report.\n\n{e}",
                parent=self.window
            )


    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        self.window.destroy()


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    app = AttendanceReport()

    app.window.mainloop()