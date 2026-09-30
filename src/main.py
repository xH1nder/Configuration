"""Эмулятор оболочки. Этап 3."""

import base64
import datetime
import getpass
import json
import socket
import sys
import tkinter as tk

max_cd = 1
max_exit = 0
max_ls = 1
max_tree = 1
max_pwd = 0
empty_count = 0
one = 1
my_user = "user"
my_host = "host"

window = None
text = None
entry = None
prompt = ""
log_path = ""
vfs_path = ""
vfs_root = None
cur_dir = "/"
log_events = []


def get_user():
    """Узнать имя пользователя."""
    try:
        return getpass.getuser()
    except Exception:
        return "user"


def get_host():
    """Узнать имя компьютера."""
    try:
        return socket.gethostname()
    except Exception:
        return "host"


def get_time():
    """Узнать текущее время строкой."""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def empty_root():
    """Пустая VFS если файл не задан."""
    return {"type": "dir", "name": "/", "children": []}


def parse(s):
    """Разобрать строку на команду и аргументы."""
    parts = s.strip().split()
    if parts == []:
        return "", []
    return parts[0], parts[1:]


def parse_args(argv):
    """Разобрать параметры --vfs --log --script."""
    vfs = ""
    log = ""
    script = ""
    wait = ""
    for part in argv:
        if wait == "vfs":
            vfs = part
            wait = ""
        elif wait == "log":
            log = part
            wait = ""
        elif wait == "script":
            script = part
            wait = ""
        elif part == "--vfs":
            wait = "vfs"
        elif part == "--log":
            wait = "log"
        elif part == "--script":
            wait = "script"
    return {"vfs": vfs, "log": log, "script": script}


def check_file(node):
    """Проверить файл VFS."""
    enc = node.get("encoding", "")
    content = node.get("content", "")
    if enc == "base64" and content != "":
        try:
            base64.b64decode(content, validate=True)
        except Exception:
            return "bad base64"
    return ""


def check_dir(node):
    """Проверить папку VFS."""
    kids = node.get("children", [])
    if not isinstance(kids, list):
        return "bad children"
    for kid in kids:
        bad = check_node(kid)
        if bad != "":
            return bad
    return ""


def check_node(node):
    """Проверить один узел VFS."""
    if not isinstance(node, dict):
        return "node must be object"
    kind = node.get("type", "")
    name = node.get("name", "")
    if kind != "dir" and kind != "file":
        return "bad type"
    if name == "":
        return "bad name"
    if kind == "file":
        return check_file(node)
    return check_dir(node)


def load_vfs(path):
    """Загрузить VFS из JSON только в память."""
    try:
        f = open(path, "r", encoding="utf-8")
        data = f.read()
        f.close()
    except Exception:
        return None, "error: vfs file not found: " + path
    try:
        root = json.loads(data)
    except Exception:
        return None, "error: vfs bad format: bad json"
    bad = check_node(root)
    if bad != "":
        return None, "error: vfs bad format: " + bad
    return root, ""


def count_vfs(node):
    """Посчитать папки и файлы в VFS."""
    kind = node.get("type", "")
    if kind == "file":
        return (empty_count, one)
    total_dirs = one
    total_files = empty_count
    for kid in node.get("children", []):
        sub_dirs, sub_files = count_vfs(kid)
        total_dirs = total_dirs + sub_dirs
        total_files = total_files + sub_files
    return (total_dirs, total_files)


def find_node(root, path):
    """Найти узел по пути."""
    if path in ["", "/"]:
        return root
    parts = [p for p in path.split("/") if p != ""]
    node = root
    for part in parts:
        if node.get("type", "") != "dir":
            return None
        found = None
        for kid in node.get("children", []):
            if kid.get("name", "") == part:
                found = kid
        if found is None:
            return None
        node = found
    return node


def get_root():
    """Взять корень VFS."""
    if vfs_root is None:
        return empty_root()
    return vfs_root


