/**
 * Face Recognition Dashboard - Modern JavaScript
 * Enhanced with theme support, proper state management, and clean interactions
 */

// Application State
class DashboardState {
    constructor() {
        this.isLoading = false;
        this.retryCount = 0;
        this.theme = localStorage.getItem('theme') || 'light';
        this.users = [];
        this.stats = {};
        this.isRecognitionActive = false;
        this.videoStream = null;
        this.refreshInterval = null;
        
        // Constants
        this.MAX_RETRIES = 3;
        this.API_BASE_URL = window.location.origin;
        this.REFRESH_INTERVAL = 30000; // 30 seconds
        this.currentTheme = 'light';
        this.chart = null;
        this.elements = new Map();
    }

    // Cache DOM elements for performance
    cacheElements() {
        const selectors = {
            'theme-toggle': '#theme-toggle',
            'theme-icon': '.theme-icon',
            'stat-users': '#stat-users',
            'stat-encodings': '#stat-encodings',
            'stat-avg': '#stat-avg',
            'users-list': '#users-list',
            'video-stream': '#video-stream',
            'video-canvas': '#video-canvas',
            'recognition-status': '#recognition-status',
            'add-user-modal': '#add-user-modal',
            'notifications': '#notifications',
            'analytics-chart': '#analytics-chart',
            'cpu-usage': '#cpu-usage',
            'memory-usage': '#memory-usage',
            'recognition-speed': '#recognition-speed'
        };

        for (const [key, selector] of Object.entries(selectors)) {
            this.elements.set(key, document.querySelector(selector));
        }
    }

    getElement(key) {
        return this.elements.get(key);
    }
}

// Global state instance
const dashboard = new DashboardState();

// Camera functionality for user creation
let cameraStream = null;
let capturedPhotos = [];
let currentUploadMode = 'file'; // 'file' or 'camera'

// Theme Management
function initializeTheme() {
    // Get saved theme or default to light
    const savedTheme = localStorage.getItem('dashboard-theme') || 'light';
    dashboard.currentTheme = savedTheme;
    document.body.className = `${dashboard.currentTheme}-theme`;
    updateThemeIcon();
}

function toggleTheme() {
    dashboard.currentTheme = dashboard.currentTheme === 'light' ? 'dark' : 'light';
    document.body.className = `${dashboard.currentTheme}-theme`;
    localStorage.setItem('dashboard-theme', dashboard.currentTheme);
    updateThemeIcon();
    showNotification(`Switched to ${dashboard.currentTheme} theme`, 'info');
}

function updateThemeIcon() {
    const themeIcon = dashboard.getElement('theme-icon');
    if (themeIcon) {
        const nextTheme = dashboard.currentTheme === 'light' ? 'dark' : 'light';
        themeIcon.innerHTML = getThemeIcon(nextTheme);
    }
}

function getThemeIcon(theme) {
    if (theme === 'dark') {
        // Moon icon for switching TO dark theme
        return `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>`;
        } else {
        // Sun icon for switching TO light theme
        return `<circle cx="12" cy="12" r="5"/>
                <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>`;
    }
}

// Event Listeners
function initializeEventListeners() {
    // Theme toggle
    const themeToggle = dashboard.getElement('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Modal close on backdrop click
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-backdrop')) {
            closeModal();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Form submission
    const addUserForm = document.getElementById('add-user-form');
    if (addUserForm) {
        addUserForm.addEventListener('submit', handleAddUser);
    }
}

// Keyboard Shortcuts
function handleKeyboardShortcuts(e) {
    // Escape key to close modal
    if (e.key === 'Escape') {
        closeModal();
    }
    
    // Ctrl/Cmd + R to refresh (prevent default and use our refresh)
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        refreshAll();
    }
    
    // Ctrl/Cmd + T to toggle theme
    if ((e.ctrlKey || e.metaKey) && e.key === 't') {
        e.preventDefault();
        toggleTheme();
    }
}

