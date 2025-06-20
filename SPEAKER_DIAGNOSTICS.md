# Диагностика проблем с распознаванием спикеров

## Обзор проблемы

Если распознавание речи работает, но разделение по спикерам не срабатывает, это может быть связано с несколькими причинами.

## Шаг 1: Проверка логов

Сначала проверьте логи приложения:

```bash
# Просмотр логов в реальном времени
docker-compose logs -f web

# Просмотр последних логов
docker-compose logs web --tail=100
```

Ищите следующие сообщения:
- `"Starting speaker recognition"`
- `"Speaker recognition completed successfully"`
- `"Found X unique speakers"`
- Ошибки с `HF_TOKEN`
- Ошибки с доступом к моделям

## Шаг 2: Проверка токена Hugging Face

1. **Проверьте файл `.env`:**
```bash
cat .env
```

Убедитесь, что `HF_TOKEN` установлен и не пустой.

2. **Получите новый токен:**
   - Перейдите на https://huggingface.co/settings/tokens
   - Создайте новый токен с правами "Read"
   - Обновите файл `.env`

3. **Примите условия использования моделей:**
   - https://huggingface.co/pyannote/speaker-diarization
   - https://huggingface.co/pyannote/segmentation  
   - https://huggingface.co/pyannote/embedding

## Шаг 3: Запуск тестового скрипта

Запустите тестовый скрипт внутри контейнера:

```bash
# Войдите в контейнер
docker-compose exec web bash

# Запустите тест
python3 /app/test_speaker_recognition.py
```

## Шаг 4: Проверка доступности моделей

Внутри контейнера проверьте доступ к моделям:

```bash
# Войдите в контейнер
docker-compose exec web bash

# Проверьте токен
echo $HF_TOKEN

# Проверьте доступ к моделям
python3 -c "
from huggingface_hub import HfApi
api = HfApi()
try:
    api.model_info('pyannote/speaker-diarization')
    print('✓ Доступ к speaker-diarization')
except:
    print('✗ Нет доступа к speaker-diarization')
"
```

## Шаг 5: Проверка GPU/CUDA

Убедитесь, что CUDA отключена:

```bash
# Внутри контейнера
python3 -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA_VISIBLE_DEVICES: {os.environ.get(\"CUDA_VISIBLE_DEVICES\", \"not set\")}')
"
```

## Шаг 6: Ручное тестирование

Создайте простой тестовый файл:

```bash
# Внутри контейнера
python3 -c "
from app.speaker_recognizer import SpeakerRecognizer
import os

# Проверяем инициализацию
sr = SpeakerRecognizer()
print('✓ SpeakerRecognizer initialized')

# Проверяем pipeline
print(f'Pipeline device: {sr.device}')
print(f'Pipeline exists: {sr.pipeline is not None}')
"
```

## Возможные решения

### Проблема 1: Неверный токен
**Симптомы:** `HF_TOKEN не установлен` или `No access to model`
**Решение:** Обновите токен в `.env` и перезапустите контейнер

### Проблема 2: Не приняты условия использования
**Симптомы:** `No access to pyannote/speaker-diarization`
**Решение:** Примите условия на Hugging Face

### Проблема 3: Проблемы с GPU
**Симптомы:** Ошибки CUDA или медленная работа
**Решение:** Убедитесь, что CUDA отключена (должно быть `CUDA available: False`)

### Проблема 4: Недостаточно памяти
**Симптомы:** `Out of memory` или зависание
**Решение:** Увеличьте память для Docker или используйте меньшую модель

### Проблема 5: Проблемы с аудиофайлом
**Симптомы:** `Audio file not found` или `Audio file is empty`
**Решение:** Проверьте, что файл существует и не пустой

## Перезапуск с очисткой

Если ничего не помогает, попробуйте полную пересборку:

```bash
# Остановите контейнеры
docker-compose down

# Удалите образы и тома
docker-compose down --rmi all --volumes

# Пересоберите
docker-compose up --build
```

## Проверка результата

После исправления проблем проверьте результат:

1. Загрузите аудиофайл
2. Запустите распознавание
3. Проверьте, что в результате есть `[SPEAKER_X]` метки
4. Если все еще `[UNKNOWN]`, проверьте логи на ошибки

## Контакты для поддержки

Если проблемы остаются:
1. Сохраните полные логи
2. Укажите версию Docker и ОС
3. Опишите шаги воспроизведения 