from .speech_recognizer import SpeechRecognizer
from .speaker_recognizer import SpeakerRecognizer
from .audio_processor import AudioProcessor
import logging
import os
import soundfile as sf
import tempfile
import shutil

logger = logging.getLogger(__name__)

class SpeakerFirstTranscriptionManager:
    def __init__(self):
        self.speech_recognizer = SpeechRecognizer()
        self.speaker_recognizer = SpeakerRecognizer()
        self.audio_processor = AudioProcessor()
    
    def process_audio(self, audio_path, progress_callback=None):
        """
        Обрабатывает аудио в новом порядке:
        1. Определяет сегменты спикеров
        2. Транскрибирует каждый сегмент отдельно
        3. Объединяет результаты с точными таймингами
        """
        try:
            def update_progress(progress, message=""):
                if progress_callback:
                    progress_callback(progress)
                    logger.info(f"Progress: {progress:.1f}% - {message}")

            logger.info("Starting speaker-first transcription process")
            update_progress(0, "Начинаем обработку")

            # Шаг 1: Определяем сегменты спикеров (20% прогресса)
            logger.info("Step 1: Speaker diarization")
            update_progress(5, "Определяем сегменты спикеров")
            
            # Передаем callback для отслеживания прогресса диаризации
            def speaker_progress_callback(progress):
                # Масштабируем прогресс диаризации от 5% до 20%
                scaled_progress = 5 + (progress * 0.15)  # 15% от общего прогресса
                update_progress(scaled_progress, f"Диаризация: {progress:.0f}%")
            
            speaker_segments = self.speaker_recognizer.recognize_speakers(audio_path, speaker_progress_callback)
            if not speaker_segments:
                logger.warning("No speaker segments found, falling back to full transcription")
                return self._fallback_full_transcription(audio_path, progress_callback)
            
            logger.info(f"Found {len(speaker_segments)} speaker segments")
            update_progress(20, f"Найдено {len(speaker_segments)} сегментов спикеров")

            # Шаг 2: Транскрибируем каждый сегмент отдельно (70% прогресса)
            logger.info("Step 2: Transcribing individual segments")
            update_progress(25, "Транскрибируем сегменты")
            
            transcribed_segments = []
            total_segments = len(speaker_segments)
            
            for i, segment in enumerate(speaker_segments):
                segment_progress = 25 + (i / total_segments) * 70  # от 25% до 95%
                update_progress(segment_progress, f"Сегмент {i+1}/{total_segments}")
                
                try:
                    # Извлекаем сегмент аудио
                    segment_audio_path = self._extract_audio_segment(
                        audio_path, 
                        segment['start'], 
                        segment['end']
                    )
                    
                    # Транскрибируем сегмент
                    segment_text = self.speech_recognizer.recognize(segment_audio_path)
                    
                    # Очищаем временный файл
                    if os.path.exists(segment_audio_path):
                        os.remove(segment_audio_path)
                    
                    # Добавляем результат
                    transcribed_segments.append({
                        'speaker': segment['speaker'],
                        'start': segment['start'],
                        'end': segment['end'],
                        'text': segment_text.strip()
                    })
                    
                    logger.info(f"Segment {i+1}: {segment['speaker']} ({segment['start']:.2f}s - {segment['end']:.2f}s) - {len(segment_text)} chars")
                    
                except Exception as e:
                    logger.error(f"Error processing segment {i+1}: {str(e)}")
                    # Добавляем пустой сегмент в случае ошибки
                    transcribed_segments.append({
                        'speaker': segment['speaker'],
                        'start': segment['start'],
                        'end': segment['end'],
                        'text': "[Ошибка транскрибации]"
                    })

            # Шаг 3: Форматируем результат (5% прогресса)
            logger.info("Step 3: Formatting results")
            update_progress(95, "Форматируем результат")
            
            final_result = self._format_results(transcribed_segments)
            
            update_progress(100, "Обработка завершена")
            logger.info("Speaker-first transcription completed successfully")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in speaker-first transcription: {str(e)}", exc_info=True)
            raise
    
    def _extract_audio_segment(self, audio_path, start_time, end_time):
        """
        Извлекает сегмент аудио из основного файла
        """
        try:
            # Создаем временный файл для сегмента
            temp_dir = tempfile.gettempdir()
            segment_filename = f"segment_{start_time:.2f}_{end_time:.2f}.wav"
            segment_path = os.path.join(temp_dir, segment_filename)
            
            # Извлекаем сегмент с помощью ffmpeg
            duration = end_time - start_time
            self.audio_processor.extract_segment(audio_path, segment_path, start_time, duration)
            
            return segment_path
            
        except Exception as e:
            logger.error(f"Error extracting audio segment: {str(e)}")
            raise
    
    def _format_results(self, transcribed_segments):
        """
        Форматирует результаты в читаемый вид
        """
        try:
            result_lines = []
            
            for segment in transcribed_segments:
                # Форматируем время начала
                start_time = self._format_timestamp(segment['start'])
                
                # Обрабатываем текст сегмента
                segment_text = segment['text']
                if segment_text:
                    # Разбиваем на строки если есть переносы
                    lines = segment_text.split('\n')
                    for line in lines:
                        if line.strip():  # Пропускаем пустые строки
                            result_lines.append(f"{start_time} [{segment['speaker']}] {line.strip()}")
                else:
                    # Если текст пустой, добавляем метку
                    result_lines.append(f"{start_time} [{segment['speaker']}] [Без речи]")
            
            return '\n'.join(result_lines)
            
        except Exception as e:
            logger.error(f"Error formatting results: {str(e)}")
            raise
    
    def _format_timestamp(self, seconds):
        """
        Форматирует время в [HH:MM:SS]
        """
        import datetime
        return datetime.datetime.utcfromtimestamp(seconds).strftime('[%H:%M:%S]')
    
    def _fallback_full_transcription(self, audio_path, progress_callback):
        """
        Fallback к полной транскрибации если не удалось определить спикеров
        """
        logger.info("Using fallback full transcription")
        if progress_callback:
            progress_callback(50)
        
        # Используем обычную транскрибацию
        text = self.speech_recognizer.recognize(audio_path, progress_callback)
        
        if progress_callback:
            progress_callback(100)
        
        return text 