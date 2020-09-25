import json
import time

from database.db_manager import DatabaseManager

db = DatabaseManager()


def link_formatting(link: str):
    """Проверяет ссылку на наличие в неё s, добавляет ееё в случаи отсутствия"""
    if link[4] != 's':
        return link[:4] + 's' + link[0][4:]


# [0] add - [1] link - [2] channel_entry_time - [3] channel_exit_time - [4] exit_start_time - [5] quantity - [6] expectation
# [0] only_add - [1] link - [2] channel_entry_time - [3] quantity - [4] expectation

def create_task(data: list):
    """Добавляет в базу данных инициализационные задания"""
    link = link_formatting(data[1])
    instruction = data[0]
    if instruction == 'add':
        max_task_id = db.get_max_id('initializing_task')
        db.adding_values_to_database('initializing_task', 7, [(max_task_id, link, int(data[2]) * 60, int(data[3]) * 60,
                                                               int(data[4]) * 60, int(data[5]), int(data[6]) * 60)])
    if instruction == 'only_add':
        max_task_id = db.get_max_id('initializing_only_add_task')
        db.adding_values_to_database('initializing_only_add_task', 5, [(max_task_id, link, int(data[2]) * 60,
                                                                        int(data[3]), int(data[4]) * 60)])
    return "Задача добавлена"


def create_task_information_message(task: list):
    """Формирует юлок информации о ходе выпонения задач"""
    text = ''
    text += f'Канал {task[1]}\n'
    text += f"Время начала    {time.strftime('%H:%M:%S   %d.%m', time.gmtime(task[2] + 18000))}\n"
    text += f"Время окончания   {time.strftime('%H:%M:%S   %d.%m', time.gmtime(task[3] + 18000))}\n"
    text += f'Подписки {task[4]} из {task[5]}\n'
    text += f'Отписки {task[6]} из {task[7]}\n\n'
    return text


def show_task(data: list):
    """Показывает ход выполнения активных задач"""
    text = ''
    for i in db.get_table_data('task_information'):
        if i[4] == i[5] and i[6] == i[7] or i[5] == 0:
            db.deleting_record_from_db('task_information', i[0])
            continue
        text += create_task_information_message(i)
    return text


def preparing_phone_number(phone):
    """Форматирует номер телефона бота"""
    if phone[0] == '+':
        phone = phone[1:]
    return int(''.join(phone.split()))


def get_bot_data_from_json(json_file_name: str):
    """Зозвращает данные о боте из json файла"""
    with open(json_file_name, "r") as file:
        bot_data = json.load(file)
        bot_data['phone'] = preparing_phone_number(bot_data['phone'])
    return bot_data


def add_bot(data: list):
    """Добавляет данные бота в базу данных"""
    json_file_name = ' '.join(data[1:])
    try:
        bot_data = get_bot_data_from_json(json_file_name)
    except FileNotFoundError:
        return "Файла с таким названием не существует"
    max_bot_id = db.get_max_id('bots')
    db.adding_values_to_database('bots', 6, [(max_bot_id, bot_data['app_id'], bot_data['app_hash'], bot_data['phone'],
                                              bot_data['session_file'], bot_data['phone'])])
    return "Бот добавлен"


def delete_task(data: list):
    pass
    """Удаляет задачи и обновляет информаию о ходе выполнения задач"""
    try:
        task_information = db.get_table_data('task_information')[int(data[1]) - 1]
    except IndexError:
        return "Нет такой задачи"
    task_id = task_information[8]
    add_task_ids = [task[0] for task in db.get_record_from_table('add_task', 'bot_id', 'task', task_id)]
    tasks_to_delete = (','.join('?' * len(add_task_ids)), add_task_ids)
    db.delete_records_whose_argument_is_in_list_and_matches_the_condition('exit_task', 'bot_id', tasks_to_delete,
                                                                          'task', task_id)
    db.deleting_record_from_db('add_task', task_id, 'task')
    db.update_record("task_information", 'count_add_task', 0, 'id', task_information[0])
    return f"Задача {data[1]} удалена"
