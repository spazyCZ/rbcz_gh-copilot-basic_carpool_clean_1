/**
 * Main JavaScript file for the Carpool Parking application
 */

// Wait for DOM to be loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Add confirm dialog to delete buttons
    const deleteButtons = document.querySelectorAll('button[type="submit"][class*="btn-danger"]');
    deleteButtons.forEach(function(button) {
        if (!button.hasAttribute('onclick')) {
            button.setAttribute('onclick', 'return confirm("Are you sure you want to delete this item?")');
        }
    });
});
