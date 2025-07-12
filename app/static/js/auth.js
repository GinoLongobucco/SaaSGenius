// Authentication JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Form elements
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginToggle = document.getElementById('loginToggle');
    const registerToggle = document.getElementById('registerToggle');
    const demoBtn = document.getElementById('demoBtn');
    
    // Alert elements
    const errorAlert = document.getElementById('errorAlert');
    const successAlert = document.getElementById('successAlert');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');

    // Toggle between login and register forms
    loginToggle.addEventListener('click', function() {
        showLoginForm();
    });

    registerToggle.addEventListener('click', function() {
        showRegisterForm();
    });

    function showLoginForm() {
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
        loginToggle.classList.add('active');
        registerToggle.classList.remove('active');
        hideAlerts();
    }

    function showRegisterForm() {
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
        registerToggle.classList.add('active');
        loginToggle.classList.remove('active');
        hideAlerts();
    }

    // Login form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value;
        const remember = document.getElementById('rememberMe').checked;
        
        if (!username || !password) {
            showError('Por favor, completa todos los campos');
            return;
        }

        const loginBtn = document.getElementById('loginBtn');
        setButtonLoading(loginBtn, true);
        hideAlerts();

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    remember: remember
                })
            });

            const data = await response.json();

            if (data.success) {
                showSuccess('¡Inicio de sesión exitoso! Redirigiendo...');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                showError(data.message || 'Error al iniciar sesión');
            }
        } catch (error) {
            console.error('Login error:', error);
            showError('Error de conexión. Por favor, intenta de nuevo.');
        } finally {
            setButtonLoading(loginBtn, false);
        }
    });

    // Register form submission
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('registerUsername').value.trim();
        const email = document.getElementById('registerEmail').value.trim();
        const password = document.getElementById('registerPassword').value;
        const acceptTerms = document.getElementById('acceptTerms').checked;
        
        if (!username || !email || !password) {
            showError('Por favor, completa todos los campos');
            return;
        }

        if (!acceptTerms) {
            showError('Debes aceptar los términos y condiciones');
            return;
        }

        if (!validatePassword(password)) {
            showError('La contraseña no cumple con los requisitos');
            return;
        }

        const registerBtn = document.getElementById('registerBtn');
        setButtonLoading(registerBtn, true);
        hideAlerts();

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (data.success) {
                showSuccess('¡Registro exitoso! Redirigiendo al dashboard...');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                showError(data.message || 'Error al registrarse');
            }
        } catch (error) {
            console.error('Register error:', error);
            showError('Error de conexión. Por favor, intenta de nuevo.');
        } finally {
            setButtonLoading(registerBtn, false);
        }
    });

    // Demo login
    if (demoBtn) {
        demoBtn.addEventListener('click', async function() {
            // Fill demo credentials in the form
            document.getElementById('loginUsername').value = 'demo';
            document.getElementById('loginPassword').value = 'demo123';
            
            setButtonLoading(demoBtn, true);
            hideAlerts();

            try {
                const response = await fetch('/auth/demo-login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                const data = await response.json();

                if (data.success) {
                    showSuccess('¡Acceso demo activado! Redirigiendo...');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1500);
                } else {
                    showError(data.message || 'Error al acceder al demo');
                }
            } catch (error) {
                console.error('Demo login error:', error);
                showError('Error de conexión. Por favor, intenta de nuevo.');
            } finally {
                setButtonLoading(demoBtn, false);
            }
        });
    }

    // Password validation for register form
    const registerPassword = document.getElementById('registerPassword');
    if (registerPassword) {
        registerPassword.addEventListener('input', function() {
            validatePasswordRequirements(this.value);
        });
    }

    // Utility functions
    function setButtonLoading(button, loading) {
        const btnText = button.querySelector('.btn-text');
        const btnLoading = button.querySelector('.btn-loading');
        
        if (loading) {
            btnText.style.display = 'none';
            btnLoading.classList.remove('hidden');
            button.disabled = true;
        } else {
            btnText.style.display = 'inline';
            btnLoading.classList.add('hidden');
            button.disabled = false;
        }
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorAlert.classList.remove('hidden');
        successAlert.classList.add('hidden');
    }

    function showSuccess(message) {
        successMessage.textContent = message;
        successAlert.classList.remove('hidden');
        errorAlert.classList.add('hidden');
    }

    function hideAlerts() {
        errorAlert.classList.add('hidden');
        successAlert.classList.add('hidden');
    }

    function validatePassword(password) {
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        return Object.values(requirements).every(req => req);
    }

    function validatePasswordRequirements(password) {
        const requirements = {
            'req-length': password.length >= 8,
            'req-uppercase': /[A-Z]/.test(password),
            'req-lowercase': /[a-z]/.test(password),
            'req-number': /\d/.test(password),
            'req-special': /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        Object.keys(requirements).forEach(reqId => {
            const element = document.getElementById(reqId);
            const icon = element.querySelector('i');
            
            if (requirements[reqId]) {
                element.classList.add('valid');
                icon.className = 'fas fa-check';
            } else {
                element.classList.remove('valid');
                icon.className = 'fas fa-times';
            }
        });
    }
});

// Toggle password visibility
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const toggle = input.parentElement.querySelector('.password-toggle i');
    
    if (input.type === 'password') {
        input.type = 'text';
        toggle.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        toggle.className = 'fas fa-eye';
    }
}