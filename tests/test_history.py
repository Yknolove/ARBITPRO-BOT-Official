from handlers.history import is_pro_user
import unittest


class TestIsProUser(unittest.TestCase):
    def test_pro_user_recognized(self):
        self.assertTrue(is_pro_user(123456789))
        self.assertFalse(is_pro_user(111111))


if __name__ == "__main__":
    unittest.main()

