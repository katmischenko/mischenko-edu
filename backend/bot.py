import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть личный кабинет",
                    web_app=WebAppInfo(
                        url="https://katmischenko.github.io/mischenko-edu/frontend/student.html"
                    ),
                )
            ]
        ]
    )
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Здесь ты можешь:\n"
        "📋 Пройти диагностику\n"
        "📈 Следить за прогрессом\n"
        "📝 Смотреть домашние задания\n"
        "🧩 Тренироваться на задачах\n\n"
        "Нажми кнопку ниже, чтобы открыть кабинет.",
        reply_markup=keyboard,
    )


@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "📌 Доступные команды:\n"
        "/start — главное меню\n"
        "/help — помощь\n"
        "/progress — мой прогресс"
    )


@dp.message(Command("progress"))
async def progress(message: types.Message):
    await message.answer(
        "📈 Твой прогресс доступен в личном кабинете.\nНажми /start и открой кабинет."
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
