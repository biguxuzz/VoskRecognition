import os

class Config:
    UPLOAD_FOLDER = '/tmp/uploads'
    RESULT_FOLDER = '/tmp/results'
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'mp4'}
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

    # Создаем необходимые директории при запуске
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULT_FOLDER, exist_ok=True) 