// API Utilities
async function fetchWithRetry(url, options = {}) {
    const { timeout = 10000, retries = dashboard.MAX_RETRIES, ...fetchOptions } = options;
    
    for (let i = 0; i <= retries; i++) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            
            const response = await fetch(dashboard.API_BASE_URL + url, {
                ...fetchOptions,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...fetchOptions.headers
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response;
        } catch (error) {
            console.warn(`Attempt ${i + 1} failed:`, error.message);
            
            if (i === retries) {
                throw error;
            }
            
            // Exponential backoff
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
        }
    }
}

// API Health Check
async function checkApiHealth() {
    try {
        const response = await fetchWithRetry('/api/health', { timeout: 5000 });
        const data = await response.json();
        return data.success;
    } catch (error) {
        console.error('API Health check failed:', error);
        return false;
    }
}

// Load Initial Data
async function loadInitialData() {
    const isHealthy = await checkApiHealth();
    
    if (!isHealthy) {
        showNotification('API is not available. Retrying...', 'error');
        setTimeout(loadInitialData, 5000);
        return;
    }
    
    await Promise.all([
        loadUsers(),
        loadStats(),
        loadSystemHealth()
    ]);
}

// Load Users
async function loadUsers() {
    if (dashboard.isLoading) return;
    
    try {
        dashboard.isLoading = true;
        showLoadingState();
        
        const response = await fetchWithRetry('/api/users');
        const data = await response.json();
        
        if (data.success) {
            dashboard.users = data.users;
            displayUsers(data.users);
            dashboard.retryCount = 0;
        } else {
            throw new Error(data.error || 'Unknown API error');
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showError(`Failed to load users: ${error.message}`);
        
        if (dashboard.retryCount < dashboard.MAX_RETRIES) {
            dashboard.retryCount++;
            setTimeout(() => {
                console.log(`🔄 Retrying users load (attempt ${dashboard.retryCount}/${dashboard.MAX_RETRIES})`);
                loadUsers();
            }, Math.pow(2, dashboard.retryCount) * 2000);
        }
    } finally {
        dashboard.isLoading = false;
    }
}

// Display Users
function displayUsers(users) {
    const usersList = dashboard.getElement('users-list');
    if (!usersList) return;
    
    if (users.length === 0) {
        usersList.innerHTML = `
            <div class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                </svg>
                <p>No users registered yet</p>
                <button class="btn primary" onclick="showAddUserModal()">Add First User</button>
            </div>
        `;
        return;
    }
    
    usersList.innerHTML = users.map((user, index) => `
        <div class="user-item" data-user-name="${user.name}">
            <div class="user-avatar">
                <div class="user-avatar-small">
                    ${user.name.charAt(0).toUpperCase()}
                    </div>
                </div>
            <div class="user-info">
                <h4>${escapeHtml(user.name)}</h4>
                <p>${user.face_count || 0} face samples</p>
                <span class="user-meta">Created ${formatDate(user.created_at)}</span>
            </div>
            <div class="user-actions">
                <button class="icon-btn" onclick="viewUserDetails('${escapeHtml(user.name)}')" title="View Details">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                    </svg>
                    </button>
                <button class="icon-btn danger" onclick="deleteUser('${escapeHtml(user.name)}')" title="Delete">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3,6 5,6 21,6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                    </button>
                </div>
        </div>
    `).join('');
}

// Load Statistics
async function loadStats() {
    try {
        const response = await fetchWithRetry('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            dashboard.stats = data.stats;
            displayStats(data.stats);
        } else {
            throw new Error(data.error || 'Failed to load statistics');
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        showNotification('Failed to load statistics', 'error');
    }
}

// Display Statistics
function displayStats(stats) {
    animateNumber('stat-users', stats.total_users);
    animateNumber('stat-encodings', stats.total_face_encodings);
    animateNumber('stat-avg', stats.average_encodings_per_user, 1);
    
    // Update system status
    const systemStatus = document.getElementById('system-status');
    if (systemStatus) {
        systemStatus.textContent = stats.total_users > 0 ? 'Active' : 'Ready';
    }
}

// Load System Health
async function loadSystemHealth() {
    try {
        const response = await fetchWithRetry('/api/system/info');
        const data = await response.json();
        
        if (data.success) {
            displaySystemHealth(data.system);
        }
    } catch (error) {
        console.error('Error loading system health:', error);
    }
}

// Display System Health
function displaySystemHealth(system) {
    const cpuUsage = Math.round(Math.random() * 60 + 20); // Simulated
    const memoryUsage = Math.round((system.memory_total - system.memory_available) / system.memory_total * 100);
    const recognitionSpeed = Math.round(Math.random() * 10 + 5); // Simulated
    
    updateMetric('cpu-usage', `${cpuUsage}%`, cpuUsage);
    updateMetric('memory-usage', `${memoryUsage}%`, memoryUsage);
    updateMetric('recognition-speed', `${recognitionSpeed}ms`, 100 - recognitionSpeed);
}

// Update Metric
function updateMetric(id, value, percentage) {
    const element = document.getElementById(id);
    const bar = element?.parentElement.querySelector('.metric-fill');
    
    if (element) {
        element.textContent = value;
    }
    
    if (bar) {
        bar.style.width = `${Math.min(percentage, 100)}%`;
        
        // Update color based on value
        bar.className = 'metric-fill';
        if (percentage > 80) {
            bar.classList.add('danger');
        } else if (percentage > 60) {
            bar.classList.add('warning');
        } else {
            bar.classList.add('success');
        }
    }
}

// Animate Number
function animateNumber(elementId, newValue, decimals = 0) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const currentValue = parseFloat(element.textContent) || 0;
    const difference = newValue - currentValue;
    const duration = 1000;
    const steps = 60;
    const stepValue = difference / steps;
    let currentStep = 0;
    
    const timer = setInterval(() => {
        currentStep++;
        const value = currentValue + (stepValue * currentStep);
        element.textContent = decimals > 0 ? value.toFixed(decimals) : Math.round(value);
        
        if (currentStep >= steps) {
            clearInterval(timer);
            element.textContent = decimals > 0 ? newValue.toFixed(decimals) : newValue;
        }
    }, duration / steps);
}

// Loading States
function showLoadingState() {
    const usersList = dashboard.getElement('users-list');
    if (usersList) {
        usersList.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <p>Loading users...</p>
            </div>
        `;
    }
}

function showError(message) {
    const usersList = dashboard.getElement('users-list');
    if (usersList) {
        usersList.innerHTML = `
            <div class="loading-state">
                <i data-lucide="alert-circle" style="font-size: 3rem; color: var(--danger); margin-bottom: 1rem;"></i>
                <p>${escapeHtml(message)}</p>
                <button class="btn primary" onclick="refreshUsers()">
                    <i data-lucide="refresh-cw"></i>
                    Retry
                </button>
            </div>
        `;
    }
}

// Auto Refresh
function startAutoRefresh() {
    if (dashboard.refreshInterval) {
        clearInterval(dashboard.refreshInterval);
    }
    
    dashboard.refreshInterval = setInterval(() => {
        if (!dashboard.isLoading && !document.hidden) {
    loadStats();
            loadSystemHealth();
        }
    }, dashboard.REFRESH_INTERVAL);
}

function stopAutoRefresh() {
    if (dashboard.refreshInterval) {
        clearInterval(dashboard.refreshInterval);
        dashboard.refreshInterval = null;
    }
}

// Manual refresh functions
function refreshUsers() {
    loadUsers();
}

function refreshAll() {
    loadInitialData();
    showNotification('Dashboard refreshed', 'success');
}

// Modal Management
function showAddUserModal() {
    const modal = dashboard.getElement('add-user-modal');
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // Focus on the name input
        const nameInput = document.getElementById('user-name');
        if (nameInput) {
            setTimeout(() => nameInput.focus(), 100);
        }
    }
}

function closeModal() {
    const modal = dashboard.getElement('add-user-modal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
        resetAddUserForm();
    }
}

function resetAddUserForm() {
    const form = document.getElementById('add-user-form');
    if (form) {
        form.reset();
    }
    
    if (dashboard.getElement('uploaded-files')) {
        dashboard.getElement('uploaded-files').innerHTML = '';
    }
    
    // Reset camera functionality
    stopCamera();
    capturedPhotos = [];
    currentUploadMode = 'file';
    updatePhotoCounter();
    
    // Reset tabs
    const fileTab = document.getElementById('file-tab');
    const cameraTab = document.getElementById('camera-tab');
    const fileContent = document.getElementById('file-upload-content');
    const cameraContent = document.getElementById('camera-upload-content');
    
    if (fileTab && cameraTab && fileContent && cameraContent) {
        fileTab.classList.add('active');
        cameraTab.classList.remove('active');
        fileContent.classList.remove('hidden');
        cameraContent.classList.add('hidden');
    }
}

// File Upload Management
function initializeFileUpload() {
    const uploadArea = dashboard.getElement('file-upload-area');
    const fileInput = document.getElementById('user-photos');
    const uploadLink = uploadArea?.querySelector('.upload-link');

    if (!uploadArea || !fileInput) return;

    // Click to upload
    uploadLink?.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('click', (e) => {
        if (e.target === uploadArea || e.target.closest('.upload-link')) {
            fileInput.click();
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('image/'));
        handleFileSelection(files);
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFileSelection(files);
    });
}

function handleFileSelection(files) {
    const uploadedFiles = dashboard.getElement('uploaded-files');
    if (!uploadedFiles) return;
    
    // Filter for image files
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
        showNotification('Please select image files only', 'error');
        return;
    }
    
    // Clear previous files
    uploadedFiles.innerHTML = '';
    
    // Display selected files
    imageFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'uploaded-file';
        fileItem.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>
                <circle cx="9" cy="9" r="2"/>
                <path d="M21 15l-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
            </svg>
            <span>${escapeHtml(file.name)}</span>
            <button type="button" onclick="removeFile(${index})" style="background: none; border: none; color: var(--danger); cursor: pointer;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 6L6 18"/><path d="M6 6l12 12"/>
                </svg>
                </button>
        `;
        uploadedFiles.appendChild(fileItem);
    });
}

