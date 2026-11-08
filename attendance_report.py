import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from dotenv import load_dotenv
from supabase import create_client

from ui_helpers import (
    make_hero, bhutan_now, format_time_short, empty_state_label,
    BG, CARD, WHITE, NAVY, NAVY_MID, TEXT, MUTED, BORDER, GREEN, RED
)

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def build_report_page(parent, on_back):
    make_hero(parent, "Attendance Report", "Review and export student attendance", on_back=on_back)

    date_var = tk.StringVar(value=bhutan_now().date().isoformat())
    course_var = tk.StringVar(value="All Courses")
    search_var = tk.StringVar()
    
    total_var = tk.StringVar(value="Total Records: 0")
    present_var = tk.StringVar(value="Present: 0")
    absent_var = tk.StringVar(value="Absent: —")

    # Cache for mapping IDs to names (to avoid re-downloading on every filter)
    students_map = {}
    courses_map = {}
    
    # We don't need `all_records` anymore! We fetch what we need.
    filtered_records = []

    # ---------------- FILTER CARD ----------------
    filter_card = tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
    filter_card.pack(fill="x", padx=20, pady=(20, 10))

    tk.Label(filter_card, text="Date", font=("Segoe UI", 9, "bold"), fg=TEXT, bg=CARD).grid(row=0, column=0, padx=(15, 5), pady=(12, 4), sticky="w")
    ttk.Entry(filter_card, textvariable=date_var, width=15).grid(row=1, column=0, padx=(15, 10), pady=(0, 12), sticky="w")

    tk.Label(filter_card, text="Course", font=("Segoe UI", 9, "bold"), fg=TEXT, bg=CARD).grid(row=0, column=1, padx=5, pady=(12, 4), sticky="w")
    course_combo = ttk.Combobox(filter_card, textvariable=course_var, state="readonly", width=22, style="Modern.TCombobox")
    course_combo.grid(row=1, column=1, padx=5, pady=(0, 12), sticky="w")
    course_combo["values"] = ["All Courses"]

    tk.Label(filter_card, text="Search Student", font=("Segoe UI", 9, "bold"), fg=TEXT, bg=CARD).grid(row=0, column=2, padx=5, pady=(12, 4), sticky="w")
    ttk.Entry(filter_card, textvariable=search_var, width=28).grid(row=1, column=2, padx=5, pady=(0, 12), sticky="w")

    refresh_btn = tk.Button(filter_card, text="⟳  Refresh", font=("Segoe UI", 9, "bold"), bg=NAVY, fg=WHITE, activebackground=NAVY_MID, activeforeground=WHITE, relief="flat", padx=15, pady=7, cursor="hand2")
    refresh_btn.grid(row=1, column=3, padx=(10, 5), pady=(0, 12))

    export_btn = tk.Button(filter_card, text="↓  Export CSV", font=("Segoe UI", 9, "bold"), bg=GREEN, fg=WHITE, activebackground="#1B6D2D", activeforeground=WHITE, relief="flat", padx=15, pady=7, cursor="hand2")
    export_btn.grid(row=1, column=4, padx=(5, 15), pady=(0, 12))

    # ---------------- SUMMARY ----------------
    summary = tk.Frame(parent, bg=BG)
    summary.pack(fill="x", padx=20, pady=(0, 8))
    tk.Label(summary, textvariable=total_var, font=("Segoe UI", 10, "bold"), fg=TEXT, bg=BG).pack(side="left")
    tk.Label(summary, textvariable=present_var, font=("Segoe UI", 10, "bold"), fg=GREEN, bg=BG).pack(side="left", padx=25)
    tk.Label(summary, textvariable=absent_var, font=("Segoe UI", 10, "bold"), fg=RED, bg=BG).pack(side="left")

    # ---------------- TABLE ----------------
    table_card = tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
    table_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    v_scroll = ttk.Scrollbar(table_card, orient="vertical")
    h_scroll = ttk.Scrollbar(table_card, orient="horizontal")

    tree_container = tk.Frame(table_card, bg=CARD)
    tree_container.pack(side="left", fill="both", expand=True)

    columns = ("attendance_id", "student_id", "student_name", "course", "date", "time", "status")
    tree = ttk.Treeview(tree_container, columns=columns, show="headings", style="Report.Treeview", yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    
    headings = {"attendance_id": "Attendance ID", "student_id": "Student ID", "student_name": "Student Name", "course": "Course", "date": "Date", "time": "Time", "status": "Status"}
    widths = {"attendance_id": 110, "student_id": 120, "student_name": 210, "course": 180, "date": 120, "time": 120, "status": 100}
    anchors = {"attendance_id": "center", "student_id": "center", "student_name": "w", "course": "w", "date": "center", "time": "center", "status": "center"}

    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, width=widths[col], anchor=anchors[col])

    tree.pack(fill="both", expand=True)
    tree.tag_configure("present", foreground=GREEN)
    tree.tag_configure("absent", foreground=RED)

    empty_label = empty_state_label(tree_container, "No records match your filters.")
    v_scroll.pack(side="right", fill="y")
    h_scroll.pack(side="bottom", fill="x")

    # ---------------- LOGIC ----------------
    def update_summary():
        total = len(filtered_records)
        present = sum(1 for r in filtered_records if str(r["status"]).lower() == "present")
        sel_date = date_var.get().strip()
        sel_course = course_var.get().strip()

        if sel_date and sel_course == "All Courses" and students_map:
            present_ids = {r["student_id"] for r in filtered_records if str(r["status"]).lower() == "present"}
            absent_var.set(f"Absent: {max(len(students_map) - len(present_ids), 0)}")
        else:
            absent_var.set("Absent: —")

        total_var.set(f"Total Records: {total}")
        present_var.set(f"Present: {present}")

    def apply_filters(*args):
        """Fetches ONLY the required data from Supabase based on filters."""
        nonlocal filtered_records
        sel_date = date_var.get().strip()
        sel_course = course_var.get().strip()
        search_text = search_var.get().strip().lower()

        for item in tree.get_children(): tree.delete(item)
        filtered_records = []

        try:
            # Build Supabase Query dynamically
            query = supabase.table("attendance").select("*")

            if sel_date:
                query = query.eq("attendance_date", sel_date)

            if sel_course and sel_course != "All Courses":
                # Find course_id from name
                cid = next((k for k, v in courses_map.items() if v == sel_course), None)
                if cid:
                    query = query.eq("course_id", cid)

            # Execute Server-Side Query (FAST)
            response = query.order("attendance_time", desc=True).execute()
            records = response.data or []

            for record in records:
                sid = str(record.get("student_id", ""))
                sname = students_map.get(sid, "Unknown Student")
                cid = record.get("course_id")
                cname = courses_map.get(str(cid), "No Course") if cid else "No Course"

                # Python-side search (fast since we already filtered date/course in DB)
                if search_text and search_text not in f"{sid} {sname} {cname}".lower():
                    continue

                row = {
                    "attendance_id": record.get("attendance_id", ""),
                    "student_id": sid, "student_name": sname, "course": cname,
                    "date": record.get("attendance_date", ""), 
                    "time": format_time_short(record.get("attendance_time", "")),
                    "status": record.get("status", "")
                }
                filtered_records.append(row)
                
                tag = "present" if row["status"].lower() == "present" else "absent"
                tree.insert("", "end", values=(row["attendance_id"], row["student_id"], row["student_name"], row["course"], row["date"], row["time"], row["status"]), tags=(tag,))

            if not filtered_records:
                empty_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                empty_label.place_forget()

            update_summary()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=parent)

    def load_static_data():
        """Loads student/course names ONCE when the page opens."""
        nonlocal students_map, courses_map
        try:
            s_resp = supabase.table("students").select("student_id, name").execute()
            students_map = {str(s.get("student_id")): (s.get("name") or "Unknown Student") for s in s_resp.data}

            c_resp = supabase.table("courses").select("*").execute()
            courses_map = {}
            for row in c_resp.data:
                cid = row.get("course_id")
                if cid is None: continue
                name = row.get("course_name") or row.get("name") or row.get("course_code") or str(cid)
                courses_map[str(cid)] = str(name)

            c_names = ["All Courses"] + [n for n in courses_map.values() if n not in ["All Courses"]]
            course_combo["values"] = c_names
            if course_var.get() not in c_names: course_var.set("All Courses")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load base data.\n{e}", parent=parent)

    def export_csv():
        if not filtered_records:
            messagebox.showinfo("Nothing to Export", "There are no records to export.", parent=parent)
            return

        today = bhutan_now().strftime("%Y%m%d")
        filepath = filedialog.asksaveasfilename(
            parent=parent, title="Save Report", defaultextension=".csv",
            initialfile=f"attendance_{today}.csv", filetypes=[("CSV files", "*.csv")]
        )
        if not filepath: return

        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Attendance ID", "Student ID", "Student Name", "Course", "Date", "Time", "Status"])
                for r in filtered_records:
                    writer.writerow([r["attendance_id"], r["student_id"], r["student_name"], r["course"], r["date"], r["time"], r["status"]])
            messagebox.showinfo("Export Complete", "Report exported successfully.", parent=parent)
        except Exception as e:
            messagebox.showerror("Error", f"Could not export.\n\n{e}", parent=parent)

    # Bindings
    refresh_btn.configure(command=apply_filters)
    export_btn.configure(command=export_csv)
    search_var.trace_add("write", apply_filters)
    course_combo.bind("<<ComboboxSelected>>", apply_filters)
    date_var.trace_add("write", apply_filters)
    
    # Initial Load
    load_static_data()
    apply_filters()