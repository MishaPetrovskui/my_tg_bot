import asyncio                           # [1]
from os import getenv                    # [1]
from dotenv import load_dotenv
from os import path
from aiogram.types import FSInputFile

# pip install aiogram
from aiogram import Bot, Dispatcher      # [1]
from aiogram.types import Message        # [1]
from aiogram.filters import Command

# pip install google-genai
from google import genai
from google.genai import types
from PromptBuilder import PromptBuilder


dp = Dispatcher()                        # [2]
client = None
bot = None
current_message_context = None

BASE_DIR = "/home/ec2-user/tg_bot/folder"


# Підключення до telegram-бота
def auth_telegram():
    token = getenv("BOT_TOKEN")  # [7]
    if not token:  # [7]
        error = "No token provided"  # [7]
        raise ValueError(error)  # [7]
    return Bot(token=token)  # [8]

# Підключення Gemini API
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

import random

@dp.message(Command("roll"))
async def cmd_roll(message: Message):
    result = random.randint(1, 6)
    await message.answer(f"🎲 {result}")

# Обробник команди /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Let`s talk!")

# Обробних всіх інших повідомлень
@dp.message()                            # [3]
async def any_message(                   # [4]
        message: Message,                # [5]
):
    print(f"{message.from_user.full_name}: {message.text}")
    if client is None:
        await message.answer("Hello world!")
    else:
        try:
            prompt = PromptBuilder.simple_prompt(message.text)
            await message.answer(f"DEBUG: {prompt}")
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )
        except Exception as err:
            import traceback

            traceback.print_exc()

            await message.answer(
                f"Ошибка:\n{type(err).__name__}\n{err}"
            )
        response_text = str(response.text)

async def main():
    global bot, client

    load_dotenv()
    bot = auth_telegram()
    client = auth_gemini_api()

    print("Starting bot...")
    try:
        await dp.start_polling(bot)      # [9]
    finally:
        print("Bot stopped")


if __name__ == '__main__':
    asyncio.run(main())