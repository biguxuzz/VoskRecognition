# Speech Recognition Portal

## 📌 Описание / Description

### 🇷🇺 Описание
**Speech Recognition Portal** – это веб-приложение для автоматического распознавания речи из аудио- и видеофайлов. Поддерживает форматы `.wav`, `.mp3`, `.mp4` и использует модель Whisper от OpenAI для транскрибации и pyannote/speaker-diarization для распознавания спикеров. Проект распространяется под лицензией **GPL-3.0**.

### 🇬🇧 Description
**Speech Recognition Portal** is a web application for automatic speech recognition from audio and video files. It supports `.wav`, `.mp3`, `.mp4` formats and uses OpenAI's Whisper model for transcription and pyannote/speaker-diarization for speaker recognition. The project is distributed under the **GPL-3.0** license.

---

## 🚀 Возможности / Features

### 🇷🇺 Возможности
- Загрузка файлов большого размера (`.wav`, `.mp3`, `.mp4`)
- Автоматическая конвертация аудио в формат `.wav`
- Двухэтапное распознавание:
  1. Транскрибация речи с таймкодами
  2. Распознавание спикеров
- Прогресс-бар обработки с отображением этапов
- Скачивание результата в `.txt` с указанием говорящих
- Запуск в `Docker` с поддержкой GPU
- REST API (если применимо)
- Автоматические тесты

### 🇬🇧 Features
- Upload large files (`.wav`, `.mp3`, `.mp4`)
- Automatic audio conversion to `.wav`
- Two-stage recognition:
  1. Speech transcription with timestamps
  2. Speaker recognition
- Processing progress bar with stage display
- Download result in `.txt` with speaker identification
- Deployment in `Docker` with GPU support
- REST API (if applicable)
- Automated tests

---

## 🛠️ Установка и запуск / Installation & Run

### 🇷🇺 Установка
```bash
# Клонировать репозиторий
git clone https://github.com/biguxuzz/speech-recognition-portal.git
cd speech-recognition-portal

# Собрать и запустить контейнер Docker
docker-compose up --build
```

### 🇬🇧 Installation
```bash
# Clone repository
git clone https://github.com/biguxuzz/speech-recognition-portal.git
cd speech-recognition-portal

# Build and run Docker container
docker-compose up --build
```

---

## 📜 Лицензия / License

Этот проект распространяется под лицензией **GPL-3.0**. Полный текст лицензии можно найти в файле [LICENSE](LICENSE).

This project is licensed under **GPL-3.0**. The full text of the license is available in the [LICENSE](LICENSE) file.

---

## 📧 Контакты / Contacts

- **GitHub:** [biguxuzz](https://github.com/biguxuzz)
- **Telegram:** [@biguxuzz](https://t.me/biguxuzz)
- **Email:** gorp@1cgst.ru

