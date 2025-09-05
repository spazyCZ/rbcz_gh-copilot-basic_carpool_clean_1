/**
 * Dashboard page JavaScript functionality.
 * 
 * Loads and displays dashboard data via API calls.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Load dashboard data
    loadDashboardStats();
    loadRecentActivity();
    
    // Setup reservation form
    setupReservationForm();
    
    // Refresh data every 30 seconds
    setInterval(loadDashboardStats, 30000);
});

/**
 * Load dashboard statistics
 */
async function loadDashboardStats() {
    try {
        // This would normally call multiple API endpoints
        // For now, we'll use placeholder data until APIs are implemented
        updateStatsDisplay({
            totalSpots: 15,
            availableSpots: 12,
            reservedSpots: 3,
            myReservations: 1
        });
        
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        // Don't show error to user for background data loading
    }
}

/**
 * Update statistics display
 * @param {Object} stats - Statistics data
 */
function updateStatsDisplay(stats) {
    const elements = {
        'total-spots': stats.totalSpots,
        'available-spots': stats.availableSpots,
        'reserved-spots': stats.reservedSpots,
        'my-reservations': stats.myReservations
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            element.classList.add('fade-in');
        }
    });
}

/**
 * Load recent activity
 */
async function loadRecentActivity() {
    try {
        const activityContainer = document.getElementById('recent-activity');
        if (!activityContainer) return;
        
        // Placeholder activity data
        const activities = [
            { type: 'reservation', message: 'Spot A1 reserved for today', time: '2 hours ago' },
            { type: 'login', message: 'User demo logged in', time: '3 hours ago' },
            { type: 'reservation', message: 'Spot B2 reservation cancelled', time: '5 hours ago' }
        ];
        
        const activityHTML = activities.map(activity => `
            <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                <div>
                    <small class="text-muted">${activity.type.toUpperCase()}</small>
                    <div>${activity.message}</div>
                </div>
                <small class="text-muted">${activity.time}</small>
            </div>
        `).join('');
        
        activityContainer.innerHTML = activityHTML || '<p class="text-muted">No recent activity</p>';
        
    } catch (error) {
        console.error('Error loading recent activity:', error);
        const activityContainer = document.getElementById('recent-activity');
        if (activityContainer) {
            activityContainer.innerHTML = '<p class="text-muted">Error loading activity</p>';
        }
    }
}

/**
 * Setup reservation form
 */
function setupReservationForm() {
    const form = document.getElementById('reservation-form');
    if (form) {
        form.addEventListener('submit', handleReservationSubmit);
    }
    
    // Set default date to today
    const dateInput = document.getElementById('reservation-date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
        dateInput.addEventListener('change', loadAvailableSpots);
        
        // Load spots for today
        loadAvailableSpots();
    }
}

/**
 * Load available spots for selected date
 */
async function loadAvailableSpots() {
    const dateInput = document.getElementById('reservation-date');
    const spotSelect = document.getElementById('spot-select');
    
    if (!dateInput || !spotSelect) return;
    
    const selectedDate = dateInput.value;
    if (!selectedDate) return;
    
    try {
        // Clear current options
        spotSelect.innerHTML = '<option value="">Loading...</option>';
        
        // This would normally call the spots API
        // For now, use placeholder data
        const spots = [
            { id: 'A1', location: 'Level A - Near entrance' },
            { id: 'A2', location: 'Level A - Near entrance' },
            { id: 'B1', location: 'Level B - Standard' },
            { id: 'G1', location: 'Ground level - Visitor' }
        ];
        
        spotSelect.innerHTML = '<option value="">Select a spot...</option>' +
            spots.map(spot => `<option value="${spot.id}">${spot.id} - ${spot.location}</option>`).join('');
            
    } catch (error) {
        console.error('Error loading available spots:', error);
        spotSelect.innerHTML = '<option value="">Error loading spots</option>';
    }
}

/**
 * Handle reservation form submission
 * @param {Event} event - Form submit event
 */
async function handleReservationSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const reservationData = {
        spot_id: document.getElementById('spot-select').value,
        reservation_date: document.getElementById('reservation-date').value,
        name: document.getElementById('reservation-name').value,
        notes: document.getElementById('reservation-notes').value
    };
    
    // Basic validation
    if (!reservationData.spot_id || !reservationData.reservation_date || !reservationData.name) {
        UI.showAlert('Please fill in all required fields.', 'error');
        return;
    }
    
    try {
        UI.clearAlerts();
        
        // This would normally call the reservations API
        // For now, show success message
        UI.showAlert('Reservation created successfully! (Demo mode)', 'success');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('reservationModal'));
        if (modal) {
            modal.hide();
        }
        
        // Reset form
        event.target.reset();
        
        // Refresh dashboard stats
        loadDashboardStats();
        
    } catch (error) {
        handleError(error);
    }
}

/**
 * Show reservation modal
 */
function showReservationModal() {
    const modal = new bootstrap.Modal(document.getElementById('reservationModal'));
    modal.show();
    
    // Load available spots when modal opens
    loadAvailableSpots();
}