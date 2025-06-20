class Router:
    def message(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def callback_query(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

class DummyTextFilter:
    def __eq__(self, other):
        return False

class F:
    text = DummyTextFilter()


class Bot:
    def __init__(self, token: str, parse_mode: str | None = None):
        self.token = token
        self.parse_mode = parse_mode

    async def set_my_commands(self, commands):
        pass

    async def send_message(self, chat_id, text, parse_mode: str | None = None):
        pass

    async def set_webhook(self, url: str):
        pass


class Dispatcher:
    def __init__(self, storage=None):
        self.storage = storage

    def include_router(self, router: Router):
        pass

    async def feed_update(self, bot: Bot, update):
        pass

__all__ = ["Router", "F", "Bot", "Dispatcher"]