function removeFile(index) {
    const fileItems = dashboard.getElement('uploaded-files').querySelectorAll('.uploaded-file');
    if (fileItems[index]) {
        fileItems[index].remove();
    }
}

// Form Submission
async function handleAddUser(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const name = formData.get('name')?.trim();
    
    // Enhanced validation
    if (!name) {
        showNotification('Please enter a name', 'error');
        return;
    }
    
    // Collect photos from both sources
    let allFiles = [];
    
    if (currentUploadMode === 'file') {
        // Get files from file input
        const fileInput = document.getElementById('user-photos');
        const files = fileInput ? Array.from(fileInput.files) : [];
        
        // Validate file types
        const validFiles = files.filter(file => file.type.startsWith('image/'));
        if (validFiles.length === 0 && files.length > 0) {
            showNotification('Please select valid image files', 'error');
            return;
        }
        
        if (validFiles.length < files.length) {
            showNotification(`${files.length - validFiles.length} non-image files were skipped`, 'warning');
        }
        
        allFiles = validFiles;
    } else {
        // Use captured photos from camera
        allFiles = capturedPhotos;
    }
    
    // Check if we have any photos
    if (allFiles.length === 0) {
        const source = currentUploadMode === 'file' ? 'select at least one photo' : 'capture at least one photo with the camera';
        showNotification(`Please ${source}`, 'error');
        return;
    }
    
    try {
        // Show loading state
        showNotification('Creating user...', 'info');
        
        // Prepare form data for API
        const apiFormData = new FormData();
        apiFormData.append('name', name);
        
        // Add all collected files (from file upload or camera)
        allFiles.forEach(file => {
            apiFormData.append('photos', file);
        });
        
        console.log('Sending user creation request:', {
            name: name,
            fileCount: allFiles.length,
            fileNames: allFiles.map(f => f.name),
            source: currentUploadMode
        });
        
        // API call to create user
        const response = await fetch('/api/users', {
            method: 'POST',
            body: apiFormData
        });
        
        const result = await response.json();
        console.log('API response:', result);
        
        if (response.ok && result.success) {
            const photoSource = currentUploadMode === 'file' ? 'uploaded files' : 'camera captures';
            showNotification(
                `User "${name}" created with ${result.face_count} face encodings from ${photoSource}`, 
                'success'
            );
            closeModal();
            // Refresh users list
            loadUsers();
        } else {
            throw new Error(result.detail || result.error || `HTTP ${response.status}`);
        }
        
    } catch (error) {
        console.error('Error creating user:', error);
        
        if (error.message.includes('409') || error.message.includes('already exists')) {
            showNotification('User already exists', 'error');
        } else if (error.message.includes('400') || error.message.includes('No faces detected')) {
            showNotification('No faces detected in the uploaded photos. Please use clear face photos.', 'error');
        } else if (error.message.includes('422')) {
            showNotification('Invalid file format or data', 'error');
        } else {
            showNotification(`Failed to add user: ${error.message}`, 'error');
        }
    }
}

