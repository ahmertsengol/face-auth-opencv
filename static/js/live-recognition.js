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
        this.settingsLoaded = false; // Flag to prevent settings reset after save
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
        // Range sliders
        this.initializeRangeControls();
        
        // Checkboxes
        this.initializeCheckboxControls();
        
        // Select dropdowns
        this.initializeSelectControls();
        
        // Number inputs
        this.initializeNumberControls();
    }

    initializeRangeControls() {
        const rangeControls = [
            { id: 'recognition-interval', setting: 'recognitionInterval', suffix: 'ms' },
            { id: 'confidence-threshold', setting: 'confidenceThreshold', suffix: '%', multiplier: 100 },
            { id: 'alert-volume', setting: 'alertVolume', suffix: '%' }
        ];

        rangeControls.forEach(({ id, setting, suffix, multiplier = 1 }) => {
            const slider = document.getElementById(id);
            let valueDisplay;
            
            // Find the correct value display element
            if (id === 'recognition-interval') {
                valueDisplay = document.getElementById('recognition-value');
            } else if (id === 'confidence-threshold') {
                valueDisplay = document.getElementById('confidence-value');
            } else if (id === 'alert-volume') {
                valueDisplay = document.getElementById('volume-value');
            } else {
                valueDisplay = document.getElementById(id + '-value');
            }
            
            if (slider && valueDisplay) {
                slider.value = this.settings[setting];
                const displayValue = multiplier > 1 ? Math.round(this.settings[setting] * multiplier) : this.settings[setting];
                valueDisplay.textContent = `${displayValue}${suffix}`;
                
                slider.addEventListener('input', (e) => {
                    const value = multiplier > 1 ? parseFloat(e.target.value) : parseInt(e.target.value);
                    this.settings[setting] = value;
                    const displayValue = multiplier > 1 ? Math.round(value * multiplier) : value;
                    valueDisplay.textContent = `${displayValue}${suffix}`;
                    
                    // Apply changes immediately for some settings
                    if (setting === 'recognitionInterval' && this.isActive) {
                        this.stopRecognitionLoop();
                        this.startRecognitionLoop();
                    }
                });
            }
        });
    }

    initializeCheckboxControls() {
        const checkboxControls = [
            { id: 'mirror-video', setting: 'mirrorVideo', action: () => this.applyMirrorSetting() },
            { id: 'show-fps', setting: 'showFPS', action: () => this.togglePerformanceMonitor() },
            { id: 'continuous-recognition', setting: 'continuousRecognition' },
            { id: 'save-unknown-faces', setting: 'saveUnknownFaces' },
            { id: 'show-bounding-boxes', setting: 'showBoundingBoxes' },
            { id: 'show-confidence', setting: 'showConfidence' },
            { id: 'show-recognition-history', setting: 'showRecognitionHistory' },
            { id: 'audio-alerts', setting: 'audioAlerts' },
            { id: 'recognition-sound', setting: 'recognitionSound' },
            { id: 'unknown-face-alert', setting: 'unknownFaceAlert' },
            { id: 'desktop-notifications', setting: 'desktopNotifications', action: () => this.requestNotificationPermission() },
            { id: 'auto-capture-on-recognition', setting: 'autoCaptureOnRecognition' },
            { id: 'debug-mode', setting: 'debugMode' },
            { id: 'auto-retry', setting: 'autoRetry' }
        ];

        checkboxControls.forEach(({ id, setting, action }) => {
            const checkbox = document.getElementById(id);
            if (checkbox) {
                checkbox.checked = this.settings[setting];
                checkbox.addEventListener('change', (e) => {
                    this.settings[setting] = e.target.checked;
                    if (action) action();
                    this.showNotification(
                        `${setting.replace(/([A-Z])/g, ' $1').toLowerCase()} ${e.target.checked ? 'enabled' : 'disabled'}`, 
                        'info'
                    );
                });
            }
        });
    }

    initializeSelectControls() {
        const selectControls = [
            { id: 'camera-resolution', setting: 'cameraResolution', action: () => this.applyCameraSettings() },
            { id: 'frame-rate', setting: 'frameRate', action: () => this.applyCameraSettings() },
            { id: 'camera-facing', setting: 'cameraFacing', action: () => this.applyCameraSettings() },
            { id: 'max-faces', setting: 'maxFaces' },
            { id: 'results-max-count', setting: 'resultsMaxCount' },
            { id: 'theme-preference', setting: 'themePreference', action: () => this.applyThemePreference() },
            { id: 'processing-mode', setting: 'processingMode' }
        ];

        selectControls.forEach(({ id, setting, action }) => {
            const select = document.getElementById(id);
            if (select) {
                select.value = this.settings[setting];
                select.addEventListener('change', (e) => {
                    this.settings[setting] = e.target.value;
                    if (action) action();
                    this.showNotification(
                        `${setting.replace(/([A-Z])/g, ' $1').toLowerCase()} changed to ${e.target.value}`, 
                        'info'
                    );
                });
            }
        });
    }

    initializeNumberControls() {
        const numberControls = [
            { id: 'api-timeout', setting: 'apiTimeout' }
        ];

        numberControls.forEach(({ id, setting }) => {
            const input = document.getElementById(id);
            if (input) {
                input.value = this.settings[setting];
                input.addEventListener('change', (e) => {
                    this.settings[setting] = parseInt(e.target.value);
                    this.showNotification(
                        `${setting.replace(/([A-Z])/g, ' $1').toLowerCase()} set to ${e.target.value}`, 
                        'info'
                    );
                });
            }
        });
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
            case 'b':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.toggleBoundingBoxes();
                }
                break;
            case 'f':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.togglePerformanceMonitor();
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

            // Get camera stream with settings
            const videoConstraints = this.buildVideoConstraints();
            this.videoStream = await navigator.mediaDevices.getUserMedia({
                video: videoConstraints
            });

            // Setup video element
            const video = this.elements.video;
            if (video) {
                video.srcObject = this.videoStream;
                await new Promise(resolve => {
                    video.onloadedmetadata = resolve;
                });
                
                // Apply mirror setting
                this.applyMirrorSetting();
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

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            // Validate API response structure
            if (!result || typeof result !== 'object') {
                throw new Error('Invalid API response format');
            }

            // Ensure required properties exist with defaults
            const normalizedResult = {
                success: result.success || false,
                faces_detected: result.faces_detected || 0,
                recognized: result.recognized || false,
                results: Array.isArray(result.results) ? result.results : [],
                error: result.error || null
            };

            if (normalizedResult.success) {
                this.processRecognitionResult(normalizedResult);
                
                // Update performance stats
                const processingTime = performance.now() - startTime;
                this.updatePerformanceStats(processingTime, normalizedResult.faces_detected, normalizedResult.results.length);
            } else {
                console.warn('API returned unsuccessful response:', normalizedResult.error || 'Unknown error');
                // Still process the result to show "no faces detected"
                this.processRecognitionResult(normalizedResult);
            }

        } catch (error) {
            console.error('Frame processing error:', error);
            
            // Create a safe fallback result
            const fallbackResult = {
                success: false,
                faces_detected: 0,
                recognized: false,
                results: [],
                error: error.message
            };
            
            // Update UI with fallback data
            this.updateStatsDisplay(0, 0);
        }
    }

    // Process recognition results
    processRecognitionResult(result) {
        // Validate and normalize result object
        if (!result || typeof result !== 'object') {
            console.warn('Invalid result object passed to processRecognitionResult');
            return;
        }

        // Ensure all required properties exist with safe defaults
        const safeResult = {
            faces_detected: Number(result.faces_detected) || 0,
            recognized: Boolean(result.recognized),
            results: Array.isArray(result.results) ? result.results : [],
            success: Boolean(result.success),
            error: result.error || null
        };

        // Update stats with safe values
        this.updateStatsDisplay(safeResult.faces_detected, safeResult.results.length);

        // Update results display if enabled
        if (this.settings.showRecognitionHistory) {
            this.updateResultsDisplay(safeResult);
        }
        
        // Handle audio alerts and notifications
        if (safeResult.recognized && safeResult.results.length > 0) {
            // Play recognition sound if enabled
            if (this.settings.audioAlerts && this.settings.recognitionSound) {
                this.playAlert('recognition');
            }
            
            // Desktop notification for recognized faces
            if (this.settings.desktopNotifications) {
                try {
                    const names = safeResult.results
                        .filter(r => r && r.name) // Filter out invalid results
                        .map(r => r.name)
                        .join(', ');
                    
                    if (names) {
                        this.showDesktopNotification(
                            'Face Recognition',
                            `Recognized: ${names}`,
                            '/static/images/face-icon.png'
                        );
                    }
                } catch (error) {
                    console.error('Error creating recognition notification:', error);
                }
            }
            
            // Auto-capture on recognition if enabled
            if (this.settings.autoCaptureOnRecognition) {
                setTimeout(() => this.captureFrame(), 500); // Small delay for better UX
            }
        } else if (safeResult.faces_detected > 0) {
            // Unknown face detected
            if (this.settings.audioAlerts && this.settings.unknownFaceAlert) {
                this.playAlert('unknown');
            }
            
            if (this.settings.unknownFaceAlert && this.settings.desktopNotifications) {
                this.showDesktopNotification(
                    'Unknown Face Detected',
                    `${safeResult.faces_detected} unknown face(s) detected`,
                    '/static/images/unknown-icon.png'
                );
            }
            
            // Save unknown faces if enabled
            if (this.settings.saveUnknownFaces) {
                this.saveUnknownFaceCapture();
            }
        }
        
        // Bounding boxes feature disabled
        // if (this.settings.showBoundingBoxes) {
        //     this.drawFaceBoundingBoxes(safeResult);
        // }

        // Log any errors from API
        if (safeResult.error) {
            console.warn('API returned error:', safeResult.error);
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

        // Validate result object
        if (!result || typeof result !== 'object') {
            console.warn('Invalid result object in updateResultsDisplay');
            return;
        }

        // Ensure safe defaults
        const safeResult = {
            recognized: Boolean(result.recognized),
            results: Array.isArray(result.results) ? result.results : [],
            faces_detected: Number(result.faces_detected) || 0
        };

        if (!safeResult.recognized || safeResult.results.length === 0) {
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
                            <span>Faces: ${safeResult.faces_detected}</span>
                        </div>
                    </div>
                    <div class="result-time">${new Date().toLocaleTimeString()}</div>
                </div>
            `;
            
            resultsContent.innerHTML = noMatchHtml + resultsContent.innerHTML;
        } else {
            // Show recognition results with validation
            try {
                const resultsHtml = safeResult.results
                    .filter(person => person && typeof person === 'object' && person.name) // Filter valid results
                    .map(person => {
                        // Ensure person object has required properties
                        const safePerson = {
                            name: String(person.name || 'Unknown'),
                            confidence: Number(person.confidence) || 0,
                            distance: Number(person.distance) || 0
                        };

                        return `
                            <div class="recognition-result match">
                                <div class="result-avatar">
                                    ${safePerson.name.charAt(0).toUpperCase()}
                                </div>
                                <div class="result-info">
                                    <div class="result-name">${this.escapeHtml(safePerson.name)}</div>
                                    <div class="result-details">
                                        <span>Confidence: ${Math.round(safePerson.confidence * 100)}%</span>
                                        <span>Distance: ${safePerson.distance.toFixed(3)}</span>
                                    </div>
                                </div>
                                <div class="result-time">${new Date().toLocaleTimeString()}</div>
                            </div>
                        `;
                    }).join('');
                
                resultsContent.innerHTML = resultsHtml + resultsContent.innerHTML;
            } catch (error) {
                console.error('Error rendering recognition results:', error);
                // Fallback to no match display
                const fallbackHtml = `
                    <div class="recognition-result error">
                        <div class="result-avatar unknown">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <path d="M15 9l-6 6"/>
                                <path d="M9 9l6 6"/>
                            </svg>
                        </div>
                        <div class="result-info">
                            <div class="result-name">Display Error</div>
                            <div class="result-details">
                                <span>Could not display results</span>
                            </div>
                        </div>
                        <div class="result-time">${new Date().toLocaleTimeString()}</div>
                    </div>
                `;
                resultsContent.innerHTML = fallbackHtml + resultsContent.innerHTML;
            }
        }

        // Keep only last N results based on settings
        try {
            const maxResults = parseInt(this.settings.resultsMaxCount) || 25;
            const results = resultsContent.querySelectorAll('.recognition-result');
            if (results.length > maxResults) {
                for (let i = maxResults; i < results.length; i++) {
                    results[i].remove();
                }
            }
        } catch (error) {
            console.error('Error managing results history:', error);
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
            mirrorVideo: this.getUIValue('mirror-video', 'checkbox') !== null ? this.getUIValue('mirror-video', 'checkbox') : true,

            // Recognition Settings
            recognitionInterval: parseInt(this.getUIValue('recognition-interval', 'range')) || 2000,
            confidenceThreshold: parseFloat(this.getUIValue('confidence-threshold', 'range')) || 0.6,
            maxFaces: this.getUIValue('max-faces', 'select') || '3',
            continuousRecognition: this.getUIValue('continuous-recognition', 'checkbox') !== null ? this.getUIValue('continuous-recognition', 'checkbox') : true,
            saveUnknownFaces: this.getUIValue('save-unknown-faces', 'checkbox') !== null ? this.getUIValue('save-unknown-faces', 'checkbox') : false,

            // Display Settings
            showFPS: this.getUIValue('show-fps', 'checkbox') !== null ? this.getUIValue('show-fps', 'checkbox') : true,
            showBoundingBoxes: this.getUIValue('show-bounding-boxes', 'checkbox') !== null ? this.getUIValue('show-bounding-boxes', 'checkbox') : true,
            showConfidence: this.getUIValue('show-confidence', 'checkbox') !== null ? this.getUIValue('show-confidence', 'checkbox') : true,
            showRecognitionHistory: this.getUIValue('show-recognition-history', 'checkbox') !== null ? this.getUIValue('show-recognition-history', 'checkbox') : true,
            resultsMaxCount: parseInt(this.getUIValue('results-max-count', 'select')) || 25,
            themePreference: this.getUIValue('theme-preference', 'select') || 'auto',

            // Alerts Settings
            audioAlerts: this.getUIValue('audio-alerts', 'checkbox') !== null ? this.getUIValue('audio-alerts', 'checkbox') : true,
            recognitionSound: this.getUIValue('recognition-sound', 'checkbox') !== null ? this.getUIValue('recognition-sound', 'checkbox') : true,
            unknownFaceAlert: this.getUIValue('unknown-face-alert', 'checkbox') !== null ? this.getUIValue('unknown-face-alert', 'checkbox') : false,
            alertVolume: parseInt(this.getUIValue('alert-volume', 'range')) || 50,
            desktopNotifications: this.getUIValue('desktop-notifications', 'checkbox') !== null ? this.getUIValue('desktop-notifications', 'checkbox') : false,
            autoCaptureOnRecognition: this.getUIValue('auto-capture-on-recognition', 'checkbox') !== null ? this.getUIValue('auto-capture-on-recognition', 'checkbox') : false,

            // Advanced Settings
            processingMode: this.getUIValue('processing-mode', 'select') || 'balanced',
            debugMode: this.getUIValue('debug-mode', 'checkbox') !== null ? this.getUIValue('debug-mode', 'checkbox') : false,
            apiTimeout: parseInt(this.getUIValue('api-timeout', 'number')) || 10,
            autoRetry: this.getUIValue('auto-retry', 'checkbox') !== null ? this.getUIValue('auto-retry', 'checkbox') : true
        };

        // Save to localStorage
        localStorage.setItem('live-recognition-settings', JSON.stringify(this.settings));
        
        // Apply settings without reloading from localStorage
        this.applySettings();
        
        // Close modal
        this.closeSettings();
        
        // Show success message of settings
        this.showNotification(`Settings saved successfully.`, 'success');
        
        // Add visual feedback
        this.showSettingsSavedFeedback();
        
        console.log('Settings saved:', this.settings);
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
        
        // Apply bounding boxes visibility
        const overlay = this.elements.faceOverlay;
        if (overlay) {
            if (this.settings.showBoundingBoxes) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
                overlay.innerHTML = '';
            }
        }
        
        // Apply theme
        if (this.settings.themePreference !== 'auto') {
            document.body.className = `${this.settings.themePreference}-theme live-recognition-page`;
        }
        
        // Apply mirror setting
        this.applyMirrorSetting();
        
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

    // Apply mirror setting to video element
    applyMirrorSetting() {
        const video = this.elements.video;
        if (video) {
            if (this.settings.mirrorVideo) {
                video.classList.add('mirrored');
            } else {
                video.classList.remove('mirrored');
            }
        }
    }

    // Apply camera settings
    applyCameraSettings() {
        if (this.isActive) {
            this.showNotification('Camera settings will apply on next start', 'info');
        }
    }

    // Apply theme preference
    applyThemePreference() {
        if (this.settings.themePreference !== 'auto') {
            this.currentTheme = this.settings.themePreference;
            document.body.className = `${this.currentTheme}-theme live-recognition-page`;
            localStorage.setItem('live-theme', this.currentTheme);
            this.updateThemeIcon();
        } else {
            // Auto theme based on system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            this.currentTheme = prefersDark ? 'dark' : 'light';
            document.body.className = `${this.currentTheme}-theme live-recognition-page`;
            this.updateThemeIcon();
        }
    }

    // Request notification permission
    requestNotificationPermission() {
        if (this.settings.desktopNotifications && 'Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.showNotification('Desktop notifications enabled', 'success');
                } else {
                    this.showNotification('Desktop notifications permission denied', 'warning');
                    this.settings.desktopNotifications = false;
                    const checkbox = document.getElementById('desktop-notifications');
                    if (checkbox) checkbox.checked = false;
                }
            });
        }
    }

    // Build video constraints from settings
    buildVideoConstraints() {
        const constraints = {
            facingMode: this.settings.cameraFacing
        };

        // Resolution settings
        if (this.settings.cameraResolution !== 'auto') {
            const [width, height] = this.settings.cameraResolution.split('x').map(Number);
            constraints.width = { ideal: width };
            constraints.height = { ideal: height };
        } else {
            constraints.width = { ideal: 1280 };
            constraints.height = { ideal: 720 };
        }

        // Frame rate settings
        if (this.settings.frameRate) {
            constraints.frameRate = { ideal: parseInt(this.settings.frameRate) };
        }

        return constraints;
    }

    // Save unknown face capture
    saveUnknownFaceCapture() {
        if (!this.elements.video || !this.elements.canvas) return;
        
        const video = this.elements.video;
        const canvas = this.elements.canvas;
        const ctx = canvas.getContext('2d');
        
        // Draw current frame
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Create download link
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `unknown-face-${new Date().getTime()}.jpg`;
            a.click();
            URL.revokeObjectURL(url);
        }, 'image/jpeg', 0.9);
        
        this.showNotification('Unknown face saved', 'info');
    }

    // Draw face bounding boxes
    drawFaceBoundingBoxes(result) {
        const overlay = this.elements.faceOverlay;
        if (!overlay) return;
        
        // Check if bounding boxes should be shown
        if (!this.settings.showBoundingBoxes) {
            overlay.innerHTML = '';
            overlay.classList.add('hidden');
            return;
        }
        
        overlay.classList.remove('hidden');
        
        // Clear previous boxes
        overlay.innerHTML = '';
        
        // Validate result object
        if (!result || typeof result !== 'object') {
            console.warn('Invalid result object in drawFaceBoundingBoxes');
            return;
        }

        // Ensure safe defaults
        const safeResult = {
            faces_detected: Number(result.faces_detected) || 0,
            face_locations: Array.isArray(result.face_locations) ? result.face_locations : [],
            results: Array.isArray(result.results) ? result.results : []
        };
        

        
        if (safeResult.faces_detected > 0 && safeResult.face_locations.length > 0) {
            try {
                safeResult.face_locations.forEach((location, index) => {
                    // Validate location array
                    if (!Array.isArray(location) || location.length < 4) {
                        console.warn(`Invalid face location at index ${index}:`, location);
                        return;
                    }

                    const box = document.createElement('div');
                    box.className = 'face-box';
                    
                    // Position the box (face_locations contains [top, right, bottom, left])
                    const [top, right, bottom, left] = location.map(coord => Number(coord) || 0);
                    const video = this.elements.video;
                    
                    if (video && video.videoWidth && video.videoHeight) {
                        const scaleX = video.offsetWidth / video.videoWidth;
                        const scaleY = video.offsetHeight / video.videoHeight;
                        
                        // Convert face_recognition coordinates to screen coordinates
                        const boxLeft = Math.max(0, left * scaleX);
                        const boxTop = Math.max(0, top * scaleY);
                        const boxWidth = Math.max(0, (right - left) * scaleX);
                        const boxHeight = Math.max(0, (bottom - top) * scaleY);
                        
                        box.style.left = `${boxLeft}px`;
                        box.style.top = `${boxTop}px`;
                        box.style.width = `${boxWidth}px`;
                        box.style.height = `${boxHeight}px`;
                        
                        // Add recognition status and labels
                        const matchedResult = safeResult.results[index];
                        if (matchedResult && matchedResult.name) {
                            box.classList.add('recognized');
                            
                            // Add name label
                            const label = document.createElement('div');
                            label.className = 'face-label recognized';
                            label.textContent = this.escapeHtml(matchedResult.name);
                            box.appendChild(label);
                            
                            // Add confidence badge if enabled
                            if (this.settings.showConfidence && matchedResult.confidence !== undefined) {
                                const confidenceBadge = document.createElement('div');
                                confidenceBadge.className = 'confidence-badge';
                                const confidence = Number(matchedResult.confidence) || 0;
                                confidenceBadge.textContent = `${Math.round(confidence * 100)}%`;
                                box.appendChild(confidenceBadge);
                            }
                            
                            // Play recognition sound if enabled
                            if (this.settings.recognitionSound && this.settings.audioAlerts) {
                                this.playAlert('recognition');
                            }
                            
                        } else {
                            box.classList.add('unknown');
                            
                            // Add unknown label
                            const label = document.createElement('div');
                            label.className = 'face-label unknown';
                            label.textContent = 'Unknown Face';
                            box.appendChild(label);
                            
                            // Add confidence badge for detection confidence if available
                            if (this.settings.showConfidence) {
                                const confidenceBadge = document.createElement('div');
                                confidenceBadge.className = 'confidence-badge';
                                confidenceBadge.textContent = 'Detection';
                                box.appendChild(confidenceBadge);
                            }
                            
                            // Play unknown face alert if enabled
                            if (this.settings.unknownFaceAlert && this.settings.audioAlerts) {
                                this.playAlert('unknown');
                            }
                            
                            // Save unknown face capture if enabled
                            if (this.settings.saveUnknownFaces) {
                                this.saveUnknownFaceCapture();
                            }
                        }
                        
                        // Add animation class based on processing mode
                        if (this.settings.processingMode === 'accuracy') {
                            box.classList.add('detecting');
                        }
                        
                        // Auto-capture on recognition if enabled
                        if (this.settings.autoCaptureOnRecognition && matchedResult && matchedResult.name) {
                            setTimeout(() => this.captureFrame(), 500);
                        }
                        
                        overlay.appendChild(box);
                    }
                });
                
                // Send desktop notification if enabled
                if (this.settings.desktopNotifications && safeResult.results.length > 0) {
                    const recognizedNames = safeResult.results
                        .filter(r => r.name)
                        .map(r => r.name);
                        
                    if (recognizedNames.length > 0) {
                        this.showDesktopNotification(
                            'Face Recognition',
                            `Recognized: ${recognizedNames.join(', ')}`,
                            'success'
                        );
                    }
                }
                
            } catch (error) {
                console.error('Error drawing face bounding boxes:', error);
                this.showNotification('Error drawing face boxes', 'error');
            }
        }
    }

    // Toggle bounding boxes visibility
    toggleBoundingBoxes() {
        this.settings.showBoundingBoxes = !this.settings.showBoundingBoxes;
        
        const overlay = this.elements.faceOverlay;
        if (overlay) {
            if (this.settings.showBoundingBoxes) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
                overlay.innerHTML = '';
            }
        }
        
        // Update settings checkbox
        const checkbox = document.getElementById('show-bounding-boxes');
        if (checkbox) {
            checkbox.checked = this.settings.showBoundingBoxes;
        }
        
        this.showNotification(
            `Face bounding boxes ${this.settings.showBoundingBoxes ? 'enabled' : 'disabled'}`,
            'info'
        );
        
        // Save setting
        localStorage.setItem('live-recognition-settings', JSON.stringify(this.settings));
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
            showBoundingBoxes: false,
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
        
        // Only apply settings if this is initial load, not after save
        if (!this.settingsLoaded) {
            this.applySettings();
            this.settingsLoaded = true;
        }
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
        // Check if audio alerts are enabled
        if (!this.settings.audioAlerts) {
            console.log('Audio alerts disabled');
            return;
        }

        // Check specific sound settings
        if (type === 'recognition' && !this.settings.recognitionSound) {
            console.log('Recognition sound disabled');
            return;
        }
        
        if (type === 'unknown' && !this.settings.unknownFaceAlert) {
            console.log('Unknown face alert disabled');
            return;
        }

        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            // Set volume from settings (0-100 to 0-1)
            const volume = Math.max(0, Math.min(100, this.settings.alertVolume || 50)) / 100;
            gainNode.gain.value = volume;

            // Different sounds for different events
            switch (type) {
                case 'recognition':
                    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
                    oscillator.frequency.setValueAtTime(1000, audioContext.currentTime + 0.1);
                    break;
                case 'unknown':
                    oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
                    oscillator.frequency.setValueAtTime(300, audioContext.currentTime + 0.2);
                    break;
                default:
                    oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
                    break;
            }

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
            
            console.log(`Playing ${type} alert at volume ${Math.round(volume * 100)}%`);
        } catch (error) {
            console.error('Error playing alert sound:', error);
        }
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
window.toggleBoundingBoxes = () => liveApp.toggleBoundingBoxes();

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
