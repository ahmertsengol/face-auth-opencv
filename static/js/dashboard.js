/**
 * Face Recognition Dashboard - Optimized JavaScript with Error Handling
 */

// Global variables
let refreshInterval;
let isLoading = false;
let retryCount = 0;
const MAX_RETRIES = 3;
const API_BASE_URL = window.location.origin;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard initializing...');
    
    // Check if APIs are available before loading data
    checkApiHealth().then(isHealthy => {
        if (isHealthy) {
            loadUsers();
            loadStats();
            startAutoRefresh();
            console.log('✅ Dashboard initialized successfully');
        } else {
            console.error('❌ API not available, retrying...');
            setTimeout(() => window.location.reload(), 5000);
        }
    });
});

/**
 * Check API health before making other requests
 */
async function checkApiHealth() {
    try {
        const response = await fetchWithRetry('/api/health', { timeout: 5000 });
        return response.ok;
    } catch (error) {
        console.error('API Health check failed:', error);
        return false;
    }
}

/**
 * Enhanced fetch with retry logic and timeout
 */
async function fetchWithRetry(url, options = {}) {
    const { timeout = 10000, retries = MAX_RETRIES, ...fetchOptions } = options;
    
    for (let i = 0; i <= retries; i++) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            
            const response = await fetch(API_BASE_URL + url, {
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
            
            // Wait before retry (exponential backoff)
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
        }
    }
}

/**
 * Load and display users with enhanced error handling
 */
