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

from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder


dp = Dispatcher()
client = None
bot = None

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

@dp.message(Command("roll"))
async def cmd_roll(message: Message):
    result = random.randint(1, 6)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="nothing", url="https://google.com"))
    
    await message.answer(f"🎲 {result}", reply_markup=builder.as_markup())

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Let`s talk!")

@dp.message()
async def any_message(message: Message):
    print(f"{message.from_user.full_name}: {message.text}")
    
    if client is None:
        await message.answer("Hello world! (Gemini API не подключен)")
    else:
        try:
            prompt = PromptBuilder.simple_prompt(message.text)
            
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )
            
            response_text = str(response.text)

            await message.answer(response_text)

            
        except Exception as err:
            import traceback
            traceback.print_exc()
            await message.answer(f"Ошибка:\n{type(err).__name__}\n{err}")

@dp.message(Command("tictactoe"))
async def game_tictactoe(message: Message):
    chat_id = message.chat.id
    games[chat_id] = {
        "board" = " " * 9,
        "ai" = "O",
        "human" = "X",
    }


async def main():
    global bot, client
    load_dotenv()
    
    bot = auth_telegram()
    client = auth_gemini_api()

    print("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        print("Bot stopped")

if __name__ == '__main__':
    asyncio.run(main())