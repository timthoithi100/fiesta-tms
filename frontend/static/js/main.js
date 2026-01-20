// API Base URL
const API_BASE_URL = '/api';

// Utility Functions
const utils = {
    // Get token from localStorage
    getToken() {
        return localStorage.getItem('access_token');
    },

    // Set token in localStorage
    setToken(token) {
        localStorage.setItem('access_token', token);
    },

    // Remove token from localStorage
    removeToken() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
    },

    // Get user role
    getUserRole() {
        return localStorage.getItem('user_role');
    },

    // Set user role
    setUserRole(role) {
        localStorage.setItem('user_role', role);
    },

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.getToken();
    },

    // Make authenticated API request
    async apiRequest(endpoint, options = {}) {
        const token = this.getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        };

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers
            });

            if (response.status === 401) {
                this.removeToken();
                window.location.href = '/login';
                return null;
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },

    // Show alert message
    showAlert(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;

        const container = document.querySelector('.dashboard-container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);

        setTimeout(() => {
            alertDiv.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => alertDiv.remove(), 300);
        }, 3000);
    },

    // Show loading spinner
    showLoading(container) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.id = 'loading-spinner';
        container.appendChild(spinner);
    },

    // Hide loading spinner
    hideLoading() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    },

    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-KE', {
            style: 'currency',
            currency: 'KES'
        }).format(amount);
    },

    // Format date
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    // Redirect based on role
    redirectToDashboard() {
        const role = this.getUserRole();
        if (role === 'student') {
            window.location.href = '/student/home';
        } else if (role === 'admin') {
            window.location.href = '/admin/home';
        }
    },

    // Protect route - redirect if not authenticated
    protectRoute(requiredRole = null) {
        if (!this.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }

        if (requiredRole && this.getUserRole() !== requiredRole) {
            window.location.href = '/login';
            return false;
        }

        return true;
    }
};

// Sidebar Toggle
function setupSidebar() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');

    if (menuToggle && sidebar && overlay) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });

        overlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });

        // Close sidebar when clicking a link
        const sidebarLinks = sidebar.querySelectorAll('a');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', () => {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            });
        });
    }
}

// Logout Function
function setupLogout() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            utils.removeToken();
            utils.showAlert('Logged out successfully', 'success');
            setTimeout(() => {
                window.location.href = '/login';
            }, 1000);
        });
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    setupSidebar();
    setupLogout();
});

// Export utils for use in other files
window.utils = utils;