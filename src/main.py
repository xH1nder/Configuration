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
empty_count = 0
one = 1

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
        elif part.startswith("--vfs="):
            vfs = part[len("--vfs="):]
        elif part.startswith("--log="):
            log = part[len("--log="):]
        elif part.startswith("--script="):
            script = part[len("--script="):]
    return {"vfs": vfs, "log": log, "script": script}


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
        enc = node.get("encoding", "")
        content = node.get("content", "")
        if enc == "base64" and content != "":
            try:
                base64.b64decode(content, validate=True)
            except Exception:
                return "bad base64"
        return ""
    kids = node.get("children", [])
    if not isinstance(kids, list):
        return "bad children"
    for kid in kids:
        bad = check_node(kid)
        if bad != "":
            return bad
    return ""


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
    if path == "" or path == "/":
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


def run_ls(args):
    """Заглушка ls."""
    if args == []:
        return "ls"
    return "ls: " + " ".join(args)


def run_cd(args):
    """Заглушка cd."""
    if len(args) > max_cd:
        return "cd: too many arguments"
    if args == []:
        return "cd"
    return "cd: " + " ".join(args)


def handle(s):
    """Выполнить команду."""
    cmd, args = parse(s)
    if cmd == "":
        return "", False
    if cmd == "ls":
        return run_ls(args), False
    if cmd == "cd":
        return run_cd(args), False
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


def main():
    """Запустить окно."""
    global window, text, entry, prompt
    global log_path, vfs_path, log_events
    global vfs_root, cur_dir
    args = parse_args(sys.argv[1:])
    vfs_path = args["vfs"]
    log_path = args["log"]
    script_path = args["script"]
    print("VFS: " + vfs_path)
    print("Log: " + log_path)
    print("Script: " + script_path)
    log_events = []
    user = get_user()
    host = get_host()
    prompt = user + "@" + host + ":~$ "
    window = tk.Tk()
    window.title("Эмулятор - [" + user + "@" + host + "]")
    text = tk.Text(window, state=tk.DISABLED)
    text.pack(fill=tk.BOTH, expand=True)
    entry = tk.Entry(window)
    entry.pack(fill=tk.X)
    entry.bind("<Return>", on_press)
    show(prompt + "ready, type ls, cd or exit")
    show("VFS=" + vfs_path + " LOG=" + log_path)
    if vfs_path == "":
        vfs_root = empty_root()
        show("VFS empty, run with --vfs file.json")
    else:
        root, err = load_vfs(vfs_path)
        if err != "":
            show(err)
            print(err)
            add_log("vfs " + vfs_path, err)
            vfs_root = empty_root()
        else:
            vfs_root = root
            found_dirs, found_files = count_vfs(vfs_root)
            msg = "VFS loaded: " + str(found_dirs)
            msg = msg + " dirs, " + str(found_files)
            msg = msg + " files from " + vfs_path
            show(msg)
            print(msg)
            add_log("vfs " + vfs_path, msg)
    cur_dir = "/"
    if script_path != "":
        show(prompt + "run script: " + script_path)
        bad = run_script_file(script_path)
        if bad:
            show("script finished with error")
        else:
            show("script finished ok")
    entry.focus_set()
    window.mainloop()


if __name__ == "__main__":
    main()
