# bot.py
from balethon import Client
import asyncio
import os
from dotenv import load_dotenv

load_dotenv(".env")


async def main():
    bot = Client(os.getenv("BALE_TOKEN"))
    await bot.set_webhook(os.getenv("WEBHOOK_URL"))
    print("Webhook set successfully!")


asyncio.run(main())
