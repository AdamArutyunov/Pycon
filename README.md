## Pycon

Как известно, олимпиадные программисты сдают свои решения в тестирующие системы. А промышленные программисты эти системы пишут.

Pycon — платформа для проведения олимпиад по спортивному программированию на языке Python.

Здесь есть задачи и контесты. Задачи можно решать, в контестах можно принимать участие, соревнуясь с другими программистами. Создана с нуля тестирующая система. 

Вся архитектура сделана с помощью SQLAlchemy ORM и Flask. SolutionChecker вынесен в отдельный модуль.

Финальный проект Яндекс.Лицея 2020. Уже тестируется на реальных студентах.

## Установка
Запустите `cmd` или Terminal и перейдите к папке с проектом:
`cd <path>`

Установите все необходимые библиотеки:
`pip install -r requirements.txt` или `pip3 install -r requirements.txt` (в зависимости от команды установщика пакетов для Python 3 в PATH)

Настройте файл `Constants.py`. Настройки:
`DATABASE_URI` — относительный путь к файлу базы данных. Можно оставить без изменения.
`APP_ROOT` — абсолютный путь к папке с проектом.
`APP_PORT` — порт для запуска приложения.
`PYTHON_COMMAND` — путь к интерпретатору Python (>= 3.6). Допускается краткая команда, если она прописана в PATH. 

 и выполните:
`python Pycon.py` или `python3 Pycon.py` (в зависимости от команды для запуска Python 3 в PATH)

При возникновении проблем, связанных с правами досупа, выполняйте команды через `sudo` или консоли от имени администратора в Windows.

В папке `docs` есть представление проекта, где описаны архитектурные подробности и преимущества и скриншоты всего на случай, если что-то пойдёт не так.