def join_path(cur, arg):
    """Склеить путь с текущей папкой."""
    if arg.startswith("/"):
        full = arg
    else:
        if cur == "/":
            full = "/" + arg
        else:
            full = cur + "/" + arg
    parts = []
    for p in full.split("/"):
        if p in ["", "."]:
            continue
        if p == "..":
            if parts != []:
                parts = parts[:len(parts) - one]
        else:
            parts.append(p)
    if parts == []:
        return "/"
    return "/" + "/".join(parts)


def make_prompt():
    """Собрать приглашение с текущей папкой."""
    return my_user + "@" + my_host + ":" + cur_dir + "$ "


def run_ls(args):
    """Настоящий ls по папкам VFS."""
    if len(args) > max_ls:
        return "ls: too many arguments"
    if args == []:
        path = cur_dir
    else:
        path = join_path(cur_dir, args[0])
    node = find_node(get_root(), path)
    if node is None:
        return "ls: no such file or directory: " + path
    if node.get("type", "") == "file":
        return node.get("name", "")
    names = []
    for kid in node.get("children", []):
        name = kid.get("name", "")
        if kid.get("type", "") == "dir":
            names.append(name + "/")
        else:
            names.append(name)
    if names == []:
        return "empty"
    return " ".join(names)


def run_cd(args):
    """Настоящий cd по папкам VFS."""
    global cur_dir, prompt
    if len(args) > max_cd:
        return "cd: too many arguments"
    if args == []:
        path = "/"
    else:
        path = join_path(cur_dir, args[0])
    node = find_node(get_root(), path)
    if node is None:
        return "cd: no such file or directory: " + path
    if node.get("type", "") != "dir":
        return "cd: not a directory: " + path
    cur_dir = path
    prompt = make_prompt()
    return ""


def run_pwd(args):
    """Показать текущую папку."""
    if args != []:
        return "pwd: too many arguments"
    return cur_dir


def tree_lines(node, prefix):
    """Строки дерева для узла."""
    lines = []
    for kid in node.get("children", []):
        name = kid.get("name", "")
        if kid.get("type", "") == "dir":
            lines.append(prefix + name + "/")
            lines = lines + tree_lines(kid, prefix + "  ")
        else:
            lines.append(prefix + name)
    return lines


def run_tree(args):
    """Показать дерево папок."""
    if len(args) > max_tree:
        return "tree: too many arguments"
    if args == []:
        path = cur_dir
    else:
        path = join_path(cur_dir, args[0])
    node = find_node(get_root(), path)
    if node is None:
        return "tree: no such file or directory: " + path
    if node.get("type", "") == "file":
        return node.get("name", "")
    lines = [path] + tree_lines(node, "  ")
    return "\n".join(lines)


def handle(s):
    """Выполнить команду."""
    cmd, args = parse(s)
    if cmd == "":
        return "", False
    if cmd == "ls":
        return run_ls(args), False
    if cmd == "cd":
        return run_cd(args), False
    if cmd == "pwd":
        return run_pwd(args), False
    if cmd == "tree":
        return run_tree(args), False
    if cmd == "exit":
        if len(args) > max_exit:
            return "exit: too many arguments", False
        return "exit", True
    return "error: unknown command '" + cmd + "'", False


def is_error(out):
    """Понять что вывод это ошибка."""
    if out == "":
        return False
    if "unknown command" in out:
        return True
    if "too many arguments" in out:
        return True
    if "no such file" in out:
        return True
    if "not a directory" in out:
        return True
    if out.startswith("error"):
        return True
    return False


def run_lines(lines):
    """Прогнать список команд до первой ошибки."""
    result = []
    for raw in lines:
        s = raw.strip()
        if s == "":
            continue
        out, need_exit = handle(s)
        result.append((s, out, need_exit))
        if is_error(out):
            break
        if need_exit:
            break
    return result


def escape_xml(s):
    """Убрать знаки чтобы не ломать XML."""
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s


