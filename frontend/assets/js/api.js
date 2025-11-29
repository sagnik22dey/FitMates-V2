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

    const fullUrl = `${API_BASE_URL}${endpoint}`;
    console.log(`🌐 API Request: ${options.method || 'GET'} ${fullUrl}`);

    try {
      const response = await fetch(fullUrl, config);

      // Handle unauthorized
      if (response.status === 401) {
        this.logout();
        window.location.href = '/login.html';
        throw new Error('Unauthorized');
      }

      const data = await response.json();

      if (!response.ok) {
        console.error('❌ API Error:', data);
        throw new Error(data.detail || 'Request failed');
      }

      console.log('✅ API Response:', data);
      return data;
    } catch (error) {
      console.error('❌ API Request Failed:', error);
      console.error('URL:', fullUrl);
      console.error('Error details:', error.message);
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
