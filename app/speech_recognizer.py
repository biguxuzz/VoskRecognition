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
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Проверяем доступность CUDA
        if torch.cuda.is_available():
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            logger.warning("CUDA is not available. Speech recognition will be slow!")
        
        try:
            if SpeechRecognizer._model is None:
                logger.info("Loading Whisper model...")
                logger.info(f"Whisper version: {whisper.__version__}")
                logger.info(f"PyTorch version: {torch.__version__}")
                
                start_time = time.time()
                
                # Загружаем модель
                SpeechRecognizer._model = whisper.load_model("medium")
                logger.info(f"Initial model device: {next(SpeechRecognizer._model.parameters()).device}")
                
                # Переносим на GPU если доступно
                if self.device == "cuda":
                    SpeechRecognizer._model = SpeechRecognizer._model.cuda()
                    logger.info(f"Model device after cuda(): {next(SpeechRecognizer._model.parameters()).device}")
                    
                    # Проверяем доступные параметры decode
                    try:
                        from whisper.decoding import DecodingOptions
                        logger.info(f"DecodingOptions parameters: {inspect.signature(DecodingOptions.__init__)}")
                    except Exception as e:
                        logger.warning(f"Could not inspect DecodingOptions: {e}")
                
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
            
            # Проверяем использование GPU
            if self.device == "cuda":
                logger.info(f"GPU Memory before transcription: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
            
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

            # Запускаем распознавание без параметра device
            result = self.model.transcribe(
                audio_path,
                language="ru",
                task="transcribe",
                fp16=(self.device == "cuda")
            )
            
            if self.device == "cuda":
                logger.info(f"GPU Memory after transcription: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
                torch.cuda.empty_cache()
            
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