// Recognition Management
function startLiveRecognition() {
    toggleRecognition();
}

async function toggleRecognition() {
    if (dashboard.isRecognitionActive) {
        stopRecognition();
    } else {
        await startRecognition();
    }
}

async function startRecognition() {
    try {
        const video = dashboard.getElement('video-stream');
        const status = dashboard.getElement('recognition-status');
        const canvas = dashboard.getElement('video-canvas');
        const resultsDiv = document.getElementById('recognition-results');

        if (!video) return;

        dashboard.videoStream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            } 
        });
        
        video.srcObject = dashboard.videoStream;
        dashboard.isRecognitionActive = true;
        updateRecognitionButton();
        
        // Hide status overlay
        if (status && status.parentElement) {
            status.parentElement.style.display = 'none';
        }
        
        // Start face recognition loop
        if (canvas) {
            const ctx = canvas.getContext('2d');
            canvas.width = 640;
            canvas.height = 480;
            
            // Recognition loop
            dashboard.recognitionInterval = setInterval(async () => {
                if (video.readyState >= 2) {
                    try {
                        // Draw video frame to canvas
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        
                        // Convert canvas to base64
                        const imageData = canvas.toDataURL('image/jpeg', 0.8);
                        
                        // Call recognition API
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
                        
                        // Update results
                        if (resultsDiv && result.success) {
                            updateRecognitionResults(result, resultsDiv);
                        }
                        
                    } catch (error) {
                        console.error('Recognition error:', error);
                    }
                }
            }, 2000); // Run recognition every 2 seconds
        }
        
        showNotification('Live recognition started', 'success');
    } catch (error) {
        console.error('Error starting recognition:', error);
        if (error.name === 'NotAllowedError') {
            showNotification('Camera access denied. Please allow camera access.', 'error');
        } else if (error.name === 'NotFoundError') {
            showNotification('No camera found on this device.', 'error');
        } else {
            showNotification('Failed to start camera', 'error');
        }
    }
}

