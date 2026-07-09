import asyncio
import os

import database as db
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
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

# ============================================
# TELEGRAM BOT
# ============================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

WEBAPP_URL = "https://katmischenko.github.io/mischenko-edu/frontend/index.html"


@dp.message(Command("start"))
async def start(message: types.Message):
    try:
        await message.delete()
    except:
        pass

    try:
        chat_id = message.chat.id
        updates = await bot.get_updates(offset=-10, timeout=1)
        for update in updates:
            if update.message and update.message.chat.id == chat_id:
                if update.message.from_user.id == (await bot.get_me()).id:
                    try:
                        await bot.delete_message(chat_id, update.message.message_id)
                    except:
                        pass
    except:
        pass

    await message.answer(
        "Привет! Меня зовут Екатерина, я преподаватель информатики.\n\n"
        "За 8 лет через мои уроки прошли больше 650 ребят. Кто-то сдал ЕГЭ на 90+, "
        "кто-то написал первого бота, кто-то просто перестал бояться «этих ваших компьютеров».\n\n"
        "Я верю, что программирование — это не страшно. Это интересно, логично и очень полезно.\n\n"
        "В приложении ты найдёшь всё: от первого урока до пробника. "
        "Выбирай свой путь и пошли!\n\n"
        "👇 Жми на кнопку, откроется твой будущий кабинет.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🚀 Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL)
                    )
                ]
            ]
        ),
    )


@dp.message()
async def any_message(message: types.Message):
    try:
        await message.delete()
    except:
        pass

    await message.answer(
        "👇 Жми на кнопку, чтобы открыть приложение!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🚀 Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL)
                    )
                ]
            ]
        ),
    )


async def start_bot():
    await bot.delete_my_commands()
    await dp.start_polling(bot)


# ============================================
# МОДЕЛИ API
# ============================================


class PhoneRequest(BaseModel):
    phone: str


class RegisterRequest(BaseModel):
    phone: str
    name: str
    course: str
    password: str


class LoginRequest(BaseModel):
    phone: str
    password: str


class ProfileUpdate(BaseModel):
    age: str = ""
    course: str = ""
    goal: str = ""


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


# ============================================
# API ЭНДПОИНТЫ
# ============================================


@app.post("/api/check-phone")
def check_phone(data: PhoneRequest):
    result = db.supabase.table("users").select("*").eq("phone", data.phone).execute()
    if not result.data:
        return {"exists": False}
    user_data = result.data[0]
    return {
        "exists": True,
        "user": {
            "id": user_data["id"],
            "name": user_data["name"],
            "course": user_data["course"],
            "phone": user_data["phone"],
        },
    }


@app.post("/api/login")
def login(data: LoginRequest):
    result = db.supabase.table("users").select("*").eq("phone", data.phone).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user_data = result.data[0]
    if user_data["password_hash"] != data.password:
        raise HTTPException(status_code=401, detail="Неверный пароль")

    return {
        "success": True,
        "user": {
            "id": user_data["id"],
            "name": user_data["name"],
            "course": user_data["course"],
            "phone": user_data["phone"],
        },
    }


@app.post("/api/register")
def register(data: RegisterRequest):
    existing = db.supabase.table("users").select("*").eq("phone", data.phone).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Этот номер уже зарегистрирован")

    result = (
        db.supabase.table("users")
        .insert(
            {
                "phone": data.phone,
                "name": data.name,
                "course": data.course,
                "password_hash": data.password,
            }
        )
        .execute()
    )

    user_data = result.data[0]
    return {
        "success": True,
        "user": {
            "id": user_data["id"],
            "name": user_data["name"],
            "course": user_data["course"],
            "phone": user_data["phone"],
        },
    }


@app.put("/api/profile/{user_id}")
def update_profile(user_id: int, data: ProfileUpdate):
    update_data = {}
    if data.course:
        update_data["course"] = data.course
    result = db.supabase.table("users").update(update_data).eq("id", user_id).execute()
    return {"success": True}


@app.get("/api/tracker/{user_id}")
def tracker(user_id: int):
    result = db.get_tracker(user_id)
    return {"success": True, "data": result.data}


@app.put("/api/tracker/{tracker_id}")
def update_tracker(tracker_id: int, data: TrackerUpdate):
    result = db.update_tracker(tracker_id, data.status, data.understanding)
    return {"success": True, "data": result.data}


@app.get("/api/homework/{user_id}")
def homework(user_id: int):
    result = db.get_homework(user_id)
    return {"success": True, "data": result.data}


@app.put("/api/homework/{hw_id}")
def update_homework(hw_id: int, data: HomeworkUpdate):
    result = db.update_homework(hw_id, data.status)
    return {"success": True, "data": result.data}


@app.get("/api/reports/{user_id}")
def reports(user_id: int):
    result = db.get_reports(user_id)
    return {"success": True, "data": result.data}


@app.get("/api/cheatsheets/{course}")
def cheatsheets(course: str):
    result = db.get_cheatsheets(course)
    return {"success": True, "data": result.data}


@app.get("/api/tasks")
def tasks(course: str = None):
    result = db.get_tasks(course)
    return {"success": True, "data": result.data}


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


@app.get("/api/tests/{course}")
def get_tests(course: str):
    result = db.supabase.table("tests").select("*").eq("course", course).execute()
    return {"success": True, "data": result.data}


# ============================================
# ЗАПУСК
# ============================================


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
