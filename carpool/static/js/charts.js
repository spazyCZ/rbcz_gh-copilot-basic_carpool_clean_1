/**
 * Chart utilities for the carpool application
 * Provides Chart.js integration and common chart configurations
 */

// Default chart colors
const CHART_COLORS = {
    primary: '#007bff',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    info: '#17a2b8',
    light: '#f8f9fa',
    dark: '#343a40'
};

// Chart color palette
const COLOR_PALETTE = [
    '#007bff', '#28a745', '#ffc107', '#dc3545', '#17a2b8',
    '#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#6c757d'
];

/**
 * Default chart options
 */
const DEFAULT_CHART_OPTIONS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'top',
        },
        tooltip: {
            mode: 'index',
            intersect: false,
        }
    },
    scales: {
        x: {
            display: true,
            grid: {
                display: false
            }
        },
        y: {
            display: true,
            beginAtZero: true,
            grid: {
                color: 'rgba(0,0,0,0.1)'
            }
        }
    }
};

/**
 * Chart utility class
 */
class ChartUtils {
    /**
     * Create a line chart
     * @param {HTMLCanvasElement} canvas - Canvas element
     * @param {Object} data - Chart data
     * @param {Object} options - Chart options
     * @returns {Chart} Chart instance
     */
    static createLineChart(canvas, data, options = {}) {
        const config = {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: data.datasets || []
            },
            options: {
                ...DEFAULT_CHART_OPTIONS,
                ...options,
                elements: {
                    line: {
                        tension: 0.4
                    }
                }
            }
        };

        return new Chart(canvas, config);
    }

    /**
     * Create a bar chart
     * @param {HTMLCanvasElement} canvas - Canvas element
     * @param {Object} data - Chart data
     * @param {Object} options - Chart options
     * @returns {Chart} Chart instance
     */
    static createBarChart(canvas, data, options = {}) {
        const config = {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: data.datasets || []
            },
            options: {
                ...DEFAULT_CHART_OPTIONS,
                ...options
            }
        };

        return new Chart(canvas, config);
    }

    /**
     * Create a pie chart
     * @param {HTMLCanvasElement} canvas - Canvas element
     * @param {Object} data - Chart data
     * @param {Object} options - Chart options
     * @returns {Chart} Chart instance
     */
    static createPieChart(canvas, data, options = {}) {
        const config = {
            type: 'pie',
            data: {
                labels: data.labels || [],
                datasets: data.datasets || []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                },
                ...options
            }
        };

        return new Chart(canvas, config);
    }

    /**
     * Create a doughnut chart
     * @param {HTMLCanvasElement} canvas - Canvas element
     * @param {Object} data - Chart data
     * @param {Object} options - Chart options
     * @returns {Chart} Chart instance
     */
    static createDoughnutChart(canvas, data, options = {}) {
        const config = {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: data.datasets || []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                },
                ...options
            }
        };

        return new Chart(canvas, config);
    }

    /**
     * Create a dataset with default styling
     * @param {string} label - Dataset label
     * @param {Array} data - Data array
     * @param {string} color - Primary color
     * @param {Object} options - Additional options
     * @returns {Object} Dataset object
     */
    static createDataset(label, data, color = CHART_COLORS.primary, options = {}) {
        return {
            label,
            data,
            backgroundColor: options.fill ? this.addAlpha(color, 0.2) : color,
            borderColor: color,
            borderWidth: options.borderWidth || 2,
            fill: options.fill || false,
            tension: options.tension || 0,
            ...options
        };
    }

    /**
     * Add alpha channel to a color
     * @param {string} color - Hex color
     * @param {number} alpha - Alpha value (0-1)
     * @returns {string} RGBA color string
     */
    static addAlpha(color, alpha) {
        const hex = color.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    /**
     * Get color palette for multiple datasets
     * @param {number} count - Number of colors needed
     * @returns {Array} Array of colors
     */
    static getColorPalette(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(COLOR_PALETTE[i % COLOR_PALETTE.length]);
        }
        return colors;
    }

    /**
     * Fetch chart data from API endpoint
     * @param {string} url - API endpoint URL
     * @param {Object} params - Query parameters
     * @returns {Promise} Promise resolving to chart data
     */
    static async fetchChartData(url, params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const fullUrl = queryString ? `${url}?${queryString}` : url;
            
            const response = await fetch(fullUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrf_token]')?.value || ''
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching chart data:', error);
            throw error;
        }
    }

    /**
     * Update chart data
     * @param {Chart} chart - Chart instance
     * @param {Object} newData - New data
     */
    static updateChart(chart, newData) {
        if (newData.labels) {
            chart.data.labels = newData.labels;
        }
        
        if (newData.datasets) {
            chart.data.datasets = newData.datasets;
        }
        
        chart.update();
    }

    /**
     * Create a real-time updating chart
     * @param {HTMLCanvasElement} canvas - Canvas element
     * @param {string} dataUrl - Data endpoint URL
     * @param {Object} config - Chart configuration
     * @param {number} updateInterval - Update interval in milliseconds
     * @returns {Object} Chart controller with methods
     */
    static createRealtimeChart(canvas, dataUrl, config, updateInterval = 30000) {
        let chart = null;
        let intervalId = null;

        const updateData = async () => {
            try {
                const data = await this.fetchChartData(dataUrl);
                
                if (chart) {
                    this.updateChart(chart, data);
                } else {
                    // Create chart if it doesn't exist
                    chart = new Chart(canvas, {
                        ...config,
                        data
                    });
                }
            } catch (error) {
                console.error('Error updating realtime chart:', error);
            }
        };

        const start = () => {
            updateData(); // Initial load
            intervalId = setInterval(updateData, updateInterval);
        };

        const stop = () => {
            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
            }
        };

        const destroy = () => {
            stop();
            if (chart) {
                chart.destroy();
                chart = null;
            }
        };

        return {
            start,
            stop,
            destroy,
            getChart: () => chart
        };
    }

    /**
     * Export chart as image
     * @param {Chart} chart - Chart instance
     * @param {string} filename - Download filename
     * @param {string} format - Image format (png, jpg)
     */
    static exportChart(chart, filename = 'chart', format = 'png') {
        const link = document.createElement('a');
        link.download = `${filename}.${format}`;
        link.href = chart.toBase64Image();
        link.click();
    }

    /**
     * Create responsive chart that adapts to container size
     * @param {HTMLCanvasElement} canvas - Canvas element
     * @param {Object} config - Chart configuration
     * @returns {Chart} Chart instance
     */
    static createResponsiveChart(canvas, config) {
        const observer = new ResizeObserver(() => {
            if (chart) {
                chart.resize();
            }
        });

        observer.observe(canvas.parentElement);

        const chart = new Chart(canvas, {
            ...config,
            options: {
                ...config.options,
                responsive: true,
                maintainAspectRatio: false
            }
        });

        // Store observer reference for cleanup
        chart._resizeObserver = observer;

        return chart;
    }
}

// Export for use in other modules
window.ChartUtils = ChartUtils;
window.CHART_COLORS = CHART_COLORS;
