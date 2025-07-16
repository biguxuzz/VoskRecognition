import os
import logging
import time
from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from app.audio_processor import AudioProcessor
from app.speech_recognizer import SpeechRecognizer
from app.config import Config
import uuid
from .speaker_first_transcription_manager import SpeakerFirstTranscriptionManager
import threading

# Настраиваем логирование
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
           template_folder='templates',  
           static_folder='static')       
app.config.from_object(Config)

audio_processor = AudioProcessor()
speech_recognizer = SpeechRecognizer()

# Словарь для хранения результатов
processing_results = {}

# Добавим словарь для хранения статуса задач
tasks_status = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    try:
        logger.info('Rendering index page')
        return render_template('index.html')
    except Exception as e:
        logger.error(f'Error rendering index: {str(e)}')
        return str(e), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        logger.info('Processing file upload')
        
        if 'file' not in request.files:
            logger.warning('No file in request')
            return jsonify({'error': 'Файл не найден'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning('Empty filename')
            return jsonify({'error': 'Файл не выбран'}), 400
        
        if file and allowed_file(file.filename):
            # Проверяем размер файла
            file.seek(0, 2)  # Перемещаемся в конец файла
            file_size = file.tell()  # Получаем размер
            file.seek(0)  # Возвращаемся в начало
            
            max_size = app.config['MAX_CONTENT_LENGTH']
            if file_size > max_size:
                logger.warning(f'File too large: {file_size} bytes (max: {max_size})')
                return jsonify({
                    'error': f'Файл слишком большой. Размер: {file_size / (1024*1024):.1f}MB, Максимум: {max_size / (1024*1024):.1f}MB'
                }), 413
            
            # Добавляем уникальный идентификатор к имени файла
            unique_id = str(uuid.uuid4())
            original_filename = secure_filename(file.filename)
            filename = f"{unique_id}_{original_filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Проверяем существование директории
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                logger.error(f'Upload directory does not exist: {app.config["UPLOAD_FOLDER"]}')
                os.makedirs(app.config['UPLOAD_FOLDER'])
                logger.info(f'Created upload directory: {app.config["UPLOAD_FOLDER"]}')
            
            logger.info(f'Saving file to {filepath}')
            file.save(filepath)
            
            # Проверяем, что файл действительно сохранен
            if not os.path.exists(filepath):
                logger.error(f'File was not saved successfully: {filepath}')
                return jsonify({'error': 'Ошибка сохранения файла'}), 500
            
            # Конвертируем в WAV если нужно
            if not filename.endswith('.wav'):
                logger.info(f'Converting {filepath} to WAV')
                try:
                    wav_path = audio_processor.convert_to_wav(filepath)
                    logger.info(f'Successfully converted to WAV: {wav_path}')
                    
                    # Проверяем, что WAV файл создан
                    if not os.path.exists(wav_path):
                        logger.error(f'WAV file was not created: {wav_path}')
                        return jsonify({'error': 'Ошибка конвертации в WAV'}), 500
                    
                    # Удаляем оригинальный файл только после успешной конвертации
                    os.remove(filepath)
                    logger.info(f'Removed original file: {filepath}')
                    filename = os.path.basename(wav_path)
                except Exception as e:
                    logger.error(f'Error during WAV conversion: {str(e)}')
                    # Пытаемся очистить файлы в случае ошибки
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    if os.path.exists(wav_path):
                        os.remove(wav_path)
                    return jsonify({'error': f'Ошибка конвертации: {str(e)}'}), 500
            
            logger.info(f'File processing completed successfully: {filename}')
            return jsonify({
                'message': 'Файл успешно загружен',
                'filename': filename
            })
        
        logger.warning('Invalid file type')
        return jsonify({'error': 'Недопустимый формат файла'}), 400
        
    except Exception as e:
        logger.error(f'Error in upload_file: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        logger.info('Starting recognition process')
        data = request.get_json()
        
        # Логируем полученные данные
        logger.info(f'Received data: {data}')
        
        if not data:
            logger.warning('Request body is empty')
            return jsonify({'error': 'Тело запроса пусто'}), 400
            
        # "Тихо" игнорируем запросы в старом формате (автоматические)
        # Возвращаем "успех" без реальной обработки
        if 'filename' in data and 'files' not in data:
            logger.info('Ignoring automatic recognition request (old format)')
            return jsonify({'message': 'Получено', 'task_id': 'none'}), 200
            
        if 'files' not in data:
            logger.warning(f'No files in request. Available keys: {list(data.keys())}')
            return jsonify({'error': 'Файлы не указаны'}), 400
            
        files = data['files']
        logger.info(f'Files to process: {files}')
        
        if not files:
            logger.warning('Empty files list')
            return jsonify({'error': 'Список файлов пуст'}), 400

        # Проверяем существование файлов
        for filename in files:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(filepath):
                logger.error(f'File not found: {filepath}')
                return jsonify({'error': f'Файл не найден: {filename}'}), 404
            logger.info(f'File exists: {filepath}')

        # Создаем ID задачи
        task_id = str(uuid.uuid4())
        tasks_status[task_id] = {
            'progress': 0,
            'status': 'processing',
            'current_file': 0,
            'total_files': len(files),
            'created_at': time.time(),
            'last_update': time.time()
        }
        logger.info(f'Created task {task_id} for {len(files)} files')

        def process_files():
            try:
                logger.info(f'Starting background processing for task {task_id}')
                
                # Собираем полные пути к файлам
                file_paths = [os.path.join(app.config['UPLOAD_FOLDER'], filename) for filename in files]
                logger.info(f'File paths: {file_paths}')
                
                # Создаем имя для объединенного файла
                merged_filename = f'merged_{uuid.uuid4()}.wav'
                merged_path = os.path.join(app.config['UPLOAD_FOLDER'], merged_filename)
                logger.info(f'Will merge files into: {merged_path}')
                
                # Объединяем файлы
                logger.info(f'Merging {len(file_paths)} files into {merged_path}')
                audio_processor.merge_wav_files(file_paths, merged_path)
                
                # Проверяем, что файл создан
                if not os.path.exists(merged_path):
                    raise Exception('Ошибка создания объединенного файла')
                
                logger.info('Files merged successfully')
                
                # Обновляем прогресс
                tasks_status[task_id]['progress'] = 20  # 20% за объединение файлов
                
                # Распознаем речь
                logger.info('Starting transcription of merged file')
                transcription_manager = SpeakerFirstTranscriptionManager()
                
                def update_progress(progress):
                    # Корректируем прогресс: 20% за объединение + 80% за распознавание
                    adjusted_progress = 20 + int(progress * 0.8)
                    tasks_status[task_id]['progress'] = adjusted_progress
                    tasks_status[task_id]['last_update'] = time.time()
                    logger.info(f'Task {task_id} progress: {adjusted_progress}% (raw: {progress}%)')
                
                text = transcription_manager.process_audio(merged_path, update_progress)
                
                # Сохраняем результат
                result_filename = f'result_{uuid.uuid4()}.txt'
                result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
                
                logger.info(f'Creating result file: {result_path}')
                
                # Проверяем существование директории результатов
                if not os.path.exists(app.config['RESULT_FOLDER']):
                    logger.info(f'Creating results directory: {app.config["RESULT_FOLDER"]}')
                    os.makedirs(app.config['RESULT_FOLDER'])
                
                with open(result_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                    
                # Проверяем, что файл создан
                if not os.path.exists(result_path):
                    logger.error(f'Failed to create result file: {result_path}')
                    raise Exception('Ошибка создания файла результата')
                    
                logger.info(f'Result file created successfully: {result_path}')

                # Удаляем временные файлы
                os.remove(merged_path)
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        os.remove(file_path)

                # Обновляем статус задачи
                logger.info(f'Updating task status with result file: {result_filename}')
                tasks_status[task_id].update({
                    'status': 'completed',
                    'result_file': result_filename
                })
                logger.info(f'Task status updated: {tasks_status[task_id]}')
                
            except Exception as e:
                logger.error(f'Error in process_files: {str(e)}')
                tasks_status[task_id].update({
                    'status': 'error',
                    'error': str(e)
                })

        # Запускаем обработку в отдельном потоке
        thread = threading.Thread(target=process_files)
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'message': 'Обработка начата'
        })
        
    except Exception as e:
        logger.error(f'Error in recognize: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/status/<task_id>')
def get_status(task_id):
    """Получение статуса обработки"""
    logger.info(f'Status request for task {task_id}')
    
    if task_id not in tasks_status:
        logger.warning(f'Task {task_id} not found in tasks_status')
        return jsonify({'error': 'Задача не найдена'}), 404
    
    status = tasks_status[task_id]
    logger.info(f'Task {task_id} status: {status}')
    return jsonify(status)

@app.route('/tasks')
def get_all_tasks():
    """Получение списка всех задач"""
    logger.info('Request for all tasks')
    
    tasks_list = []
    for task_id, status in tasks_status.items():
        task_info = {
            'task_id': task_id,
            'status': status.get('status', 'unknown'),
            'progress': status.get('progress', 0),
            'total_files': status.get('total_files', 0),
            'current_file': status.get('current_file', 0)
        }
        
        # Добавляем время последнего обновления
        if 'last_update' not in status:
            status['last_update'] = time.time()
        task_info['last_update'] = status['last_update']
        
        tasks_list.append(task_info)
    
    logger.info(f'Returning {len(tasks_list)} tasks')
    return jsonify(tasks_list)

@app.route('/cancel/<task_id>', methods=['POST'])
def cancel_task(task_id):
    """Отмена задачи"""
    logger.info(f'Cancel request for task {task_id}')
    
    if task_id not in tasks_status:
        logger.warning(f'Task {task_id} not found in tasks_status')
        return jsonify({'error': 'Задача не найдена'}), 404
    
    current_status = tasks_status[task_id]
    if current_status.get('status') in ['completed', 'error']:
        logger.warning(f'Task {task_id} is already {current_status["status"]}')
        return jsonify({'error': f'Задача уже {current_status["status"]}'}), 400
    
    # Помечаем задачу как отмененную
    tasks_status[task_id].update({
        'status': 'cancelled',
        'error': 'Задача отменена пользователем',
        'last_update': time.time()
    })
    
    logger.info(f'Task {task_id} cancelled successfully')
    return jsonify({'message': 'Задача отменена'})

@app.route('/download/<filename>')
def download_result(filename):
    try:
        logger.info(f'Attempting to download result file: {filename}')
        
        if not filename or filename == 'null':
            logger.error('Invalid filename provided')
            return jsonify({'error': 'Некорректное имя файла'}), 400
            
        result_path = os.path.join(app.config['RESULT_FOLDER'], filename)
        logger.info(f'Full path to result file: {result_path}')
        
        if not os.path.exists(result_path):
            logger.error(f'Result file not found: {result_path}')
            return jsonify({'error': 'Результат не найден'}), 404
            
        logger.info(f'File exists, sending: {result_path}')
        return send_file(
            result_path,
            as_attachment=True,
            download_name='transcription.txt'
        )
    except Exception as e:
        logger.error(f'Error in download_result: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Обработчик ошибки превышения размера файла"""
    logger.warning(f'File too large error: {str(e)}')
    return jsonify({
        'error': 'Файл слишком большой. Максимальный размер: 1GB'
    }), 413

if __name__ == '__main__':
    logger.info('Starting Flask application')
    app.run(host='0.0.0.0', debug=True) 