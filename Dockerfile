# Используем официальный образ Python
FROM python:3.12

# Устанавливаем PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client

# Устанавливаем рабочую директорию
WORKDIR /Work

# Копируем файлы проекта в контейнер
COPY . /Work

# Устанавливаем pipenv
RUN pip install pipenv

# Устанавливаем зависимости
RUN pipenv install

# Команда для запуска Django
CMD ["pipenv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
