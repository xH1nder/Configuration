# Практическая работа, Вариант №19, Этапы 1-3

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

Примеры этапа 1:

```
user@host:~$ ls /tmp home
ls: /tmp home
user@host:~$ cd a b
cd: too many arguments
user@host:~$ foo
error: unknown command 'foo'
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
   ошибке.

## Этап 3. VFS

Что добавлено:

1. VFS грузится из JSON файла только в память,
   файл на диске никак не меняется.
   Папки это type dir с children,
   файлы это type file с content,
   бинарные файлы лежат в base64.
2. При загрузке пишется сколько папок и файлов
   нашлось, например VFS loaded: 4 dirs, 3 files.
3. Ошибки загрузки показываются в окне и в консоли:
   файл не найден, битый json, неверный формат.
4. Настоящие команды ls и cd по папкам VFS
   будут на этапе 4, пока заглушки как раньше.

Новые функции этапа 3:

- empty_root дает пустую VFS без файла,
- check_node проверяет один узел,
- load_vfs грузит JSON только в память,
- count_vfs считает папки и файлы,
- find_node ищет узел по пути.

Пример VFS (vfs_deep.json, 3 уровня и base64):

```json
{"type": "dir", "name": "/",
 "children": [
  {"type": "dir", "name": "home",
   "children": [
    {"type": "dir", "name": "user",
     "children": [
      {"type": "dir", "name": "docs",
       "children": [
        {"type": "file", "name": "report.txt",
         "content": "Report in deep folder"}]},
      {"type": "file", "name": "photo.bin",
       "encoding": "base64",
       "content": "aGVsbG8gd29ybGQ="}]}]}]}
```

Файлы VFS для проверки:

- vfs_min.json - минимум, один файл,
- vfs_small.json - несколько файлов и папка,
- vfs_deep.json - 3 уровня и base64,
- vfs_bad.json - неверный формат для ошибки.

## Что где лежит

- src/main.py - весь код этапов 1-3.
- tests/test_main.py - 15 тестов.
- start_good.txt, start_bad.txt - скрипты этапа 2.
- start_vfs.txt - скрипт этапа 3 со всеми
  командами и ошибкой в конце.
- test_log.bat, test_script.bat, test_all.bat -
  проверка параметров.
- test_vfs.bat - проверка всех вариантов VFS:
  минимальный, несколько файлов, 3 уровня,
  битый файл и отсутствующий файл.
- vfs_min.json, vfs_small.json, vfs_deep.json,
  vfs_bad.json - варианты VFS.

## Как запустить

Просто окно:

```bat
run.bat
```

С VFS и скриптом:

```bat
run.bat --vfs vfs_deep.json --log log.xml --script start_vfs.txt
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
test_vfs.bat
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

## Примеры этапа 3

Хорошая VFS грузится и показывает счет:

```
VFS loaded: 4 dirs, 3 files from vfs_deep.json
user@host:~$ run script: start_vfs.txt
user@host:~$ ls /home
ls: /home
script finished with error
```

Битая VFS дает ошибку:

```
error: vfs bad format: bad type
```

Нет файла тоже ошибка:

```
error: vfs file not found: no_such.json
```

Этапы 1-3 выполнены.
