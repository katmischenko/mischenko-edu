import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)


# ─── USERS ───


def get_user_by_id(user_id: int):
    return supabase.table("users").select("*").eq("id", user_id).single().execute()


def get_user_by_name(name: str):
    return supabase.table("users").select("*").eq("name", name).single().execute()


def create_user(name: str, course: str, password_hash: str):
    return (
        supabase.table("users")
        .insert({"name": name, "course": course, "password_hash": password_hash})
        .execute()
    )


# ─── TRACKER ───


def get_tracker(user_id: int):
    return supabase.table("tracker").select("*").eq("user_id", user_id).execute()


def update_tracker(tracker_id: int, status: str = None, understanding: int = None):
    data = {}
    if status:
        data["status"] = status
    if understanding is not None:
        data["understanding"] = understanding
    return supabase.table("tracker").update(data).eq("id", tracker_id).execute()


# ─── HOMEWORK ───


def get_homework(user_id: int):
    return supabase.table("homework").select("*").eq("user_id", user_id).execute()


def update_homework(hw_id: int, status: str = None):
    return (
        supabase.table("homework").update({"status": status}).eq("id", hw_id).execute()
    )


# ─── REPORTS ───


def get_reports(user_id: int):
    return (
        supabase.table("reports")
        .select("*")
        .eq("user_id", user_id)
        .order("id", desc=True)
        .execute()
    )


# ─── CHEATSHEETS ───


def get_cheatsheets(course: str):
    return supabase.table("cheatsheets").select("*").eq("course", course).execute()


# ─── TASKS BANK ───


def get_tasks(course: str = None):
    query = supabase.table("tasks_bank").select("*")
    if course:
        query = query.eq("course", course)
    return query.execute()


# ─── DIAGNOSTICS ───


def save_diagnostics(user_id: int, answers: dict, result: str, level: str, gaps: str):
    return (
        supabase.table("diagnostics")
        .insert(
            {
                "user_id": user_id,
                "answers": answers,
                "result": result,
                "level": level,
                "gaps": gaps,
            }
        )
        .execute()
    )


def get_diagnostics(user_id: int):
    return (
        supabase.table("diagnostics")
        .select("*")
        .eq("user_id", user_id)
        .order("id", desc=True)
        .execute()
    )
