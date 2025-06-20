from .speech_recognizer import SpeechRecognizer
from .speaker_recognizer import SpeakerRecognizer
import logging
import os

logger = logging.getLogger(__name__)

class TranscriptionManager:
    def __init__(self):
        self.speech_recognizer = SpeechRecognizer()
        self.speaker_recognizer = SpeakerRecognizer()
    
    def process_audio(self, audio_path, progress_callback=None):
        try:
            def update_progress(progress):
                if progress_callback:
                    rounded_progress = round(progress, 1)
                    progress_callback(rounded_progress)
                    logger.info(f"Current progress: {rounded_progress}%")

            logger.info("Starting speech recognition")
            
            try:
                # Подробное логирование перед распознаванием
                logger.info(f"Audio path: {audio_path}")
                logger.info(f"File exists: {os.path.exists(audio_path)}")
                logger.info(f"File size: {os.path.getsize(audio_path) if os.path.exists(audio_path) else 'N/A'}")
                
                transcription = self.speech_recognizer.recognize(
                    audio_path, 
                    progress_callback=update_progress
                )
                logger.info("Speech recognition completed successfully")
                
            except Exception as e:
                logger.error(f"Speech recognition error: {str(e)}", exc_info=True)
                raise
                
            logger.info("Starting speaker recognition")
            update_progress(90)
            
            speakers = []
            try:
                logger.info("Attempting speaker recognition...")
                speakers = self.speaker_recognizer.recognize_speakers(audio_path)
                logger.info(f"Speaker recognition completed successfully. Found {len(speakers)} speaker segments")
                
                if not speakers:
                    logger.warning("Speaker recognition returned empty list - continuing without speaker info")
                    
            except Exception as e:
                logger.error(f"Speaker recognition error: {str(e)}", exc_info=True)
                logger.warning("Continuing without speaker recognition - will use UNKNOWN for all speakers")
                speakers = []  # Пустой список для продолжения работы
                
            # Объединяем результаты
            final_result = self._merge_results(transcription, speakers)
            logger.info("Results merged successfully")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in process_audio: {str(e)}", exc_info=True)
            raise
    
    def _merge_results(self, transcription, speakers):
        """Объединяет результаты распознавания речи и спикеров"""
        try:
            logger.info(f"Merging transcription ({len(transcription.split())} words) with {len(speakers)} speaker segments")
            
            # Логируем информацию о спикерах для диагностики
            logger.info("Speaker segments:")
            for i, speaker in enumerate(speakers):
                logger.info(f"  {i}: {speaker['speaker']} from {speaker['start']:.2f}s to {speaker['end']:.2f}s")
            
            lines = transcription.split('\n')
            result = []
            
            for line_num, line in enumerate(lines):
                # Пропускаем пустые строки
                if not line.strip():
                    continue
                    
                try:
                    time_str = line[:10]  # [HH:MM:SS]
                    text = line[11:].strip()
                    
                    # Преобразуем время в секунды для поиска спикера
                    time_parts = time_str[1:-1].split(':')
                    seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])
                    
                    logger.info(f"Line {line_num}: time={time_str} ({seconds:.2f}s), text='{text[:50]}...'")
                    
                    # Ищем спикера для данного времени с допуском
                    current_speaker = "UNKNOWN"
                    tolerance = 1.0  # Допуск в 1 секунду
                    
                    for speaker_info in speakers:
                        # Проверяем, попадает ли время в диапазон с допуском
                        if (speaker_info['start'] - tolerance) <= seconds <= (speaker_info['end'] + tolerance):
                            current_speaker = speaker_info['speaker']
                            logger.info(f"  -> Found speaker: {current_speaker} (range: {speaker_info['start']:.2f}s - {speaker_info['end']:.2f}s, tolerance: ±{tolerance}s)")
                            break
                    else:
                        logger.info(f"  -> No speaker found for {seconds:.2f}s (tolerance: ±{tolerance}s), using UNKNOWN")
                    
                    # Форматируем строку с информацией о спикере
                    result.append(f"{time_str} [{current_speaker}] {text}")
                    
                except Exception as e:
                    logger.error(f"Error processing line '{line}': {str(e)}")
                    result.append(line)  # Добавляем исходную строку в случае ошибки
            
            logger.info(f"Successfully merged {len(result)} lines")
            return '\n'.join(result)
            
        except Exception as e:
            logger.error(f"Error merging results: {str(e)}")
            return transcription  # Возвращаем исходный текст в случае ошибки
    
    def _find_speaker(self, time_str, speakers):
        """Находит спикера для заданного времени"""
        # Преобразуем время из строки в секунды
        time_parts = time_str[1:-1].split(':')  # убираем [] и разбиваем
        seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
        
        # Допуск для сопоставления времени
        tolerance = 1.0
        
        # Ищем спикера с допуском
        for speaker_info in speakers:
            if (speaker_info['start'] - tolerance) <= seconds <= (speaker_info['end'] + tolerance):
                return speaker_info['speaker']
        
        return "UNKNOWN" 