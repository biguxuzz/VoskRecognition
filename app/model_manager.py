import os
import wget
import zipfile
import shutil

class ModelManager:
    MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-ru-0.22.zip"
    MODEL_DIR = "/app/models"
    MODEL_NAME = "vosk-model-ru-0.22"
    
    @classmethod
    def ensure_model_exists(cls):
        """Проверяет наличие модели и загружает её при необходимости"""
        model_path = os.path.join(cls.MODEL_DIR, cls.MODEL_NAME)
        
        # Если модель уже существует, ничего не делаем
        if os.path.exists(model_path):
            print(f"Модель {cls.MODEL_NAME} уже установлена")
            return model_path
            
        print(f"Модель {cls.MODEL_NAME} не найдена. Начинаем загрузку...")
        
        # Создаем директорию для моделей если её нет
        os.makedirs(cls.MODEL_DIR, exist_ok=True)
        
        # Загружаем архив с моделью
        zip_path = os.path.join(cls.MODEL_DIR, f"{cls.MODEL_NAME}.zip")
        wget.download(cls.MODEL_URL, zip_path)
        
        # Распаковываем архив
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(cls.MODEL_DIR)
            
        # Удаляем архив
        os.remove(zip_path)
        
        print(f"\nМодель {cls.MODEL_NAME} успешно установлена")
        return model_path 