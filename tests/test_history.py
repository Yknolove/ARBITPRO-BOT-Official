import sys
import types
import unittest

# Stub aiogram module to import handlers.history without installing dependencies
aiogram_stub = types.ModuleType("aiogram")

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

aiogram_stub.Router = Router
aiogram_stub.F = F

aiogram_types_stub = types.ModuleType("aiogram.types")
class Message: pass
aiogram_types_stub.Message = Message
aiogram_stub.types = aiogram_types_stub
sys.modules.setdefault('aiogram', aiogram_stub)
sys.modules.setdefault('aiogram.types', aiogram_types_stub)

from handlers.history import is_pro_user

class TestIsProUser(unittest.TestCase):
    def test_pro_user_recognized(self):
        self.assertTrue(is_pro_user(123456789))
        self.assertFalse(is_pro_user(111111))

if __name__ == '__main__':
    unittest.main()
