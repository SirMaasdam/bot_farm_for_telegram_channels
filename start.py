from asyncio import new_event_loop
from threading import Thread
from functions.bot_farm_functions import main_logic
from telegram_bot.telegram_bot_start import start_bot


if __name__ == "__main__":
    """Запуск всех скриптов"""
    loop = new_event_loop()
    thread1 = Thread(target=start_bot, args=(loop, ), daemon=True)
    thread1.start()

    main_logic()
