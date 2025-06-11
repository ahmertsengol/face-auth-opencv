/**
 * Live Face Recognition - Full Screen Application
 */

// Application State
class LiveRecognitionApp {
    constructor() {
        this.isActive = false;
        this.videoStream = null;
        this.recognitionInterval = null;
        this.currentTheme = localStorage.getItem('live-theme') || 'light';
        this.settings = {
            recognitionInterval: 2000,
            confidenceThreshold: 0.6,
            showFPS: true,
            autoCapture: true
        };
        
        // Performance tracking
        this.stats = {
            facesDetected: 0,
            recognized: 0,
            processingTimes: [],
            fps: 0,
            lastFrameTime: 0
        };
        
        // DOM elements cache
        this.elements = {};
        
        // Load settings from localStorage
        this.loadSettings();
    }

    // Initialize the application
    async init() {
        this.cacheElements();
        this.initializeTheme();
        this.initializeEventListeners();
        this.updateConnectionStatus('ready');
        this.startPerformanceMonitor();
        
        console.log('🎥 Live Recognition App initialized');
    }

    // Cache DOM elements for performance
    cacheElements() {
        const selectors = {
            'video': '#live-video',
            'canvas': '#live-canvas',
            'overlay': '#video-overlay',
            'faceOverlay': '#face-overlay',
            'startStopBtn': '#start-stop-btn',
            'captureBtn': '#capture-btn',
            'statusIndicator': '#connection-status',
            'statusText': '#status-text',
            'resultsContent': '#results-content',
            'facesCount': '#faces-count',
            'recognizedCount': '#recognized-count',
            'processingSpeed': '#processing-speed',
            'fpsCounter': '#fps-counter',
            'latencyCounter': '#latency-counter',
            'performanceMonitor': '#performance-monitor',
            'settingsModal': '#settings-modal',
            'themeToggle': '#theme-toggle',
            'notifications': '#notifications'
        };

        for (const [key, selector] of Object.entries(selectors)) {
            this.elements[key] = document.querySelector(selector);
        }
    }

