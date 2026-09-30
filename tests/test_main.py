"""Тесты этапов 1, 2, 3 и 4."""

import os
import tempfile
import unittest

import src.main
from src.main import count_vfs, find_node, handle, is_error
from src.main import load_vfs, parse, parse_args
from src.main import run_lines, save_log


def make_root():
    """Собрать маленькую VFS для тестов."""
    return {"type": "dir", "name": "/", "children": [
        {"type": "dir", "name": "home", "children": [
            {"type": "dir", "name": "user", "children": [
                {"type": "file", "name": "f.txt",
                 "content": "x"}]}]},
        {"type": "file", "name": "a.txt", "content": "A"}]}


class TestStage1(unittest.TestCase):
    """Проверка парсера и выхода."""

    def test_parse(self):
        """Парсер делит команду и аргументы."""
        cmd, args = parse("ls /tmp home")
        self.assertEqual(cmd, "ls")
        self.assertEqual(args, ["/tmp", "home"])

    def test_cd_error(self):
        """Cd с двумя аргументами дает ошибку."""
        src.main.vfs_root = make_root()
        src.main.cur_dir = "/"
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
        self.assertTrue(is_error("ls: no such file"))
        self.assertTrue(is_error("cd: not a directory"))
        self.assertTrue(is_error("rmdir: missing operand"))
        self.assertTrue(is_error("rmdir: cannot remove"))
        self.assertTrue(is_error("cp: cannot stat"))
        self.assertTrue(is_error("cp: same file"))
        self.assertFalse(is_error("readme.txt home/"))
        self.assertFalse(is_error(""))

    def test_script_stop(self):
        """Скрипт останавливается на ошибке."""
        done = run_lines(["pwd", "foo", "ls"])
        self.assertEqual(len(done), len(["pwd", "foo"]))
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


class TestStage3(unittest.TestCase):
    """Проверка загрузки VFS."""

    def make_json(self, text):
        """Создать временный json и вернуть путь."""
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".json", mode="w",
            encoding="utf-8")
        tmp.write(text)
        tmp.close()
        return tmp.name

    def test_load_min(self):
        """Минимальная VFS грузится."""
        path = self.make_json(
            '{"type": "dir", "name": "/", '
            '"children": [{"type": "file", '
            '"name": "a.txt", "content": "hi"}]}')
        root, err = load_vfs(path)
        self.assertEqual(err, "")
        self.assertEqual(root["name"], "/")
        os.remove(path)

    def test_load_missing(self):
        """Нет файла дает ошибку."""
        root, err = load_vfs("no_such_vfs_123.json")
        self.assertEqual(root, None)
        self.assertIn("not found", err)

    def test_load_bad_json(self):
        """Битый json дает ошибку."""
        path = self.make_json("{bad json")
        root, err = load_vfs(path)
        self.assertEqual(root, None)
        self.assertIn("bad format", err)
        os.remove(path)

    def test_load_deep(self):
        """Три уровня находятся."""
        path = self.make_json(
            '{"type": "dir", "name": "/", "children": ['
            '{"type": "dir", "name": "home", "children": ['
            '{"type": "dir", "name": "user", "children": ['
            '{"type": "dir", "name": "docs", "children": ['
            '{"type": "file", "name": "f.txt", '
            '"content": "x"}]}]}]}]}')
        root, err = load_vfs(path)
        self.assertEqual(err, "")
        node = find_node(root, "/home/user/docs")
        self.assertNotEqual(node, None)
        self.assertEqual(node["name"], "docs")
        self.assertEqual(find_node(root, "/nope"), None)
        found_dirs, found_files = count_vfs(root)
        dirs = ["/", "home", "user", "docs"]
        self.assertEqual(found_dirs, len(dirs))
        self.assertEqual(found_files, len(["f.txt"]))
        os.remove(path)

    def test_base64(self):
        """Бинарный файл проверяется."""
        good = self.make_json(
            '{"type": "dir", "name": "/", "children": ['
            '{"type": "file", "name": "a.bin", '
            '"encoding": "base64", '
            '"content": "aGVsbG8="}]}')
        root, err = load_vfs(good)
        self.assertEqual(err, "")
        os.remove(good)
        bad = self.make_json(
            '{"type": "dir", "name": "/", "children": ['
            '{"type": "file", "name": "a.bin", '
            '"encoding": "base64", "content": "!!!"}]}')
        root, err = load_vfs(bad)
        self.assertEqual(root, None)
        self.assertIn("bad base64", err)
        os.remove(bad)


