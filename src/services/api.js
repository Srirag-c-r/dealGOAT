// API service for backend integration
// This will connect to Django backend when ready

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    // Add Authorization header if token exists
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Token ${token}`
    }

    // If we are sending FormData, let the browser set the Content-Type
    if (options.body instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    try {
      const response = await fetch(url, config)

      // Handle non-JSON responses
      let data
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        data = await response.json()
      } else {
        const text = await response.text()
        throw new Error(text || 'An error occurred')
      }

      if (!response.ok) {
        // Handle Django validation errors, which might be a dictionary of field errors
        if (typeof data === 'object' && data !== null) {
          const errorMessages = Object.entries(data)
            .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(' ') : messages}`)
            .join('\n');
          if (errorMessages) {
            throw new Error(errorMessages);
          }
        }

        // Fallback for other error formats
        throw new Error(data.message || data.detail || 'An unknown error occurred');
      }

      return data
    } catch (error) {
      // Network errors
      if (error.message === 'Failed to fetch' || error.message.includes('NetworkError')) {
        throw new Error('Cannot connect to server. Make sure Django backend is running on http://localhost:8000')
      }
      throw error
    }
  }

  // Login
  async login(credentials) {
    return this.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
  }

  // User registration
  async register(userData) {
    return this.request('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
  }

  // Send OTP
  async sendOTP(email) {
    return this.request('/auth/send-otp/', {
      method: 'POST',
      body: JSON.stringify({ email }),
    })
  }

  // Verify OTP
  async verifyOTP(email, otp) {
    return this.request('/auth/verify-otp/', {
      method: 'POST',
      body: JSON.stringify({ email, otp }),
    })
  }

  // Complete registration
  async completeRegistration(userData) {
    return this.request('/auth/complete-registration/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  // Check email availability
  async checkEmail(email) {
    return this.request(`/auth/check-email/?email=${email}`, {
      method: 'GET',
    })
  }

  // Request password reset
  async requestPasswordReset(data) {
    return this.request('/auth/password-reset/request/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Verify password reset token
  async verifyPasswordResetToken(data) {
    return this.request('/auth/password-reset/verify/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Reset password
  async resetPassword(data) {
    return this.request('/auth/password-reset/reset/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }
  // Create a new listing
  async createListing(formData) {
    // Note: formData should be a FormData object to handle image uploads
    return this.request('/predictions/listings/create/', {
      method: 'POST',
      headers: {
        // Content-Type must be undefined for FormData to let browser set boundary
      },
      body: formData,
    })
  }

  // Get user's active listings
  async getUserListings() {
    return this.request('/predictions/listings/my-listings/', {
      method: 'GET',
    })
  }

  // Get public active listings with filters from query params
  async getActiveListings(filters = {}) {
    const queryParams = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key]) {
        queryParams.append(key, filters[key]);
      }
    });

    return this.request(`/predictions/listings/all/?${queryParams.toString()}`, {
      method: 'GET',
    })
  }

  // Get single listing details
  async getListingDetails(id) {
    return this.request(`/predictions/listings/details/${id}/`, {
      method: 'GET',
    })
  }

  // Delete listing
  async deleteListing(id) {
    return this.request(`/predictions/listings/delete/${id}/`, {
      method: 'DELETE',
    })
  }

  // Update listing status
  async updateListingStatus(id, status) {
    return this.request(`/predictions/listings/status/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    })
  }

  // ==================== MESSAGING METHODS ====================

  // Start or get conversation for a listing
  async startConversation(listingId) {
    return this.request(`/predictions/messages/start/${listingId}/`, {
      method: 'POST',
    })
  }

  // Get all conversations for current user
  async getConversations() {
    return this.request('/predictions/messages/conversations/', {
      method: 'GET',
    })
  }

  // Get messages in a conversation
  async getConversationMessages(conversationId) {
    return this.request(`/predictions/messages/conversation/${conversationId}/`, {
      method: 'GET',
    })
  }

  // Mark messages as read
  async markMessagesRead(conversationId) {
    return this.request(`/predictions/messages/read/${conversationId}/`, {
      method: 'PATCH',
    })
  }

  // Update user profile picture
  async updateProfile(formData) {
    return this.request('/auth/update-profile/', {
      method: 'POST',
      body: formData,
    })
  }
}

export default new ApiService()