def save_log(path, events):
    """Записать лог в XML файл."""
    f = open(path, "w", encoding="utf-8")
    f.write('<?xml version="1.0" encoding="utf-8"?>\n')
    f.write("<log>\n")
    for user, moment, cmd, out in events:
        f.write("  <event>\n")
        f.write("    <user>" + escape_xml(user) + "</user>\n")
        f.write("    <time>" + escape_xml(moment) + "</time>\n")
        f.write("    <command>" + escape_xml(cmd) + "</command>\n")
        f.write("    <output>" + escape_xml(out) + "</output>\n")
        f.write("  </event>\n")
    f.write("</log>\n")
    f.close()


def add_log(cmd, out):
    """Добавить событие в лог файл."""
    if log_path == "":
        return
    user = get_user()
    moment = get_time()
    log_events.append((user, moment, cmd, out))
    save_log(log_path, log_events)


def show(msg):
    """Показать строку в окне."""
    text.config(state=tk.NORMAL)
    text.insert(tk.END, msg + "\n")
    text.config(state=tk.DISABLED)
    text.see(tk.END)


def do_one(s):
    """Выполнить одну строку и показать."""
    show(prompt + s)
    out, need_exit = handle(s)
    if out != "":
        show(out)
    add_log(s, out)
    return out, need_exit


def on_press(event):
    """Обработка Enter."""
    s = entry.get()
    entry.delete(0, tk.END)
    out, need_exit = do_one(s)
    if is_error(out):
        show("error: stop, fix command")
    if need_exit:
        window.destroy()


def run_script_file(path):
    """Выполнить стартовый скрипт."""
    try:
        f = open(path, "r", encoding="utf-8")
        lines = f.readlines()
        f.close()
    except Exception:
        show("error: script file not found: " + path)
        return True
    done = run_lines(lines)
    for s, out, need_exit in done:
        show(prompt + s)
        if out != "":
            show(out)
        add_log(s, out)
        if is_error(out):
            show("error: script stopped on error")
            return True
        if need_exit:
            window.destroy()
            return True
    rest = [x for x in lines if x.strip() != ""]
    if len(done) < len(rest):
        show("error: script stopped on error")
    return False


def setup_window():
    """Создать окно эмулятора."""
    global window, text, entry
    window = tk.Tk()
    window.title("Эмулятор - [" + my_user + "@" + my_host + "]")
    text = tk.Text(window, state=tk.DISABLED)
    text.pack(fill=tk.BOTH, expand=True)
    entry = tk.Entry(window)
    entry.pack(fill=tk.X)
    entry.bind("<Return>", on_press)
    show(prompt + "ready, type ls, cd, pwd, tree or exit")
    show("VFS=" + vfs_path + " LOG=" + log_path)


def load_vfs_show():
    """Загрузить VFS и показать результат."""
    global vfs_root
    if vfs_path == "":
        vfs_root = empty_root()
        show("VFS empty, run with --vfs file.json")
        return
    root, err = load_vfs(vfs_path)
    if err != "":
        show(err)
        print(err)
        add_log("vfs " + vfs_path, err)
        vfs_root = empty_root()
        return
    vfs_root = root
    found_dirs, found_files = count_vfs(vfs_root)
    msg = "VFS loaded: " + str(found_dirs)
    msg = msg + " dirs, " + str(found_files)
    msg = msg + " files from " + vfs_path
    show(msg)
    print(msg)
    add_log("vfs " + vfs_path, msg)


def run_start_script(script_path):
    """Выполнить стартовый скрипт."""
    if script_path == "":
        return
    show(prompt + "run script: " + script_path)
    bad = run_script_file(script_path)
    if bad:
        show("script finished with error")
    else:
        show("script finished ok")


def main():
    """Запустить окно."""
    global window, text, entry, prompt
    global log_path, vfs_path, log_events
    global vfs_root, cur_dir, my_user, my_host
    args = parse_args(sys.argv[1:])
    vfs_path = args["vfs"]
    log_path = args["log"]
    script_path = args["script"]
    print("VFS: " + vfs_path)
    print("Log: " + log_path)
    print("Script: " + script_path)
    log_events = []
    my_user = get_user()
    my_host = get_host()
    cur_dir = "/"
    prompt = make_prompt()
    setup_window()
    load_vfs_show()
    run_start_script(script_path)
    entry.focus_set()
    window.mainloop()


if __name__ == "__main__":
    main()
