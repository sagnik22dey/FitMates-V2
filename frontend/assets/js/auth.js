// Authentication Utilities

/**
 * Check if user is logged in and redirect if not
 */
function requireAuth() {
    console.log('🔐 Checking authentication...');
    const isAuth = api.isAuthenticated();
    console.log('Is authenticated:', isAuth);
    if (!isAuth) {
        console.log('❌ Not authenticated, redirecting to login');
        window.location.href = '/login.html';
        return false;
    }
    console.log('✅ Authentication check passed');
    return true;
}

/**
 * Check if user has admin role
 */
function requireAdmin() {
    console.log('🔐 Checking admin role...');
    const user = api.getUser();
    console.log('Current user:', user);
    if (!user || user.role !== 'admin') {
        console.log('❌ Not admin, redirecting to login');
        window.location.href = '/login.html';
        return false;
    }
    console.log('✅ Admin check passed');
    return true;
}

/**
 * Check if user has client role
 */
function requireClient() {
    console.log('🔐 Checking client role...');
    const user = api.getUser();
    console.log('Current user:', user);
    if (!user || user.role !== 'client') {
        console.log('❌ Not client, redirecting to login');
        window.location.href = '/login.html';
        return false;
    }
    console.log('✅ Client check passed');
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
