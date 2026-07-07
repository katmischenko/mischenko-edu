import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

WEBAPP_URL = "https://katmischenko.github.io/mischenko-edu/frontend/index.html"


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 <b>Добро пожаловать в mischenko.edu!</b>\n\n"
        "Здесь ты найдёшь свой путь в IT: программирование, подготовка к экзаменам, создание сайтов и не только.",
        parse_mode="HTML",
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


async def main():
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Главное меню"),
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
