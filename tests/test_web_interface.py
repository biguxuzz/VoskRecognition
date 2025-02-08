import pytest
from app.main import app
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'html' in response.data

def test_upload_no_file(client):
    response = client.post('/upload')
    assert response.status_code == 400
    assert b'error' in response.data

def test_upload_valid_file(client, tmp_path):
    test_wav = tmp_path / "test.wav"
    test_wav.write_bytes(b'RIFF' + b'\x00' * 100)
    
    with open(str(test_wav), 'rb') as f:
        response = client.post(
            '/upload',
            data={'file': (f, 'test.wav')}
        )
    assert response.status_code == 200
    assert b'filename' in response.data 