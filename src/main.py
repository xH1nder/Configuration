"""Эмулятор оболочки. Этап 1."""

import getpass
import socket
import tkinter as tk

max_cd = 1
max_exit = 0

window = None
text = None
entry = None
prompt = ""


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


def parse(s):
    """Разобрать строку на команду и аргументы."""
    parts = s.strip().split()
    if parts == []:
        return "", []
    return parts[0], parts[1:]


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


def show(msg):
    """Показать строку в окне."""
    text.config(state=tk.NORMAL)
    text.insert(tk.END, msg + "\n")
    text.config(state=tk.DISABLED)
    text.see(tk.END)


def on_press(event):
    """Обработка Enter."""
    s = entry.get()
    entry.delete(0, tk.END)
    show(prompt + s)
    out, need_exit = handle(s)
    if out != "":
        show(out)
    if need_exit:
        window.destroy()


def main():
    """Запустить окно."""
    global window, text, entry, prompt
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
    entry.focus_set()
    window.mainloop()


if __name__ == "__main__":
    main()
