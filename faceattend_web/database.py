
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing SUPABASE_URL or SUPABASE_KEY. "
        "Please check your .env file."
    )

# Connect to the existing Supabase project
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# -------------------------------
# STUDENT FUNCTIONS
# -------------------------------

def get_all_students():
    """Retrieve all registered students."""
    response = (
        supabase.table("students")
        .select("*")
        .order("student_id")
        .execute()
    )
    return response.data or []


def get_student_by_id(student_id):
    """Find a student using their ID."""
    response = (
        supabase.table("students")
        .select("*")
        .eq("student_id", student_id)
        .execute()
    )
    return response.data[0] if response.data else None


def register_student(data):
    """Register a new student."""
    response = (
        supabase.table("students")
        .insert(data)
        .execute()
    )
    return response.data


# -------------------------------
# COURSE FUNCTIONS
# -------------------------------

def get_all_courses():
    """Retrieve all courses."""
    response = (
        supabase.table("courses")
        .select("*")
        .order("course_id")
        .execute()
    )
    return response.data or []


def add_course(data):
    """Add a new course."""
    response = (
        supabase.table("courses")
        .insert(data)
        .execute()
    )
    return response.data


def update_course(course_id, data):
    """Update an existing course."""
    response = (
        supabase.table("courses")
        .update(data)
        .eq("course_id", course_id)
        .execute()
    )
    return response.data


def delete_course(course_id):
    """Delete a course."""
    response = (
        supabase.table("courses")
        .delete()
        .eq("course_id", course_id)
        .execute()
    )
    return response.data


# -------------------------------
# ATTENDANCE FUNCTIONS
# -------------------------------

def get_all_attendance():
    """Retrieve attendance records."""
    response = (
        supabase.table("attendance")
        .select("*")
        .order("attendance_date", desc=True)
        .execute()
    )
    return response.data or []


def mark_attendance(data):
    """Insert an attendance record."""
    response = (
        supabase.table("attendance")
        .insert(data)
        .execute()
    )
    return response.data


def get_attendance_by_date(attendance_date):
    """Retrieve attendance for a particular date."""
    response = (
        supabase.table("attendance")
        .select("*")
        .eq("attendance_date", attendance_date)
        .execute()
    )
    return response.data or []


# -------------------------------
# DASHBOARD STATISTICS
# -------------------------------

def get_dashboard_stats():
    """Get basic dashboard statistics."""
    students = get_all_students()
    courses = get_all_courses()
    attendance = get_all_attendance()

    return {
        "total_students": len(students),
        "total_courses": len(courses),
        "total_attendance": len(attendance),
        "present_today": sum(
            1 for record in attendance
            if record.get("status") == "Present"
        )
    }
