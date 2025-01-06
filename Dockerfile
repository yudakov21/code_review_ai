FROM python:3.11.3

RUN mkdir /review_app

WORKDIR /review_app

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файлы проекта
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN poetry install --only main --no-interaction --no-ansi --no-root


# Копируем остальной код проекта
COPY . .

# Запускаем приложение
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8006"]
