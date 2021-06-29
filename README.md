# Система управления аккаунтами Telegram для подписки и отписки от каналов.


> Внимание!
> Код программы был написан в октябре 2020 года и некоторые методы библиотеки могли устареть, также возможно изменился API Telegram.


## Оглавление
1. [Функционал](#Функционал)
2. [Команды для управление задачами через бот Telegram](#Команды-для-управление-задачами-через-бот-Telegram)
3. [Исполнение задач](#Исполнение-задач)
4. [База данных](#База-данных)


##Функционал

> Для запуска программы используется файл **start.py**

###Система имеет следующий функционал:

- Позволяет загружать данные Telegram аккаунтов в базу данных
- Автоматическое формирование задач с рандомным выбором аккаунтов, контролем времени подписки
и отписки от каналов и возможностью переноса выполнения задач на определенное время
- Возможность формирование задач только на подписку
- Аккаунты выполняют "просмотр" последник постов в канала
- Просмотр информации о ходе выполнения задач
- Удаление задач (произойдет плановая отписка аккаунтов, которые уже подписались)
- Автоматическое удаление заблокированных аккаунтов и замена на новый аакаунт для выполнения этой задачи
- Игнорирование недействительных ссылок
- Автоматический перенос времни выполнения задач на времня, когда программа была неактивна

##Команды для управление задачами через бот Telegram

Telegram бот написан с использованием библиотеки **aiogram**.

Функции работы бота находятся в файле **functions/telegram_bot_functions.py**.

Логика приема сообщений и передачи в функции прописана в файле **telegram_bot/handlers.py**.

В файле **config.py** находятся **BOT_TOKEN** и **ADMIN_ID** необходимые для работы бота, они подгружаются из окружения
при помощи библиотеки **python-dotenv**. Необходимо создать файл .env и прописать в нем эти переменные окружения.

###Команды управления

- |аргумент| заменить аргументом

####Просмотр списка задач

>task

####Удаление необходимой задачи

>delete |номер задачи из списка|


####Добавление задачи на подписку и одписку

>add |*ссылка на канал| |**время в течении которого будут подписываться аккаунты| |**Время в течении которого боты отписываются от канала|
> |**время через сколько аккаунты начнут отписываться от канала (время от начала первой подписки)| |количство аккаунтов для подписки| 
> |**время на которое отложить выполнение скрипта|

####Добавление задачи только на подписку

>only_add |*ссылка на канал| |**время в течении которого будут подписываться аккаунты| |количство аккаунтов для подписки| 
> |**время на которое отложить выполнение скрипта|

#####* полная ссылка https://t.me/joinchat/............
#####** время в минутах

####Добавление аккаунта

Необходимы 2 файла для каждого аккаунта с расширениями **name.session** и **name.json**. Названия у файлов одного аккаунта должны быть одинаковвыми.
Файлы должны находитсЯ в папке проекта

Команда:

> add_bot |название файла.json|

##Исполнение задач

Функции для исполнения задач находятся в **functions/bot_farm_functions.py**

##База данных

В программе используется база данных **sqlite3** (не лучший выбор, т.к. работа с ней происходит в многопоточном режиме, 
предпочтительнее было бы использовать **postgres** или **mysql**)

Для выполенения запросов к базе данных используется класс **DatabaseManager** с singleton реализацией (Используется только 1 объект этого класса во всех частях программы), 
который находится в файле **database/db_manager.py**

При запуске программы, проверяет наличие базы данных и инициализирует с первичными данными для работы при её отсутствии. За это отвечает файл 
**database/initializing_database.py**

Программа обращается к базе данных в многопоточном режиме, поэтому установлена настройка **check_same_thread=False**

Во избежании комфликта при одновременном обращении к базе данных из разных потоков, используется блокировка потока **Lock()**, которая находитя в **threading**