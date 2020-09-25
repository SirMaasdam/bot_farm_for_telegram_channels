import random
from typing import Any

import telethon
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon import TelegramClient
import time

from telethon.tl import functions

from database.db_manager import DatabaseManager
from exeptions.exception import InvalidHashError, InvalidBotIdError

import sqlite3

db = DatabaseManager()


def get_channel_hash(bot_ids: list, channel_hash: str):
    """Возвращает id канала"""
    try:
        for bot in bot_ids:
            channel_id = task_execution(bot, channel_hash, 'add', True)
            if channel_id:
                return channel_id, bot
    except InvalidHashError:
        return [None, None]
    except InvalidBotIdError:
        return [None, None]
    else:
        return [None, None]


def add_task_information(channel_link: str, end_time: int, bots_number: int, expectation: int,
                         task_id: int) -> None:
    """Создает запись в таблице мониторинга выполнения задачи"""
    max_id = db.get_max_id('task_information')
    creation_time = int(time.time())
    task_information_id = max_id + 1
    db.adding_values_to_database('task_information', 9, [(task_information_id, channel_link, creation_time, end_time, 1,
                                                          bots_number, 0, expectation, task_id)])


def creating_task_queue(bots_number: int, bot_ids: list, channel_link: str, task_id: int, channel_id: int,
                        first_subscribed_bot_id: int, channel_exit_time: int, channel_entry_time: int,
                        expectation: int, exit_start_time: int):
    """Создает задачи на подписку и отписку от канала"""
    using_id = []
    add_task_list = []
    exit_task_list = []
    exit_interval = channel_exit_time // bots_number
    entry_interval = channel_entry_time // bots_number
    add_task_id = db.get_max_id('add_task')
    exit_task_id = db.get_max_id('exit_task')
    time_now = int(time.time())

    for i in range(1, bots_number + 1):
        random_bot = random.choice(bot_ids)
        while random_bot in using_id:
            random_bot = random.choice(bot_ids)
        using_id.append(random_bot)
        add_task_list.append((add_task_id, random_bot, channel_link, time_now + expectation + entry_interval * i,
                              task_id))
        add_task_id += 1
        exit_task_list.append((exit_task_id, random_bot, channel_id,
                               time_now + exit_start_time + expectation + exit_interval * i, channel_link, task_id))
        exit_task_id += 1
        if i == bots_number:
            exit_task_list.append((exit_task_id, first_subscribed_bot_id, channel_id,
                                   time_now + exit_start_time + expectation + exit_interval * i, channel_link, task_id))
    db.adding_values_to_database('add_task', 5, add_task_list)
    db.adding_values_to_database('exit_task', 6, exit_task_list)


def create_only_add_task_queue(bots_number: int, channel_entry_time: int, bot_ids: list, channel_link: str,
                               expectation: int, task_id: int):
    """Создает задачи только на подписку на каналы"""
    add_task_list = []
    entry_interval = channel_entry_time // bots_number
    using_id = []
    add_task_id = db.get_max_id('task_only_add')
    time_now = int(time.time())

    for i in range(1, bots_number + 1):
        random_bot = random.choice(bot_ids)
        while random_bot in using_id:
            random_bot = random.choice(bot_ids)
        using_id.append(random_bot)
        add_task_list.append((add_task_id, random_bot, channel_link, time_now + expectation + entry_interval * i,
                              task_id))
    db.adding_values_to_database('task_only_add', 5, add_task_list)


def initial_task_processing(task_id: int):
    """Первичная обработка задачи на вступленые и выход из канала"""
    task = db.get_record_data('initializing_task', task_id)

    task_id = task[0]
    channel_link = task[1]
    channel_entry_time = task[2]
    channel_exit_time = task[3]
    exit_start_time = task[4]
    bots_number = task[5]
    expectation = task[6]
    end_time = int(time.time()) + channel_link + channel_entry_time + channel_exit_time
    bot_ids = db.get_list_record_ids('bots')

    add_task_information(channel_link, end_time, bots_number, expectation, task_id)

    channel_id, first_subscribed_bot_id = get_channel_hash(bot_ids, channel_link[22:])
    if not channel_id:
        return
    creating_task_queue(bots_number=bots_number, bot_ids=bot_ids, channel_link=channel_link, task_id=task_id,
                        channel_id=channel_id, first_subscribed_bot_id=first_subscribed_bot_id,
                        channel_exit_time=channel_exit_time, channel_entry_time=channel_entry_time,
                        expectation=expectation, exit_start_time=exit_start_time)