    // Initialize event listeners
    initializeEventListeners() {
        // Theme toggle
        if (this.elements.themeToggle) {
            this.elements.themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Settings modal controls
        this.initializeSettingsControls();

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    }

    // Initialize settings controls
    initializeSettingsControls() {
        const intervalSlider = document.getElementById('recognition-interval');
        const confidenceSlider = document.getElementById('confidence-threshold');
        const intervalValue = document.getElementById('interval-value');
        const confidenceValue = document.getElementById('confidence-value');
        const showFpsCheckbox = document.getElementById('show-fps');

        if (intervalSlider && intervalValue) {
            intervalSlider.value = this.settings.recognitionInterval;
            intervalValue.textContent = `${this.settings.recognitionInterval}ms`;
            
            intervalSlider.addEventListener('input', (e) => {
                this.settings.recognitionInterval = parseInt(e.target.value);
                intervalValue.textContent = `${this.settings.recognitionInterval}ms`;
            });
        }

        if (confidenceSlider && confidenceValue) {
            confidenceSlider.value = this.settings.confidenceThreshold;
            confidenceValue.textContent = `${Math.round(this.settings.confidenceThreshold * 100)}%`;
            
            confidenceSlider.addEventListener('input', (e) => {
                this.settings.confidenceThreshold = parseFloat(e.target.value);
                confidenceValue.textContent = `${Math.round(this.settings.confidenceThreshold * 100)}%`;
            });
        }

        if (showFpsCheckbox) {
            showFpsCheckbox.checked = this.settings.showFPS;
            showFpsCheckbox.addEventListener('change', (e) => {
                this.settings.showFPS = e.target.checked;
                this.togglePerformanceMonitor();
            });
        }
    }

    // Handle keyboard shortcuts
    handleKeyboardShortcuts(e) {
        switch (e.key) {
            case ' ':
                e.preventDefault();
                this.toggleRecognition();
                break;
            case 'c':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.captureFrame();
                }
                break;
            case 's':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.openSettings();
                }
                break;
            case 'Escape':
                this.closeSettings();
                break;
        }
    }

    // Theme management
    initializeTheme() {
        document.body.className = `${this.currentTheme}-theme live-recognition-page`;
        this.updateThemeIcon();
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        document.body.className = `${this.currentTheme}-theme live-recognition-page`;
        localStorage.setItem('live-theme', this.currentTheme);
        this.updateThemeIcon();
        this.showNotification(`Switched to ${this.currentTheme} theme`, 'info');
    }

    updateThemeIcon() {
        const themeIcon = this.elements.themeToggle?.querySelector('.theme-icon');
        if (themeIcon) {
            if (this.currentTheme === 'light') {
                themeIcon.innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>`;
            } else {
                themeIcon.innerHTML = `<circle cx="12" cy="12" r="5"/>
                    <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>`;
            }
        }
    }

    // Connection status management
    updateConnectionStatus(status) {
        const indicator = this.elements.statusIndicator;
        const text = this.elements.statusText;
        
        if (indicator) {
            indicator.className = 'status-indicator';
            indicator.classList.add(status === 'connected' ? 'connected' : 
                                   status === 'connecting' ? 'connecting' : 'disconnected');
        }
        
        if (text) {
            const statusTexts = {
                'ready': 'Ready',
                'connecting': 'Connecting...',
                'connected': 'Live',
                'disconnected': 'Disconnected',
                'error': 'Error'
            };
            text.textContent = statusTexts[status] || 'Unknown';
        }
    }

    // Recognition controls
    async toggleRecognition() {
        if (this.isActive) {
            await this.stopRecognition();
        } else {
            await this.startRecognition();
        }
    }

    async startRecognition() {
        try {
            this.updateConnectionStatus('connecting');
            this.showNotification('Starting camera...', 'info');

            // Get camera stream
            this.videoStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                }
            });

            // Setup video element
            const video = this.elements.video;
            if (video) {
                video.srcObject = this.videoStream;
                await new Promise(resolve => {
                    video.onloadedmetadata = resolve;
                });
            }

            // Setup canvas
            const canvas = this.elements.canvas;
            if (canvas && video) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            }

            // Hide overlay
            this.hideVideoOverlay();

            // Start recognition loop
            this.startRecognitionLoop();

            // Update UI
            this.isActive = true;
            this.updateStartStopButton();
            this.updateConnectionStatus('connected');
            this.enableCaptureButton();
            
            this.showNotification('Live recognition started', 'success');

        } catch (error) {
            console.error('Error starting recognition:', error);
            this.updateConnectionStatus('error');
            
            if (error.name === 'NotAllowedError') {
                this.showNotification('Camera access denied. Please allow camera access.', 'error');
            } else if (error.name === 'NotFoundError') {
                this.showNotification('No camera found on this device.', 'error');
            } else {
                this.showNotification('Failed to start camera: ' + error.message, 'error');
            }
        }
    }

    async stopRecognition() {
        // Stop video stream
        if (this.videoStream) {
            this.videoStream.getTracks().forEach(track => track.stop());
            this.videoStream = null;
        }

        // Stop recognition loop
        this.stopRecognitionLoop();

        // Clear video
        const video = this.elements.video;
        if (video) {
            video.srcObject = null;
        }

        // Show overlay
        this.showVideoOverlay();

        // Update UI
        this.isActive = false;
        this.updateStartStopButton();
        this.updateConnectionStatus('ready');
        this.disableCaptureButton();

        this.showNotification('Live recognition stopped', 'info');
    }

    startRecognitionLoop() {
        this.recognitionInterval = setInterval(async () => {
            if (this.isActive && this.elements.video && this.elements.video.readyState >= 2) {
                await this.processFrame();
            }
        }, this.settings.recognitionInterval);
    }

    stopRecognitionLoop() {
        if (this.recognitionInterval) {
            clearInterval(this.recognitionInterval);
            this.recognitionInterval = null;
        }
    }

    // Frame processing
    async processFrame() {
        const startTime = performance.now();
        
        try {
            const video = this.elements.video;
            const canvas = this.elements.canvas;
            
            if (!video || !canvas) return;

            // Draw frame to canvas
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Convert to base64
            const imageData = canvas.toDataURL('image/jpeg', 0.8);

            // Send to recognition API
            const response = await fetch('/api/recognize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image_data: imageData
                })
            });

            const result = await response.json();

            if (result.success) {
                this.processRecognitionResult(result);
                
                // Update performance stats
                const processingTime = performance.now() - startTime;
                this.updatePerformanceStats(processingTime, result.faces_detected, result.results.length);
            }

        } catch (error) {
            console.error('Frame processing error:', error);
        }
    }

    // Process recognition results
    processRecognitionResult(result) {
        // Update stats
        this.updateStatsDisplay(result.faces_detected, result.results.length);

        // Update results display
        this.updateResultsDisplay(result);
        
        // Handle audio alerts and notifications
        if (result.recognized && result.results.length > 0) {
            this.playAlert('recognition');
            
            // Desktop notification for recognized faces
            if (this.settings.desktopNotifications) {
                const names = result.results.map(r => r.name).join(', ');
                this.showDesktopNotification(
                    'Face Recognition',
                    `Recognized: ${names}`,
                    '/static/images/face-icon.png'
                );
            }
            
            // Auto-capture on recognition (Disabled - users can manually capture if needed)
            // if (this.settings.autoCaptureOnRecognition) {
            //     setTimeout(() => this.captureFrame(), 500); // Small delay for better UX
            // }
        } else if (result.faces_detected > 0) {
            // Unknown face detected
            this.playAlert('unknown');
            
            if (this.settings.unknownFaceAlert && this.settings.desktopNotifications) {
                this.showDesktopNotification(
                    'Unknown Face Detected',
                    `${result.faces_detected} unknown face(s) detected`,
                    '/static/images/unknown-icon.png'
                );
            }
        }
    }

    // UI Updates
    updateStartStopButton() {
        const btn = this.elements.startStopBtn;
        if (!btn) return;

        const svg = btn.querySelector('svg');
        const span = btn.querySelector('span');

        if (this.isActive) {
            // Stop icon
            svg.innerHTML = `<rect width="6" height="6" x="9" y="9"/>`;
            span.textContent = 'Stop Recognition';
            btn.classList.remove('primary');
            btn.classList.add('danger');
        } else {
            // Play icon
            svg.innerHTML = `<polygon points="5,3 19,12 5,21"/>`;
            span.textContent = 'Start Recognition';
            btn.classList.remove('danger');
            btn.classList.add('primary');
        }
    }

    enableCaptureButton() {
        if (this.elements.captureBtn) {
            this.elements.captureBtn.disabled = false;
        }
    }

    disableCaptureButton() {
        if (this.elements.captureBtn) {
            this.elements.captureBtn.disabled = true;
        }
    }

    hideVideoOverlay() {
        if (this.elements.overlay) {
            this.elements.overlay.classList.add('hidden');
        }
    }

    showVideoOverlay() {
        if (this.elements.overlay) {
            this.elements.overlay.classList.remove('hidden');
        }
    }

    updateStatsDisplay(facesDetected, recognized) {
        if (this.elements.facesCount) {
            this.elements.facesCount.textContent = facesDetected;
        }
        if (this.elements.recognizedCount) {
            this.elements.recognizedCount.textContent = recognized;
        }
    }

    updateResultsDisplay(result) {
        const resultsContent = this.elements.resultsContent;
        if (!resultsContent) return;

        if (!result.recognized || result.results.length === 0) {
            // Show no match result
            const noMatchHtml = `
                <div class="recognition-result no-match">
                    <div class="result-avatar unknown">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M15 9l-6 6"/>
                            <path d="M9 9l6 6"/>
                        </svg>
                    </div>
                    <div class="result-info">
                        <div class="result-name">No Match Found</div>
                        <div class="result-details">
                            <span>Faces: ${result.faces_detected}</span>
                        </div>
                    </div>
                    <div class="result-time">${new Date().toLocaleTimeString()}</div>
                </div>
            `;
            
            resultsContent.innerHTML = noMatchHtml + resultsContent.innerHTML;
        } else {
            // Show recognition results
            const resultsHtml = result.results.map(person => `
                <div class="recognition-result match">
                    <div class="result-avatar">
                        ${person.name.charAt(0).toUpperCase()}
                    </div>
                    <div class="result-info">
                        <div class="result-name">${this.escapeHtml(person.name)}</div>
                        <div class="result-details">
                            <span>Confidence: ${Math.round(person.confidence * 100)}%</span>
                            <span>Distance: ${person.distance.toFixed(3)}</span>
                        </div>
                    </div>
                    <div class="result-time">${new Date().toLocaleTimeString()}</div>
                </div>
            `).join('');
            
            resultsContent.innerHTML = resultsHtml + resultsContent.innerHTML;
        }

        // Keep only last 10 results
        const results = resultsContent.querySelectorAll('.recognition-result');
        if (results.length > 10) {
            for (let i = 10; i < results.length; i++) {
                results[i].remove();
            }
        }

        // Auto-scroll to top for new results
        resultsContent.scrollTop = 0;
    }

    // Performance monitoring
    startPerformanceMonitor() {
        setInterval(() => {
            this.updateFPSCounter();
        }, 1000);
    }

    updatePerformanceStats(processingTime, facesDetected, recognized) {
        this.stats.processingTimes.push(processingTime);
        if (this.stats.processingTimes.length > 10) {
            this.stats.processingTimes.shift();
        }

        this.stats.facesDetected = facesDetected;
        this.stats.recognized = recognized;

        // Update processing speed display
        const avgTime = this.stats.processingTimes.reduce((a, b) => a + b, 0) / this.stats.processingTimes.length;
        if (this.elements.processingSpeed) {
            this.elements.processingSpeed.textContent = `${Math.round(avgTime)}ms`;
        }

        // Update latency counter
        if (this.elements.latencyCounter) {
            this.elements.latencyCounter.textContent = `${Math.round(avgTime)}ms`;
        }
    }

    updateFPSCounter() {
        const now = performance.now();
        if (this.stats.lastFrameTime) {
            const fps = 1000 / (now - this.stats.lastFrameTime);
            this.stats.fps = fps;
            
            if (this.elements.fpsCounter) {
                this.elements.fpsCounter.textContent = Math.round(fps);
            }
        }
        this.stats.lastFrameTime = now;
    }

    togglePerformanceMonitor() {
        if (this.elements.performanceMonitor) {
            this.elements.performanceMonitor.classList.toggle('hidden', !this.settings.showFPS);
        }
    }

    // Frame capture
    captureFrame() {
        if (!this.isActive || !this.elements.video) {
            this.showNotification('Start recognition first', 'warning');
            return;
        }

        const video = this.elements.video;
        const canvas = this.elements.canvas;

        if (video && canvas) {
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Create download link
            canvas.toBlob((blob) => {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `live-capture-${new Date().getTime()}.jpg`;
                a.click();
                URL.revokeObjectURL(url);
            }, 'image/jpeg', 0.9);

            this.showNotification('Frame captured and downloaded', 'success');
        }
    }

    // Advanced Settings Management
    openSettings() {
        if (this.elements.settingsModal) {
            this.elements.settingsModal.classList.add('show');
            this.loadSettingsToUI();
        }
    }

    closeSettings() {
        if (this.elements.settingsModal) {
            this.elements.settingsModal.classList.remove('show');
        }
    }

    loadSettingsToUI() {
        // Camera Settings
        this.setUIValue('camera-resolution', this.settings.cameraResolution);
        this.setUIValue('frame-rate', this.settings.frameRate);
        this.setUIValue('camera-facing', this.settings.cameraFacing);
        this.setUIValue('mirror-video', this.settings.mirrorVideo);

        // Recognition Settings
        this.setUIValue('recognition-interval', this.settings.recognitionInterval);
        this.setUIValue('confidence-threshold', this.settings.confidenceThreshold);
        this.setUIValue('max-faces', this.settings.maxFaces);
        this.setUIValue('continuous-recognition', this.settings.continuousRecognition);
        this.setUIValue('save-unknown-faces', this.settings.saveUnknownFaces);

        // Display Settings
        this.setUIValue('show-fps', this.settings.showFPS);
        this.setUIValue('show-bounding-boxes', this.settings.showBoundingBoxes);
        this.setUIValue('show-confidence', this.settings.showConfidence);
        this.setUIValue('show-recognition-history', this.settings.showRecognitionHistory);
        this.setUIValue('results-max-count', this.settings.resultsMaxCount);
        this.setUIValue('theme-preference', this.settings.themePreference);

        // Alerts Settings
        this.setUIValue('audio-alerts', this.settings.audioAlerts);
        this.setUIValue('recognition-sound', this.settings.recognitionSound);
        this.setUIValue('unknown-face-alert', this.settings.unknownFaceAlert);
        this.setUIValue('alert-volume', this.settings.alertVolume);
        this.setUIValue('desktop-notifications', this.settings.desktopNotifications);
        this.setUIValue('auto-capture-on-recognition', this.settings.autoCaptureOnRecognition);

        // Advanced Settings
        this.setUIValue('processing-mode', this.settings.processingMode);
        this.setUIValue('debug-mode', this.settings.debugMode);
        this.setUIValue('api-timeout', this.settings.apiTimeout);
        this.setUIValue('auto-retry', this.settings.autoRetry);

        // Update range value displays
        this.updateRangeDisplays();
    }

    setUIValue(id, value) {
        const element = document.getElementById(id);
        if (!element) return;

        if (element.type === 'checkbox') {
            element.checked = value;
        } else {
            element.value = value;
        }
    }

    updateRangeDisplays() {
        this.updateRangeDisplay('recognition-interval', this.settings.recognitionInterval, 'ms');
        this.updateRangeDisplay('confidence-threshold', Math.round(this.settings.confidenceThreshold * 100), '%');
        this.updateRangeDisplay('alert-volume', this.settings.alertVolume, '%');
    }

    updateRangeDisplay(rangeId, value, suffix = '') {
        const display = document.getElementById(rangeId.replace('-', '-value').replace('threshold', 'value').replace('volume', 'value'));
        if (display) {
            display.textContent = value + suffix;
        }
    }

    saveSettings() {
        // Collect all settings from UI
        this.settings = {
            // Camera Settings
            cameraResolution: this.getUIValue('camera-resolution', 'select') || '1280x720',
            frameRate: parseInt(this.getUIValue('frame-rate', 'select')) || 30,
            cameraFacing: this.getUIValue('camera-facing', 'select') || 'user',
            mirrorVideo: this.getUIValue('mirror-video', 'checkbox') || true,

            // Recognition Settings
            recognitionInterval: parseInt(this.getUIValue('recognition-interval', 'range')) || 2000,
            confidenceThreshold: parseFloat(this.getUIValue('confidence-threshold', 'range')) || 0.6,
            maxFaces: this.getUIValue('max-faces', 'select') || '3',
            continuousRecognition: this.getUIValue('continuous-recognition', 'checkbox') || true,
            saveUnknownFaces: this.getUIValue('save-unknown-faces', 'checkbox') || false,

            // Display Settings
            showFPS: this.getUIValue('show-fps', 'checkbox') || true,
            showBoundingBoxes: this.getUIValue('show-bounding-boxes', 'checkbox') || true,
            showConfidence: this.getUIValue('show-confidence', 'checkbox') || true,
            showRecognitionHistory: this.getUIValue('show-recognition-history', 'checkbox') || true,
            resultsMaxCount: parseInt(this.getUIValue('results-max-count', 'select')) || 25,
            themePreference: this.getUIValue('theme-preference', 'select') || 'auto',

            // Alerts Settings
            audioAlerts: this.getUIValue('audio-alerts', 'checkbox') || true,
            recognitionSound: this.getUIValue('recognition-sound', 'checkbox') || true,
            unknownFaceAlert: this.getUIValue('unknown-face-alert', 'checkbox') || false,
            alertVolume: parseInt(this.getUIValue('alert-volume', 'range')) || 50,
            desktopNotifications: this.getUIValue('desktop-notifications', 'checkbox') || false,
            autoCaptureOnRecognition: this.getUIValue('auto-capture-on-recognition', 'checkbox') || false,

            // Advanced Settings
            processingMode: this.getUIValue('processing-mode', 'select') || 'balanced',
            debugMode: this.getUIValue('debug-mode', 'checkbox') || false,
            apiTimeout: parseInt(this.getUIValue('api-timeout', 'number')) || 10,
            autoRetry: this.getUIValue('auto-retry', 'checkbox') || true
        };

        // Save to localStorage
        localStorage.setItem('live-recognition-settings', JSON.stringify(this.settings));
        
        // Apply settings
        this.applySettings();
        
        // Close modal
        this.closeSettings();
        
        // Show success message
        this.showNotification('Settings saved successfully', 'success');
        
        // Add visual feedback
        this.showSettingsSavedFeedback();
    }

    getUIValue(id, type) {
        const element = document.getElementById(id);
        if (!element) return null;

        switch (type) {
            case 'checkbox':
                return element.checked;
            case 'range':
            case 'number':
                return element.value;
            case 'select':
                return element.value;
            default:
                return element.value;
        }
    }

    applySettings() {
        // Apply performance monitor visibility
        this.togglePerformanceMonitor();
        
        // Apply theme
        if (this.settings.themePreference !== 'auto') {
            document.body.className = `${this.settings.themePreference}-theme live-recognition-page`;
        }
        
        // Request desktop notification permission if enabled
        if (this.settings.desktopNotifications && 'Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
        
        // Update recognition interval if currently running
        if (this.isActive) {
            this.stopRecognitionLoop();
            this.startRecognitionLoop();
        }
    }

    loadSettings() {
        const defaultSettings = {
            // Camera Settings
            cameraResolution: '1280x720',
            frameRate: 30,
            cameraFacing: 'user',
            mirrorVideo: true,

            // Recognition Settings
            recognitionInterval: 2000,
            confidenceThreshold: 0.6,
            maxFaces: '3',
            continuousRecognition: true,
            saveUnknownFaces: false,

            // Display Settings
            showFPS: true,
            showBoundingBoxes: true,
            showConfidence: true,
            showRecognitionHistory: true,
            resultsMaxCount: 25,
            themePreference: 'auto',

            // Alerts Settings
            audioAlerts: true,
            recognitionSound: true,
            unknownFaceAlert: false,
            alertVolume: 50,
            desktopNotifications: false,
            autoCaptureOnRecognition: false,

            // Advanced Settings
            processingMode: 'balanced',
            debugMode: false,
            apiTimeout: 10,
            autoRetry: true
        };

        const saved = localStorage.getItem('live-recognition-settings');
        this.settings = saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
        
        // Apply loaded settings
        this.applySettings();
    }

    resetSettings() {
        if (confirm('Are you sure you want to reset all settings to default values?')) {
            localStorage.removeItem('live-recognition-settings');
            this.loadSettings();
            this.loadSettingsToUI();
            this.showNotification('Settings reset to defaults', 'info');
        }
    }

    exportSettings() {
        const settingsData = {
            settings: this.settings,
            exportDate: new Date().toISOString(),
            version: '1.0'
        };

        const blob = new Blob([JSON.stringify(settingsData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `live-recognition-settings-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('Settings exported successfully', 'success');
    }

    importSettings() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    if (data.settings) {
                        this.settings = { ...this.settings, ...data.settings };
                        localStorage.setItem('live-recognition-settings', JSON.stringify(this.settings));
                        this.applySettings();
                        this.loadSettingsToUI();
                        this.showNotification('Settings imported successfully', 'success');
                    } else {
                        throw new Error('Invalid settings file format');
                    }
                } catch (error) {
                    this.showNotification('Failed to import settings: Invalid file format', 'error');
                }
            };
            reader.readAsText(file);
        };
        
        input.click();
    }

    clearAllData() {
        if (confirm('Are you sure you want to clear all data? This will reset all settings and clear browser storage.')) {
            localStorage.clear();
            sessionStorage.clear();
            this.loadSettings();
            this.loadSettingsToUI();
            this.showNotification('All data cleared', 'warning');
        }
    }

    showSettingsSavedFeedback() {
        const modal = this.elements.settingsModal;
        if (modal) {
            modal.classList.add('setting-saved');
            setTimeout(() => {
                modal.classList.remove('setting-saved');
            }, 2000);
        }
    }

    // Audio Alert System
    playAlert(type = 'recognition') {
        if (!this.settings.audioAlerts) return;

        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        // Set volume from settings
        gainNode.gain.value = this.settings.alertVolume / 100;

        // Different sounds for different events
        switch (type) {
            case 'recognition':
                if (this.settings.recognitionSound) {
                    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
                    oscillator.frequency.setValueAtTime(1000, audioContext.currentTime + 0.1);
                }
                break;
            case 'unknown':
                if (this.settings.unknownFaceAlert) {
                    oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
                    oscillator.frequency.setValueAtTime(300, audioContext.currentTime + 0.2);
                }
                break;
        }

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    }

    // Desktop Notifications
    showDesktopNotification(title, message, icon = null) {
        if (!this.settings.desktopNotifications || !('Notification' in window) || Notification.permission !== 'granted') {
            return;
        }

        new Notification(title, {
            body: message,
            icon: icon || '/favicon.ico',
            tag: 'live-recognition'
        });
    }

    // Notification system
    showNotification(message, type = 'info', duration = 5000) {
        const container = this.elements.notifications;
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: `<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22,4 12,14.01 9,11.01"/>`,
            error: `<circle cx="12" cy="12" r="10"/><line x1="15" x2="9" y1="9" y2="15"/><line x1="9" x2="15" y1="9" y2="15"/>`,
            warning: `<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/>`,
            info: `<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>`
        };

        notification.innerHTML = `
            <div class="notification-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    ${icons[type] || icons.info}
                </svg>
            </div>
            <div class="notification-content">
                <p>${this.escapeHtml(message)}</p>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 6L6 18"/><path d="M6 6l12 12"/>
                </svg>
            </button>
        `;

        container.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.add('show'), 10);

        // Auto-remove
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.classList.remove('show');
                    setTimeout(() => notification.remove(), 300);
                }
            }, duration);
        }

        return notification;
    }

    // Utility functions
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Cleanup
    cleanup() {
        this.stopRecognition();
    }
}

