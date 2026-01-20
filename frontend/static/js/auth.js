// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }
        
        // 1. Store token
        utils.setToken(data.access_token);
        
        // 2. Extract role from JWT Payload instead of a second API call
        // JWT is [header].[payload].[signature]. We want index 1.
        const base64Url = data.access_token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(window.atob(base64));
        
        // 3. Set role and redirect
        utils.setUserRole(payload.role.toLowerCase()); // Ensure it matches 'admin' or 'student'
        
        utils.showAlert('Login successful!', 'success');
        setTimeout(() => {
            utils.redirectToDashboard();
        }, 500);
        
    } catch (error) {
        utils.showAlert(error.message, 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// Handle Signup
async function handleSignup(event) {
    event.preventDefault();
    
    const formData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        first_name: document.getElementById('first_name').value,
        middle_name: document.getElementById('middle_name').value || null,
        last_name: document.getElementById('last_name').value,
        gender: document.getElementById('gender').value,
        date_of_birth: document.getElementById('date_of_birth').value,
        phone_number: document.getElementById('phone_number').value,
        city: document.getElementById('city').value,
        address: document.getElementById('address').value || null,
        program: document.getElementById('program').value
    };
    
    const confirmPassword = document.getElementById('confirm_password').value;
    
    if (formData.password !== confirmPassword) {
        utils.showAlert('Passwords do not match', 'error');
        return;
    }
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating account...';
    
    try {
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Signup failed');
        }
        
        utils.showAlert('Account created successfully! Please login.', 'success');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
        
    } catch (error) {
        utils.showAlert(error.message, 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// Setup Login Form
function setupLoginForm() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
}

// Setup Signup Form
function setupSignupForm() {
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Redirect if already logged in
    if (utils.isAuthenticated()) {
        utils.redirectToDashboard();
        return;
    }
    
    setupLoginForm();
    setupSignupForm();
});