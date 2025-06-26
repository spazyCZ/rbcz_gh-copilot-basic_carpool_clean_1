/**
 * Dashboard JavaScript functionality
 * Handles dashboard widgets, charts, and real-time updates
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

/**
 * Initialize dashboard functionality
 */
function initializeDashboard() {
    // Initialize charts
    initializeCharts();
    
    // Initialize real-time updates
    initializeRealtimeUpdates();
    
    // Initialize dashboard controls
    initializeDashboardControls();
    
    // Initialize notifications
    initializeNotifications();
    
    // Initialize quick actions
    initializeQuickActions();
}

/**
 * Initialize dashboard charts
 */
function initializeCharts() {
    // Reservations trend chart
    const reservationsTrendCanvas = document.getElementById('reservationsTrendChart');
    if (reservationsTrendCanvas) {
        ChartUtils.fetchChartData('/api/dashboard/reservations-trend')
            .then(data => {
                const chart = ChartUtils.createLineChart(reservationsTrendCanvas, {
                    labels: data.labels,
                    datasets: [{
                        label: 'Reservations',
                        data: data.values,
                        borderColor: CHART_COLORS.primary,
                        backgroundColor: ChartUtils.addAlpha(CHART_COLORS.primary, 0.1),
                        fill: true,
                        tension: 0.4
                    }]
                }, {
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            display: false
                        },
                        y: {
                            display: false
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error loading reservations trend chart:', error);
                showChartError(reservationsTrendCanvas);
            });
    }

    // Parking utilization chart
    const utilizationCanvas = document.getElementById('parkingUtilizationChart');
    if (utilizationCanvas) {
        ChartUtils.fetchChartData('/api/dashboard/parking-utilization')
            .then(data => {
                const chart = ChartUtils.createDoughnutChart(utilizationCanvas, {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: [
                            CHART_COLORS.success,
                            CHART_COLORS.warning,
                            CHART_COLORS.danger
                        ],
                        borderWidth: 0
                    }]
                }, {
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    },
                    cutout: '70%'
                });
            })
            .catch(error => {
                console.error('Error loading parking utilization chart:', error);
                showChartError(utilizationCanvas);
            });
    }

    // Carpool activity chart
    const carpoolCanvas = document.getElementById('carpoolActivityChart');
    if (carpoolCanvas) {
        ChartUtils.fetchChartData('/api/dashboard/carpool-activity')
            .then(data => {
                const chart = ChartUtils.createBarChart(carpoolCanvas, {
                    labels: data.labels,
                    datasets: [{
                        label: 'Active Carpools',
                        data: data.values,
                        backgroundColor: CHART_COLORS.info,
                        borderRadius: 4
                    }]
                }, {
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error loading carpool activity chart:', error);
                showChartError(carpoolCanvas);
            });
    }

    // Weekly stats chart
    const weeklyStatsCanvas = document.getElementById('weeklyStatsChart');
    if (weeklyStatsCanvas) {
        ChartUtils.fetchChartData('/api/dashboard/weekly-stats')
            .then(data => {
                const chart = ChartUtils.createLineChart(weeklyStatsCanvas, {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Reservations',
                            data: data.reservations,
                            borderColor: CHART_COLORS.primary,
                            backgroundColor: ChartUtils.addAlpha(CHART_COLORS.primary, 0.1),
                            fill: false,
                            tension: 0.4
                        },
                        {
                            label: 'Carpools',
                            data: data.carpools,
                            borderColor: CHART_COLORS.success,
                            backgroundColor: ChartUtils.addAlpha(CHART_COLORS.success, 0.1),
                            fill: false,
                            tension: 0.4
                        }
                    ]
                });
            })
            .catch(error => {
                console.error('Error loading weekly stats chart:', error);
                showChartError(weeklyStatsCanvas);
            });
    }
}

/**
 * Initialize real-time updates for dashboard stats
 */
function initializeRealtimeUpdates() {
    // Update dashboard stats every 30 seconds
    setInterval(updateDashboardStats, 30000);
    
    // Update recent activity every 60 seconds
    setInterval(updateRecentActivity, 60000);
}

/**
 * Update dashboard statistics
 */
async function updateDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const stats = await response.json();

        // Update stat cards
        updateStatCard('total-reservations', stats.total_reservations);
        updateStatCard('active-carpools', stats.active_carpools);
        updateStatCard('available-spots', stats.available_spots);
        updateStatCard('system-users', stats.system_users);

        // Update progress bars if they exist
        updateProgressBar('utilization-progress', stats.utilization_percentage);

    } catch (error) {
        console.error('Error updating dashboard stats:', error);
    }
}

/**
 * Update recent activity feed
 */
