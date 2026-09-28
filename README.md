# Практическая работа, Вариант №19, Этапы 1-2

Эмулятор командной строки UNIX.
Сделан на Python + tkinter.

Сопталев Никита Дмитривевич, ИКБО-32-25

## Этап 1. REPL-прототип

Что надо было: окно GUI, парсер по пробелам,
заглушки ls и cd, команда exit.

Что сделано:

1. Сделал окно GUI. Заголовок берется из ОС:
   Эмулятор - [username@hostname].
2. Написал функцию parse - делит ввод по пробелам
   на команду и аргументы.
3. Сделал заглушки ls и cd - просто выводят свое
   имя и аргументы.
4. Сделал команду exit - закрывает окно.
5. Добавил ошибки: неизвестная команда и
   неверные аргументы.

Функции этапа 1:

- get_user и get_host берут данные ОС,
- parse разбирает ввод,
- run_ls и run_cd заглушки,
- handle выполняет команду,
- main открывает окно.

Примеры этапа 1:

```
user@host:~$ ls
ls
user@host:~$ ls /tmp home
ls: /tmp home
user@host:~$ cd /tmp
cd: /tmp
user@host:~$ cd a b
cd: too many arguments
user@host:~$ foo
error: unknown command 'foo'
user@host:~$ exit
exit
```

## Этап 2. Конфигурация

Что добавлено:

1. Параметры запуска:
   --vfs путь к VFS, --log путь к логу,
   --script путь к стартовому скрипту.
   При запуске все параметры печатаются
   в консоль для отладки.
2. Лог в XML: каждый вызов команды пишется
   в файл с именем пользователя и временем.
3. Стартовый скрипт: файл с командами
   выполняется при запуске, на экране видно
   и ввод и вывод. Останавливается на первой
   ошибке и пишет что скрипт остановлен.
4. VFS пока не используется, только печатается,
   сама VFS будет на этапе 3.

Новые функции этапа 2:

- parse_args разбирает параметры,
- get_time дает время для лога,
- is_error проверяет ошибка ли вывод,
- run_lines гоняет скрипт до ошибки,
- save_log и add_log пишут XML,
- run_script_file читает файл скрипта.

## Что где лежит

- src/main.py - весь код этапов 1 и 2.
- tests/test_main.py - 10 тестов.
- start_good.txt - хороший скрипт без ошибок.
- start_bad.txt - скрипт с ошибкой посередине.
- test_log.bat, test_script.bat, test_all.bat -
  скрипты Windows для проверки параметров.

## Как запустить

Просто окно:

```bat
run.bat
```

С логом:

```bat
run.bat --log log.xml
```

Со скриптом:

```bat
run.bat --script start_good.txt
```

Все вместе:

```bat
run.bat --vfs vfs.json --log log.xml --script start_good.txt
```

Тесты:

```
python -m unittest discover -s tests -v
```

Проверка скриптами Windows:

```
test_log.bat
test_script.bat
test_all.bat
```

## Пример лога log.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<log>
  <event>
    <user>nikita</user>
    <time>2026-09-28 10:00:00</time>
    <command>ls /tmp</command>
    <output>ls: /tmp</output>
  </event>
</log>
```

## Примеры этапа 2

Хороший скрипт выполняется весь:

```
user@host:~$ run script: start_good.txt
user@host:~$ ls
ls
user@host:~$ cd /tmp
cd: /tmp
script finished ok
```

Плохой останавливается:

```
user@host:~$ run script: start_bad.txt
user@host:~$ ls
ls
user@host:~$ foo_bad_command
error: unknown command 'foo_bad_command'
error: script stopped on error
```

Этапы 1 и 2 выполнены.