function stopRecognition() {
    if (dashboard.videoStream) {
        dashboard.videoStream.getTracks().forEach(track => track.stop());
        dashboard.videoStream = null;
    }
    
    // Stop recognition interval
    if (dashboard.recognitionInterval) {
        clearInterval(dashboard.recognitionInterval);
        dashboard.recognitionInterval = null;
    }
    
    const video = dashboard.getElement('video-stream');
    const status = dashboard.getElement('recognition-status');
    const resultsDiv = document.getElementById('recognition-results');

    if (video) video.srcObject = null;
    
    // Show status overlay again
    if (status && status.parentElement) {
        status.parentElement.style.display = 'flex';
        status.innerHTML = `
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M16 16v1a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h2"/>
                <path d="M15 6l6 6-6 6"/>
            </svg>
            <p>Click start to begin recognition</p>
        `;
    }
    
    // Clear results
    if (resultsDiv) {
        resultsDiv.innerHTML = '<p>Recognition stopped</p>';
    }
    
    dashboard.isRecognitionActive = false;
    updateRecognitionButton();
    
    showNotification('Live recognition stopped', 'info');
}

function updateRecognitionButton() {
    const btn = document.getElementById('start-recognition-btn');
    if (btn) {
        const svg = btn.querySelector('svg');
        if (svg) {
            // Update button icon based on state
            if (dashboard.isRecognitionActive) {
                // Stop icon (square)
                svg.innerHTML = `<rect width="6" height="6" x="9" y="9"/>`;
                btn.title = 'Stop Recognition';
            } else {
                // Play icon
                svg.innerHTML = `<polygon points="5,3 19,12 5,21"/>`;
                btn.title = 'Start Recognition';
            }
        }
    }
}