class TestStage4(unittest.TestCase):
    """Проверка ls, cd, pwd, tree."""

    def setUp(self):
        """Готовить VFS перед тестом."""
        src.main.vfs_root = make_root()
        src.main.cur_dir = "/"
        src.main.prompt = src.main.make_prompt()

    def test_ls_root(self):
        """Ls корня показывает папки и файлы."""
        out, flag = handle("ls")
        self.assertIn("home/", out)
        self.assertIn("a.txt", out)
        self.assertFalse(flag)

    def test_ls_deep(self):
        """Ls папки показывает ее файлы."""
        out, flag = handle("ls /home/user")
        self.assertEqual(out, "f.txt")
        self.assertFalse(flag)

    def test_ls_file(self):
        """Ls файла показывает его имя."""
        out, flag = handle("ls /a.txt")
        self.assertEqual(out, "a.txt")

    def test_ls_missing(self):
        """Ls нет папки дает ошибку."""
        out, flag = handle("ls /nope")
        self.assertIn("no such file", out)
        self.assertFalse(flag)

    def test_cd_pwd(self):
        """Cd меняет папку, pwd показывает."""
        out, flag = handle("cd /home/user")
        self.assertEqual(out, "")
        self.assertFalse(flag)
        out, flag = handle("pwd")
        self.assertEqual(out, "/home/user")

    def test_cd_relative(self):
        """Cd понимает относительный путь."""
        src.main.cur_dir = "/home"
        out, flag = handle("cd user")
        self.assertEqual(out, "")
        self.assertEqual(src.main.cur_dir, "/home/user")

    def test_cd_dotdot(self):
        """Cd .. идет наверх."""
        src.main.cur_dir = "/home/user"
        out, flag = handle("cd ..")
        self.assertEqual(out, "")
        self.assertEqual(src.main.cur_dir, "/home")

    def test_cd_errors(self):
        """Cd в файл и в никуда дает ошибку."""
        out, flag = handle("cd /a.txt")
        self.assertIn("not a directory", out)
        self.assertFalse(flag)
        out, flag = handle("cd /nope")
        self.assertIn("no such file", out)
        self.assertEqual(src.main.cur_dir, "/")

    def test_tree(self):
        """Tree показывает дерево."""
        out, flag = handle("tree /home")
        self.assertIn("user/", out)
        self.assertIn("f.txt", out)
        self.assertFalse(flag)

    def test_pwd_args(self):
        """Pwd с аргументами дает ошибку."""
        out, flag = handle("pwd x")
        self.assertIn("too many", out)
        self.assertFalse(flag)


def make_root5():
    """Собрать VFS для тестов этапа 5."""
    return {"type": "dir", "name": "/", "children": [
        {"type": "file", "name": "a.txt", "content": "A"},
        {"type": "dir", "name": "empty", "children": []},
        {"type": "dir", "name": "full", "children": [
            {"type": "file", "name": "x.txt",
             "content": "X"}]}]}


class TestStage5(unittest.TestCase):
    """Проверка rmdir и cp."""

    def setUp(self):
        """Готовить VFS перед тестом."""
        src.main.vfs_root = make_root5()
        src.main.cur_dir = "/"
        src.main.prompt = src.main.make_prompt()

    def test_rmdir_ok(self):
        """Пустая папка удаляется."""
        out, flag = handle("rmdir empty")
        self.assertEqual(out, "")
        self.assertFalse(flag)
        self.assertEqual(src.main.find_node(
            src.main.vfs_root, "/empty"), None)

    def test_rmdir_full(self):
        """Непустая папка не удаляется."""
        out, flag = handle("rmdir full")
        self.assertIn("not empty", out)
        self.assertFalse(flag)

    def test_rmdir_file(self):
        """Файл удалить как папку нельзя."""
        out, flag = handle("rmdir a.txt")
        self.assertIn("not a directory", out)
        self.assertFalse(flag)

    def test_rmdir_args(self):
        """Rmdir без аргументов и в никуда ошибка."""
        out, flag = handle("rmdir")
        self.assertIn("missing operand", out)
        self.assertFalse(flag)
        out, flag = handle("rmdir /nope")
        self.assertIn("no such file", out)
        self.assertEqual(src.main.cur_dir, "/")

    def test_cp_ok(self):
        """Файл копируется под новым именем."""
        out, flag = handle("cp a.txt b.txt")
        self.assertEqual(out, "")
        self.assertFalse(flag)
        node = src.main.find_node(src.main.vfs_root, "/b.txt")
        self.assertNotEqual(node, None)
        self.assertEqual(node["content"], "A")

    def test_cp_into_dir(self):
        """Файл копируется внутрь папки."""
        out, flag = handle("cp a.txt empty")
        self.assertEqual(out, "")
        node = src.main.find_node(
            src.main.vfs_root, "/empty/a.txt")
        self.assertNotEqual(node, None)

    def test_cp_overwrite(self):
        """Файл перезаписывается копией."""
        handle("cp a.txt b.txt")
        out, flag = handle("cp full/x.txt b.txt")
        self.assertEqual(out, "")
        node = src.main.find_node(src.main.vfs_root, "/b.txt")
        self.assertEqual(node["content"], "X")

    def test_cp_missing_src(self):
        """Нет исходника дает ошибку."""
        out, flag = handle("cp /nope /b.txt")
        self.assertIn("cannot stat", out)
        self.assertFalse(flag)

    def test_cp_dir_src(self):
        """Папку копировать нельзя."""
        out, flag = handle("cp full /b.txt")
        self.assertIn("cannot copy directory", out)
        self.assertFalse(flag)

    def test_cp_args(self):
        """Cp без аргументов и с лишними ошибка."""
        out, flag = handle("cp a.txt")
        self.assertIn("missing operand", out)
        self.assertFalse(flag)
        out, flag = handle("cp a b c")
        self.assertIn("too many", out)

    def test_cp_same(self):
        """Копия в себя дает ошибку."""
        out, flag = handle("cp a.txt a.txt")
        self.assertIn("same file", out)
        self.assertFalse(flag)


if __name__ == "__main__":
    unittest.main()
