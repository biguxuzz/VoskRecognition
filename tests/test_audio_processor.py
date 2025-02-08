import pytest
import os
from app.audio_processor import AudioProcessor

@pytest.fixture
def audio_processor():
    return AudioProcessor()

def test_convert_wav_file(audio_processor, tmp_path):
    # Создаем тестовый WAV файл
    test_wav = tmp_path / "test.wav"
    test_wav.write_bytes(b'RIFF' + b'\x00' * 100)
    
    result = audio_processor.convert_to_wav(str(test_wav))
    assert result == str(test_wav)

def test_convert_mp3_file(audio_processor, tmp_path):
    # Создаем тестовый MP3 файл
    test_mp3 = tmp_path / "test.mp3"
    test_mp3.write_bytes(b'ID3' + b'\x00' * 100)
    
    result = audio_processor.convert_to_wav(str(test_mp3))
    assert result.endswith('.wav')
    assert os.path.exists(result) 