// Global app instance
const liveApp = new LiveRecognitionApp();

// Global functions for HTML onclick handlers
window.toggleRecognition = () => liveApp.toggleRecognition();
window.captureFrame = () => liveApp.captureFrame();
window.openSettings = () => liveApp.openSettings();
window.closeSettings = () => liveApp.closeSettings();
window.saveSettings = () => liveApp.saveSettings();
window.resetSettings = () => liveApp.resetSettings();
window.exportSettings = () => liveApp.exportSettings();
window.importSettings = () => liveApp.importSettings();
window.clearAllData = () => liveApp.clearAllData();

// Settings Tab Management
window.switchSettingsTab = (tabName) => {
    // Remove active class from all tabs and content
    document.querySelectorAll('.settings-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.settings-tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab and content
    const selectedTab = event.target.closest('.settings-tab');
    const selectedContent = document.getElementById(tabName + '-settings');
    
    if (selectedTab && selectedContent) {
        selectedTab.classList.add('active');
        selectedContent.classList.add('active');
    }
};

// Range Input Event Handlers
document.addEventListener('DOMContentLoaded', () => {
    // Update range displays on input
    document.addEventListener('input', (e) => {
        if (e.target.type === 'range') {
            const id = e.target.id;
            const value = e.target.value;
            let suffix = '';
            let displayValue = value;
            
            switch (id) {
                case 'recognition-interval':
                    suffix = 'ms';
                    break;
                case 'confidence-threshold':
                    suffix = '%';
                    displayValue = Math.round(value * 100);
                    break;
                case 'alert-volume':
                    suffix = '%';
                    break;
            }
            
            liveApp.updateRangeDisplay(id, displayValue, suffix);
        }
    });
});

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎥 Initializing Live Recognition App...');
    liveApp.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    liveApp.cleanup();
});
