// static/js/api.js
const API_BASE = 'http://localhost:8000/api';

// Экспортируем t/applyI18n, если они объявлены в шаблоне
function t(key) {
    if (typeof window !== 'undefined' && window.t) return window.t(key);
    return key;
}

console.log('Токен из localStorage:', localStorage.getItem('access_token') ? 'Есть' : 'Нет');
console.log('User из localStorage:', localStorage.getItem('user_data') ? 'Есть' : 'Нет');

// Хранилище токенов
let accessToken = localStorage.getItem('access_token');
let refreshToken = localStorage.getItem('refresh_token');
let currentUser = null;

console.log('API.js загружен. Токен есть:', !!accessToken);

// ============ ОСНОВНЫЕ ФУНКЦИИ ============

// Сохранение токенов и данных пользователя
function saveAuthData(data) {
    if (data.access) {
        accessToken = data.access;
        localStorage.setItem('access_token', data.access);
        console.log('Access токен сохранен');
    }
    if (data.refresh) {
        refreshToken = data.refresh;
        localStorage.setItem('refresh_token', data.refresh);
    }
    if (data.user) {
        currentUser = data.user;
        localStorage.setItem('user_data', JSON.stringify(data.user));
        console.log('Данные пользователя сохранены:', data.user.username);
    }
}

// Очистка данных
function clearAuthData() {
    accessToken = null;
    refreshToken = null;
    currentUser = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    console.log('Авторизация очищена');
}

// Проверка статуса email подтверждения
function checkEmailConfirmation() {
    if (!currentUser) return false;
    
    const emailConfirmed = currentUser.email_confirmed;
    console.log('Статус email подтверждения:', emailConfirmed);
    
    if (!emailConfirmed) {
        // Скрываем функционал, требующий подтверждения
        const elements = document.querySelectorAll('.email-confirmed-only');
        elements.forEach(el => {
            el.style.display = 'none';
        });
        
        // Показываем предупреждение на страницах
        if (window.location.pathname === '/profile/') {
            const warningDiv = document.getElementById('email-warning-profile');
            if (!warningDiv) {
                const container = document.querySelector('.container.py-4');
                if (container) {
                    const warning = document.createElement('div');
                    warning.id = 'email-warning-profile';
                    warning.className = 'alert alert-warning mb-4';
                    warning.innerHTML = `
                        <i class="bi bi-envelope-exclamation me-2"></i>
                        Ваш email не подтвержден. Некоторые функции недоступны.
                        <a href="#" onclick="resendConfirmation()" class="alert-link ms-1">
                            Отправить подтверждение еще раз
                        </a>
                    `;
                    container.insertBefore(warning, container.firstChild);
                }
            }
        }
        
        return false;
    }
    
    // Если email подтвержден, показываем скрытые элементы
    const elements = document.querySelectorAll('.email-confirmed-only');
    elements.forEach(el => {
        el.style.display = '';
    });
    
    // Убираем предупреждения
    const warning = document.getElementById('email-warning-profile');
    if (warning) warning.remove();
    
    return true;
}

// Проверка авторизации при загрузке страницы
function checkAuthOnLoad() {
    console.log('Проверка авторизации при загрузке...');
    
    const savedToken = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user_data');

    // Если токен есть, но профиля нет — все равно пытаемся загрузить профиль
    if (savedToken) {
        // Принудительно переключаем интерфейс в авторизованный режим сразу
        updateAuthUI({ username: t('ui.loading'), email_confirmed: true });
        if (savedUser) {
            try {
                currentUser = JSON.parse(savedUser);
                console.log('Найден сохраненный пользователь:', currentUser.username);
                updateAuthUI(currentUser);
                checkEmailConfirmation();
            } catch (e) {
                console.error('Ошибка парсинга user_data:', e);
                clearAuthData();
            }
        } else {
            console.log('Токен есть, но user_data нет — пробуем получить профиль');
            getProfile().then(user => {
                if (user) {
                    currentUser = user;
                    localStorage.setItem('user_data', JSON.stringify(user));
                    updateAuthUI(user);
                    checkEmailConfirmation();
                }
            }).catch(err => {
                console.warn('Не удалось получить профиль, очищаем auth:', err);
                clearAuthData();
                updateAuthUI(null);
            });
        }

        // Проверяем валидность токена через секунду и обновляем данные
        setTimeout(() => {
            getProfile().then(user => {
                if (user) {
                    currentUser = user;
                    localStorage.setItem('user_data', JSON.stringify(user));
                    checkEmailConfirmation();
                }
            }).catch(error => {
                console.warn('Токен невалиден, очищаем:', error);
                clearAuthData();
                updateAuthUI(null);
            });
        }, 1000);
    } else {
        console.log('Пользователь не авторизован');
        updateAuthUI(null);
    }
}

