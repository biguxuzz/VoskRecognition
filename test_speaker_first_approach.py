#!/usr/bin/env python3
"""
Тестовый скрипт для проверки нового подхода с приоритетом спикеров
"""

import os
import sys
import logging
from pathlib import Path

# Добавляем путь к модулям приложения
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from speaker_first_transcription_manager import SpeakerFirstTranscriptionManager

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_speaker_first_approach(audio_file_path):
    """
    Тестирует новый подход с приоритетом спикеров
    """
    try:
        logger.info(f"Testing speaker-first approach with file: {audio_file_path}")
        
        # Проверяем существование файла
        if not os.path.exists(audio_file_path):
            logger.error(f"Audio file not found: {audio_file_path}")
            return False
        
        # Создаем менеджер транскрибации
        transcription_manager = SpeakerFirstTranscriptionManager()
        
        # Обрабатываем аудио
        def progress_callback(progress):
            logger.info(f"Progress: {progress:.1f}%")
        
        result = transcription_manager.process_audio(audio_file_path, progress_callback)
        
        # Выводим результат
        logger.info("Transcription completed successfully!")
        logger.info("=" * 50)
        logger.info("RESULT:")
        logger.info("=" * 50)
        print(result)
        logger.info("=" * 50)
        
        # Сохраняем результат в файл
        output_file = f"speaker_first_result_{os.path.basename(audio_file_path)}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        logger.info(f"Result saved to: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}", exc_info=True)
        return False

def main():
    """
    Основная функция для запуска тестов
    """
    if len(sys.argv) != 2:
        print("Usage: python test_speaker_first_approach.py <audio_file_path>")
        print("Example: python test_speaker_first_approach.py uploads/test_audio.wav")
        sys.exit(1)
    
    audio_file_path = sys.argv[1]
    
    logger.info("Starting speaker-first transcription test")
    success = test_speaker_first_approach(audio_file_path)
    
    if success:
        logger.info("Test completed successfully!")
        sys.exit(0)
    else:
        logger.error("Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 