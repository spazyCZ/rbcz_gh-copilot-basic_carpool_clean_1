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
        // Load spot statistics from API
        const response = await API.get('/spots/statistics');
        
        if (response.data && response.data.statistics) {
            const stats = response.data.statistics;
            const todayStats = stats.today_statistics;
            
            updateStatsDisplay({
                totalSpots: stats.total_spots,
                availableSpots: todayStats.available_count,
                reservedSpots: todayStats.reserved_count,
                myReservations: 0 // Will be loaded separately
            });
            
            // Load user's reservation count
            loadUserReservationCount();
        }
        
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        // Show fallback data on error
        updateStatsDisplay({
            totalSpots: '?',
            availableSpots: '?',
            reservedSpots: '?',
            myReservations: '?'
        });
    }
}

/**
 * Load user's reservation count
 */
async function loadUserReservationCount() {
    try {
        const response = await API.get('/reservations');
        
        if (response.data && response.data.reservations) {
            const activeReservations = response.data.reservations.filter(r => r.is_active);
            const upcomingReservations = activeReservations.filter(r => {
                const reservationDate = new Date(r.reservation_date);
                return reservationDate >= new Date();
            });
            
            // Update the my reservations count
            const element = document.getElementById('my-reservations');
            if (element) {
                element.textContent = upcomingReservations.length;
                element.classList.add('fade-in');
            }
        }
        
    } catch (error) {
        console.error('Error loading user reservations:', error);
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
        
        // Fetch available spots from API
        const response = await API.get(`/spots?date=${selectedDate}`);
        
        if (response.data && response.data.spots) {
            const spots = response.data.spots;
            
            if (spots.length === 0) {
                spotSelect.innerHTML = '<option value="">No spots available for selected date</option>';
            } else {
                spotSelect.innerHTML = '<option value="">Select a spot...</option>' +
                    spots.map(spot => {
                        const features = [];
                        if (spot.is_handicap_accessible) features.push('♿');
                        if (spot.is_electric_charging) features.push('⚡');
                        const featureText = features.length > 0 ? ` ${features.join(' ')}` : '';
                        
                        return `<option value="${spot.id}">${spot.id} - ${spot.location}${featureText}</option>`;
                    }).join('');
            }
        } else {
            spotSelect.innerHTML = '<option value="">Error loading spots</option>';
        }
            
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
        
        // Create reservation via API
        const response = await API.post('/reservations', reservationData);
        
        if (response.data && response.data.success) {
            UI.showAlert('Reservation created successfully!', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('reservationModal'));
            if (modal) {
                modal.hide();
            }
            
            // Reset form
            event.target.reset();
            
            // Refresh dashboard stats
            loadDashboardStats();
            loadRecentActivity();
        } else {
            UI.showAlert('Failed to create reservation. Please try again.', 'error');
        }
        
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