FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Установка Python и системных зависимостей
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Создание временных директорий и директории для моделей
RUN mkdir -p /tmp/uploads /tmp/results /app/models

# Копирование и установка requirements.txt
COPY --chmod=0644 requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Копирование исходного кода с правильными правами
COPY --chmod=0755 ./app /app/app/
COPY --chmod=0755 ./tests /app/tests/

# Создание необходимых директорий для приложения
RUN mkdir -p app/templates \
    app/static/css \
    app/static/js \
    app/static/images

# Проверка наличия необходимых директорий
RUN test -d app/templates && \
    test -d app/static/css && \
    test -d app/static/js && \
    test -d app/static/images

EXPOSE 5000

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.main
ENV FLASK_ENV=development

CMD ["python3", "-m", "app.main"] 