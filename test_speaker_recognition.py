#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы распознавания спикеров
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Добавляем путь к модулям приложения
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

def test_speaker_recognition():
    """Тестирует распознавание спикеров"""
    try:
        from speaker_recognizer import SpeakerRecognizer
        
        logger.info("Testing speaker recognition initialization...")
        
        # Проверяем токен
        hf_token = os.getenv('HF_TOKEN')
        if not hf_token:
            logger.error("HF_TOKEN не найден в переменных окружения")
            return False
            
        logger.info("HF_TOKEN найден")
        
        # Инициализируем распознаватель спикеров
        speaker_recognizer = SpeakerRecognizer()
        logger.info("Speaker recognizer initialized successfully")
        
        # Проверяем, что pipeline создан
        if speaker_recognizer.pipeline is None:
            logger.error("Pipeline не инициализирован")
            return False
            
        logger.info("Pipeline initialized successfully")
        
        # Проверяем устройство
        logger.info(f"Speaker recognizer device: {speaker_recognizer.device}")
        
        # Безопасная проверка устройства pipeline
        try:
            if hasattr(speaker_recognizer.pipeline, 'device'):
                logger.info(f"Pipeline device: {speaker_recognizer.pipeline.device}")
            else:
                logger.info("Pipeline device: CPU (default)")
        except Exception as e:
            logger.warning(f"Could not determine pipeline device: {e}")
            logger.info("Pipeline device: CPU (assumed)")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing speaker recognition: {str(e)}", exc_info=True)
        return False

def test_pytorch_cuda():
    """Тестирует доступность CUDA"""
    try:
        import torch
        
        logger.info(f"PyTorch version: {torch.__version__}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            logger.info(f"CUDA device count: {torch.cuda.device_count()}")
            logger.info(f"Current device: {torch.cuda.current_device()}")
            logger.info(f"Device name: {torch.cuda.get_device_name(0)}")
        else:
            logger.info("CUDA not available - this is expected for CPU-only setup")
            
        return True
        
    except Exception as e:
        logger.error(f"Error testing PyTorch CUDA: {str(e)}", exc_info=True)
        return False

def main():
    """Основная функция тестирования"""
    logger.info("Starting speaker recognition tests...")
    
    # Тест PyTorch и CUDA
    logger.info("=" * 50)
    logger.info("Testing PyTorch and CUDA...")
    if not test_pytorch_cuda():
        logger.error("PyTorch CUDA test failed")
        return False
    
    # Тест распознавания спикеров
    logger.info("=" * 50)
    logger.info("Testing speaker recognition...")
    if not test_speaker_recognition():
        logger.error("Speaker recognition test failed")
        return False
    
    logger.info("=" * 50)
    logger.info("All tests passed! Speaker recognition should work correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 