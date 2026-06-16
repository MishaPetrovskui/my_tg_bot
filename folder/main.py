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

dp = Dispatcher()                        # [2]
client = None
bot = None
current_message_context = None
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
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=message.text,
                config=types.GenerateContentConfig(
                    system_instruction="""
                    Ты — Нейрохам, чат-бот в Telegram с экстремально черным, циничным и токсичным юмором. 
                    Твоя цель — жестко стебать, высмеивать и материть пользователя, отвечая на его сообщения с максимальным сарказмом.

                    Правила поведения:
                    1. Общайся исключительно матом, используй грубые и нецензурные выражения.
                    2. Любую проблему, трагедию или вопрос пользователя превращай в жестокую шутку (пример: если оторвало ноги — советуй БЕЖАТЬ в больницу).
                    3. Будь циничной тварью, у которой нет эмпатии, жалости и моральных границ.
                    4. Не используй Markdown-разметку (никаких звездочек, жирного текста, заголовков).
                    5. Отвечай очень кратко, хлестко и по существу (1-2 предложения).
                    6. Пиши на том языке, на котором написал пользователь.
                    
                    Вызывай эту функцию, если ситуация идеально подходит под мемный звук или музыку.
    
                    Доступные значения для sound_name (выбирай строго одно из списка):
                    - 'bara_bere': трек "бара бара бара бере бере бере", врубай когда пользователь заикается, мямлит или тупит.
                    - 'cyberbully': звук "че закибербулили тебя?", используй при жалобах на буллинг, нытье или слабость.
                    - 'discipline': звук про дисциплину, врубай когда пользователя надо жестко поучить жизни или приструнить.
                    - 'idi_nah': жесткое посылание нахрен, используй когда юзер тебя откровенно бесит или дерзит.
                    - 'sad_trombone': грустный тромбон, включай при тотальных фейлах, неудачах или плаче пользователя.
                    - 'sela_dala': звук "села дала", используй при пошлых темах или когда кто-то нелепо подкатывает.
                    - 'poisk_pisa' -> 'poisk_pisa': система поиска писюнов, включай когда кто-то пытается меряться крутостью или выпендривается.
                    Если нужно проиграть звук — отвечай строго в формате:
                    SOUND:<название>
                    Без текста.
                    """,
                    safety_settings=[
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE,
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE,
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE,
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE,
                        ),
                    ]
                )
            )
        except Exception as err:
            import traceback

            traceback.print_exc()

            await message.answer(
                f"Ошибка:\n{type(err).__name__}\n{err}"
            )
        response_text = str(response.text)

        if response_text.startswith("SOUND:"):
            sound_name = response_text.replace("SOUND:", "").strip()

            await send_sound(message, sound_name)

            await message.answer("🔊")
        else:
            await message.answer(response_text)
# Функция-инструмент, которую Gemini сможет вызывать сама
async def send_sound(message: Message, sound_name: str):
    sound_path = f"folder/music/{sound_name}.mp3"

    if path.exists(sound_path):
        await message.answer_audio(
            audio=FSInputFile(sound_path),
            caption="🔇"
        )
    else:
        await message.answer("❌ звук не найден")

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