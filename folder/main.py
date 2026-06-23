import asyncio
import random
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from google import genai
from PromptBuilder import PromptBuilder

from db import DataBase


dp = Dispatcher()
client = None
bot = None
test_db = None

games: dict[int, dict] = {}


def auth_telegram():
    token = getenv("BOT_TOKEN")
    if not token:
        raise ValueError("No token provided")
    return Bot(token=token)


def auth_gemini_api():
    api_key = getenv("GEMINI_API_KEY")
    if not api_key:
        print("No GEMINI_API_KEY provided. Running without Gemini API")
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        print("Can`t connect to Gemini API. Running without one.")
    return None


@dp.message(Command("start"))
async def cmd_start(message: Message):
    if test_db:
        test_db.add_user(message.from_user.id, message.from_user.full_name)
    await message.answer("Let`s talk!")


@dp.message(Command("db"))
async def cmd_db(message: Message):
    if test_db is None:
        await message.answer("БД не підключена")
        return
    users = test_db.get_all_users()
    if not users:
        await message.answer("Таблиця порожня")
        return
    text = "\n".join(f"• {u['full_name']} (id: {u['user_id']})" for u in users)
    await message.answer(f"Користувачі:\n{text}")


@dp.message(Command("roll"))
async def cmd_roll(message: Message):
    result = random.randint(1, 6)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="nothing", url="https://google.com"))
    await message.answer(f"🎲 {result}", reply_markup=builder.as_markup())


@dp.message(Command("tictactoe"))
async def game_tictactoe(message: Message):
    chat_id = message.chat.id
    games[chat_id] = {
        "board": " " * 9,
        "ai": "O",
        "human": "X",
    }
    await message.answer("Гра хрестики-нулики розпочата!")


@dp.message()
async def any_message(message: Message):
    print(f"{message.from_user.full_name}: {message.text}")

    if client is None:
        await message.answer("Hello world! (Gemini API не підключено)")
    else:
        try:
            prompt = PromptBuilder.simple_prompt(message.text)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            await message.answer(str(response.text))
        except Exception as err:
            import traceback
            traceback.print_exc()
            await message.answer(f"Помилка:\n{type(err).__name__}\n{err}")


async def main():
    global bot, client, test_db
    load_dotenv()

    bot = auth_telegram()
    client = auth_gemini_api()

    try:
        test_db = DataBase("users")
        print(f"DB connected: {test_db}")
    except Exception as err:
        print(f"Can`t connect to DB: {err}")
        test_db = None

    print("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        print("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())