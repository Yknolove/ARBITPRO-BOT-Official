class Message:
    def __init__(self, text: str = "", chat=None):
        self.text = text
        self.chat = chat or type("Chat", (), {"id": 0})()

    async def answer(self, text: str, parse_mode: str | None = None):
        pass


class InlineKeyboardButton:
    def __init__(self, text: str, callback_data: str):
        self.text = text
        self.callback_data = callback_data


class InlineKeyboardMarkup:
    def __init__(self, inline_keyboard=None):
        self.inline_keyboard = inline_keyboard or []


class CallbackQuery:
    def __init__(self, data: str = "", message: Message | None = None):
        self.data = data
        self.message = message


class BotCommand:
    def __init__(self, command: str, description: str):
        self.command = command
        self.description = description

__all__ = [
    "Message",
    "InlineKeyboardMarkup",
    "InlineKeyboardButton",
    "CallbackQuery",
    "BotCommand",
]
