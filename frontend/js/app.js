const API_URL = 'http://localhost:8000/api';

// Auth State
function getToken() {
    return localStorage.getItem('access_token');
}

function isLoggedIn() {
    return !!getToken();
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login.html';
}

// UI Updates
function updateNav() {
    const authLinks = document.getElementById('auth-links');
    if (isLoggedIn()) {
        authLinks.innerHTML = `
            <a href="/dashboard.html" class="nav-link">Dashboard</a>
            <a href="/history.html" class="nav-link">History</a>
            <button onclick="logout()" class="btn btn-outline">Logout</button>
        `;
    } else {
        authLinks.innerHTML = `
            <a href="/login.html" class="nav-link">Login</a>
            <a href="/register.html" class="btn btn-primary">Get Started</a>
        `;
    }
}

// API Calls
async function apiCall(endpoint, method = 'GET', body = null, isFile = false) {
    const headers = {};
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    if (!isFile) {
        headers['Content-Type'] = 'application/json';
    }

    const options = {
        method,
        headers,
    };

    if (body) {
        options.body = isFile ? body : JSON.stringify(body);
    }

    const response = await fetch(`${API_URL}${endpoint}`, options);
    if (response.status === 401) {
        logout();
        return null;
    }
    return response;
}

document.addEventListener('DOMContentLoaded', updateNav);

// Social Login Handler
// Social Login Handler (Event Delegation)
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-social');
    if (btn) {
        e.preventDefault();

        let provider = '';
        if (btn.classList.contains('btn-google')) provider = 'google';
        else if (btn.classList.contains('btn-facebook')) provider = 'facebook';
        else if (btn.classList.contains('btn-apple')) provider = 'apple';

        if (provider) {
            window.location.href = `/api/auth/login/${provider}`;
        }
    }
});
