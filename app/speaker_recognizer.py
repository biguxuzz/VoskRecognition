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
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Speaker recognizer using device: {self.device}")
        
        self.hf_token = os.getenv('HF_TOKEN')
        if not self.hf_token:
            raise ValueError("HF_TOKEN не установлен в переменных окружения")
            
        logger.info("Logging in to Hugging Face...")
        try:
            # Явная авторизация в Hugging Face
            login(token=self.hf_token)
            
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
                except Exception as e:
                    logger.error(f"No access to {model}. Please visit https://huggingface.co/{model} "
                               f"and accept the user conditions.")
                    raise ValueError(f"Нет доступа к модели {model}. Необходимо принять условия "
                                  f"использования на https://huggingface.co/{model}")
            
            if SpeakerRecognizer._pipeline is None:
                logger.info("Initializing speaker recognition pipeline...")
                SpeakerRecognizer._pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization",
                    use_auth_token=self.hf_token
                )
                # Явно переносим на GPU
                SpeakerRecognizer._pipeline = SpeakerRecognizer._pipeline.to(self.device)
                
                if str(self.device) == "cuda":
                    torch.cuda.empty_cache()
            
            self.pipeline = SpeakerRecognizer._pipeline
            logger.info("Speaker recognition initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {str(e)}")
            raise
        
    def recognize_speakers(self, audio_path, progress_callback=None):
        """Распознает спикеров в аудиофайле"""
        try:
            logger.info(f"Starting speaker recognition for {audio_path}")
            start_time = time.time()
            
            # Применяем диаризацию
            diarization = self.pipeline(audio_path)
            
            # Преобразуем результаты в удобный формат
            speakers = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speakers.append({
                    'start': turn.start,
                    'end': turn.end,
                    'speaker': f"SPEAKER_{speaker[-1]}"  # Упрощаем имена спикеров
                })
            
            logger.info(f"Found {len(set(s['speaker'] for s in speakers))} unique speakers")
            logger.info(f"Speaker recognition completed in {time.time() - start_time:.2f} seconds")
            
            if progress_callback:
                progress_callback(100)
                
            return speakers
            
        except Exception as e:
            logger.error(f"Ошибка при распознавании спикеров: {str(e)}")
            return [] 