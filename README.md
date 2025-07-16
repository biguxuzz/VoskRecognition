# Speech Recognition Portal

## 📌 Описание / Description

### 🇷🇺 Описание
**Speech Recognition Portal** – это веб-приложение для автоматического распознавания речи из аудио- и видеофайлов. Поддерживает форматы `.wav`, `.mp3`, `.mp4` и использует модель Whisper от OpenAI для транскрибации и pyannote/speaker-diarization для распознавания спикеров. Проект распространяется под лицензией **GPL-3.0**.

### 🇬🇧 Description
**Speech Recognition Portal** is a web application for automatic speech recognition from audio and video files. It supports `.wav`, `.mp3`, `.mp4` formats and uses OpenAI's Whisper model for transcription and pyannote/speaker-diarization for speaker recognition. The project is distributed under the **GPL-3.0** license.

---

## 🚀 Возможности / Features

### 🇷🇺 Возможности
- Загрузка нескольких файлов большого размера (`.wav`, `.mp3`, `.mp4`)
- Возможность изменения порядка файлов перед объединением
- Автоматическое объединение нескольких файлов в один
- Автоматическая конвертация аудио в формат `.wav`
- **Новый подход с приоритетом спикеров:**
  1. Сначала определяется сегментация спикеров с точными таймингами
  2. Затем каждый сегмент транскрибируется отдельно
  3. Результат объединяется с сохранением точных границ времени
- Прогресс-бар обработки с отображением этапов
- Скачивание результата в `.txt` с указанием говорящих
- Запуск в `Docker` с поддержкой CPU
- REST API (если применимо)
- Автоматические тесты

### 🇬🇧 Features
- Upload multiple large files (`.wav`, `.mp3`, `.mp4`)
- Ability to change file order before merging
- Automatic merging of multiple files into one
- Automatic audio conversion to `.wav` format
- **New speaker-first approach:**
  1. Speaker segmentation with precise timings is determined first
  2. Each segment is then transcribed separately
  3. Results are merged while preserving exact time boundaries
- Processing progress bar with stage display
- Download result in `.txt` with speaker indication
- Docker deployment with CPU support
- REST API (if applicable)
- Automatic tests

---

## 🔄 Новый подход с приоритетом спикеров / New Speaker-First Approach

### 🇷🇺 Преимущества нового подхода
- **Точность таймингов**: Каждый сегмент транскрибируется отдельно, что обеспечивает точные границы времени
- **Лучшее качество распознавания**: Короткие сегменты часто распознаются лучше, чем длинные
- **Четкое разделение спикеров**: Нет смешивания речи разных спикеров в одном сегменте
- **Fallback механизм**: Если не удается определить спикеров, система автоматически переключается на полную транскрибацию

### 🇬🇧 Benefits of the new approach
- **Timing accuracy**: Each segment is transcribed separately, ensuring precise time boundaries
- **Better recognition quality**: Short segments are often recognized better than long ones
- **Clear speaker separation**: No mixing of different speakers' speech in one segment
- **Fallback mechanism**: If speaker detection fails, the system automatically switches to full transcription

### 🇷🇺 Тестирование нового подхода
```bash
python test_speaker_first_approach.py uploads/test_audio.wav
```

### 🇬🇧 Testing the new approach
```bash
python test_speaker_first_approach.py uploads/test_audio.wav
```

Подробная документация: [SPEAKER_FIRST_APPROACH.md](SPEAKER_FIRST_APPROACH.md)

Detailed documentation: [SPEAKER_FIRST_APPROACH.md](SPEAKER_FIRST_APPROACH.md)

---

## 🛠️ Установка и запуск / Installation and Setup

### 🇷🇺 Требования
- Docker и Docker Compose
- Минимум 4GB RAM
- Процессор с поддержкой AVX2 (для оптимальной производительности)
- Аккаунт на Hugging Face с токеном доступа

