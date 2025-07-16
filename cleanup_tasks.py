#!/usr/bin/env python3
"""
Скрипт для очистки зависших задач
"""

import requests
import time
import json
import sys

def get_all_tasks(base_url="http://localhost:5000"):
    """Получает список всех задач (если есть такой endpoint)"""
    try:
        # Попробуем получить список задач
        response = requests.get(f"{base_url}/tasks")
        if response.status_code == 200:
            return response.json()
        else:
            print("Endpoint /tasks не найден, попробуем другой способ")
            return None
    except:
        return None

def check_task_status(task_id, base_url="http://localhost:5000"):
    """Проверяет статус задачи"""
    try:
        response = requests.get(f"{base_url}/status/{task_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def cancel_task(task_id, base_url="http://localhost:5000"):
    """Отменяет задачу"""
    try:
        response = requests.post(f"{base_url}/cancel/{task_id}")
        return response.status_code == 200
    except:
        return False

def cleanup_stuck_tasks(base_url="http://localhost:5000", timeout_minutes=30):
    """Очищает зависшие задачи"""
    print(f"Поиск зависших задач (таймаут: {timeout_minutes} минут)")
    print("=" * 50)
    
    # Получаем список задач
    tasks = get_all_tasks(base_url)
    
    if tasks is None:
        print("Не удалось получить список задач автоматически")
        print("Пожалуйста, укажите ID задачи вручную:")
        task_id = input("ID задачи: ").strip()
        if task_id:
            tasks = [task_id]
        else:
            return
    
    stuck_tasks = []
    
    for task_id in tasks:
        print(f"Проверяем задачу {task_id}...")
        status = check_task_status(task_id, base_url)
        
        if status is None:
            print(f"  ❌ Задача {task_id} не найдена")
            continue
        
        task_status = status.get('status', 'unknown')
        progress = status.get('progress', 0)
        
        print(f"  Статус: {task_status}, Прогресс: {progress}%")
        
        # Проверяем, зависла ли задача
        if task_status == 'processing':
            # Проверяем время последнего обновления (если есть)
            if 'last_update' in status:
                last_update = status['last_update']
                time_since_update = time.time() - last_update
                if time_since_update > timeout_minutes * 60:
                    stuck_tasks.append(task_id)
                    print(f"  ⚠️  Задача {task_id} зависла ({time_since_update/60:.1f} минут без обновления)")
            else:
                # Если нет времени обновления, считаем зависшей если прогресс 0
                if progress == 0:
                    stuck_tasks.append(task_id)
                    print(f"  ⚠️  Задача {task_id} может быть зависшей (прогресс 0%)")
    
    if not stuck_tasks:
        print("✅ Зависших задач не найдено")
        return
    
    print(f"\nНайдено {len(stuck_tasks)} зависших задач:")
    for task_id in stuck_tasks:
        print(f"  - {task_id}")
    
    response = input("\nОтменить эти задачи? (y/N): ").strip().lower()
    if response == 'y':
        print("Отменяем задачи...")
        for task_id in stuck_tasks:
            if cancel_task(task_id, base_url):
                print(f"  ✅ Задача {task_id} отменена")
            else:
                print(f"  ❌ Не удалось отменить задачу {task_id}")
    else:
        print("Отмена операций")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    cleanup_stuck_tasks(base_url, timeout) 