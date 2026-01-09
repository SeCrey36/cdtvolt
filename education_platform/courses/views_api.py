from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.db.models import F
from django.shortcuts import get_object_or_404
from .models import UserProfile, Course, TimeSlot, Enrollment, News
from .serializers import (
    UserRegisterSerializer, UserProfileSerializer, UserLoginSerializer,
    ChangePasswordSerializer, ConfirmEmailSerializer, ResendConfirmationSerializer,
    CourseSerializer, TimeSlotSerializer, EnrollmentSerializer, 
    CreateEnrollmentSerializer
)


# гарантируем наличие профиля (для созданных через createsuperuser)
def ensure_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile

# ============ AUTHENTICATION VIEWS ============

class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Регистрация успешна! Проверьте email для подтверждения.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомизированный сериализатор для добавления данных пользователя"""
    def validate(self, attrs):
        data = super().validate(attrs)

        # Добавляем информацию о пользователе
        user = self.user
        ensure_profile(user)
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
    """Кастомизированный view для получения JWT токенов"""
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    """Выход пользователя (добавление refresh токена в черный список)"""
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Успешный выход"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ============ EMAIL CONFIRMATION VIEWS ============

class ConfirmEmailView(APIView):
    """Подтверждение email по токену - УПРОЩЕННАЯ версия"""
    permission_classes = (AllowAny,)
    
    def get(self, request, token=None):
        """GET запрос для подтверждения по ссылке из письма"""
        print(f"Получен токен: {token}")
        
        if not token or token.strip() == '':
            return Response(
                {'error': 'Токен не указан'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Ищем профиль по токену
            profile = UserProfile.objects.get(email_confirmation_token=token)
            print(f"Найден пользователь: {profile.user.username}")
            
            # Подтверждаем email (ПРОСТОЙ способ)
            profile.email_confirmed = True
            profile.email_confirmation_token = ''  # Очищаем токен
            profile.save()
            
            print(f"Email подтвержден для: {profile.user.email}")
            
            # Возвращаем успешный ответ
            return Response({
                'success': True,
                'message': 'Email успешно подтвержден!',
                'user': {
                    'username': profile.user.username,
                    'email': profile.user.email,
                    'email_confirmed': True
                }
            })
            
        except UserProfile.DoesNotExist:
            print(f"Токен не найден в базе")
            return Response(
                {'error': 'Неверный токен подтверждения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"Ошибка: {str(e)}")
            return Response(
                {'error': f'Ошибка при подтверждении: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

class ResendConfirmationView(APIView):
    """Повторная отправка подтверждения email"""
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = ResendConfirmationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            ensure_profile(user)
            
            # Генерируем новый токен
            token = user.profile.generate_confirmation_token()
            
            # Отправляем email (в консоль для разработки)
            print(f"\n=== ПОВТОРНАЯ ОТПРАВКА ПОДТВЕРЖДЕНИЯ ===\n"
                  f"Кому: {user.email}\n"
                  f"Токен: {token}\n"
                  f"==============================\n")
            
            return Response({
                'message': 'Письмо с подтверждением отправлено',
                'email': user.email
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============ USER PROFILE VIEWS ============

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Получение и обновление профиля пользователя"""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        return ensure_profile(self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Получить профиль пользователя с дополнительной информацией"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Добавляем информацию о записях пользователя
        enrollments = Enrollment.objects.filter(user=request.user)
        enrollment_serializer = EnrollmentSerializer(enrollments, many=True)
        
        data = serializer.data
        data['enrollments'] = enrollment_serializer.data
        data['enrollments_count'] = enrollments.count()
        
        return Response(data)

class ChangePasswordView(generics.UpdateAPIView):
    """Изменение пароля"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = self.get_object()
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if not user.check_password(old_password):
            return Response(
                {"error": "Старый пароль неверный"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        return Response({"message": "Пароль успешно изменен"})

# ============ USER ENROLLMENTS ============

class UserEnrollmentsView(generics.ListAPIView):
    """Список записей пользователя"""
    permission_classes = (IsAuthenticated,)
    serializer_class = EnrollmentSerializer
    
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).order_by('-created_at')

class CreateEnrollmentView(generics.CreateAPIView):
    """Создание записи на курс (авторизованным пользователем)"""
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateEnrollmentSerializer
    
    def perform_create(self, serializer):
        serializer.save()

# ============ PUBLIC VIEWS ============

class CourseListView(generics.ListAPIView):
    """Список курсов (публичный)"""
    permission_classes = (AllowAny,)
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer

class CourseDetailView(generics.RetrieveAPIView):
    """Детали курса (публичный)"""
    permission_classes = (AllowAny,)
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer

class CourseTimeSlotsView(generics.ListAPIView):
    """Расписание курса (публичное)"""
    permission_classes = (AllowAny,)
    serializer_class = TimeSlotSerializer
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id, is_active=True)
        return TimeSlot.objects.filter(course=course, is_active=True)

class AvailableTimeSlotsView(generics.ListAPIView):
    """Доступные слоты курса (со свободными местами)"""
    permission_classes = (AllowAny,)
    serializer_class = TimeSlotSerializer
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id, is_active=True)
        return TimeSlot.objects.filter(
            course=course, 
            is_active=True,
            booked_seats__lt=F('max_seats')
        )