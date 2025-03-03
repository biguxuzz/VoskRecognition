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
        
        this.currentTaskId = null;
        this.progressCheckInterval = null;
        
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
            // Показываем прогресс-бар
            this.dropZone.style.display = 'none';
            this.progressContainer.style.display = 'block';
            this.updateProgress(0);
            
            // Загрузка файла
            const formData = new FormData();
            formData.append('file', file);
            
            const uploadResponse = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!uploadResponse.ok) throw new Error('Ошибка загрузки файла');
            
            const uploadResult = await uploadResponse.json();
            
            // Начинаем распознавание
            const recognizeResponse = await fetch('/recognize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: uploadResult.filename
                })
            });
            
            if (!recognizeResponse.ok) throw new Error('Ошибка распознавания');
            
            const recognizeResult = await recognizeResponse.json();
            this.currentTaskId = recognizeResult.task_id;
            
            // Запускаем проверку прогресса
            this.startProgressCheck();
            
        } catch (error) {
            this.showError(error.message);
        }
    }

    startProgressCheck() {
        if (this.progressCheckInterval) {
            clearInterval(this.progressCheckInterval);
        }
        
        this.progressCheckInterval = setInterval(async () => {
            try {
                const response = await fetch(`/status/${this.currentTaskId}`);
                if (!response.ok) throw new Error('Ошибка получения статуса');
                
                const status = await response.json();
                
                // Обновляем прогресс
                if (status.progress !== undefined) {
                    this.updateProgress(status.progress);
                    console.log(`Progress updated: ${status.progress}%`);
                }
                
                // Проверяем завершение
                if (status.status === 'completed') {
                    clearInterval(this.progressCheckInterval);
                    this.showResult(status.result_file);
                    console.log('Processing completed');
                } else if (status.status === 'error') {
                    clearInterval(this.progressCheckInterval);
                    this.showError(status.error);
                    console.error('Processing error:', status.error);
                }
                
            } catch (error) {
                clearInterval(this.progressCheckInterval);
                this.showError(error.message);
                console.error('Progress check error:', error);
            }
        }, 500);  // Проверяем каждые 500мс вместо 1000мс
    }

    updateProgress(progress) {
        this.progressFill.style.width = `${progress}%`;
        this.statusText.textContent = `Обработано ${Math.round(progress)}%`;
        
        // Обновляем статус шагов
        const steps = document.querySelectorAll('.step');
        const currentStep = Math.floor(progress / 25);  // 4 шага по 25%
        
        steps.forEach((step, index) => {
            if (index < currentStep) {
                step.classList.add('complete');
                step.classList.remove('active');
            } else if (index === currentStep) {
                step.classList.add('active');
                step.classList.remove('complete');
            } else {
                step.classList.remove('active', 'complete');
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