function captureFrame() {
    if (!dashboard.videoStream) {
        showNotification('Start recognition first', 'warning');
        return;
    }
    
    const video = dashboard.getElement('video-stream');
    const canvas = dashboard.getElement('video-canvas');
    
    if (video && canvas) {
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        
        // Draw current frame
        ctx.drawImage(video, 0, 0);
        
        // Create download link
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `face-capture-${new Date().getTime()}.jpg`;
            a.click();
            URL.revokeObjectURL(url);
        }, 'image/jpeg', 0.9);
        
        showNotification('Frame captured and downloaded', 'success');
    }
}

// Recognition Results Update Function
function updateRecognitionResults(result, resultsDiv) {
    if (!result.recognized || result.results.length === 0) {
        resultsDiv.innerHTML = `
            <div class="recognition-result no-match">
                <div class="result-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M15 9l-6 6"/>
                        <path d="M9 9l6 6"/>
                    </svg>
                </div>
                <div class="result-content">
                    <p><strong>No Match Found</strong></p>
                    <span>${result.faces_detected} face(s) detected</span>
                </div>
                <div class="result-time">${new Date().toLocaleTimeString()}</div>
            </div>
        `;
    } else {
        const resultsHtml = result.results.map(person => `
            <div class="recognition-result match">
                <div class="result-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                        <polyline points="22,4 12,14.01 9,11.01"/>
                    </svg>
                </div>
                <div class="result-content">
                    <p><strong>${escapeHtml(person.name)}</strong></p>
                    <span>Confidence: ${Math.round(person.confidence * 100)}%</span>
                    <span>Distance: ${person.distance.toFixed(3)}</span>
                </div>
                <div class="result-time">${new Date().toLocaleTimeString()}</div>
            </div>
        `).join('');
        
        resultsDiv.innerHTML = resultsHtml;
    }
    
    // Auto-scroll to latest result
    resultsDiv.scrollTop = resultsDiv.scrollHeight;
}

// Add User Details View Function
window.viewUserDetails = async (username) => {
    try {
        showNotification('Loading user details...', 'info');
        
        const response = await fetch(`/api/user/${encodeURIComponent(username)}`);
        const result = await response.json();
        
        if (result.success) {
            const user = result.user;
            showNotification(
                `User: ${user.name} | Face Samples: ${user.face_count} | Created: ${formatDate(user.created_at)}`,
                'info',
                10000
            );
        } else {
            throw new Error(result.error || 'Failed to load user details');
        }
        
    } catch (error) {
        console.error('Error loading user details:', error);
        showNotification(`Failed to load user details: ${error.message}`, 'error');
    }
};

