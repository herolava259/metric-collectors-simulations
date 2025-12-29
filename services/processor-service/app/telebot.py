from telegram import Bot
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_alert_message(message):
    async with bot:
        await bot.send_message(text=message, chat_id=CHAT_ID)

