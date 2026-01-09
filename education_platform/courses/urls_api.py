from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views_api import (
    RegisterView, CustomTokenObtainPairView, LogoutView,
    ConfirmEmailView, ResendConfirmationView,
    UserProfileView, ChangePasswordView, UserEnrollmentsView,
    CreateEnrollmentView, CourseListView, CourseDetailView,
    CourseTimeSlotsView, AvailableTimeSlotsView
)

urlpatterns = [
    # ===== Аутентификация =====
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='api_login'),
    path('auth/logout/', LogoutView.as_view(), name='api_logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_refresh'),
    
    # ===== Подтверждение email =====
    path('auth/confirm-email/', ConfirmEmailView.as_view(), name='api_confirm_email'),
    path('auth/confirm-email/<str:token>/', ConfirmEmailView.as_view(), name='api_confirm_email_token'),
    path('auth/resend-confirmation/', ResendConfirmationView.as_view(), name='api_resend_confirmation'),
    
    # ===== Личный кабинет =====
    path('profile/', UserProfileView.as_view(), name='api_profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='api_change_password'),
    path('profile/enrollments/', UserEnrollmentsView.as_view(), name='api_user_enrollments'),
    
    # ===== Записи на курсы =====
    path('enrollments/create/', CreateEnrollmentView.as_view(), name='api_create_enrollment'),
    
    # ===== Публичные данные =====
    path('courses/', CourseListView.as_view(), name='api_course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='api_course_detail'),
    path('courses/<int:course_id>/slots/', CourseTimeSlotsView.as_view(), name='api_course_slots'),
    path('courses/<int:course_id>/available-slots/', AvailableTimeSlotsView.as_view(), name='api_available_slots'),
]