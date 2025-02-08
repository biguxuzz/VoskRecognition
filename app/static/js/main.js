class SpeechRecognitionApp {
    constructor() {
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('fileInput');
        this.uploadForm = document.getElementById('uploadForm');
        this.progressContainer = document.querySelector('.progress-container');
        this.resultContainer = document.querySelector('.result-container');
        this.progressFill = document.querySelector('.progress-fill');
        this.statusText = document.querySelector('.status-text');
        this.downloadButton = document.getElementById('downloadButton');
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Drag and drop события
        this.dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.dropZone.classList.add('dragover');
        });

        this.dropZone.addEventListener('dragleave', () => {
            this.dropZone.classList.remove('dragover');
        });

        this.dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length) {
                this.handleFileUpload(files[0]);
            }
        });

        // Клик по зоне загрузки
        this.dropZone.addEventListener('click', () => {
            this.fileInput.click();
        });

        // Выбор файла через input
        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Кнопка скачивания
        this.downloadButton.addEventListener('click', () => {
            this.downloadResult();
        });
    }

    async handleFileUpload(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            // Показываем прогресс
            this.showProgress();
            this.updateProgress('convert', 'Загрузка файла...');

            // Загружаем файл
            const uploadResponse = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) {
                throw new Error('Ошибка загрузки файла');
            }

            const uploadResult = await uploadResponse.json();
            
            // Начинаем распознавание
            this.updateProgress('recognize', 'Распознавание речи...');
            
            const recognizeResponse = await fetch('/recognize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: uploadResult.filename
                })
            });

            if (!recognizeResponse.ok) {
                throw new Error('Ошибка распознавания');
            }

            const recognizeResult = await recognizeResponse.json();
            
            // Показываем результат
            this.updateProgress('complete', 'Готово!');
            this.showResult(recognizeResult.result_file);

        } catch (error) {
            this.showError(error.message);
        }
    }

    showProgress() {
        this.dropZone.style.display = 'none';
        this.progressContainer.style.display = 'block';
        this.resultContainer.style.display = 'none';
    }

    updateProgress(step, text) {
        const steps = ['convert', 'split', 'recognize', 'complete'];
        const currentIndex = steps.indexOf(step);
        
        // Обновляем прогресс-бар
        const progress = (currentIndex + 1) / steps.length * 100;
        this.progressFill.style.width = `${progress}%`;
        
        // Обновляем текст статуса
        this.statusText.textContent = text;
        
        // Обновляем статусы шагов
        steps.forEach((s, index) => {
            const stepElement = document.querySelector(`[data-step="${s}"]`);
            if (index < currentIndex) {
                stepElement.classList.add('complete');
                stepElement.classList.remove('active');
            } else if (index === currentIndex) {
                stepElement.classList.add('active');
                stepElement.classList.remove('complete');
            } else {
                stepElement.classList.remove('active', 'complete');
            }
        });
    }

    showResult(filename) {
        this.progressContainer.style.display = 'none';
        this.resultContainer.style.display = 'block';
        this.downloadButton.setAttribute('data-filename', filename);
    }

    showError(message) {
        this.statusText.textContent = `Ошибка: ${message}`;
        this.statusText.style.color = 'var(--error-color)';
    }

    async downloadResult() {
        const filename = this.downloadButton.getAttribute('data-filename');
        window.location.href = `/download/${filename}`;
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    new SpeechRecognitionApp();
}); 