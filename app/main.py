import os
import logging
from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from app.audio_processor import AudioProcessor
from app.speech_recognizer import SpeechRecognizer
from app.config import Config
import uuid
from .transcription_manager import TranscriptionManager
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
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            logger.info(f'Saving file to {filepath}')
            file.save(filepath)
            
            logger.info('File saved successfully')
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
        
        if not data or 'filename' not in data:
            logger.warning('No filename in request')
            return jsonify({'error': 'Имя файла не указано'}), 400
            
        filename = data['filename']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            logger.warning(f'File not found: {filepath}')
            return jsonify({'error': 'Файл не найден'}), 404

        # Создаем ID задачи
        task_id = str(uuid.uuid4())
        tasks_status[task_id] = {
            'progress': 0,
            'status': 'processing'
        }

        def process_audio():
            try:
                # Конвертируем в WAV если нужно
                logger.info('Converting to WAV')
                wav_path = audio_processor.convert_to_wav(filepath)
                
                # Обновляем прогресс
                def update_progress(progress):
                    tasks_status[task_id]['progress'] = progress

                # Распознаем речь и спикеров
                logger.info('Starting transcription')
                transcription_manager = TranscriptionManager()
                text = transcription_manager.process_audio(wav_path, update_progress)
                
                # Сохраняем результат
                result_path = os.path.join(
                    app.config['RESULT_FOLDER'],
                    f'result_{os.path.splitext(filename)[0]}.txt'
                )
                
                logger.info(f'Saving result to {result_path}')
                with open(result_path, 'w', encoding='utf-8') as f:
                    f.write(text)

                # Обновляем статус задачи
                tasks_status[task_id].update({
                    'status': 'completed',
                    'result_file': os.path.basename(result_path)
                })
                
            except Exception as e:
                logger.error(f'Error in process_audio: {str(e)}')
                tasks_status[task_id].update({
                    'status': 'error',
                    'error': str(e)
                })

        # Запускаем обработку в отдельном потоке
        thread = threading.Thread(target=process_audio)
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
    if task_id not in tasks_status:
        return jsonify({'error': 'Задача не найдена'}), 404
    
    return jsonify(tasks_status[task_id])

@app.route('/download/<filename>')
def download_result(filename):
    try:
        result_path = os.path.join(app.config['RESULT_FOLDER'], filename)
        if os.path.exists(result_path):
            return send_file(
                result_path,
                as_attachment=True,
                download_name='transcription.txt'
            )
        return jsonify({'error': 'Результат не найден'}), 404
    except Exception as e:
        logger.error(f'Error in download_result: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info('Starting Flask application')
    app.run(host='0.0.0.0', debug=True) 