async function updateRecentActivity() {
    try {
        const response = await fetch('/api/dashboard/recent-activity', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const activities = await response.json();
        const activityContainer = document.getElementById('recent-activity-list');
        
        if (activityContainer && activities.length > 0) {
            activityContainer.innerHTML = activities.map(activity => `
                <div class="activity-item d-flex align-items-center mb-3">
                    <div class="activity-icon me-3">
                        <i class="fas ${getActivityIcon(activity.type)} text-${getActivityColor(activity.type)}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-text">${activity.description}</div>
                        <small class="text-muted">${formatTimeAgo(activity.timestamp)}</small>
                    </div>
                </div>
            `).join('');
        }

    } catch (error) {
        console.error('Error updating recent activity:', error);
    }
}

/**
 * Initialize dashboard controls
 */
function initializeDashboardControls() {
    // Date range picker
    const dateRangePicker = document.getElementById('dashboard-date-range');
    if (dateRangePicker) {
        dateRangePicker.addEventListener('change', function() {
            refreshDashboardData(this.value);
        });
    }

    // Refresh button
    const refreshBtn = document.getElementById('refresh-dashboard');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            refreshDashboard();
        });
    }

    // Auto-refresh toggle
    const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
    if (autoRefreshToggle) {
        autoRefreshToggle.addEventListener('change', function() {
            toggleAutoRefresh(this.checked);
        });
    }
}

/**
 * Initialize notifications
 */
function initializeNotifications() {
    // Check for notifications on load
    checkNotifications();
    
    // Set up notification polling
    setInterval(checkNotifications, 60000);
}

/**
 * Initialize quick actions
 */
function initializeQuickActions() {
    // Quick reservation button
    const quickReserveBtn = document.getElementById('quick-reserve-btn');
    if (quickReserveBtn) {
        quickReserveBtn.addEventListener('click', function() {
            window.location.href = '/reservations/make';
        });
    }

    // Quick carpool button
    const quickCarpoolBtn = document.getElementById('quick-carpool-btn');
    if (quickCarpoolBtn) {
        quickCarpoolBtn.addEventListener('click', function() {
            window.location.href = '/carpools/create';
        });
    }

    // View all reservations button
    const viewReservationsBtn = document.getElementById('view-reservations-btn');
    if (viewReservationsBtn) {
        viewReservationsBtn.addEventListener('click', function() {
            window.location.href = '/reservations';
        });
    }
}

/**
 * Utility functions
 */

function updateStatCard(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        // Animate the number change
        animateNumber(element, parseInt(element.textContent) || 0, value);
    }
}

function updateProgressBar(elementId, percentage) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.width = `${percentage}%`;
        element.setAttribute('aria-valuenow', percentage);
    }
}

function animateNumber(element, start, end) {
    const duration = 1000;
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

function getActivityIcon(type) {
    const icons = {
        'reservation': 'fa-calendar-plus',
        'carpool': 'fa-car',
        'user': 'fa-user',
        'admin': 'fa-cog',
        'system': 'fa-server'
    };
    return icons[type] || 'fa-info-circle';
}

function getActivityColor(type) {
    const colors = {
        'reservation': 'primary',
        'carpool': 'success',
        'user': 'info',
        'admin': 'warning',
        'system': 'secondary'
    };
    return colors[type] || 'muted';
}

function formatTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = now - time;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
}

function showChartError(canvas) {
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#6c757d';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Unable to load chart', canvas.width / 2, canvas.height / 2);
}

function refreshDashboard() {
    // Show loading state
    const refreshBtn = document.getElementById('refresh-dashboard');
    if (refreshBtn) {
        const originalContent = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        refreshBtn.disabled = true;
        
        // Refresh all data
        Promise.all([
            updateDashboardStats(),
            updateRecentActivity()
        ]).finally(() => {
            refreshBtn.innerHTML = originalContent;
            refreshBtn.disabled = false;
            
            // Re-initialize charts
            setTimeout(() => {
                initializeCharts();
            }, 100);
        });
    }
}

function refreshDashboardData(dateRange) {
    // Implement date range filtering
    console.log('Refreshing dashboard data for range:', dateRange);
    // This would typically make an API call with the date range parameter
}

function toggleAutoRefresh(enabled) {
    if (enabled) {
        console.log('Auto-refresh enabled');
        // Auto-refresh is already set up with setInterval
    } else {
        console.log('Auto-refresh disabled');
        // Would need to clear intervals here
    }
}

async function checkNotifications() {
    try {
        const response = await fetch('/api/notifications', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const notifications = await response.json();
            updateNotificationBadge(notifications.unread_count);
        }
    } catch (error) {
        console.error('Error checking notifications:', error);
    }
}

function updateNotificationBadge(count) {
    const badge = document.getElementById('notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'inline';
        } else {
            badge.style.display = 'none';
        }
    }
}
