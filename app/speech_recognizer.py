import whisper
import torch
import os
import logging
import time
from pathlib import Path
import soundfile as sf
import datetime
import threading
import inspect

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpeechRecognizer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
            
        self.initialized = True
        # Принудительно используем CPU для совместимости
        self.device = "cpu"
        logger.info("Using CPU for speech recognition")
        
        try:
            if SpeechRecognizer._model is None:
                logger.info("Loading Whisper model...")
                logger.info(f"Whisper version: {whisper.__version__}")
                logger.info(f"PyTorch version: {torch.__version__}")
                
                start_time = time.time()
                
                # Загружаем модель
                SpeechRecognizer._model = whisper.load_model("medium")
                logger.info(f"Initial model device: {next(SpeechRecognizer._model.parameters()).device}")
                
                # Убеждаемся, что модель на CPU
                SpeechRecognizer._model = SpeechRecognizer._model.cpu()
                logger.info(f"Model device after cpu(): {next(SpeechRecognizer._model.parameters()).device}")
                
                logger.info(f"Model loaded in {time.time() - start_time:.2f} seconds")
                
            self.model = SpeechRecognizer._model
            logger.info(f"Speech recognizer initialized on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise

    def _format_timestamp(self, seconds):
        """Форматирует время в [HH:MM:SS]"""
        return datetime.datetime.utcfromtimestamp(seconds).strftime('[%H:%M:%S]')
    
    def recognize(self, audio_path, progress_callback=None):
        """Транскрибирует аудио файл"""
        progress_thread = None
        stop_progress = threading.Event()  # Флаг для остановки потока
        
        try:
            logger.info(f"Starting transcription of {audio_path}")
            logger.info(f"Whisper version: {whisper.__version__}")
            logger.info(f"Available Whisper methods: {dir(self.model)}")
            logger.info(f"Transcribe method signature: {inspect.signature(self.model.transcribe)}")
            
            # Проверяем доступные параметры для transcribe
            try:
                source = inspect.getsource(self.model.transcribe)
                logger.info(f"Transcribe method source: {source}")
            except Exception as e:
                logger.warning(f"Could not get transcribe source: {e}")

            start_time = time.time()
            
            # Получаем длительность аудио
            audio_info = sf.info(audio_path)
            total_duration = audio_info.duration
            
            if progress_callback:
                progress_callback(5)
                logger.info("Starting transcription: 5%")

            # Обновленная функция прогресса с проверкой флага остановки
            def progress_updater():
                try:
                    logger.info("Progress updater thread started")
                    start = time.time()
                    while not stop_progress.is_set():
                        elapsed = time.time() - start
                        estimated_progress = min(85, (elapsed / total_duration) * 100)
                        progress = 5 + estimated_progress
                        progress_callback(progress)
                        logger.info(f"Progress update: {progress:.1f}%")
                        time.sleep(1)
                    logger.info("Progress updater thread stopping normally")
                except Exception as e:
                    logger.error(f"Error in progress updater: {str(e)}", exc_info=True)
                finally:
                    logger.info("Progress updater thread finished")

            if progress_callback:
                progress_thread = threading.Thread(target=progress_updater)
                progress_thread.daemon = True
                logger.info("Starting progress thread")
                progress_thread.start()

            # Запускаем распознавание для CPU (fp16=False)
            result = self.model.transcribe(
                audio_path,
                language="ru",
                task="transcribe",
                fp16=False  # Отключаем fp16 для CPU
            )
            
            # Форматируем результат с тайм-кодами
            transcription = []
            total_segments = len(result["segments"])
            
            for i, segment in enumerate(result["segments"]):
                timestamp = self._format_timestamp(segment["start"])
                transcription.append(f"{timestamp} {segment['text'].strip()}")
                
                # Обновляем прогресс финальной обработки
                if progress_callback:
                    progress = 85 + (i + 1) / total_segments * 5  # от 85% до 90%
                    progress_callback(progress)
                    logger.info(f"Processing segment {i+1}/{total_segments}: {progress:.1f}%")
            
            logger.info(f"Transcription completed in {time.time() - start_time:.2f} seconds")
            
            if progress_callback:
                progress_callback(90)  # Сигнализируем о завершении основной части
                
            return "\n".join(transcription)
            
        except Exception as e:
            logger.error(f"Error in recognition: {str(e)}", exc_info=True)
            raise
        finally:
            if progress_thread:
                logger.info("Stopping progress thread")
                stop_progress.set()  # Сигнализируем потоку о необходимости остановки
                progress_thread.join(timeout=2)  # Ждем завершения потока
                logger.info(f"Progress thread is{'not ' if progress_thread.is_alive() else ' '}stopped")