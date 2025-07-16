from pyannote.audio import Pipeline
import torch
import os
import logging
import time
import soundfile as sf
from dotenv import load_dotenv
from huggingface_hub import login, HfApi

# Загружаем переменные окружения явно
load_dotenv()

logger = logging.getLogger(__name__)

class SpeakerRecognizer:
    _instance = None
    _pipeline = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpeakerRecognizer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
            
        self.initialized = True
        # Принудительно используем CPU для совместимости
        self.device = torch.device("cpu")
        logger.info(f"Speaker recognizer using device: {self.device}")
        
        self.hf_token = os.getenv('HF_TOKEN')
        if not self.hf_token:
            logger.error("HF_TOKEN не установлен в переменных окружения")
            raise ValueError("HF_TOKEN не установлен в переменных окружения")
            
        logger.info("Logging in to Hugging Face...")
        try:
            # Явная авторизация в Hugging Face
            login(token=self.hf_token)
            logger.info("Successfully logged in to Hugging Face")
            
            # Проверяем доступ к необходимым моделям
            api = HfApi()
            models_to_check = [
                "pyannote/speaker-diarization",
                "pyannote/segmentation",
                "pyannote/embedding"
            ]
            
            for model in models_to_check:
                try:
                    api.model_info(model)
                    logger.info(f"Access confirmed for {model}")
                except Exception as e:
                    logger.error(f"No access to {model}. Please visit https://huggingface.co/{model} "
                               f"and accept the user conditions.")
                    raise ValueError(f"Нет доступа к модели {model}. Необходимо принять условия "
                                  f"использования на https://huggingface.co/{model}")
            
            if SpeakerRecognizer._pipeline is None:
                logger.info("Initializing speaker recognition pipeline...")
                
                # Принудительно отключаем CUDA для pyannote.audio
                os.environ['CUDA_VISIBLE_DEVICES'] = ''
                torch.cuda.is_available = lambda: False
                
                SpeakerRecognizer._pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization",
                    use_auth_token=self.hf_token
                )
                
                # Явно переносим на CPU
                SpeakerRecognizer._pipeline = SpeakerRecognizer._pipeline.to(self.device)
                
                logger.info("Pipeline moved to CPU successfully")
                
                # Безопасная проверка устройства pipeline
                try:
                    # Проверяем, есть ли у pipeline атрибут device
                    if hasattr(SpeakerRecognizer._pipeline, 'device'):
                        logger.info(f"Pipeline device: {SpeakerRecognizer._pipeline.device}")
                    else:
                        logger.info("Pipeline device: CPU (default)")
                except Exception as e:
                    logger.warning(f"Could not determine pipeline device: {e}")
                    logger.info("Pipeline device: CPU (assumed)")
            
            self.pipeline = SpeakerRecognizer._pipeline
            logger.info("Speaker recognition initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {str(e)}", exc_info=True)
            raise
        
    def recognize_speakers(self, audio_path, progress_callback=None):
        """Распознает спикеров в аудиофайле"""
        try:
            logger.info(f"Starting speaker recognition for {audio_path}")
            
            # Проверяем существование файла
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return []
                
            # Проверяем размер файла
            file_size = os.path.getsize(audio_path)
            logger.info(f"Audio file size: {file_size} bytes")
            
            if file_size == 0:
                logger.error("Audio file is empty")
                return []
            
            start_time = time.time()
            
            # Применяем диаризацию с детальным логированием
            logger.info("Running diarization pipeline...")
            logger.info("Step 1: Loading audio file...")
            if progress_callback:
                progress_callback(10)
            
            # Добавляем логирование для отслеживания прогресса
            logger.info("Step 2: Processing audio through pipeline...")
            if progress_callback:
                progress_callback(20)
            
            # Запускаем pipeline с таймаутом и логированием
            pipeline_start = time.time()
            logger.info(f"Pipeline started at {pipeline_start}")
            
            # Добавляем промежуточные логи каждые 30 секунд
            def log_progress():
                elapsed = time.time() - pipeline_start
                logger.info(f"Pipeline running for {elapsed:.1f} seconds...")
                if progress_callback:
                    # Обновляем прогресс от 20% до 80% во время работы pipeline
                    progress = 20 + min(60, int(elapsed / 30) * 10)  # +10% каждые 30 секунд
                    progress_callback(progress)
            
            # Запускаем логирование прогресса в отдельном потоке
            import threading
            progress_thread = threading.Thread(target=lambda: self._log_progress_periodically(pipeline_start, progress_callback))
            progress_thread.daemon = True
            progress_thread.start()
            
            try:
                # Добавляем таймаут для pipeline (максимум 30 минут) с использованием threading
                import threading
                import queue
                
                result_queue = queue.Queue()
                exception_queue = queue.Queue()
                
                def run_pipeline():
                    try:
                        result = self.pipeline(audio_path)
                        result_queue.put(result)
                    except Exception as e:
                        exception_queue.put(e)
                
                # Запускаем pipeline в отдельном потоке
                pipeline_thread = threading.Thread(target=run_pipeline)
                pipeline_thread.daemon = True
                pipeline_thread.start()
                
                # Ждем результат с таймаутом
                try:
                    diarization = result_queue.get(timeout=1800)  # 30 минут таймаут
                    logger.info("Diarization completed successfully")
                except queue.Empty:
                    logger.error("Pipeline timed out after 30 minutes")
                    raise TimeoutError("Pipeline timeout after 30 minutes")
                except Exception as e:
                    # Проверяем, есть ли исключение в очереди
                    try:
                        pipeline_exception = exception_queue.get_nowait()
                        raise pipeline_exception
                    except queue.Empty:
                        raise e
                    
            except Exception as e:
                logger.error(f"Pipeline failed after {time.time() - pipeline_start:.1f} seconds: {str(e)}")
                raise
            
            pipeline_end = time.time()
            logger.info(f"Pipeline completed in {pipeline_end - pipeline_start:.2f} seconds")
            
            if progress_callback:
                progress_callback(80)
            
            # Преобразуем результаты в удобный формат
            logger.info("Step 3: Processing diarization results...")
            speakers = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speakers.append({
                    'start': turn.start,
                    'end': turn.end,
                    'speaker': f"SPEAKER_{speaker[-1]}"  # Упрощаем имена спикеров
                })
            
            unique_speakers = set(s['speaker'] for s in speakers)
            logger.info(f"Found {len(unique_speakers)} unique speakers: {list(unique_speakers)}")
            logger.info(f"Total speaker segments: {len(speakers)}")
            logger.info(f"Speaker recognition completed in {time.time() - start_time:.2f} seconds")
            
            if progress_callback:
                progress_callback(100)
                
            return speakers
            
        except Exception as e:
            logger.error(f"Ошибка при распознавании спикеров: {str(e)}", exc_info=True)
            logger.warning("Returning empty speaker list due to error")
            return []
    
    def _log_progress_periodically(self, start_time, progress_callback):
        """Логирует прогресс каждые 30 секунд"""
        import time
        while True:
            time.sleep(30)
            elapsed = time.time() - start_time
            logger.info(f"Pipeline still running... Elapsed time: {elapsed:.1f} seconds")
            if progress_callback:
                # Обновляем прогресс от 20% до 80% во время работы pipeline
                progress = 20 + min(60, int(elapsed / 30) * 10)  # +10% каждые 30 секунд
                progress_callback(progress) 