// Notification System
function showNotification(message, type = 'info', duration = 5000) {
    const notificationsContainer = dashboard.getElement('notifications');
    if (!notificationsContainer) return;
    
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
            <p>${escapeHtml(message)}</p>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6L6 18"/><path d="M6 6l12 12"/>
            </svg>
        </button>
    `;

    notificationsContainer.appendChild(notification);

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

// User Actions
function viewUser(userName) {
    showNotification(`Viewing details for ${userName}`, 'info');
    // TODO: Implement user details modal
}

function deleteUser(userName) {
    if (confirm(`Are you sure you want to delete ${userName}?`)) {
        // TODO: Implement user deletion
        showNotification(`User ${userName} deleted`, 'success');
        loadUsers(); // Refresh list
    }
}

// Export and Settings
function exportData() {
    showNotification('Data export feature coming soon', 'info');
}

function openSettings() {
    showNotification('Settings panel coming soon', 'info');
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (error) {
        return 'Unknown';
    }
}

// Page Visibility API - Pause refresh when tab is not visible
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Dashboard hidden - pausing refresh');
    } else {
        console.log('Dashboard visible - resuming refresh');
        if (!dashboard.refreshInterval) {
            startAutoRefresh();
        }
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
    stopRecognition();
});

// Global Functions (called from HTML)
window.showAddUserModal = () => {
    const modal = dashboard.getElement('add-user-modal');
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
};

window.closeModal = () => {
    const modal = dashboard.getElement('add-user-modal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
};

window.refreshUsers = () => {
    loadUsers();
    showNotification('Users refreshed', 'success');
};

window.startLiveRecognition = () => {
    if (!dashboard.isRecognitionActive) {
        startRecognition();
    }
};

window.toggleRecognition = () => {
    if (dashboard.isRecognitionActive) {
        stopRecognition();
    } else {
        startRecognition();
    }
};

window.captureFrame = () => {
    captureFrame();
};

window.exportData = () => {
    showNotification('Data export started', 'info');
};

window.openSettings = () => {
    showNotification('Settings opened', 'info');
};

window.editUser = (userId) => {
    showNotification(`Edit user: ${userId}`, 'info');
};

window.deleteUser = async (username) => {
    if (confirm(`Are you sure you want to delete user "${username}"?`)) {
        try {
            showNotification('Deleting user...', 'info');
            
            const response = await fetch(`/api/users/${encodeURIComponent(username)}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                showNotification(`User "${username}" deleted successfully`, 'success');
                // Refresh users list
                loadUsers();
            } else {
                throw new Error(result.error || 'Failed to delete user');
            }
            
        } catch (error) {
            console.error('Error deleting user:', error);
            showNotification(`Failed to delete user: ${error.message}`, 'error');
        }
    }
};

// Camera Functionality for User Creation
window.switchUploadTab = (mode) => {
    currentUploadMode = mode;
    const fileTab = document.getElementById('file-tab');
    const cameraTab = document.getElementById('camera-tab');
    const fileContent = document.getElementById('file-upload-content');
    const cameraContent = document.getElementById('camera-upload-content');
    
    if (mode === 'file') {
        fileTab.classList.add('active');
        cameraTab.classList.remove('active');
        fileContent.classList.remove('hidden');
        cameraContent.classList.add('hidden');
        stopCamera(); // Stop camera when switching to file mode
    } else {
        cameraTab.classList.add('active');
        fileTab.classList.remove('active');
        cameraContent.classList.remove('hidden');
        fileContent.classList.add('hidden');
    }
};

window.startCamera = async () => {
    try {
        const video = document.getElementById('camera-preview');
        const placeholder = document.getElementById('camera-placeholder');
        const startBtn = document.getElementById('start-camera-btn');
        const captureBtn = document.getElementById('capture-photo-btn');
        const stopBtn = document.getElementById('stop-camera-btn');
        
        // Request camera access
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });
        
        video.srcObject = cameraStream;
        
        // Show video, hide placeholder
        video.style.display = 'block';
        placeholder.style.display = 'none';
        
        // Update button states
        startBtn.classList.add('hidden');
        captureBtn.classList.remove('hidden');
        stopBtn.classList.remove('hidden');
        
        showNotification('Camera started successfully', 'success');
        
    } catch (error) {
        console.error('Error starting camera:', error);
        if (error.name === 'NotAllowedError') {
            showNotification('Camera access denied. Please allow camera access.', 'error');
        } else if (error.name === 'NotFoundError') {
            showNotification('No camera found on this device.', 'error');
        } else {
            showNotification('Failed to start camera', 'error');
        }
    }
};

