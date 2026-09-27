"""Тесты этапа 1."""

import unittest

from src.main import handle, parse


class TestStage1(unittest.TestCase):
    """Проверка заглушек."""

    def test_parse(self):
        """Парсер делит команду и аргументы."""
        cmd, args = parse("ls /tmp home")
        self.assertEqual(cmd, "ls")
        self.assertEqual(args, ["/tmp", "home"])

    def test_ls(self):
        """Ls выводит имя и аргументы."""
        out, flag = handle("ls a b")
        self.assertEqual(out, "ls: a b")
        self.assertFalse(flag)

    def test_cd_error(self):
        """Cd с двумя аргументами дает ошибку."""
        out, flag = handle("cd a b")
        self.assertIn("too many", out)
        self.assertFalse(flag)

    def test_unknown(self):
        """Неизвестная команда дает ошибку."""
        out, flag = handle("foo")
        self.assertIn("unknown command", out)
        self.assertFalse(flag)

    def test_exit(self):
        """Exit закрывает."""
        out, flag = handle("exit")
        self.assertEqual(out, "exit")
        self.assertTrue(flag)


if __name__ == "__main__":
    unittest.main()
