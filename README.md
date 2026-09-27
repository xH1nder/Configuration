# Практическая работа, Вариант №19, Этап 1

Эмулятор командной строки UNIX.
Сделан на Python + tkinter.

Сопталев Никита Дмитривевич, ИКБО-32-25

## Что сделано

1. Сделал окно GUI. Заголовок берется из ОС:
   Эмулятор - [username@hostname].
2. Написал функцию parse - делит ввод по пробелам
   на команду и аргументы.
3. Сделал заглушки ls и cd - просто выводят свое
   имя и аргументы.
4. Сделал команду exit - закрывает окно.
5. Добавил ошибки: неизвестная команда и
   неверные аргументы.

## Что где лежит

- src/main.py - весь код этапа 1:
  get_user и get_host берут данные ОС,
  parse разбирает ввод,
  run_ls и run_cd заглушки,
  handle выполняет команду,
  main открывает окно.
- tests/test_main.py - 5 простых тестов.

## Как запустить

```bat
run.bat
```

Как проверить тесты:

```
python -m unittest discover -s tests -v
```

## Примеры

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

Этап 1 выполнен.