async function loadUsers() {
    if (isLoading) return;
    
    try {
        isLoading = true;
        const tbody = document.getElementById('users-tbody');
        
        // Show loading
        showLoadingState(tbody);
        
        const response = await fetchWithRetry('/api/users');
        const data = await response.json();
        
        if (data.success) {
            displayUsers(data.users);
            retryCount = 0; // Reset retry count on success
        } else {
            throw new Error(data.error || 'Unknown API error');
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showError(`Kullanıcılar yüklenemedi: ${error.message}`);
        
        // Auto-retry with exponential backoff
        if (retryCount < MAX_RETRIES) {
            retryCount++;
            setTimeout(() => {
                console.log(`🔄 Retrying users load (attempt ${retryCount}/${MAX_RETRIES})`);
                loadUsers();
            }, Math.pow(2, retryCount) * 2000);
        }
    } finally {
        isLoading = false;
    }
}

/**
 * Show loading state in table
 */
function showLoadingState(tbody) {
    tbody.innerHTML = `
        <tr>
            <td colspan="4" class="text-center">
                <div class="d-flex align-items-center justify-content-center py-3">
                    <div class="spinner-border text-primary me-2" role="status">
                        <span class="visually-hidden">Yükleniyor...</span>
                    </div>
                    <span>Veriler yükleniyor...</span>
                </div>
            </td>
        </tr>
    `;
}

/**
 * Display users in table with enhanced UI
 */
function displayUsers(users) {
    const tbody = document.getElementById('users-tbody');
    
    if (users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-muted py-4">
                    <i class="bi bi-info-circle display-6 text-muted"></i>
                    <div class="mt-2">Henüz kayıtlı kullanıcı yok</div>
                    <small>Kullanıcı eklemek için "Kullanıcı Ekle" butonunu kullanın</small>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = users.map((user, index) => `
        <tr class="fade-in" style="animation-delay: ${index * 0.1}s">
            <td>
                <div class="d-flex align-items-center">
                    <div class="bg-primary rounded-circle text-white d-flex align-items-center justify-content-center me-2" style="width: 32px; height: 32px; font-size: 0.8rem;">
                        ${escapeHtml(user.name).charAt(0).toUpperCase()}
                    </div>
                    <strong>${escapeHtml(user.name)}</strong>
                </div>
            </td>
            <td>
                <span class="badge bg-success">${user.face_count}</span>
                <small class="text-muted ms-1">örnek</small>
            </td>
            <td>
                <small class="text-muted">
                    ${formatDate(user.created_at)}
                </small>
            </td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-outline-info" onclick="viewUser('${escapeHtml(user.name)}')" title="Görüntüle">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteUser('${escapeHtml(user.name)}')" title="Sil">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

/**
 * Load and display statistics with error handling
 */
async function loadStats() {
    try {
        const response = await fetchWithRetry('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            displayStats(data.stats);
        } else {
            throw new Error(data.error || 'Stats API error');
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        // Don't show error for stats, just keep previous values
        displayStats({
            total_users: '?',
            total_face_encodings: '?',
            average_encodings_per_user: '?'
        });
    }
}

/**
 * Display statistics with animation
 */
function displayStats(stats) {
    // Animate number changes
    animateNumber('stat-users', stats.total_users);
    animateNumber('stat-encodings', stats.total_face_encodings);
    animateNumber('stat-avg', stats.average_encodings_per_user);
    animateNumber('total-users', stats.total_users);
}

/**
 * Animate number changes
 */
function animateNumber(elementId, newValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const currentValue = element.textContent;
    if (currentValue !== newValue.toString()) {
        element.style.transform = 'scale(1.1)';
        element.style.transition = 'transform 0.2s';
        
        setTimeout(() => {
            element.textContent = newValue;
            element.style.transform = 'scale(1)';
        }, 100);
    }
}

/**
 * Refresh all data with user feedback
 */
function refreshStats() {
    console.log('🔄 Refreshing dashboard...');
    
    // Show refresh indicator
    const refreshBtn = document.querySelector('button[onclick="refreshStats()"]');
    if (refreshBtn) {
        const originalText = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> <span class="spinner-border spinner-border-sm"></span>';
        refreshBtn.disabled = true;
        
        // Reset button after refresh
        setTimeout(() => {
            refreshBtn.innerHTML = originalText;
            refreshBtn.disabled = false;
        }, 2000);
    }
    
    loadUsers();
    loadStats();
}

/**
 * Start auto-refresh with user notification
 */
function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        if (!document.hidden) { // Only refresh if page is visible
            refreshStats();
        }
    }, 30000); // 30 seconds
    
    console.log('🔄 Auto-refresh started (30s interval)');
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
        console.log('⏹️ Auto-refresh stopped');
    }
}

/**
 * Enhanced error display
 */
function showError(message) {
    console.error('Dashboard Error:', message);
    
    const tbody = document.getElementById('users-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="4" class="text-center text-danger py-4">
                <i class="bi bi-exclamation-triangle display-6 text-danger"></i>
                <div class="mt-2">${escapeHtml(message)}</div>
                <button class="btn btn-sm btn-outline-primary mt-2" onclick="loadUsers()">
                    <i class="bi bi-arrow-clockwise"></i> Tekrar Dene
                </button>
            </td>
        </tr>
    `;
}

/**
 * Enhanced user interaction functions
 */
function startRecognition() {
    showNotification('🎯 Canlı tanıma özelliği yakında eklenecek!', 'info');
}

function showAddUser() {
    showNotification('👤 Web üzerinden kullanıcı ekleme özelliği yakında gelecek!', 'info');
}

function viewUser(userName) {
    showNotification(`👁️ ${userName} kullanıcısının detay sayfası yakında hazır olacak!`, 'info');
}

function deleteUser(userName) {
    if (confirm(`⚠️ ${userName} kullanıcısını silmek istediğinizden emin misiniz?`)) {
        showNotification('🗑️ Web üzerinden kullanıcı silme özelliği yakında eklenecek!', 'warning');
    }
}

/**
 * Show notification (simple toast-like notification)
 */
function showNotification(message, type = 'info') {
    const alertClass = {
        'info': 'alert-info',
        'success': 'alert-success',
        'warning': 'alert-warning',
        'danger': 'alert-danger'
    }[type] || 'alert-info';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} position-fixed top-0 end-0 m-3 fade-in`;
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}

/**
 * Utility: Escape HTML (XSS protection)
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Utility: Format date with error handling
 */
function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('tr-TR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return dateString?.substring(0, 19)?.replace('T', ' ') || 'Bilinmiyor';
    }
}

/**
 * Handle page visibility change
 */
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.log('📱 Page hidden, pausing auto-refresh');
    } else {
        console.log('👀 Page visible, resuming auto-refresh');
        // Refresh data when page becomes visible again
        setTimeout(refreshStats, 1000);
    }
});

/**
 * Handle window beforeunload
 */
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
    console.log('👋 Dashboard cleanup completed');
});

/**
 * Handle connection errors
 */
window.addEventListener('online', function() {
    showNotification('🌐 İnternet bağlantısı yeniden kuruldu', 'success');
    setTimeout(refreshStats, 1000);
});

window.addEventListener('offline', function() {
    showNotification('📡 İnternet bağlantısı kesildi', 'warning');
}); 