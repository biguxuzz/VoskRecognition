#!/usr/bin/env python3
"""
Скрипт для тестирования загрузки файлов разных размеров
"""

import requests
import os
import tempfile
import time

def create_test_file(size_mb, filename="test_audio.wav"):
    """Создает тестовый файл указанного размера"""
    size_bytes = size_mb * 1024 * 1024
    
    # Создаем временный файл
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)
    
    # Создаем файл с нулями (имитация аудио)
    with open(filepath, 'wb') as f:
        f.write(b'\x00' * size_bytes)
    
    return filepath

def test_upload(filepath, base_url="http://localhost:5000"):
    """Тестирует загрузку файла"""
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    
    print(f"Тестируем загрузку файла: {filename}")
    print(f"Размер: {file_size / (1024*1024):.1f}MB")
    
    try:
        with open(filepath, 'rb') as f:
            files = {'file': (filename, f, 'audio/wav')}
            
            start_time = time.time()
            response = requests.post(f"{base_url}/upload", files=files)
            upload_time = time.time() - start_time
            
            print(f"Статус ответа: {response.status_code}")
            print(f"Время загрузки: {upload_time:.2f} секунд")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Успешно: {data.get('message', 'OK')}")
                return True
            elif response.status_code == 413:
                print("❌ Ошибка 413: Файл слишком большой")
                try:
                    error_data = response.json()
                    print(f"Сообщение сервера: {error_data.get('error', 'Unknown error')}")
                except:
                    print("Не удалось получить детали ошибки")
                return False
            else:
                print(f"❌ Ошибка {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Сообщение сервера: {error_data.get('error', 'Unknown error')}")
                except:
                    print("Не удалось получить детали ошибки")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка при загрузке: {str(e)}")
        return False

def main():
    """Основная функция тестирования"""
    print("Тестирование загрузки файлов разных размеров")
    print("=" * 50)
    
    # Тестируем файлы разных размеров
    test_sizes = [1, 10, 50, 100, 500, 1000]  # MB
    
    for size_mb in test_sizes:
        print(f"\n--- Тест {size_mb}MB ---")
        filepath = create_test_file(size_mb, f"test_{size_mb}mb.wav")
        
        success = test_upload(filepath)
        
        # Очищаем временный файл
        try:
            os.remove(filepath)
        except:
            pass
        
        if not success:
            print(f"❌ Загрузка файла {size_mb}MB не удалась")
            break
        else:
            print(f"✅ Загрузка файла {size_mb}MB успешна")
        
        # Небольшая пауза между тестами
        time.sleep(1)
    
    print("\nТестирование завершено")

if __name__ == "__main__":
    main() 