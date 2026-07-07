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

WEBAPP_URL = "https://katmischenko.github.io/mischenko-edu/frontend/index.html"


@dp.message(Command("start"))
async def start(message: types.Message):
    # Удаляем команду /start
    try:
        await message.delete()
    except:
        pass

    # Удаляем последние сообщения бота (до 5 штук)
    try:
        chat_id = message.chat.id
        # Получаем последние сообщения
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

    # Отправляем приветствие
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


async def main():
    await bot.delete_my_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
