#!/usr/bin/env python3
"""
Скрипт для тестирования и мониторинга прогресса обработки
"""

import requests
import time
import json
import sys

def check_task_status(task_id, base_url="http://localhost:5000"):
    """Проверяет статус задачи"""
    try:
        response = requests.get(f"{base_url}/status/{task_id}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка получения статуса: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return None

def cancel_task(task_id, base_url="http://localhost:5000"):
    """Отменяет задачу"""
    try:
        response = requests.post(f"{base_url}/cancel/{task_id}")
        if response.status_code == 200:
            print("✅ Задача отменена успешно")
            return True
        else:
            print(f"❌ Ошибка отмены задачи: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка запроса отмены: {e}")
        return False

def monitor_task(task_id, base_url="http://localhost:5000", interval=10):
    """Мониторит задачу с заданным интервалом"""
    print(f"Мониторинг задачи {task_id}")
    print("=" * 50)
    print("Нажмите Ctrl+C для отмены задачи")
    print()
    
    start_time = time.time()
    last_progress = -1
    last_progress_time = start_time
    
    try:
        while True:
            status = check_task_status(task_id, base_url)
            
            if status is None:
                print("Не удалось получить статус задачи")
                time.sleep(interval)
                continue
            
            current_time = time.time()
            elapsed = current_time - start_time
            
            print(f"[{time.strftime('%H:%M:%S')}] Прошло времени: {elapsed:.1f}с")
            print(f"Статус: {status.get('status', 'unknown')}")
            print(f"Прогресс: {status.get('progress', 0)}%")
            
            if 'current_file' in status and 'total_files' in status:
                print(f"Файлы: {status['current_file']}/{status['total_files']}")
            
            if 'error' in status:
                print(f"Ошибка: {status['error']}")
                break
            
            if status.get('status') == 'completed':
                print("✅ Задача завершена!")
                if 'result_file' in status:
                    print(f"Результат: {status['result_file']}")
                break
            
            if status.get('status') == 'error':
                print("❌ Задача завершилась с ошибкой!")
                break
            
            if status.get('status') == 'cancelled':
                print("🚫 Задача отменена!")
                break
            
            # Проверяем, изменился ли прогресс
            current_progress = status.get('progress', 0)
            if current_progress != last_progress:
                print(f"🔄 Прогресс изменился: {last_progress}% → {current_progress}%")
                last_progress = current_progress
                last_progress_time = current_time
            else:
                # Проверяем, не завис ли прогресс
                time_since_progress = current_time - last_progress_time
                if time_since_progress > 300:  # 5 минут без прогресса
                    print(f"⚠️  Внимание: прогресс не менялся {time_since_progress:.1f} секунд")
            
            print("-" * 30)
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал прерывания")
        print("Отменяем задачу...")
        if cancel_task(task_id, base_url):
            print("Задача отменена. Выход из мониторинга.")
        else:
            print("Не удалось отменить задачу. Выход из мониторинга.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python test_progress.py <task_id> [base_url] [interval]")
        print("Пример: python test_progress.py 9b60dfea-4dc0-4030-99d3-1f0c534e7217")
        sys.exit(1)
    
    task_id = sys.argv[1]
    base_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5000"
    interval = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    monitor_task(task_id, base_url, interval) 