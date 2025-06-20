class CommandStart:
    """Placeholder for aiogram.filters.CommandStart"""

    def __init__(self, command: str = "start"):
        self.command = command


class Command:
    """Placeholder for aiogram.filters.Command"""

    def __init__(self, command: str):
        self.command = command


__all__ = ["CommandStart", "Command"]
