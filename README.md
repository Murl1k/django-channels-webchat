# Webchat

### Представление
***

Webchat - проект, написанный на Django 4.1.6. Webchat представляет собой простой приватный мессенджер в режиме реального времени, написанный при помощи django-channels.

![Project preview](https://user-images.githubusercontent.com/109019309/223375795-026ed711-8121-42b2-8343-051ef9335afd.gif)


### Функционал
***

- Авторизация, регистрация пользователя
- Общение в приватном чате с другим пользователем в режиме реального времени
- Сохранение истории чата и автоматическая загрузка прошлых сообщений
- Поиск собеседника среди всех пользователей
- Автоматическое создание чата без участия админки
- Кастомизация профиля: загрузка аватара, установка пользовательского статуса
- Тестирование для представлений и моделей
- Админка

### Стек
***

##### Frontend:
HTML, CSS, JS(WebSocket, Ajax)

#### Backend:

- Python 3.10
- Django 4.1.6
- Django-channels(daphne) 4.0.0

### Установка.
---
1. Создать виртуальное окружение и установить требуемые пакеты командой:
> pip install -r requirements.txt

2. Сделать django миграции:
> python manage.py migrate

3. Запустить сервер.
> python manage.py runserver

