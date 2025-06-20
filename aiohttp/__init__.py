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
