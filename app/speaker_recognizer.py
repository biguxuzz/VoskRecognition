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
            
            # Применяем диаризацию
            logger.info("Running diarization pipeline...")
            diarization = self.pipeline(audio_path)
            logger.info("Diarization completed")
            
            # Преобразуем результаты в удобный формат
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