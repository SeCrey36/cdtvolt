from django.urls import include, path
from . import views
from .views import CourseDetailView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .swagger_config import swagger_info
from rest_framework import permissions

app_name = 'courses'

# Создаем схему для Swagger
schema_view = get_schema_view(
    swagger_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # HTML страницы
    path('', views.index, name='index'),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('register/', views.register_page, name='register_page'),
    path('login/', views.login_page, name='login_page'),
    path('profile/', views.profile_page, name='profile_page'),
    path('news/', views.news_page, name='news_page'),
    path('api-test/', views.api_test_page, name='api_test'),
    
    # API endpoints
    path('api/', include('courses.urls_api')),
    
    # Swagger документация
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), 
         name='schema-json'),
]