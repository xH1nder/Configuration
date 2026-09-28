"""Тесты этапов 1 и 2."""

import os
import tempfile
import unittest

from src.main import handle, is_error, parse, parse_args
from src.main import run_lines, save_log


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


class TestStage2(unittest.TestCase):
    """Проверка параметров, ошибок и лога."""

    def test_args(self):
        """Параметры разбираются."""
        args = parse_args(["--vfs", "a.json"])
        self.assertEqual(args["vfs"], "a.json")
        args = parse_args(["--log", "l.xml"])
        self.assertEqual(args["log"], "l.xml")
        args = parse_args(["--script", "s.txt"])
        self.assertEqual(args["script"], "s.txt")

    def test_args_empty(self):
        """Без параметров все пустое."""
        args = parse_args([])
        self.assertEqual(args["vfs"], "")
        self.assertEqual(args["log"], "")
        self.assertEqual(args["script"], "")

    def test_is_error(self):
        """Ошибки находятся."""
        self.assertTrue(is_error("error: unknown command"))
        self.assertTrue(is_error("cd: too many arguments"))
        self.assertFalse(is_error("ls: a"))
        self.assertFalse(is_error(""))

    def test_script_stop(self):
        """Скрипт останавливается на ошибке."""
        done = run_lines(["ls a", "foo", "ls b"])
        self.assertEqual(len(done), len(["ls a", "foo"]))
        self.assertIn("unknown", done[1][1])

    def test_log_file(self):
        """Лог пишется в XML."""
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        path = tmp.name
        events = [("bob", "2026-01-01 10:00:00", "ls", "ls")]
        save_log(path, events)
        with open(path, encoding="utf-8") as f:
            data = f.read()
        self.assertIn("<log>", data)
        self.assertIn("<user>bob</user>", data)
        self.assertIn("<command>ls</command>", data)
        os.remove(path)


if __name__ == "__main__":
    unittest.main()
