import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv() # Loads from the root .env file

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY. Please check your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_all_students():
    response = supabase.table("students").select("*").order("student_id").execute()
    return response.data or []

def get_all_courses():
    response = supabase.table("courses").select("*").order("course_id").execute()
    return response.data or []

def get_all_attendance():
    response = supabase.table("attendance").select("*").order("attendance_date", desc=True).execute()
    return response.data or []

def register_student(data):
    response = supabase.table("students").insert(data).execute()
    return response.data

def add_course(data):
    response = supabase.table("courses").insert(data).execute()
    return response.data

def delete_course(course_id):
    response = supabase.table("courses").delete().eq("course_id", course_id).execute()
    return response.data

def mark_attendance(data):
    response = supabase.table("attendance").insert(data).execute()
    return response.data