from vosk import Model, KaldiRecognizer
from .model_manager import ModelManager
import json
import wave

class SpeechRecognizer:
    def __init__(self):
        model_path = ModelManager.ensure_model_exists()
        self.model = Model(model_path)
    
    def recognize(self, wav_path):
        """Распознает речь из WAV файла"""
        result_text = []
        
        with wave.open(wav_path, 'rb') as wf:
            recognizer = KaldiRecognizer(self.model, wf.getframerate())
            
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if result['text']:
                        result_text.append(result['text'])
        
        # Получаем последний результат
        final_result = json.loads(recognizer.FinalResult())
        if final_result['text']:
            result_text.append(final_result['text'])
        
        return '\n'.join(result_text) 