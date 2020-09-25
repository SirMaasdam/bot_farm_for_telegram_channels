from threading import Lock
import sqlite3
from typing import Any

from database.initializing_database import create_db

lock = Lock()


class MetaSingleton(type):
    """Мета класс Singleton, возвращает объект, если он уже существует"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DatabaseManager(metaclass=MetaSingleton):
    """Класс для запросов к базе данных"""

    connection = None

    def __init__(self):
        create_db()
        self.connection = sqlite3.connect("server.sqlite", check_same_thread=False)
        self.cursorobj = self.connection.cursor()

    def connect(self):
        return self.cursorobj

    def get_record_data(self, table_name: str, record_id: int):
        """Возвращает все данные для записи из базы данных"""
        with lock:
            return self.cursorobj.execute(f'SELECT * from "{table_name}" WHERE id=?', (record_id,)).fetchone()

    def get_list_record_ids(self, table_name: str):
        """Возвращает список с id всех ботов в база денных"""
        with lock:
            return [data[0] for data in self.cursorobj.execute(f'SELECT * from "{table_name}"').fetchall()]

    def get_max_id(self, table_name: str):
        """Возвращает максимальный id в таблице"""
        with lock:
            max_id = self.cursorobj.execute(f'SELECT max(id) from "{table_name}"').fetchone()[0]
            return max_id if max_id else 1

    def adding_values_to_database(self, table_name: str, arguments_number: int, argument_values: list):
        """Записывает в таблицу массив значений"""
        with lock:
            arguments = "(?" + ', ?' * (arguments_number - 1) + ")"
            self.cursorobj.executemany(f'INSERT INTO "{table_name}" VALUES {arguments}', argument_values)
            self.connection.commit()

    def deleting_record_from_db(self, table_name: str, record_id: int, condition_column: str = 'id'):
        """Удаляет запись из таблицы"""
        with lock:
            self.cursorobj.execute(f'DELETE from "{table_name}" WHERE "{condition_column}"=?', (record_id,))
            self.connection.commit()

    def get_bot_ids_that_are_not_in_task(self, table_name: str, channel: str):
        """Возвращаяет данные ботов, которые нет в задаче на добавление в канал"""
        with lock:
            return [bot[0] for bot in
                    self.cursorobj.execute(
                        f'SELECT * from bots WHERE NOT EXISTS (SELECT bot_id from "{table_name}" WHERE channel=?)',
                        (channel,)).fetchall()]

    def update_record_with_two_conditions(self, table_name: str, change_column: str, change_argument: Any,
                                          first_condition_column: str, first_condition_argument: Any,
                                          two_condition_column: str, two_condition_argument: Any):
        with lock:
            self.cursorobj.execute(
                f'UPDATE "{table_name}" SET "{change_column}"=? WHERE "{first_condition_column}"=? AND "{two_condition_column}"=?',
                (change_argument, first_condition_argument, two_condition_argument))
            self.connection.commit()

    def delete_records_whose_argument_is_in_list_and_matches_the_condition(self, table_name: str,
                                                                           firs_condition_column: str,
                                                                           firs_condition_argument: tuple,
                                                                           second_condition_column: str,
                                                                           second_condition_argument: Any):
        with lock:
            self.cursorobj.execute(
                f'DELETE from "{table_name}" WHERE "{firs_condition_column}" IN (%s) AND "{second_condition_column}" = '
                f'"{second_condition_argument}"' % firs_condition_argument)
            self.connection.commit()

    def get_record_from_table(self, table_name: str, column_name: str, condition_column: str = 'id',
                              condition_argument: Any = 1):
        """Обновляет определенные данные из записи в таблице, которые удовлетворяю условию"""
        with lock:
            return self.cursorobj.execute(f'SELECT "{column_name}" from "{table_name}" WHERE "{condition_column}"=?',
                                          (condition_argument,)).fetchone()[0]

    def update_record(self, table_name: str, change_column: str, change_argument: Any, condition_column: str,
                      condition_argument: Any):
        """Обновляет записи таблицы, которые удовлетворяю условию"""
        with lock:
            self.cursorobj.execute(f'UPDATE "{table_name}" SET "{change_column}"=? WHERE "{condition_column}"=?',
                                   (change_argument, condition_argument))
            self.connection.commit()

    def get_table_data(self, table_name: str):
        """Возвращает все данные для кадой записи из таблицы"""
        with lock:
            return self.cursorobj.execute(f'SELECT * from "{table_name}"').fetchall()

    def get_records_that_are_less_then_condition(self, table_name: str, condition_column: str, condition_argument: Any):
        """Возращает записи, которые подходят по условию"""
        with lock:
            return self.cursorobj.execute(f'SELECT * from "{table_name}" WHERE "{condition_column}"<?',
                                          (condition_argument,)).fetchall()
