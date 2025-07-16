# Мониторинг прогресса и управление задачами

## Проблемы и решения

### 1. Зависание speaker diarization
Процесс speaker diarization может зависать на длительное время без видимого прогресса. Добавлены инструменты для мониторинга и управления задачами.

### 2. Ошибка 413 Request Entity Too Large
Файлы большого размера могут вызывать ошибку превышения лимита. Решения:
- Увеличен лимит до 1GB
- Добавлена проверка размера на клиенте и сервере
- Улучшена обработка ошибок

## Новые функции

### 1. Детальное логирование
- Добавлено логирование каждого этапа pipeline
- Прогресс обновляется каждые 30 секунд
- Таймаут 30 минут для pipeline

### 2. API endpoints

#### Получение статуса задачи
```bash
GET /status/<task_id>
```

#### Получение списка всех задач
```bash
GET /tasks
```

#### Отмена задачи
```bash
POST /cancel/<task_id>
```

### 3. Скрипты мониторинга

#### test_progress.py
Мониторинг конкретной задачи с возможностью отмены:

```bash
python test_progress.py <task_id> [base_url] [interval]
```

Пример:
```bash
python test_progress.py 9b60dfea-4dc0-4030-99d3-1f0c534e7217
```

Особенности:
- Показывает прогресс в реальном времени
- Предупреждает о зависших задачах (5+ минут без прогресса)
- Ctrl+C для отмены задачи

#### cleanup_tasks.py
Поиск и отмена зависших задач:

```bash
python cleanup_tasks.py [base_url] [timeout_minutes]
```

Пример:
```bash
python cleanup_tasks.py http://localhost:5000 30
```

#### test_file_upload.py
Тестирование загрузки файлов разных размеров:

```bash
python test_file_upload.py
```

## Использование

### 1. Запуск мониторинга
```bash
# Мониторинг конкретной задачи
python test_progress.py 9b60dfea-4dc0-4030-99d3-1f0c534e7217

# Мониторинг с кастомным интервалом (5 секунд)
python test_progress.py 9b60dfea-4dc0-4030-99d3-1f0c534e7217 http://localhost:5000 5
```

### 2. Очистка зависших задач
```bash
# Поиск задач, зависших более 30 минут
python cleanup_tasks.py

# Поиск задач, зависших более 10 минут
python cleanup_tasks.py http://localhost:5000 10
```

### 3. Тестирование загрузки файлов
```bash
# Тестирование файлов разных размеров
python test_file_upload.py
```

### 4. Ручная отмена задачи
```bash
curl -X POST http://localhost:5000/cancel/9b60dfea-4dc0-4030-99d3-1f0c534e7217
```

## Логирование

### Новые логи в speaker_recognizer.py:
- `Step 1: Loading audio file...`
- `Step 2: Processing audio through pipeline...`
- `Pipeline started at <timestamp>`
- `Pipeline still running... Elapsed time: <seconds>`
- `Pipeline completed in <seconds>`
- `Step 3: Processing diarization results...`

### Новые логи в main.py:
- `Task <id> progress: <progress>% (raw: <raw_progress>%)`
- `Status request for task <id>`
- `Task <id> status: <status>`
- `File too large: <size> bytes (max: <max_size>)`

## Таймауты и лимиты

- **Pipeline timeout**: 30 минут
- **Progress warning**: 5 минут без изменений
- **Stuck task detection**: 30 минут (настраивается)
- **Max file size**: 1GB
- **Client-side file size check**: 1GB

## Статусы задач

- `processing` - задача выполняется
- `completed` - задача завершена успешно
- `error` - задача завершилась с ошибкой
- `cancelled` - задача отменена пользователем

## Структура данных задачи

```json
{
  "progress": 45,
  "status": "processing",
  "current_file": 0,
  "total_files": 1,
  "created_at": 1640995200.0,
  "last_update": 1640995260.0,
  "result_file": "result_xxx.txt"  // только для completed
}
```

## Обработка ошибок

### Ошибка 413 (File Too Large)
- Автоматическая проверка размера на клиенте
- Проверка размера на сервере
- Информативные сообщения об ошибке
- Максимальный размер: 1GB

### Ошибки pipeline
- Таймаут 30 минут
- Детальное логирование
- Возможность отмены задачи
- Fallback к обычной транскрибации 