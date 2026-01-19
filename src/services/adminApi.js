import axios from 'axios';

/**
 * API Configuration
 * Centralized API service with interceptors and error handling
 */

// Base URL from environment variable or default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30 seconds
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Token ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle 401 Unauthorized - Token expired or invalid
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            // Avoid infinite redirect if already on login page
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }

        // Handle 403 Forbidden - Insufficient permissions
        if (error.response?.status === 403) {
            console.error('Access forbidden:', error.response.data);
        }

        // Handle 500 Server Error
        if (error.response?.status >= 500) {
            console.error('Server error:', error.response.data);
        }

        return Promise.reject(error);
    }
);

/**
 * Admin API Service
 * All admin-related API calls
 */
export const adminAPI = {
    // Dashboard
    getDashboardStats: () => apiClient.get('/auth/admin/dashboard/stats/'),

    // User Management
    getUserList: (params) => apiClient.get('/auth/admin/list/', { params }),
    getUserDetails: (userId) => apiClient.get(`/auth/admin/${userId}/details/`),
    suspendUser: (userId, data) => apiClient.post(`/auth/admin/${userId}/suspend/`, data),
    getUserAnalytics: () => apiClient.get('/auth/admin/analytics/users/'),

    // Listing Moderation
    getListingStats: () => apiClient.get('/predictions/admin/dashboard/stats/'),
    getListingList: (params) => apiClient.get('/predictions/admin/listings/list/', { params }),
    getPendingListings: () => apiClient.get('/predictions/admin/listings/pending/'),
    getFlaggedListings: () => apiClient.get('/predictions/admin/listings/flagged/'),
    moderateListing: (listingId, data) => apiClient.post(`/predictions/admin/listings/${listingId}/moderate/`, data),
    runFraudCheck: (data) => apiClient.post('/predictions/admin/listings/fraud-check/', data),

    // System Monitoring
    getRecommendationStats: () => apiClient.get('/recommendations/admin/dashboard/stats/'),
    getSystemHealth: () => apiClient.get('/recommendations/admin/system-health/'),
    getSettings: () => apiClient.get('/recommendations/admin/settings/get/'),
    updateSetting: (data) => apiClient.post('/recommendations/admin/settings/update/', data),
    generateReport: (data) => apiClient.post('/recommendations/admin/reports/generate/', data),
};

export default apiClient;