### 🇬🇧 Requirements
- Docker and Docker Compose
- Minimum 4GB RAM
- CPU with AVX2 support (for optimal performance)
- Hugging Face account with access token

### 🇷🇺 Регистрация на Hugging Face

Для работы с распознаванием спикеров необходимо:

1. **Создать аккаунт на Hugging Face:**
   - Перейдите на https://huggingface.co/join
   - Заполните форму регистрации
   - Подтвердите email

2. **Получить токен доступа:**
   - Войдите в аккаунт на https://huggingface.co
   - Перейдите в Settings → Access Tokens: https://huggingface.co/settings/tokens
   - Нажмите "New token"
   - Введите название токена (например, "speech-recognition")
   - Выберите роль "Read"
   - Нажмите "Generate token"
   - Скопируйте токен (он понадобится позже)

3. **Принять условия использования моделей:**
   Перейдите на эти страницы и нажмите "Accept":
   - https://huggingface.co/pyannote/speaker-diarization
   - https://huggingface.co/pyannote/segmentation
   - https://huggingface.co/pyannote/embedding

### 🇬🇧 Hugging Face Registration

For speaker recognition functionality:

1. **Create Hugging Face account:**
   - Go to https://huggingface.co/join
   - Fill out the registration form
   - Confirm your email

2. **Get access token:**
   - Log in to https://huggingface.co
   - Go to Settings → Access Tokens: https://huggingface.co/settings/tokens
   - Click "New token"
   - Enter token name (e.g., "speech-recognition")
   - Select role "Read"
   - Click "Generate token"
   - Copy the token (you'll need it later)

3. **Accept model usage terms:**
   Go to these pages and click "Accept":
   - https://huggingface.co/pyannote/speaker-diarization
   - https://huggingface.co/pyannote/segmentation
   - https://huggingface.co/pyannote/embedding

### 🇷🇺 Быстрый запуск
1. Клонируйте репозиторий:
```bash
git clone https://github.com/biguxuzz/VoskRecognition.git
cd VoskRecognition
```

2. Создайте файл `.env` с необходимыми переменными:
```bash
HF_TOKEN=your_huggingface_token_here
UPLOAD_FOLDER=/data/uploads
RESULT_FOLDER=/data/results
```

3. Запустите приложение:
```bash
docker-compose up --build
```

4. Откройте браузер и перейдите по адресу: `http://localhost:5000`

### 🇬🇧 Quick Start
1. Clone the repository:
```bash
git clone https://github.com/biguxuzz/VoskRecognition.git
cd VoskRecognition
```

2. Create `.env` file with required variables:
```bash
HF_TOKEN=your_huggingface_token_here
UPLOAD_FOLDER=/data/uploads
RESULT_FOLDER=/data/results
```

3. Start the application:
```bash
docker-compose up --build
```

4. Open your browser and go to: `http://localhost:5000`

---

## 📋 Конфигурация / Configuration

### 🇷🇺 Переменные окружения
- `HF_TOKEN` - токен Hugging Face для доступа к моделям
- `UPLOAD_FOLDER` - папка для загруженных файлов
- `RESULT_FOLDER` - папка для результатов

### 🇬🇧 Environment Variables
- `HF_TOKEN` - Hugging Face token for model access
- `UPLOAD_FOLDER` - folder for uploaded files
- `RESULT_FOLDER` - folder for results

---

## 📝 Лицензия / License

Этот проект распространяется под лицензией **GPL-3.0**. См. файл `LICENSE` для подробностей.

This project is distributed under the **GPL-3.0** license. See the `LICENSE` file for details.

---

## 🤝 Вклад в проект / Contributing

Мы приветствуем вклады в проект! Пожалуйста, создавайте issues и pull requests.

We welcome contributions to the project! Please create issues and pull requests.

---

## 📧 Контакты / Contacts

- **GitHub:** [biguxuzz](https://github.com/biguxuzz)
- **Telegram:** [@biguxuzz](https://t.me/biguxuzz)
- **Email:** gorp@1cgst.ru