// API Configuration - Use current origin for mobile support
const API_BASE_URL = window.location.origin;

// API Utility Functions
const api = {
  /**
   * Get authentication token from localStorage
   */
  getToken() {
    return localStorage.getItem('auth_token');
  },

  /**
   * Get user data from localStorage
   */
  getUser() {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  },

  /**
   * Make an authenticated API request
   */
  async request(endpoint, options = {}) {
    const token = this.getToken();
    const method = options.method || 'GET';
    const fullUrl = `${API_BASE_URL}${endpoint}`;

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add authorization header if token exists
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // Log API call using logger
    if (window.logger) {
      window.logger.apiCall(method, fullUrl, options.body);
    }

    const startTime = performance.now();

    try {
      const response = await fetch(fullUrl, config);

      // Handle unauthorized
      if (response.status === 401) {
        if (window.logger) {
          window.logger.warn('Unauthorized API call, redirecting to login');
        }
        this.logout();
        window.location.href = '/login.html';
        throw new Error('Unauthorized');
      }

      const data = await response.json();

      if (!response.ok) {
        if (window.logger) {
          window.logger.apiError(method, fullUrl, data);
        }
        throw new Error(data.detail || 'Request failed');
      }

      // Log response and performance
      const duration = performance.now() - startTime;
      if (window.logger) {
        window.logger.apiResponse(method, fullUrl, data);
        window.logger.performance(`API ${method} ${endpoint}`, duration);
      }

      return data;
    } catch (error) {
      if (window.logger) {
        window.logger.apiError(method, fullUrl, error);
      } else {
        console.error('API Request Failed:', error);
      }
      throw error;
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
      body: JSON.stringify(data),
    });
  },

  /**
   * PUT request
   */
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * DELETE request
   */
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  },

  /**
   * Login
   */
  async login(email, password) {
    const response = await this.post('/api/auth/login', { email, password });

    // Store token and user data
    localStorage.setItem('auth_token', response.access_token);
    localStorage.setItem('user_data', JSON.stringify({
      id: response.user_id,
      email: response.email,
      name: response.name,
      role: response.role,
    }));

    return response;
  },

  /**
   * Logout
   */
  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.getToken();
  },

  /**
   * Verify token
   */
  async verifyToken() {
    try {
      const response = await this.get('/api/auth/verify');
      return response.valid;
    } catch (error) {
      return false;
    }
  },
};

// Export for use in other scripts
window.api = api;
