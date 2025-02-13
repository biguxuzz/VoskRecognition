# Внутренний портал по распознаванию лекций и совещаний

## 1. Введение

Целью разработки является создание внутреннего портала для автоматического распознавания речи из аудио- и видеофайлов, конвертации их в текст и предоставления пользователю результата в виде текстового файла.

Данный проект будет распространяться под лицензией **GPL-3.0**. Это означает, что исходный код должен быть открыт, а производные работы также должны соблюдать условия данной лицензии.

## 2. Функциональные требования

### 2.1. Загрузка файлов

- Пользователь должен иметь возможность загружать файлы большого размера через веб-интерфейс.
- Поддерживаемые форматы файлов для загрузки: `.wav`, `.mp3`, `.mp4`.
- Загруженные файлы должны автоматически конвертироваться в формат `.wav`, если они изначально в формате `.mp3` или `.mp4`.

### 2.2. Начало процесса распознавания

- После загрузки файла пользователь должен видеть кнопку **"Начать распознавание"**.
- При нажатии на кнопку начинается процесс транскрибации.
- Пользователь должен видеть индикатор выполнения процесса в виде прогресс-бара с этапами:
  1. Конвертация (если необходимо)
  2. Разделение файла на фрагменты (если требуется)
  3. Распознавание речи
  4. Сборка результата

### 2.3. Вывод результата

- После завершения процесса распознавания пользователь должен иметь возможность скачать текстовый файл с результатом (`.txt`).
- Текстовый файл должен содержать транскрибированные данные, разбитые по абзацам.

## 3. Технические требования

### 3.1. Технологический стек

- **Язык программирования**: Python 3.9+
- **Фреймворк для веб-интерфейса**: Flask
- **Библиотеки для работы с аудио**:
  - `vosk` – для транскрибации
  - `soundfile` – для работы с аудиофайлами
  - `numpy` – для обработки данных
  - `ffmpeg` – для конвертации файлов в нужный формат

### 3.2. Обработка файлов

- Загруженные файлы должны сохраняться в временном хранилище (например, `/tmp/uploads/`).
- При загрузке `.mp3` и `.mp4` файлы должны конвертироваться в `.wav` с частотой дискретизации 16kHz, моно.
- Для конвертации необходимо использовать `ffmpeg`.

### 3.3. Запуск и развертывание

- Приложение должно быть упаковано в **Docker-контейнер**.
- Docker-контейнер должен содержать все необходимые зависимости.
- Должен быть подготовлен `Dockerfile` с инструкциями по сборке.

### 3.4. Используемая модель

- Для транскрибации необходимо использовать модель **vosk-model-ru-0.22.zip**.
- Модель должна загружаться при запуске сервиса и кэшироваться для повторного использования.

## 4. Требования к интерфейсу

- Веб-интерфейс должен быть минималистичным и удобным.
- Основные элементы интерфейса:
  - Поле для загрузки файла
  - Кнопка "Начать распознавание"
  - Прогресс-бар выполнения
  - Кнопка "Скачать результат"
- Все процессы должны сопровождаться пользователю понятными статусами (например, "Файл обрабатывается", "Идет распознавание", "Готово").

## 5. Автоматическое тестирование

- Разработка должна содержать **автоматические тесты**.
- Тесты должны покрывать:
  - Загрузку файла
  - Конвертацию аудио
  - Запуск процесса распознавания
  - Корректность полученного текста
  - Отображение результатов в интерфейсе
- Используемые инструменты тестирования:
  - `pytest` – для unit-тестов
  - `selenium` (или `pytest-flask`) – для тестирования интерфейса

## 6. Деплой и эксплуатация

- Портал должен работать внутри корпоративной сети.
- Должна быть предоставлена инструкция по развертыванию.
- Контейнер должен запускаться через `docker-compose`.

## 7. Документация

- Разработчик должен предоставить:
  - README-файл с инструкцией по установке и запуску.
  - Документацию API, если сервис будет поддерживать REST API.
  - Описание архитектуры и структуры проекта.

## 8. Лицензия

- Код проекта распространяется под лицензией **GPL-3.0**.
- Любые изменения и производные проекты должны соблюдать условия данной лицензии.
- В исходном коде должна присутствовать лицензия в виде заголовков в файлах и отдельного LICENSE-файла в корне репозитория.

