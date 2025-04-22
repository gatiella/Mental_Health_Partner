document.addEventListener('DOMContentLoaded', function() {
    // Common Functions
    const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    const showError = (element, message) => {
        const errorElement = element.parentElement.querySelector('.error-message');
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        element.classList.add('is-invalid');
    };

    const clearErrors = () => {
        document.querySelectorAll('.error-message').forEach(el => {
            el.style.display = 'none';
        });
        document.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
    };

    // Password Strength Indicator
    const initPasswordStrength = () => {
        const passwordInput = document.getElementById('password1');
        if (passwordInput) {
            const strengthIndicator = document.createElement('div');
            strengthIndicator.className = 'password-strength';
            strengthIndicator.innerHTML = '<div class="strength-indicator"></div>';
            passwordInput.parentElement.appendChild(strengthIndicator);

            passwordInput.addEventListener('input', function() {
                const strength = calculatePasswordStrength(this.value);
                const indicator = strengthIndicator.querySelector('.strength-indicator');
                indicator.style.width = `${strength.percentage}%`;
                indicator.style.backgroundColor = strength.color;
            });
        }
    };

    const calculatePasswordStrength = (password) => {
        const strength = {
            0: { color: '#e74c3c', percentage: 25 },
            1: { color: '#e67e22', percentage: 50 },
            2: { color: '#f1c40f', percentage: 75 },
            3: { color: '#2ecc71', percentage: 100 }
        };
        
        let score = 0;
        if (password.length >= 8) score++;
        if (password.match(/[A-Z]/)) score++;
        if (password.match(/[0-9]/)) score++;
        if (password.match(/[^A-Za-z0-9]/)) score++;
        
        return strength[Math.min(score, 3)];
    };

    // Registration Form Handling
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        initPasswordStrength();
        
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearErrors();
            
            const formData = {
                username: registerForm.username.value.trim(),
                email: registerForm.email.value.trim(),
                password1: registerForm.password1.value,
                password2: registerForm.password2.value
            };

            // Client-side validation
            let isValid = true;
            if (formData.password1 !== formData.password2) {
                showError(registerForm.password2, 'Passwords do not match');
                isValid = false;
            }
            if (!registerForm.terms.checked) {
                showError(registerForm.terms, 'You must accept the terms');
                isValid = false;
            }

            if (isValid) {
                try {
                    const response = await fetch('/api/users/register/', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData),
                    });

                    const data = await response.json();
                    if (response.ok) {
                        window.location.href = '/api/auth/login/';
                    } else {
                        Object.keys(data.errors).forEach(field => {
                            const input = registerForm.querySelector(`[name="${field}"]`);
                            if (input) showError(input, data.errors[field][0]);
                        });
                    }
                } catch (error) {
                    console.error('Registration error:', error);
                }
            }
        });
    }

    // Login Form Handling
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearErrors();

            const formData = {
                username: loginForm.username.value.trim(),
                password: loginForm.password.value
            };

            try {
                const response = await fetch('/api/auth/login/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData),
                });

                if (response.ok) {
                    if (loginForm.rememberMe.checked) {
                        localStorage.setItem('rememberMe', 'true');
                    }
                    window.location.href = '/api/users/me/';
                } else {
                    const error = await response.json();
                    showError(loginForm.password, error.detail || 'Invalid credentials');
                }
            } catch (error) {
                console.error('Login error:', error);
            }
        });
    }

    // Remember Me Functionality
    if (localStorage.getItem('rememberMe') === 'true') {
        document.getElementById('rememberMe').checked = true;
    }
});