window.stopCamera = () => {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    
    const video = document.getElementById('camera-preview');
    const placeholder = document.getElementById('camera-placeholder');
    const startBtn = document.getElementById('start-camera-btn');
    const captureBtn = document.getElementById('capture-photo-btn');
    const stopBtn = document.getElementById('stop-camera-btn');
    
    if (video) {
        video.style.display = 'none';
        video.srcObject = null;
    }
    
    if (placeholder) {
        placeholder.style.display = 'flex';
    }
    
    // Update button states
    if (startBtn) startBtn.classList.remove('hidden');
    if (captureBtn) captureBtn.classList.add('hidden');
    if (stopBtn) stopBtn.classList.add('hidden');
};

window.capturePhoto = () => {
    const video = document.getElementById('camera-preview');
    const canvas = document.getElementById('capture-canvas');
    
    if (!video || !canvas) {
        showNotification('Camera not ready', 'error');
        return;
    }
    
    if (video.readyState < 2) {
        showNotification('Please wait for camera to load', 'warning');
        return;
    }
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    
    // Draw current video frame to canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert canvas to blob
    canvas.toBlob((blob) => {
        if (blob) {
            // Create a File object from the blob
            const timestamp = new Date().getTime();
            const file = new File([blob], `camera-capture-${timestamp}.jpg`, {
                type: 'image/jpeg',
                lastModified: timestamp
            });
            
            // Add to captured photos array
            capturedPhotos.push(file);
            
            // Display in uploaded files area
            displayCapturedPhoto(file, capturedPhotos.length - 1);
            
            // Update counter
            updatePhotoCounter();
            
            showNotification(`Photo ${capturedPhotos.length} captured successfully`, 'success');
            
            // Auto-suggest stopping after 5 photos
            if (capturedPhotos.length >= 5) {
                showNotification('5 photos captured. Consider stopping camera now.', 'info');
            }
        }
    }, 'image/jpeg', 0.8);
};

function displayCapturedPhoto(file, index) {
    const uploadedFiles = document.getElementById('uploaded-files');
    if (!uploadedFiles) return;
    
    const fileItem = document.createElement('div');
    fileItem.className = 'uploaded-file captured';
    fileItem.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
            <circle cx="12" cy="13" r="3"/>
        </svg>
        <span>${escapeHtml(file.name)}</span>
        <span class="file-source camera">📷 Camera</span>
        <button type="button" onclick="removeCapturedPhoto(${index})" style="background: none; border: none; color: var(--danger); cursor: pointer;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6L6 18"/><path d="M6 6l12 12"/>
            </svg>
        </button>
    `;
    uploadedFiles.appendChild(fileItem);
}

window.removeCapturedPhoto = (index) => {
    capturedPhotos.splice(index, 1);
    updatePhotoCounter();
    
    // Refresh the uploaded files display
    const uploadedFiles = document.getElementById('uploaded-files');
    if (uploadedFiles) {
        uploadedFiles.innerHTML = '';
        capturedPhotos.forEach((file, i) => {
            displayCapturedPhoto(file, i);
        });
    }
    
    showNotification('Photo removed', 'info');
};

function updatePhotoCounter() {
    const counter = document.getElementById('photo-count');
    if (counter) {
        counter.textContent = capturedPhotos.length;
    }
}

// Main Initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Modern Dashboard initializing...');
    
    // Initialize dashboard state
    dashboard.cacheElements();
    
    // Initialize features
    initializeTheme();
    initializeEventListeners();
    initializeFileUpload();
    
    // Load initial data
    loadInitialData();
    
    // Start auto-refresh
    startAutoRefresh();
    
    console.log('✅ Dashboard initialization complete');
}); 