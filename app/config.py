import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/data/uploads')
    RESULT_FOLDER = os.getenv('RESULT_FOLDER', '/data/results')
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'mp4'}
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

    # Создаем необходимые директории при запуске
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULT_FOLDER, exist_ok=True) 