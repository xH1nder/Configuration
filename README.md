# Практическая работа, Вариант №19, Этапы 1-4

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

Файлы VFS для проверки:

- vfs_min.json - минимум, один файл,
- vfs_small.json - несколько файлов и папка,
- vfs_deep.json - 3 уровня и base64,
- vfs_bad.json - неверный формат для ошибки.

## Этап 4. Основные команды

Что добавлено:

1. Настоящие ls и cd по папкам VFS в памяти:
   ls показывает файлы и папки, папки с /,
   cd меняет текущую папку, понимает .. и .
   и относительные пути.
2. Новая команда pwd - показывает текущую папку.
3. Новая команда tree - показывает дерево папок.
4. Приглашение теперь показывает папку:
   user@host:/home/user$ вместо user@host:~$.
5. Ошибки как в UNIX: no such file or directory,
   not a directory, too many arguments.
   Все изменения только в памяти, файл VFS
   на диске не меняется.

Новые функции этапа 4:

- get_root берет корень VFS,
- join_path склеивает путь с текущей папкой,
- make_prompt собирает приглашение с папкой,
- run_ls настоящий листинг папки,
- run_cd меняет cur_dir,
- run_pwd возвращает cur_dir,
- tree_lines и run_tree рисуют дерево.

Примеры этапа 4 на vfs_deep.json:

```
user@host:/$ pwd
/
user@host:/$ ls
readme.txt home/
user@host:/$ ls /home/user/docs
report.txt data.txt
user@host:/$ ls /readme.txt
readme.txt
user@host:/$ cd /home/user
user@host:/home/user$ pwd
/home/user
user@host:/home/user$ ls
docs/ photo.bin
user@host:/home/user$ tree /home
/home
  user/
    docs/
      report.txt
      data.txt
    photo.bin
user@host:/home/user$ cd ..
user@host:/home$ pwd
/home
user@host:/home$ ls /nope
ls: no such file or directory: /nope
user@host:/home$ cd /readme.txt
cd: not a directory: /readme.txt
```

## Что где лежит

- src/main.py - весь код этапов 1-4.
- tests/test_main.py - 24 теста.
- start_good.txt, start_bad.txt - скрипты этапа 2.
- start_vfs.txt - скрипт этапа 3.
- start_stage4.txt - скрипт этапа 4 со всеми
  командами ls, cd, pwd, tree и ошибкой в конце.
- test_log.bat, test_script.bat, test_all.bat -
  проверка параметров.
- test_vfs.bat - проверка всех вариантов VFS.
- test_stage4.bat - проверка команд этапа 4.
- vfs_min.json, vfs_small.json, vfs_deep.json,
  vfs_bad.json - варианты VFS.

## Как запустить

Просто окно:

```bat
run.bat
```

С VFS и скриптом этапа 4:

```bat
run.bat --vfs vfs_deep.json --log log.xml --script start_stage4.txt
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
test_stage4.bat
```

## Пример лога log.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<log>
  <event>
    <user>nikita</user>
    <time>2026-09-28 10:00:00</time>
    <command>ls</command>
    <output>readme.txt home/</output>
  </event>
</log>
```

Этапы 1-4 выполнены.
