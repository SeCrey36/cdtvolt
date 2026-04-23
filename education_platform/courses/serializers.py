from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import UserProfile, Instructor, Course, TimeSlot, Enrollment, News

# ============ USER SERIALIZERS ============

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'phone')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Пользователь с таким email уже существует"})
        
        return attrs
    
    def create(self, validated_data):
        phone = validated_data.pop('phone', '')
        validated_data.pop('password2')
        
        # Создаем пользователя
        user = User.objects.create_user(**validated_data)
        print(f"Пользователь создан: {user.id} - {user.email}")
        
        # Создаем профиль пользователя
        from .models import UserProfile
        profile = UserProfile.objects.create(user=user)
        
        if phone:
            profile.phone = phone
            profile.save()
        
        print(f"Профиль создан для {user.username}")
        
        # Генерируем токен и отправляем письмо
        token = profile.generate_confirmation_token()
        self.send_confirmation_email(user, token)
        
        return user
    
    def send_confirmation_email(self, user, token):
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from django.conf import settings
        
        confirmation_url = f"http://127.0.0.1:8000/api/auth/confirm-email/{token}/"
        
        # Подготовка письма
        subject = 'Подтверждение email - Образовательная платформа'
        
        # HTML версия
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h2>Здравствуйте, {user.first_name}!</h2>
            <p>Для подтверждения email перейдите по ссылке:</p>
            <p><a href="{confirmation_url}">{confirmation_url}</a></p>
            <p>Или используйте код: <strong>{token}</strong></p>
        </body>
        </html>
        """
        
        # Текстовая версия
        text_content = f"""
        Подтверждение email
        
        Здравствуйте, {user.first_name}!
        
        Для подтверждения email перейдите по ссылке:
        {confirmation_url}
        
        Или используйте код: {token}
        """
        
        try:
            # 1. Прямое подключение через smtplib с SSL
            # Используем SMTP_SSL для порта 465
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
            
            # 2. Логинимся
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            
            # 3. Создаем сообщение
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.DEFAULT_FROM_EMAIL
            msg['To'] = user.email
            
            # Добавляем обе версии
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # 4. Отправляем
            server.send_message(msg)
            server.quit()
            
            print(f"Письмо отправлено на {user.email} через SMTP_SSL")
            
        except Exception as e:
            print(f"Ошибка SMTP_SSL: {type(e).__name__}: {str(e)}")
            print(f"Ссылка для теста: {confirmation_url}")

class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
        
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
            
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"username": "Пользователь не найден"})
            
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Неверный пароль"})
            
        attrs['user'] = user
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'phone', 'email_confirmed', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        # Гарантируем наличие профиля, даже если пользователь создан без него
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            UserProfile.objects.get_or_create(user=request.user)
        return super().to_internal_value(data)
    
    def update(self, instance, validated_data):
        # Обновляем данные пользователя
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()
        
        # Обновляем профиль
        return super().update(instance, validated_data)

class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают"})
        return attrs

class ConfirmEmailSerializer(serializers.Serializer):
    """Сериализатор для подтверждения email"""
    token = serializers.CharField(required=True)
    
    def validate(self, attrs):
        token = attrs.get('token')
        try:
            profile = UserProfile.objects.get(email_confirmation_token=token)
            # Проверяем не истек ли токен
            if profile.email_confirmation_sent_at:
                hours_passed = (timezone.now() - profile.email_confirmation_sent_at).total_seconds() / 3600
                if hours_passed > 24:
                    raise serializers.ValidationError({"token": "Токен подтверждения истек"})
            attrs['profile'] = profile
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({"token": "Неверный токен подтверждения"})
        
        return attrs
    
    def save(self):
        """Подтверждает email"""
        profile = self.validated_data['profile']
        profile.confirm_email()
        return True

class ResendConfirmationSerializer(serializers.Serializer):
    """Сериализатор для повторной отправки подтверждения"""
    email = serializers.EmailField(required=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
            if user.profile.email_confirmed:
                raise serializers.ValidationError({"email": "Email уже подтвержден"})
            attrs['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Пользователь с таким email не найден"})
        
        return attrs

# ============ COURSE SERIALIZERS ============

class CourseSerializer(serializers.ModelSerializer):
    instructors = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'image', 'instructors', 
                 'price', 'duration_minutes', 'is_active']

class TimeSlotSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    free_seats = serializers.IntegerField(read_only=True)
    has_free_seats = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'course', 'course_title', 'day_of_week', 'time_slot',
                 'max_seats', 'booked_seats', 'free_seats', 'has_free_seats',
                 'room', 'is_active']

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    time_slots_info = serializers.SerializerMethodField()
    feedback = serializers.CharField(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course_title', 'time_slots_info', 'student_name',
                 'student_email', 'created_at', 'decision_status', 'feedback']
    
    def get_time_slots_info(self, obj):
        slots = obj.time_slots.all()
        return [
            {
                'day': slot.get_day_of_week_display(),
                'time': slot.get_time_display(),
                'room': slot.room,
            }
            for slot in slots
        ]

class CreateEnrollmentSerializer(serializers.ModelSerializer):
    time_slot_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Enrollment
        fields = ['student_name', 'student_phone', 'student_email',
                 'student_comment', 'data_consent', 'time_slot_ids',
                 'student_surname', 'student_first_name', 'student_patronymic',
                 'student_passport_series', 'student_passport_number', 'student_passport_issued_by']
        extra_kwargs = {
            'student_surname': {'required': True, 'allow_blank': False},
            'student_first_name': {'required': True, 'allow_blank': False},
            'student_patronymic': {'required': False, 'allow_blank': True},
            'student_passport_series': {'required': True, 'allow_blank': False},
            'student_passport_number': {'required': True, 'allow_blank': False},
            'student_passport_issued_by': {'required': True, 'allow_blank': False},
        }
    
    def validate(self, attrs):
        # Проверяем, что пользователь подтвердил email
        user = self.context.get('request').user
        if user:
            # Гарантируем наличие профиля для суперпользователей
            UserProfile.objects.get_or_create(user=user)
        if user and not user.profile.email_confirmed:
            raise serializers.ValidationError(
                {"email": "Подтвердите email перед записью на курс"}
            )
        
        slot_ids = attrs.get('time_slot_ids', [])
        
        if not slot_ids:
            raise serializers.ValidationError("Выберите хотя бы одно занятие")
        
        # Проверяем слоты
        slots = TimeSlot.objects.filter(id__in=slot_ids, is_active=True)
        if len(slots) != len(slot_ids):
            raise serializers.ValidationError("Некоторые слоты не найдены")
        
        # Проверяем доступность
        unavailable_slots = []
        for slot in slots:
            if not slot.has_free_seats:
                unavailable_slots.append(f"{slot.get_day_of_week_display()} {slot.get_time_display()}")
        
        if unavailable_slots:
            raise serializers.ValidationError(
                f"На следующие занятия нет мест: {', '.join(unavailable_slots)}"
            )
        
        # Проверяем, что все слоты с одного курса
        courses = set(slot.course.id for slot in slots)
        if len(courses) > 1:
            raise serializers.ValidationError("Все занятия должны быть с одного курса")
        
        attrs['time_slots'] = slots
        
        return attrs
    
    def create(self, validated_data):
        user = self.context.get('request').user
        slot_ids = validated_data.pop('time_slot_ids')
        slots = validated_data.pop('time_slots')
        
        # Автозаполняем данные из профиля пользователя если он авторизован
        if user and user.is_authenticated:
            validated_data.setdefault('student_name', f"{user.first_name} {user.last_name}".strip())
            validated_data.setdefault('student_email', user.email)
            if user.profile.phone:
                validated_data.setdefault('student_phone', user.profile.phone)
            validated_data['user'] = user

            # Если заказчик не заполнил полное имя отдельными полями, пробуем автозаполнить
            validated_data.setdefault('student_first_name', user.first_name)
            validated_data.setdefault('student_surname', user.last_name)

        # Синхронизируем отображаемое поле student_name с полями ФИО для договора
        fio = ' '.join(
            part for part in [
                validated_data.get('student_surname', ''),
                validated_data.get('student_first_name', ''),
                validated_data.get('student_patronymic', ''),
            ] if part
        ).strip()
        if fio:
            validated_data['student_name'] = fio
        
        validated_data.pop('course', None)
        enrollment = Enrollment.objects.create(**validated_data)
        enrollment.time_slots.set(slots)
        
        # Обновляем счетчики мест
        for slot in slots:
            slot.booked_seats += 1
            slot.save()
        
        return enrollment

# ============ INSTRUCTOR SERIALIZERS ============

class InstructorSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Instructor
        fields = ['id', 'name', 'user_email', 'photo', 'bio']