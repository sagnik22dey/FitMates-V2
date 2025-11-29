// Authentication Utilities

/**
 * Check if user is logged in and redirect if not
 */
function requireAuth() {
    if (window.logger) {
        window.logger.debug('Checking authentication...');
    }
    const isAuth = api.isAuthenticated();
    
    if (!isAuth) {
        if (window.logger) {
            window.logger.warn('Not authenticated, redirecting to login');
        }
        window.location.href = '/login.html';
        return false;
    }
    
    if (window.logger) {
        window.logger.debug('Authentication check passed');
    }
    return true;
}

/**
 * Check if user has admin role
 */
function requireAdmin() {
    if (window.logger) {
        window.logger.debug('Checking admin role...');
    }
    const user = api.getUser();
    
    if (!user || user.role !== 'admin') {
        if (window.logger) {
            window.logger.warn('Not admin, redirecting to login');
        }
        window.location.href = '/login.html';
        return false;
    }
    
    if (window.logger) {
        window.logger.debug('Admin check passed', { user: user.email });
    }
    return true;
}

/**
 * Check if user has client role
 */
function requireClient() {
    if (window.logger) {
        window.logger.debug('Checking client role...');
    }
    const user = api.getUser();
    
    if (!user || user.role !== 'client') {
        if (window.logger) {
            window.logger.warn('Not client, redirecting to login');
        }
        window.location.href = '/login.html';
        return false;
    }
    
    if (window.logger) {
        window.logger.debug('Client check passed', { user: user.email });
    }
    return true;
}

/**
 * Redirect based on user role
 */
function redirectByRole() {
    const user = api.getUser();
    if (!user) {
        window.location.href = '/login.html';
        return;
    }

    if (user.role === 'admin') {
        window.location.href = '/admin/dashboard.html';
    } else if (user.role === 'client') {
        window.location.href = '/user/dashboard.html';
    }
}

/**
 * Logout and redirect to login
 */
function logout() {
    api.logout();
    window.location.href = '/login.html';
}

/**
 * Get current user
 */
function getCurrentUser() {
    return api.getUser();
}

// Export functions
window.auth = {
    requireAuth,
    requireAdmin,
    requireClient,
    redirectByRole,
    logout,
    getCurrentUser,
};
