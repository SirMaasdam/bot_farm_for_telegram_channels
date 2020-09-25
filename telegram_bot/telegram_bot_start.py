import asyncio

from aiogram import Bot, Dispatcher, executor
from config import BOT_TOKEN

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


def start_bot(loop):
    """Запуск телеграм бота"""
    from telegram_bot.handlers import dp, send_to_admin
    asyncio.set_event_loop(loop)
    loop.run_until_complete(executor.start_polling(dp, on_startup=send_to_admin))
