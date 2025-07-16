import os
import subprocess
import soundfile as sf
import numpy as np

class AudioProcessor:
    def convert_to_wav(self, input_path):
        """Конвертирует аудио/видео файл в WAV формат"""
        filename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(os.path.dirname(input_path), f"{filename}.wav")
        
        if input_path.endswith('.wav'):
            return input_path
            
        command = [
            'ffmpeg', '-i', input_path,
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y', output_path
        ]
        
        try:
            subprocess.run(command, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Ошибка конвертации файла: {e.stderr.decode()}")

    def merge_wav_files(self, input_files, output_path):
        """Объединяет несколько WAV файлов в один"""
        try:
            # Создаем временный файл со списком файлов для ffmpeg
            temp_list = output_path + '.txt'
            with open(temp_list, 'w', encoding='utf-8') as f:
                for file in input_files:
                    f.write(f"file '{file}'\n")

            # Используем ffmpeg для объединения файлов
            command = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', temp_list,
                '-c', 'copy',
                '-y', output_path
            ]

            subprocess.run(command, check=True, capture_output=True)
            
            # Удаляем временный файл
            os.remove(temp_list)
            
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Ошибка объединения файлов: {e.stderr.decode()}")
        except Exception as e:
            raise Exception(f"Ошибка при объединении файлов: {str(e)}")

    def extract_segment(self, input_path, output_path, start_time, duration):
        """
        Извлекает сегмент аудио из основного файла
        
        Args:
            input_path: путь к входному аудио файлу
            output_path: путь для сохранения сегмента
            start_time: время начала сегмента в секундах
            duration: длительность сегмента в секундах
        """
        try:
            command = [
                'ffmpeg', '-i', input_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y', output_path
            ]
            
            subprocess.run(command, check=True, capture_output=True)
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Ошибка извлечения сегмента: {e.stderr.decode()}")
        except Exception as e:
            raise Exception(f"Ошибка при извлечении сегмента: {str(e)}") 