import pytest
from app.speech_recognizer import SpeechRecognizer
import wave
import numpy as np

@pytest.fixture
def speech_recognizer():
    return SpeechRecognizer()

def test_recognize_empty_audio(speech_recognizer, tmp_path):
    # Создаем пустой WAV файл
    test_wav = tmp_path / "empty.wav"
    with wave.open(str(test_wav), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(np.zeros(16000, dtype=np.int16).tobytes())
    
    result = speech_recognizer.recognize(str(test_wav))
    assert isinstance(result, str) 