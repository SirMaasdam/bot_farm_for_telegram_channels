from telegram_bot.telegram_bot_start import bot, dp
import aiogram
from aiogram.types import Message
from config import ADMIN_ID

from functions.telegram_bot_functions import show_task, delete_task, create_task, add_bot


async def send_to_admin(*args):
    """Оповещает админа о запуске бота"""
    await bot.send_message(chat_id=ADMIN_ID, text="Бот запущен")


funk = {
    "tasks": show_task,
    "delete": delete_task,
    "add": create_task,
    "only_add": create_task,
    "add_bot": add_bot
}


@dp.message_handler()
async def echo(message: Message):
    """Работа бота в Telegram"""
    try:
        data = message.text.split()
        text = "Не правильный ввод"
        instruction = data[0].lower()
        if instruction in funk:
            text = funk[instruction](data)
        await message.reply(text=text)
    except aiogram.utils.exceptions.MessageTextIsEmpty:
        await message.reply(text='Задач нет')
    except ValueError:
        await message.reply(text='Некоректные введенные данные')
    except IndexError:
        await message.reply(text='Некоректные введенные данные')
    except TypeError:
        await message.reply(text='Некоректные введенные данные')
    except KeyError:
        await message.reply(text='Ошибка в файле инициализатора данных бота')

