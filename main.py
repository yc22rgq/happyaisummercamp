import openai
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from config import settings

bot = Bot(token=settings.telegram_token)
dp = Dispatcher(bot)

@dp.message_handler(content_types=ContentType.VOICE)
async def handle_voice_message(message: types.Message):
    voice = await message.voice.get_file()
    voice_file_path = f"downloads/{voice.file_id}.ogg"
    await bot.download_file(voice.file_path, voice_file_path)

    # Конвертация голосового сообщения в текст
    with open(voice_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    await message.reply(transcript["text"])

async def get_openai_response(prompt: str) -> str:
    response = await openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        api_key=settings.openai_api_key
    )
    return response.choices[0].message["content"]

async def text_to_speech(text: str) -> bytes:
    response = await openai.Audio.create(
        model="text-to-speech-1",
        input=text,
        api_key=settings.openai_api_key
    )
    return response["audio"]

@dp.message_handler(content_types=ContentType.VOICE)
async def handle_voice_message(message: types.Message):
    voice = await message.voice.get_file()
    voice_file_path = f"downloads/{voice.file_id}.ogg"
    await bot.download_file(voice.file_path, voice_file_path)

    # Конвертация голосового сообщения в текст
    with open(voice_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    user_text = transcript["text"]
    response_text = await get_openai_response(user_text)

    # Озвучка ответа
    audio_data = await text_to_speech(response_text)
    audio_file_path = f"downloads/{voice.file_id}_response.ogg"
    with open(audio_file_path, "wb") as audio_file:
        audio_file.write(audio_data)

    await message.reply_voice(types.InputFile(audio_file_path))


if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)