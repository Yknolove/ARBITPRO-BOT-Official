class FSMContext:
    """Simplified in-memory FSM context placeholder."""

    def __init__(self):
        self.state = None
        self.data = {}

    async def set_state(self, state):
        self.state = state

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def get_data(self):
        return dict(self.data)

    async def clear(self):
        self.state = None
        self.data.clear()


__all__ = ["FSMContext"]