// Обновление интерфейса
function updateAuthUI(user) {
    const usernameDisplay = document.getElementById('username-display');
    const authElements = document.querySelectorAll('.auth-only');
    const guestElements = document.querySelectorAll('.guest-only');
    const emailConfirmationItem = document.getElementById('email-confirmation-item');
    const body = document.body;
    
    if (user) {
        console.log('Обновляем UI: авторизован как', user.username);
        body.classList.add('authed');
        body.classList.remove('guest');
        if (usernameDisplay) {
            usernameDisplay.textContent = user.username;
            // Добавляем бейдж, если email не подтвержден
            if (!user.email_confirmed) {
                usernameDisplay.innerHTML = `${user.username} <span class="badge bg-warning ms-1" style="font-size: 0.6em;">Email не подтвержден</span>`;
            }
        }
        
        // Показываем/скрываем пункт меню для подтверждения email
        if (emailConfirmationItem) {
            emailConfirmationItem.style.display = user.email_confirmed ? 'none' : 'block';
        }
        
        authElements.forEach(el => el.style.display = '');
        guestElements.forEach(el => el.style.display = 'none');
    } else {
        console.log('Обновляем UI: гость');
        body.classList.add('guest');
        body.classList.remove('authed');
        if (usernameDisplay) {
            usernameDisplay.textContent = 'Гость';
        }
        if (emailConfirmationItem) {
            emailConfirmationItem.style.display = 'none';
        }
        authElements.forEach(el => el.style.display = 'none');
        guestElements.forEach(el => el.style.display = '');
    }
    
    // Проверяем элементы, требующие подтверждения email
    checkEmailConfirmation();
}

// ============ API ЗАПРОСЫ ============

// Базовый запрос с обработкой токенов
async function apiRequest(url, method = 'GET', data = null, requireAuth = true) {
    const headers = {
        'Content-Type': 'application/json',
    };

    if (requireAuth && accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
        console.log('Запрос с токеном:', url);
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
            console.log('Токен истек, пытаемся обновить...');
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                // Повторяем запрос с новым токеном
                headers['Authorization'] = `Bearer ${accessToken}`;
                options.headers = headers;
                response = await fetch(API_BASE + url, options);
            } else {
                clearAuthData();
                updateAuthUI(null);
                throw new Error('Требуется повторная авторизация');
            }
        }

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || 'Ошибка запроса');
        }

        return await response.json();

    } catch (error) {
        console.error('API Request Error:', url, error);
        throw error;
    }
}

// Обновление токена
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
            saveAuthData(data);
            console.log('Токен обновлен');
            return true;
        }
    } catch (error) {
        console.error('Ошибка обновления токена:', error);
    }

    clearAuthData();
    return false;
}

// ============ АУТЕНТИФИКАЦИЯ ============

// Регистрация
async function apiRegister(userData) {
    if (apiRegister._inFlight) {
        console.warn('apiRegister already in flight, skipping duplicate');
        return Promise.reject(new Error('Запрос уже отправляется'));
    }
    apiRegister._inFlight = true;
    try {
        return await apiRequest('/auth/register/', 'POST', userData, false);
    } finally {
        apiRegister._inFlight = false;
    }
}

