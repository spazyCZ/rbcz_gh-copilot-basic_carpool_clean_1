/**
 * Login page JavaScript functionality.
 * 
 * Handles login form submission via API calls.
 */

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});

/**
 * Handle login form submission
 * @param {Event} event - Form submit event
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    const loginData = {
        username: formData.get('username') || document.getElementById('username').value,
        password: formData.get('password') || document.getElementById('password').value,
        remember: document.getElementById('remember-me').checked
    };
    
    // Basic validation
    if (!loginData.username || !loginData.password) {
        UI.showAlert('Please enter both username and password.', 'error');
        return;
    }
    
    try {
        UI.clearAlerts();
        
        // Make login API call
        const response = await API.post('/auth/login', loginData);
        
        if (response.data && response.data.user) {
            UI.showAlert('Login successful! Redirecting...', 'success');
            
            // Redirect to dashboard after short delay
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            UI.showAlert('Login failed. Please try again.', 'error');
        }
        
    } catch (error) {
        handleError(error);
        
        // Clear password field on error
        document.getElementById('password').value = '';
    }
}