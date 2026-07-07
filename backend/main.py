import os

import bcrypt
import database as db
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="mischenko-edu API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── МОДЕЛИ ───


class LoginRequest(BaseModel):
    name: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    course: str
    password: str


class TrackerUpdate(BaseModel):
    status: str = None
    understanding: int = None


class HomeworkUpdate(BaseModel):
    status: str


class DiagnosticRequest(BaseModel):
    answers: dict
    result: str
    level: str
    gaps: str


class ReportCreate(BaseModel):
    user_id: int
    month: str
    lessons: str = "0"
    hwDone: str = "0"
    topics: str = "0"
    score: str = ""
    plan: str = ""


# ─── АВТОРИЗАЦИЯ ───


@app.post("/api/login")
def login(data: LoginRequest):
    result = db.supabase.table("users").select("*").eq("name", data.name).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Ищем пользователя с подходящим паролем
    user_data = None
    for u in result.data:
        if u["password_hash"] == data.password:
            user_data = u
            break

    if not user_data:
        raise HTTPException(status_code=401, detail="Неверный пароль")

    return {
        "success": True,
        "user": {
            "id": user_data["id"],
            "name": user_data["name"],
            "course": user_data["course"],
        },
    }


@app.post("/api/register")
def register(data: RegisterRequest):
    result = db.create_user(data.name, data.course, data.password)
    user_data = result.data[0]
    return {
        "success": True,
        "user": {
            "id": user_data["id"],
            "name": user_data["name"],
            "course": user_data["course"],
        },
    }


# ─── ТРЕКЕР ───


@app.get("/api/tracker/{user_id}")
def tracker(user_id: int):
    result = db.get_tracker(user_id)
    return {"success": True, "data": result.data}


@app.put("/api/tracker/{tracker_id}")
def update_tracker(tracker_id: int, data: TrackerUpdate):
    result = db.update_tracker(tracker_id, data.status, data.understanding)
    return {"success": True, "data": result.data}


# ─── ДОМАШКИ ───


@app.get("/api/homework/{user_id}")
def homework(user_id: int):
    result = db.get_homework(user_id)
    return {"success": True, "data": result.data}


@app.put("/api/homework/{hw_id}")
def update_homework(hw_id: int, data: HomeworkUpdate):
    result = db.update_homework(hw_id, data.status)
    return {"success": True, "data": result.data}


# ─── ОТЧЁТЫ ───


@app.get("/api/reports/{user_id}")
def reports(user_id: int):
    result = db.get_reports(user_id)
    return {"success": True, "data": result.data}


# ─── ШПАРГАЛКИ ───


@app.get("/api/cheatsheets/{course}")
def cheatsheets(course: str):
    result = db.get_cheatsheets(course)
    return {"success": True, "data": result.data}


# ─── БАНК ЗАДАЧ ───


@app.get("/api/tasks")
def tasks(course: str = None):
    result = db.get_tasks(course)
    return {"success": True, "data": result.data}


# ─── ДИАГНОСТИКА ───


@app.post("/api/diagnostics/{user_id}")
def save_diagnostics(user_id: int, data: DiagnosticRequest):
    result = db.save_diagnostics(
        user_id, data.answers, data.result, data.level, data.gaps
    )
    return {"success": True}


@app.get("/api/diagnostics/{user_id}")
def get_diagnostics(user_id: int):
    result = db.get_diagnostics(user_id)
    return {"success": True, "data": result.data}


# ─── АДМИНКА ───


@app.get("/api/admin/students")
def admin_students():
    result = db.supabase.table("users").select("*").execute()
    return {"success": True, "data": result.data}


@app.post("/api/admin/reports")
def admin_create_report(data: ReportCreate):
    result = (
        db.supabase.table("reports")
        .insert(
            {
                "user_id": data.user_id,
                "month": data.month,
                "lessons_done": int(data.lessons) if data.lessons.isdigit() else 0,
                "skipped": 0,
                "homework_done": int(data.hwDone) if data.hwDone.isdigit() else 0,
                "new_topics": int(data.topics) if data.topics.isdigit() else 0,
                "score": data.score,
                "difficulties": "",
                "plan": data.plan,
            }
        )
        .execute()
    )
    return {"success": True}


# ─── ТЕСТЫ ───


@app.get("/api/tests/{course}")
def get_tests(course: str):
    result = db.supabase.table("tests").select("*").eq("course", course).execute()
    return {"success": True, "data": result.data}


# ─── ЗАПУСК ───

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
