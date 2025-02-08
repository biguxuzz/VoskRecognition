FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg wget unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Создание временных директорий и директории для моделей
RUN mkdir -p /tmp/uploads /tmp/results /app/models

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"] 