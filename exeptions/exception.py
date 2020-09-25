class InvalidHashError(Exception):
    """Исключение возникает из-за недействительности хеша"""

    def __init__(self, channel_hash, message="Недействительная ссылка"):
        self.channel_hash = channel_hash
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.channel_hash} -> {self.message}'


class InvalidBotIdError(Exception):
    """Исключение возникает из-за ошибок в зарплате"""

    def __init__(self, bot_id, message="Неправильный id бота"):
        self.bot_id = bot_id
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.bot_id} -> {self.message}'
