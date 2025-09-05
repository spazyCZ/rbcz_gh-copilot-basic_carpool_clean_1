/**
 * Main JavaScript module for the parking reservation application.
 * 
 * Provides common utilities, API communication, and shared functionality
 * for all pages. Follows the REST-only data flow policy.
 */

// Application configuration
const APP_CONFIG = {
    API_BASE_URL: '/api/v1',
    DEFAULT_TIMEOUT: 10000,
    POLLING_INTERVAL: 30000
};

// API utility functions
const API = {
    /**
     * Make authenticated API request
     * @param {string} endpoint - API endpoint (without base URL)
     * @param {Object} options - Fetch options
     * @returns {Promise} API response
     */
    async request(endpoint, options = {}) {
        const url = `${APP_CONFIG.API_BASE_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            showLoading(true);
            
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new APIError(data.error || { code: 'UNKNOWN_ERROR', message: 'Request failed' });
            }
            
            return data;
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError({ code: 'NETWORK_ERROR', message: 'Network request failed' });
        } finally {
            showLoading(false);
        }
    },

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * PATCH request
     */
    async patch(endpoint, data) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
};

// Custom error class for API errors
class APIError extends Error {
    constructor(errorData) {
        super(errorData.message);
        this.code = errorData.code;
        this.name = 'APIError';
    }
}

// UI utility functions
const UI = {
    /**
     * Show alert message to user
     * @param {string} message - Message to display
     * @param {string} type - Alert type (success, error, warning, info)
     */
    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container');
        if (!alertContainer) return;
        
        const alertClass = type === 'error' ? 'danger' : type;
        const alertHTML = `
            <div class="alert alert-${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.innerHTML = alertHTML;
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = alertContainer.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    },

    /**
     * Clear all alerts
     */
    clearAlerts() {
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            alertContainer.innerHTML = '';
        }
    },

    /**
     * Format date for display
     * @param {string|Date} date - Date to format
     * @returns {string} Formatted date string
     */
    formatDate(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    /**
     * Format datetime for display
     * @param {string|Date} datetime - Datetime to format
     * @returns {string} Formatted datetime string
     */
    formatDateTime(datetime) {
        if (!datetime) return '';
        const d = new Date(datetime);
        return d.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};

// Global loading state management
function showLoading(show = true) {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        if (show) {
            spinner.classList.remove('d-none');
        } else {
            spinner.classList.add('d-none');
        }
    }
}

// Global error handler
function handleError(error) {
    console.error('Application error:', error);
    
    if (error instanceof APIError) {
        let message = error.message;
        
        // Handle specific error codes
        switch (error.code) {
            case 'AUTH_REQUIRED':
                message = 'Please log in to continue.';
                // Redirect to login page
                window.location.href = '/login';
                return;
            case 'RESERVATION_CONFLICT':
                message = 'This spot is already reserved for the selected date.';
                break;
            case 'RATE_LIMIT_EXCEEDED':
                message = 'Too many requests. Please try again later.';
                break;
            case 'NETWORK_ERROR':
                message = 'Network error. Please check your connection.';
                break;
        }
        
        UI.showAlert(message, 'error');
    } else {
        UI.showAlert('An unexpected error occurred. Please try again.', 'error');
    }
}

// Global logout function
async function logout() {
    try {
        await API.post('/auth/logout', {});
        window.location.href = '/login';
    } catch (error) {
        handleError(error);
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Parking Reservation System initialized');
    
    // Set minimum date for date inputs to today
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(input => {
        if (!input.hasAttribute('min')) {
            input.setAttribute('min', today);
        }
    });
    
    // Global form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Export for other modules
window.APP_CONFIG = APP_CONFIG;
window.API = API;
window.UI = UI;
window.handleError = handleError;