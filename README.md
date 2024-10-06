# Django Project Setup


## Установка

1. Создайте виртуальное окружение и активируйте его:

    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

2. Установите необходимые зависимости:

    ```bash
    pip install -r requirements.txt
    ```

## Настройка проекта

1. Переименуйте файл `.env.dev.example` в `.env` и настройте переменные окружения. Пример файла:

    ```bash
    SECRET_KEY=django-insecure-jsp7vi%&d33*g^po98m^y6_w54_dczhbpy
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=Get from Google Console      (Authorized redirect URIs for google authentification http://localhost:8000/accounts/complete/google-oauth2/)
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=Get from Google Console   (Authorized redirect URIs for google authentification http://localhost:8000/accounts/complete/google-oauth2/)
    ```

2. Примените миграции для базы данных:

    ```bash
    python manage.py migrate
    ```


## Запуск проекта

Чтобы запустить проект на локальном сервере, выполните команду:

1.
```bash
docker run --name redis -d -p 6379:6379 redis
```

2.

```bash
python manage.py runserver
```

3.

```bash
celery -A freenglish.celery_app worker --loglevel=info --pool=solo
```

4.

```bash
daphne -b 0.0.0.0 -p 8001 asgi:application
```

