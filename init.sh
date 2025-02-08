#!/bin/bash

# Создание директорий для данных
mkdir -p tmp/uploads tmp/results models

# Установка прав
chmod -R 777 tmp models

# Сборка и запуск контейнеров
docker-compose up --build 