def initial_only_add_task_processing(task_id: int):
    """Первичная обработка задачи на вступление в канал"""
    task = db.get_record_data('initializing_only_add_task', task_id)

    channel_link = task[1]
    channel_entry_time = task[2]
    bots_number = task[3]
    expectation = task[4]
    bot_ids = db.get_list_record_ids('bots')

    create_only_add_task_queue(bots_number, channel_entry_time, bot_ids, channel_link,
                               expectation, task_id)


def replacing_bot(bot_id: int, channel: str, is_only_add: bool = False):
    """Производит замену бота для задачи"""
    table_name = 'task_only_add' if is_only_add else 'add_task'
    bot_ids = db.get_bot_ids_that_are_not_in_task(table_name, channel)
    random_bot = random.choice(bot_ids)
    db.update_record_with_two_conditions(table_name, 'bot_id', random_bot, 'bot_id', bot_id, 'channel', channel)
    if not is_only_add:
        db.update_record_with_two_conditions('exit_task', 'bot_id', random_bot, 'bot_id', bot_id, 'channel', channel)


def bot_authorization(client, phone: int):
    """Авторизует бота и ставит его статус в онлайн"""
    client.start(phone=phone)
    client(functions.account.UpdateStatusRequest(
        offline=False
    ))


def join_channel(client, channel_hash: str):
    """Бот вступает в канал"""
    updates = client(ImportChatInviteRequest(hash=channel_hash))
    client(functions.channels.JoinChannelRequest(
        channel=updates.chats[0].id
    ))
    return updates


def viewing_posts(client, updates, quantity: int):
    """Бот просматривает последние quantity количество постов"""
    messages = client.get_messages(updates.chats[0].id)
    for i in range(quantity):
        try:
            client(functions.messages.GetMessagesViewsRequest(
                peer=updates.chats[0].id,
                id=[messages[0].id - i],
                increment=True
            ))
        except IndexError:
            continue


def exit_channel(client, channel_id: int):
    """Бот выходит из канала"""
    client(functions.channels.LeaveChannelRequest(
        channel=channel_id
    ))


def bot_replacement_or_delete_settings(bot_id: int, channel_hash: Any, task_type: str, delete: bool = False,
                                       return_channel_id: bool = False):
    """Определяет настройки для замены бота в задаче на подписку на канал и необходимость удаления бота"""
    if not return_channel_id:
        if task_type == 'only_add':
            replacing_bot(bot_id, channel_hash, True)
        elif task_type == 'add':
            replacing_bot(bot_id, channel_hash)
    if delete:
        db.deleting_record_from_db('bots', bot_id)


def task_execution(bot_id: int, channel_hash: Any, type_task: str, return_channel_id: bool = False):
    """Исполнение задачи"""
    bot = db.get_record_data('bots', bot_id)
    if not bot:
        raise InvalidBotIdError(bot_id)
    bot_id = bot[0]
    api_id = bot[1]
    api_hash = bot[2]
    session_name = bot[4]
    phone = bot[5]
    client = TelegramClient(session_name, api_id, api_hash)
    try:
        bot_authorization(client, phone)
        if type_task != 'exit':
            updates = join_channel(client, channel_hash)
            viewing_posts(client, updates, 15)
            client.disconnect()
            if return_channel_id:
                return updates.chats[0].id
            return True
        if type_task == 'exit':
            exit_channel(client, channel_hash)
            client.disconnect()
    except TypeError:
        client.disconnect()
    except telethon.errors.rpcerrorlist.InviteHashExpiredError:  # неправильный хеш
        client.disconnect()
        raise InvalidHashError(channel_hash)
    except RuntimeError:  # бот удален
        if type_task == 'exit':
            return True
        bot_replacement_or_delete_settings(bot_id, channel_hash, type_task, delete=True,
                                           return_channel_id=return_channel_id)
        return None
    except telethon.errors.rpcerrorlist.FloodWaitError:  # бан флуда
        client.disconnect()
        return None
    except telethon.errors.rpcerrorlist.PhoneNumberBannedError:  # бот удален
        if type_task == 'exit':
            return True
        bot_replacement_or_delete_settings(bot_id, channel_hash, type_task, delete=True,
                                           return_channel_id=return_channel_id)
        return None
    except telethon.errors.rpcerrorlist.ChannelsTooMuchError:  # превышено ограничение по подпискам
        client.disconnect()
        if type_task == 'exit':
            return True
        bot_replacement_or_delete_settings(bot_id, channel_hash, type_task, return_channel_id=return_channel_id)
        return None
    except telethon.errors.rpcerrorlist.UserAlreadyParticipantError:  # бот уже подписан на канал
        client.disconnect()
        if type_task == 'exit':
            return True
        bot_replacement_or_delete_settings(bot_id, channel_hash, type_task, return_channel_id=return_channel_id)
        return None
    except ValueError:
        client.disconnect()
    except IndexError:
        client.disconnect()
    except sqlite3.OperationalError:  # база данных заблокирована
        client.disconnect()
        time.sleep(1)
        return task_execution(bot_id, channel_hash, type_task, return_channel_id)
    except telethon.errors.rpcerrorlist.AuthKeyDuplicatedError:  # бот находится в 2 сессиях
        client.disconnect()
        if type_task == 'exit':
            return True
        bot_replacement_or_delete_settings(bot_id, channel_hash, type_task, return_channel_id=return_channel_id)
        return None
    except telethon.errors.rpcerrorlist.UserNotParticipantError:  # бот не является частью группы или канала
        client.disconnect()
        return True
    except telethon.errors.rpcerrorlist.ChannelPrivateError:
        client.disconnect()
        if return_channel_id:
            return None
        return True


