# Установка зависимостей
FROM python:3.10

# Установка pipenv
RUN pip install --upgrade pip
RUN pip install pipenv

# Копирование Pipfile и Pipfile.lock
WORKDIR /app
COPY Pipfile* /app/

# Установка зависимостей с помощью pipenv
RUN pipenv install

EXPOSE 8000

# Копирование приложения
COPY . /app

# Запуск приложения
CMD ["uvicorn", "src.main:app", "--host 0.0.0.0",  "--port 8000", "--reload"]
