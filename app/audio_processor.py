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