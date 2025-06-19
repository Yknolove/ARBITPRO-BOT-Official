class Router:
    def message(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

class DummyTextFilter:
    def __eq__(self, other):
        return False

class F:
    text = DummyTextFilter()

__all__ = ["Router", "F"]
