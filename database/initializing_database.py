import os
import sqlite3
import time


def create_db():
    """Первичная инициализация базы данных"""
    if not os.path.isfile('server.sqlite'):
        db = sqlite3.connect('server.sqlite')
        sql = db.cursor()

        sql.execute("""CREATE TABLE IF NOT EXISTS time_end (
            id INT PRIMARY KEY,
            time_finish INT NOT NULL
        )""")

        sql.execute("""CREATE TABLE IF NOT EXISTS bots (
            id INT PRIMARY KEY,
            api_id INT NOT NULL,
            api_hash TEXT NOT NULL,
            link TEXT NOT NULL,
            session_name TEXT NOT NULL,
            phone INT NOT NULL
        )""")

        sql.execute("""CREATE TABLE IF NOT EXISTS add_task (
            id INT PRIMARY KEY,
            bot_id INT NOT NULL,
            channel TEXT NOT NULL,
            channel_entry_time INT NOT NULL,
            task INT NOT NULL
        )""")

        sql.execute("""CREATE TABLE IF NOT EXISTS exit_task (
            id INT PRIMARY KEY,
            bot_id INT NOT NULL,
            channel BIGINT NOT NULL,
            channel_exit_time INT NOT NULL,
            link TEXT NOT NULL,
            task INT NOT NULL
        )""")

        sql.execute("""CREATE TABLE IF NOT EXISTS initializing_task (
            id INT PRIMARY KEY,
            channel TEXT NOT NULL,
            channel_entry_time INT NOT NULL,
            channel_exit_time INT NOT NULL,
            exit_start_time INT NOT NULL,
            quantity INT NOT NULL,
            expectation BIGINT NOT NULL
        )""")

        sql.execute("""CREATE TABLE IF NOT EXISTS task_information (
            id INT PRIMARY KEY,
            channel TEXT,
            creation_time INT NOT NULL,
            end_time INT NOT NULL,
            already_joined INT NOT NULL,
            count_add_task INT NOT NULL,
            count_now_leave already_exit INT NOT NULL,
            count_exit_task INT NOT NULL,
            task INT
        )""")

        sql.execute("""CREATE TABLE IF NOT EXISTS count_task (
            id INT PRIMARY KEY,
            count_task INT NOT NULL
        )""")

        sql.execute("""CREATE TABLE IF NOT EXISTS initializing_only_add_task (
            id INT PRIMARY KEY,
            channel TEXT NOT NULL,
            channel_entry_time INT NOT NULL,
            quantity INT NOT NULL,
            expectation BIGINT NOT NULL
        )""")

        sql.execute("""CREATE TABLE IF NOT EXISTS task_only_add  (
            id INT PRIMARY KEY,
            bot_id INT NOT NULL,
            channel TEXT NOT NULL,
            channel_entry_time INT NOT NULL,
            task INT NOT NULL
        )""")

        sql.execute("""CREATE TABLE IF NOT EXISTS count_only_add_task (
            id INT PRIMARY KEY,
            count_task INT NOT NULL
        )""")

        sql.execute("""CREATE TABLE IF NOT EXISTS message (
            ID INT PRIMARY KEY NOT NULL,
            AGE TEXT NOT NULL
        );""")

        sql.execute(f"INSERT INTO time_end VALUES (?, ?)", (1, int(time.time())))
        sql.execute(f"INSERT INTO count_task VALUES (?, ?)", (1, 0))
        sql.execute(f"INSERT INTO count_only_add_task VALUES (?, ?)", (1, 0))

        db.commit()
