import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
import aiohttp
import asyncio

API_TOKEN = 'YOUR_TELEGRAM_BOT_API_TOKEN'
WHISPER_API_URL = 'https://api.openai.com/v1/whisper'
ASSISTANT_API_URL = 'https://api.openai.com/v1/assistant'
TTS_API_URL = 'https://api.openai.com/v1/tts'
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def transcribe_voice(file_path):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            WHISPER_API_URL,
            headers={'Authorization': f'Bearer {OPENAI_API_KEY}'},
            data={'file': open(file_path, 'rb')}
        ) as response:
            result = await response.json()
            return result['text']


async def get_assistant_response(text):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            ASSISTANT_API_URL,
            headers={'Authorization': f'Bearer {OPENAI_API_KEY}'},
            json={'prompt': text}
        ) as response:
            result = await response.json()
            return result['choices'][0]['text']


async def text_to_speech(text):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            TTS_API_URL,
            headers={'Authorization': f'Bearer {OPENAI_API_KEY}'},
            json={'text': text}
        ) as response:
            result = await response.json()
            return result['audio_content']


@dp.message_handler(content_types=ContentType.VOICE)
async def handle_voice_message(message: types.Message):
    voice = await message.voice.get_file()
    file_path = f'downloads/{voice.file_id}.ogg'
    await bot.download_file(voice.file_path, file_path)

    transcribed_text = await transcribe_voice(file_path)
    assistant_response = await get_assistant_response(transcribed_text)
    audio_content = await text_to_speech(assistant_response)

    with open(f'{voice.file_id}.mp3', 'wb') as audio_file:
        audio_file.write(audio_content)

    await message.reply_voice(types.InputFile(f'{voice.file_id}.mp3'))


async def main():
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())