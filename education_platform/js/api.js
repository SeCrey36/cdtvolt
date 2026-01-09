const API_BASE = 'http://localhost:8000/api';

// Хранилище токенов
let accessToken = localStorage.getItem('access_token');
let refreshToken = localStorage.getItem('refresh_token');

// ============ ОСНОВНЫЕ ФУНКЦИИ API ============

// Сохранение токенов
function saveTokens(data) {
    if (data.access) {
        accessToken = data.access;
        localStorage.setItem('access_token', data.access);
    }
    if (data.refresh) {
        refreshToken = data.refresh;
        localStorage.setItem('refresh_token', data.refresh);
    }
}

// Очистка токенов
function clearTokens() {
    accessToken = null;
    refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

// Функция для авторизованных запросов
async function apiRequest(url, method = 'GET', data = null, requireAuth = true) {
    const headers = {
        'Content-Type': 'application/json',
    };

    if (requireAuth && accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const options = {
        method: method,
        headers: headers,
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        let response = await fetch(API_BASE + url, options);
        
        // Если токен истек, пытаемся обновить
        if (response.status === 401 && requireAuth && refreshToken) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                // Повторяем запрос с новым токеном
                headers['Authorization'] = `Bearer ${accessToken}`;
                options.headers = headers;
                response = await fetch(API_BASE + url, options);
            }
        }

        // Обработка ответа
        if (!response.ok) {
            const errorText = await response.text();
            let errorData;
            try {
                errorData = JSON.parse(errorText);
            } catch {
                errorData = { detail: errorText || 'Неизвестная ошибка' };
            }
            throw new Error(JSON.stringify(errorData));
        }

        // Если ответ пустой (204 No Content)
        if (response.status === 204) {
            return null;
        }

        return await response.json();

    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Обновление access токена
async function refreshAccessToken() {
    if (!refreshToken) return false;

    try {
        const response = await fetch(`${API_BASE}/auth/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            saveTokens(data);
            return true;
        }
    } catch (error) {
        console.error('Token refresh failed:', error);
    }

    clearTokens();
    return false;
}

// ============ АУТЕНТИФИКАЦИЯ ============

// Регистрация
async function apiRegister(userData) {
    return apiRequest('/auth/register/', 'POST', userData, false);
}

// Вход
async function apiLogin(username, password) {
    const data = { username, password };
    const result = await apiRequest('/auth/login/', 'POST', data, false);
    saveTokens(result);
    return result.user;
}

// Выход
async function apiLogout() {
    try {
        if (refreshToken) {
            await apiRequest('/auth/logout/', 'POST', { refresh: refreshToken });
        }
    } catch (error) {
        console.warn('Logout warning:', error);
    } finally {
        clearTokens();
    }
}

// Проверка авторизации
async function checkAuth() {
    if (!accessToken) {
        updateAuthUI(null);
        return null;
    }

    try {
        const userData = await apiRequest('/profile/');
        updateAuthUI(userData);
        return userData;
    } catch (error) {
        console.warn('Auth check failed:', error);
        updateAuthUI(null);
        return null;
    }
}

// Обновление интерфейса в зависимости от авторизации
function updateAuthUI(userData) {
    const usernameDisplay = document.getElementById('username-display');
    const authButtons = document.querySelectorAll('.auth-only');
    const guestButtons = document.querySelectorAll('.guest-only');

    if (userData) {
        // Пользователь авторизован
        if (usernameDisplay) {
            usernameDisplay.textContent = userData.username;
        }
        authButtons.forEach(el => el.style.display = '');
        guestButtons.forEach(el => el.style.display = 'none');
    } else {
        // Пользователь не авторизован
        if (usernameDisplay) {
            usernameDisplay.textContent = 'Гость';
        }
        authButtons.forEach(el => el.style.display = 'none');
        guestButtons.forEach(el => el.style.display = '');
    }
}

// ============ РАБОТА С КУРСАМИ ============

// Получить список курсов
async function getCourses() {
    return apiRequest('/courses/', 'GET', null, false);
}

// Получить детали курса
async function getCourse(id) {
    return apiRequest(`/courses/${id}/`, 'GET', null, false);
}

// Получить ячейки расписания курса
async function getCourseTimeSlots(courseId) {
    return apiRequest(`/courses/${courseId}/slots/`, 'GET', null, false);
}

// Получить доступные ячейки (со свободными местами)
async function getAvailableTimeSlots(courseId) {
    return apiRequest(`/courses/${courseId}/available-slots/`, 'GET', null, false);
}

// ============ ЗАПИСИ НА КУРСЫ ============

// Создать запись на курс
async function createEnrollment(enrollmentData) {
    return apiRequest('/enrollments/create/', 'POST', enrollmentData, true);
}

// Получить мои записи
async function getMyEnrollments() {
    return apiRequest('/profile/enrollments/', 'GET', null, true);
}

// ============ ПРОФИЛЬ ============

// Получить профиль
async function getProfile() {
    return apiRequest('/profile/', 'GET', null, true);
}

// Обновить профиль
async function updateProfile(profileData) {
    return apiRequest('/profile/', 'PATCH', profileData, true);
}

// Сменить пароль
async function changePassword(oldPassword, newPassword) {
    return apiRequest('/profile/change-password/', 'PUT', {
        old_password: oldPassword,
        new_password: newPassword,
        new_password2: newPassword
    }, true);
}

// ============ ПОДТВЕРЖДЕНИЕ EMAIL ============

// Подтвердить email
async function confirmEmail(token) {
    return apiRequest(`/auth/confirm-email/${token}/`, 'GET', null, false);
}

// Повторная отправка подтверждения
async function resendConfirmation(email) {
    return apiRequest('/auth/resend-confirmation/', 'POST', { email }, false);
}