/**
 * Main JavaScript file for the Carpool application.
 * Contains common functionality used across multiple pages.
 */

// Global application object
window.CarpoolApp = {
    // Configuration
    config: {
        ajaxTimeout: 10000,
        refreshInterval: 30000,
        chartColors: {
            primary: '#007bff',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#17a2b8'
        }
    },

    // Utility functions
    utils: {
        /**
         * Format a date string for display
         * @param {string} dateString - ISO date string
         * @param {object} options - Formatting options
         * @returns {string} Formatted date
         */
        formatDate: function(dateString, options = {}) {
            const date = new Date(dateString);
            const defaultOptions = {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            };
            return date.toLocaleDateString('en-US', { ...defaultOptions, ...options });
        },

        /**
         * Format a datetime string for display
         * @param {string} datetimeString - ISO datetime string
         * @returns {string} Formatted datetime
         */
        formatDateTime: function(datetimeString) {
            const date = new Date(datetimeString);
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        },

        /**
         * Show a Bootstrap toast notification
         * @param {string} message - Message to display
         * @param {string} type - Type of notification (success, error, warning, info)
         */
        showToast: function(message, type = 'info') {
            const toastContainer = this.getToastContainer();
            const toastId = 'toast-' + Date.now();
            
            const toastHtml = `
                <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">
                            <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                            ${message}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;
            
            toastContainer.insertAdjacentHTML('beforeend', toastHtml);
            
            const toastElement = document.getElementById(toastId);
            const toast = new bootstrap.Toast(toastElement, {
                autohide: true,
                delay: type === 'error' ? 8000 : 5000
            });
            
            toast.show();
            
            // Remove element after hiding
            toastElement.addEventListener('hidden.bs.toast', function() {
                toastElement.remove();
            });
        },

        /**
         * Get or create toast container
         * @returns {HTMLElement} Toast container element
         */
        getToastContainer: function() {
            let container = document.getElementById('toast-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'toast-container';
                container.className = 'toast-container position-fixed top-0 end-0 p-3';
                container.style.zIndex = '1100';
                document.body.appendChild(container);
            }
            return container;
        },

        /**
         * Get icon for toast type
         * @param {string} type - Toast type
         * @returns {string} FontAwesome icon class
         */
        getToastIcon: function(type) {
            const icons = {
                success: 'check-circle',
                error: 'exclamation-triangle',
                warning: 'exclamation-circle',
                info: 'info-circle'
            };
            return icons[type] || 'info-circle';
        },

        /**
         * Debounce function execution
         * @param {Function} func - Function to debounce
         * @param {number} wait - Wait time in milliseconds
         * @returns {Function} Debounced function
         */
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        /**
         * Get CSRF token from meta tag or form
         * @returns {string} CSRF token
         */
        getCSRFToken: function() {
            // Try to get from meta tag first
            const metaToken = document.querySelector('meta[name="csrf-token"]');
            if (metaToken) {
                return metaToken.getAttribute('content');
            }
            
            // Fall back to form input
            const inputToken = document.querySelector('input[name="csrf_token"]');
            if (inputToken) {
                return inputToken.value;
            }
            
            return '';
        }
    },

    // API helper functions
    api: {
        /**
         * Make an AJAX request with common error handling
         * @param {string} url - Request URL
         * @param {object} options - Request options
         * @returns {Promise} Fetch promise
         */
        request: function(url, options = {}) {
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                timeout: CarpoolApp.config.ajaxTimeout
            };

            // Add CSRF token for POST requests
            if (options.method === 'POST' || options.method === 'PUT' || options.method === 'DELETE') {
                defaultOptions.headers['X-CSRFToken'] = CarpoolApp.utils.getCSRFToken();
            }

            const mergedOptions = { ...defaultOptions, ...options };
            
            // Merge headers
            if (options.headers) {
                mergedOptions.headers = { ...defaultOptions.headers, ...options.headers };
            }

            return fetch(url, mergedOptions)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('API request failed:', error);
                    CarpoolApp.utils.showToast('Request failed: ' + error.message, 'error');
                    throw error;
                });
        },

        /**
         * Get dashboard statistics
         * @returns {Promise} API response promise
         */
        getDashboardStats: function() {
            return this.request('/api/dashboard-stats');
        },

        /**
         * Get parking spot availability
         * @param {string} date - Date in YYYY-MM-DD format
         * @returns {Promise} API response promise
         */
        getParkingSpots: function(date) {
            const url = date ? `/api/parking-spots?date=${date}` : '/api/parking-spots';
            return this.request(url);
        },

        /**
         * Get recent activity
         * @param {number} limit - Number of activities to fetch
         * @returns {Promise} API response promise
         */
        getRecentActivity: function(limit = 10) {
            return this.request(`/api/recent-activity?limit=${limit}`);
        },

        /**
         * Get upcoming reservations
         * @param {number} days - Number of days to look ahead
         * @returns {Promise} API response promise
         */
        getUpcomingReservations: function(days = 7) {
            return this.request(`/api/upcoming-reservations?days=${days}`);
        }
    },

    // Chart helper functions
    charts: {
        /**
         * Create a doughnut chart
         * @param {HTMLCanvasElement} canvas - Canvas element
         * @param {object} data - Chart data
         * @param {object} options - Chart options
         * @returns {Chart} Chart.js instance
         */
        createDoughnutChart: function(canvas, data, options = {}) {
            const defaultOptions = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            };

            return new Chart(canvas, {
                type: 'doughnut',
                data: data,
                options: { ...defaultOptions, ...options }
            });
        },

        /**
         * Create a line chart
         * @param {HTMLCanvasElement} canvas - Canvas element
         * @param {object} data - Chart data
         * @param {object} options - Chart options
         * @returns {Chart} Chart.js instance
         */
        createLineChart: function(canvas, data, options = {}) {
            const defaultOptions = {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            };

            return new Chart(canvas, {
                type: 'line',
                data: data,
                options: { ...defaultOptions, ...options }
            });
        }
    },

    // Form helper functions
    forms: {
        /**
         * Validate a form and show errors
         * @param {HTMLFormElement} form - Form element
         * @returns {boolean} True if valid
         */
        validate: function(form) {
            let isValid = true;
            const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');

            inputs.forEach(input => {
                this.clearFieldError(input);
                
                if (!input.value.trim()) {
                    this.showFieldError(input, 'This field is required');
                    isValid = false;
                }
            });

            return isValid;
        },

        /**
         * Show field error
         * @param {HTMLElement} field - Input field
         * @param {string} message - Error message
         */
        showFieldError: function(field, message) {
            field.classList.add('is-invalid');
            
            let feedback = field.parentNode.querySelector('.invalid-feedback');
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentNode.appendChild(feedback);
            }
            
            feedback.textContent = message;
        },

        /**
         * Clear field error
         * @param {HTMLElement} field - Input field
         */
        clearFieldError: function(field) {
            field.classList.remove('is-invalid');
            const feedback = field.parentNode.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.remove();
            }
        },

        /**
         * Serialize form data to JSON
         * @param {HTMLFormElement} form - Form element
         * @returns {object} Form data as object
         */
        serialize: function(form) {
            const formData = new FormData(form);
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                if (data[key]) {
                    // Handle multiple values (e.g., checkboxes)
                    if (Array.isArray(data[key])) {
                        data[key].push(value);
                    } else {
                        data[key] = [data[key], value];
                    }
                } else {
                    data[key] = value;
                }
            }
            
            return data;
        }
    },

    // Initialize application
    init: function() {
        console.log('Carpool App initialized');

        // Set up global error handler
        window.addEventListener('error', function(event) {
            console.error('Global error:', event.error);
        });

        // Set up CSRF token in meta tag if not present
        if (!document.querySelector('meta[name="csrf-token"]')) {
            const token = this.utils.getCSRFToken();
            if (token) {
                const meta = document.createElement('meta');
                meta.name = 'csrf-token';
                meta.content = token;
                document.head.appendChild(meta);
            }
        }

        // Auto-dismiss alerts after 5 seconds
        setTimeout(() => {
            const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
            alerts.forEach(alert => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, 5000);

        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    CarpoolApp.init();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CarpoolApp;
}