def update_task_time(table_name: str, column: str, program_stop_time: int, time_now: int):
    """Переносит время исполнения задачи, на определенное время"""
    for i in db.get_table_data(table_name):
        add_task_id = i[0]
        channel_entry_time = i[3]
        channel_entry_time = time_now + channel_entry_time - program_stop_time
        db.update_record('add_task', column, channel_entry_time, 'id', add_task_id)


def recalculating_tasks():
    """Переносит время исполнения всех задач, на время отсутствия работы программы"""
    program_stop_time = db.get_record_from_table('time_end', 'time_finish')
    time_now = int(time.time()) + 60
    update_task_time('add_task', 'channel_entry_time', program_stop_time, time_now)
    update_task_time('exit_task', 'channel_exit_time', program_stop_time, time_now)


def update_task_information(table_name: str, change_column: str, search_column: str, search_argument: int):
    """Обновляет информацию о ходе выполнения задач"""
    change_argument = db.get_record_from_table(table_name, change_column, search_column, search_argument)
    if change_argument:
        db.update_record(table_name, change_column, change_argument, search_column, search_argument)


def check_task_queue(table_name: str, condition_column: str, type_task: str):
    """Проверяет очередь задач и исполняет их"""
    for task in db.get_records_that_are_less_then_condition(table_name, condition_column, int(time.time())):
        task_id = task[0]
        bot_id = task[1]
        channel_hash = task[2]
        try:
            is_done = task_execution(bot_id, channel_hash, type_task)
        except InvalidBotIdError:
            is_done = True
        except InvalidHashError:
            is_done = True
        if is_done:
            db.deleting_record_from_db(table_name, task_id)
            if type_task == 'add':
                update_task_information('task_information', 'already_joined', 'task', task[4])
            elif type_task == 'exit':
                update_task_information('task_information', 'already_exit', 'task', task[5])
        break


def tasks_monitoring():
    """Запускает проверку каждого вида задач"""
    check_task_queue('add_task', 'channel_entry_time', 'add')
    check_task_queue('exit_task', 'channel_exit_time', 'exit')
    check_task_queue('task_only_add', 'channel_entry_time', 'only_add')


def checking_for_new_initialization_tasks(table_name_count_task: str, column_name_count_task: str,
                                          table_name_initializing_task: str):
    """Производи проверку на добавоение новых инициализационных задач и инициализирует их"""
    count_task = db.get_record_from_table(table_name_count_task, column_name_count_task)
    count_task_max = db.get_max_id(table_name_initializing_task)
    if count_task != count_task_max and count_task:
        initial_task_processing(count_task_max + 1)
        db.update_record(table_name_count_task, column_name_count_task, count_task_max + 1, 'id', 1)


def updating_the_end_point_of_the_program():
    """Обновляет запись о времени, когда программа работа в последний раз"""
    if int(time.time()) > db.get_record_from_table('time_end', 'time_finish'):
        db.update_record('time_end', 'time_finish', int(time.time()), 'id', 1)


def main_logic():
    time.sleep(1)
    recalculating_tasks()
    while True:
        print(1)
        tasks_monitoring()
        checking_for_new_initialization_tasks('count_task', 'count_task', 'initializing_task')
        checking_for_new_initialization_tasks('count_only_add_task', 'count_task', 'initializing_only_add_task')

        updating_the_end_point_of_the_program()

        time.sleep(1)
