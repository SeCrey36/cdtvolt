# Фрагменты кода связанные с JWT токенами

## REST/Settings
File: `education_platform/settings.py`
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
```

## API Routing
File: `education_platform/courses/urls_api.py`
```python
from rest_framework_simplejwt.views import TokenRefreshView
from .views_api import (
    RegisterView, CustomTokenObtainPairView, LogoutView,
    ConfirmEmailView, ResendConfirmationView,
    UserProfileView, ChangePasswordView, UserEnrollmentsView,
    CreateEnrollmentView, CourseListView, CourseDetailView,
    CourseTimeSlotsView, AvailableTimeSlotsView
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='api_login'),
    path('auth/logout/', LogoutView.as_view(), name='api_logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_refresh'),
    path('auth/confirm-email/', ConfirmEmailView.as_view(), name='api_confirm_email'),
    path('auth/confirm-email/<str:token>/', ConfirmEmailView.as_view(), name='api_confirm_email_token'),
    path('auth/resend-confirmation/', ResendConfirmationView.as_view(), name='api_resend_confirmation'),
    path('profile/', UserProfileView.as_view(), name='api_profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='api_change_password'),
    path('profile/enrollments/', UserEnrollmentsView.as_view(), name='api_user_enrollments'),
    path('enrollments/create/', CreateEnrollmentView.as_view(), name='api_create_enrollment'),
    path('courses/', CourseListView.as_view(), name='api_course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='api_course_detail'),
    path('courses/<int:course_id>/slots/', CourseTimeSlotsView.as_view(), name='api_course_slots'),
    path('courses/<int:course_id>/available-slots/', AvailableTimeSlotsView.as_view(), name='api_available_slots'),
]
```

## Views and Serializer
File: `education_platform/courses/views_api.py`
```python
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email_confirmed': user.profile.email_confirmed,
        }
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({"message": "Успешный выход"}, status=status.HTTP_205_RESET_CONTENT)
```