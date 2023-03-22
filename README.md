### Учебный проект

# Проект Yatube
**Yatube** - социальная сеть для публикации личных дневников. Сайт на котором можно создать свою страницу, если на нее зайти, то можно посмотреть все записи автора.
Пользователи могут заходить на чужие страницы, подписываться на авторов и комментировать их записи. Автор может выбрать имя и уникальный адрес для своей страницы.
Записи можно отправить в сообщество и посмотреть там записи разных авторов.

## Установка
### Как запустить проект:

1. Клонировать репозитрий и перейти в него в командной строке:

```
    $git clone 
    $cd api_final_yatube
```

2. Создать и активировать виртуалье окружение:

```
    $python -m venv venv
    $. venv/Scripts/activate
```

3. Установить зависимости из файла requirements.txt.

```
    $python -m pip install --upgrade pip
    $pip install -r requirements.txt
```

4. Выполнить миграции:

```
    $python manage.py makemigrations
    $python manage.py migrate
```

5. Запустить проект:

```$python manage.py runserver```

## Технологии

<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" /><img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green"/><img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" /><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" />


## Разработчик
| [<img src="https://github.com/saturnovikov.png?size=115" width="115"><br><sub>@saturnovikov</sub>](https://github.com/saturnovikov) |
| :---------------------------------------------------------------------------------------------------------------------: |
**Новиков Антон**: студент Yandex-practicum, курс Python разработчик.

