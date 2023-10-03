#  Foodgram «Продуктовый помощник»

## Описание

«Продуктовый помощник» - это сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать и скачивать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек технологий

* Python 3.9,
* Django 3.2,
* Django REST Framework 3.14,
* PostgreSQL 13.0
* Gunicorn 20.1
* Nginx 1.22
* Docker

---

## Запуск проекта в dev-режиме

Клонируйте репозиторий и перейдите в него в командной строке:

```bash
git clone git@github.com:tsromych/foodgram-project-react.git
```
```bash
cd foodgram-project-react
```

Cоздайте виртуальное окружение:

```bash
# Для Windows
python -m venv venv

# Для MacOS, Linux
python3 -m venv env
```

Активируйте виртуальное окружение:

```bash
# Для Windows
source venv/Scripts/activate

# Для MacOS, Linux
source env/bin/activate
```

Перейдите в папку `backend` и установите зависимости:

```bash
# Для Windows
python -m pip install --upgrade pip

# Для MacOS, Linux
python3 -m pip install --upgrade pip

cd backend
```
```bash
pip install -r requirements.txt
```

В папке `backend` выполните миграции:

```bash
# Для Windows
python manage.py migrate

# Для MacOS, Linux
python3 manage.py migrate
```

Запустите проект:

```bash
# Для Windows
python manage.py runserver

# Для MacOS, Linux
python3 manage.py runserver
```

### Загрузка данных

В директории `/backend/data` подготовлен csv-файл с данными для заполнения таблицы ингридиентов. Для загрузки этих данных выполните в терминале management-команду:

```bash
# Для Windows
python manage.py import_ingredients_to_db

# Для MacOS, Linux
python3 manage.py import_ingredients_to_db
```

Так же для корректной работы приложения необходимо создать несколько тегов.

---

## Запуск проекта в Docker-контейнерах

Клонируйте репозиторий и перейдите в него в командной строке:

```bash
git clone git@github.com:tsromych/foodgram-project-react.git
```
```bash
cd foodgram-project-react
```

Перейдите в папку `infra`. Создайте файл .env и заполните его данными. Перечень данных указан в файле `.env.example`, выполните команду:

```bash
docker compose up
```

В папке с файлом `docker-compose.yml` выполните миграции командой:

```bash
docker compose exec backend python3 manage.py migrate
```

Выполните команду сборки статики:

```bash
docker compose exec backend python3 manage.py collectstatic
```

Копируйте собранные файлы в `/static/`

```bash
docker compose exec backend cp -r /app/collected_static/. /static/
```

Создайте суперпользователя:

```bash
docker compose exec backend python3 manage.py createsuperuser
```

### Загрузка данных

С проектом поставляются готовые данные ингредиентов. Заполнить базу ингредиентами можно выполнив команду:

```bash
docker compose exec backend python3 manage.py import_ingredients_to_db
```

Также необходимо заполнить базу данных тегами. Для этого требуется войти в админ-зону проекта под логином и паролем суперпользователя, созданного ранее.

---

## Автор

[Роман Цуленков](https://github.com/tsromych)

