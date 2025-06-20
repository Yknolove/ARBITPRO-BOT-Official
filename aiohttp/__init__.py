class ClientSession:
    async def get(self, url, **kwargs):
        class Resp:
            async def json(self):
                return {}
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                pass
        return Resp()

    async def post(self, url, json=None, **kwargs):
        class Resp:
            async def json(self):
                return {}
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                pass
        return Resp()

# minimal stubs for aiohttp.web used in the application

class _Router:
    def add_post(self, path, handler):
        pass


class _Application:
    def __init__(self):
        self.router = _Router()


class _AppRunner:
    def __init__(self, app):
        self.app = app

    async def setup(self):
        pass


class _TCPSite:
    def __init__(self, runner, port=0):
        self.runner = runner
        self.port = port

    async def start(self):
        pass


class _Response:
    def __init__(self, text=""):
        self.text = text


class web:
    Response = _Response
    Application = _Application
    AppRunner = _AppRunner
    TCPSite = _TCPSite

    async def post(self, url, json=None, **kwargs):
        class Resp:
            async def json(self):
                return {}
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                pass
        return Resp()
