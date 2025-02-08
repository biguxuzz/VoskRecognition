import os
from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from .audio_processor import AudioProcessor
from .speech_recognizer import SpeechRecognizer
from .config import Config

app = Flask(__name__, 
           template_folder='templates',  # Путь к шаблонам
           static_folder='static')       # Путь к статическим файлам
app.config.from_object(Config)

audio_processor = AudioProcessor()
speech_recognizer = SpeechRecognizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'message': 'Файл успешно загружен',
            'filename': filename
        })
    
    return jsonify({'error': 'Недопустимый формат файла'}), 400

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    filename = request.json.get('filename')
    if not filename:
        return jsonify({'error': 'Имя файла не указано'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Конвертация файла если необходимо
    wav_path = audio_processor.convert_to_wav(filepath)
    
    # Распознавание речи
    text = speech_recognizer.recognize(wav_path)
    
    # Сохранение результата
    result_path = os.path.join(
        app.config['RESULT_FOLDER'],
        f"{os.path.splitext(filename)[0]}.txt"
    )
    
    with open(result_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return jsonify({
        'message': 'Распознавание завершено',
        'result_file': os.path.basename(result_path)
    })

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(
        os.path.join(app.config['RESULT_FOLDER'], filename),
        as_attachment=True
    )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 