// Вход (ОСНОВНОЙ МЕТОД!)
async function apiLogin(username, password) {
    console.log('Пытаемся войти с логином:', username);
    
    const response = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Ошибка входа');
    }

    const data = await response.json();
    console.log('Успешный вход! Получены данные:', data);
    
    // Сохраняем токены и данные пользователя, если есть
    saveAuthData(data);

    // Если пользователь не пришел в ответе, сразу покажем авторизованное меню, пока тянем профиль
    let userObj = data.user;
    if (!userObj) {
        updateAuthUI({ username: t('ui.loading'), email_confirmed: true });
        try {
            userObj = await getProfile();
            if (userObj) {
                currentUser = userObj;
                localStorage.setItem('user_data', JSON.stringify(userObj));
            }
        } catch (err) {
            console.warn('Не удалось загрузить профиль после логина:', err);
        }
    }
    
    // Проверяем email подтверждение
    if (userObj && !userObj.email_confirmed) {
        console.warn('Email не подтвержден!');
        if (window.location.pathname !== '/confirm-email/') {
            showAlert('warning', 'Подтвердите email', 
                     'На вашу почту отправлено письмо с подтверждением');
        }
        checkEmailConfirmation();
    }
    
    // Обновляем интерфейс
    updateAuthUI(userObj || currentUser);
    
    return data;
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
        clearAuthData();
        updateAuthUI(null);
        console.log('Выход выполнен');
    }
}

// ============ КУРСЫ И ЗАПИСИ ============

// Получить курсы
async function getCourses() {
    return apiRequest('/courses/', 'GET', null, false);
}

// Получить детали курса
async function getCourse(id) {
    return apiRequest(`/courses/${id}/`, 'GET', null, false);
}

// Получить доступные ячейки
async function getAvailableTimeSlots(courseId) {
    return apiRequest(`/courses/${courseId}/available-slots/`, 'GET', null, false);
}

// Создать запись на курс
async function createEnrollment(enrollmentData) {
    // Проверяем email подтверждение перед записью
    if (!checkEmailConfirmation()) {
        throw new Error('Для записи на курс необходимо подтвердить email');
    }
    return apiRequest('/enrollments/create/', 'POST', enrollmentData, true);
}

// Получить профиль
async function getProfile() {
    return apiRequest('/profile/', 'GET', null, true);
}

// Получить свои записи
async function getMyEnrollments() {
    return apiRequest('/profile/enrollments/', 'GET', null, true);
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

// ============ УТИЛИТЫ ============

// Показать уведомление
function showAlert(type, title, message, duration = 5000) {
    // Создаем элемент уведомления
    let alertDiv = document.getElementById('global-alert');
    if (!alertDiv) {
        alertDiv = document.createElement('div');
        alertDiv.id = 'global-alert';
        alertDiv.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 1000; min-width: 300px;';
        document.body.appendChild(alertDiv);
    }
    
    const colors = {
        success: 'alert-success',
        error: 'alert-danger', 
        warning: 'alert-warning',
        info: 'alert-info'
    };
    
    alertDiv.innerHTML = `
        <div class="alert ${colors[type]} alert-dismissible fade show">
            <strong>${title}</strong><br>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    if (duration > 0) {
        setTimeout(() => {
            alertDiv.innerHTML = '';
        }, duration);
    }
}

// Выход (глобальная функция)
window.logout = async function() {
    await apiLogout();
    window.location.href = '/';
};

// ============ ИНИЦИАЛИЗАЦИЯ ============

// Запускаем проверку авторизации при загрузке
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, проверяем авторизацию...');
    checkAuthOnLoad();
});

// ============ ГЛОБАЛЬНЫЕ СЛУШАТЕЛИ СОБЫТИЙ ============

// Обновляем интерфейс при изменении авторизации
function onAuthChange(user) {
    console.log('Событие: изменение авторизации', user?.username || 'гость');
    currentUser = user;
    
    // Обновляем все страницы
    updateAuthUI(user);
    
    // Если на странице курса, обновляем ее
    if (window.location.pathname.includes('/course/')) {
        updateCoursePageAuth();
    }
}

// Переопределяем saveAuthData чтобы триггерить событие
const originalSaveAuthData = saveAuthData;
window.saveAuthData = function(data) {
    originalSaveAuthData(data);
    onAuthChange(data.user || currentUser);
};
// Переназначаем имя функции, чтобы остальные вызовы использовали обертку
saveAuthData = window.saveAuthData;

// Переопределяем clearAuthData
const originalClearAuthData = clearAuthData;
window.clearAuthData = function() {
    originalClearAuthData();
    onAuthChange(null);
};
clearAuthData = window.clearAuthData;

// Экспортируем функции для доступа из шаблонов
window.updateCoursePageAuth = function() {
    // Эта функция будет переопределена в course_detail.html
    console.log('Обновление страницы курса (базовая версия)');
};

window.showAlert = showAlert;
window.createEnrollment = createEnrollment;
window.checkEmailConfirmation = checkEmailConfirmation;