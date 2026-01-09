from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

# Профиль пользователя
class UserProfile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    
    # Поля для подтверждения email
    email_confirmed = models.BooleanField(
        default=False,
        verbose_name='Email подтвержден'
    )
    
    email_confirmation_token = models.CharField(
        max_length=100,
        default = '',
        blank=True,
        verbose_name='Токен подтверждения email'
    )
    
    email_confirmation_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время отправки подтверждения'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f"Профиль: {self.user.username}"
    
    def generate_confirmation_token(self):
        """Генерирует токен для подтверждения email"""
        token = str(uuid.uuid4())
        self.email_confirmation_token = token
        self.email_confirmation_sent_at = timezone.now()
        self.save()
        return token
    
    def confirm_email(self):
        """Подтверждает email пользователя"""
        self.email_confirmed = True
        self.email_confirmation_token = ''
        self.save()

# Преподаватель
class Instructor(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        verbose_name='Пользователь'
    )
    name = models.CharField(max_length=200, verbose_name='Имя преподавателя')
    photo = models.ImageField(
        upload_to='instructors/',
        blank=True,
        null=True,
        verbose_name='Фото'
    )
    bio = models.TextField(blank=True, verbose_name='Биография')
    
    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
    
    def __str__(self):
        return self.name

# Курс
class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название курса')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        upload_to='courses/', 
        blank=True, 
        null=True,
        verbose_name='Картинка'
    )
    
    # Связь M2M с преподавателями
    instructors = models.ManyToManyField(
        Instructor,
        related_name='courses',
        verbose_name='Преподаватели'
    )
    
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0.00,
        verbose_name='Стоимость'
    )
    duration_minutes = models.IntegerField(
        default=60,
        verbose_name='Длительность занятия (минуты)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
    
    def __str__(self):
        return self.title
    
    def get_instructors_names(self):
        return ', '.join([instr.name for instr in self.instructors.all()])

# Ячейка расписания
class TimeSlot(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Саббота'),
        (6, 'Воскресенье'),
    ]
    
    TIME_SLOTS = [
        ('8-10', '8:00-10:00'),
        ('10-12', '10:00-12:00'),
        ('12-14', '12:00-14:00'),
        ('14-16', '14:00-16:00'),
        ('16-18', '16:00-18:00'),
        ('18-20', '18:00-20:00'),
        ('20-22', '20:00-22:00'),
    ]
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='time_slots',
        verbose_name='Курс'
    )
    
    day_of_week = models.IntegerField(
        choices=DAYS_OF_WEEK,
        verbose_name='День недели'
    )
    
    time_slot = models.CharField(
        max_length=5,
        choices=TIME_SLOTS,
        verbose_name='Время'
    )
    
    max_seats = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        verbose_name='Максимальное количество мест'
    )
    
    booked_seats = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Занято мест'
    )
    
    room = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Кабинет/зал'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )
    
    class Meta:
        ordering = ['day_of_week', 'time_slot']
        unique_together = ['course', 'day_of_week', 'time_slot']
        verbose_name = 'Ячейка расписания'
        verbose_name_plural = 'Ячейки расписания'
    
    def __str__(self):
        return f"{self.course.title} - {self.get_day_of_week_display()} {self.get_time_display()}"
    
    @property
    def free_seats(self):
        """Свободные места"""
        return max(0, self.max_seats - self.booked_seats)
    
    @property
    def has_free_seats(self):
        """Есть ли свободные места?"""
        return self.booked_seats < self.max_seats
    
    def get_time_display(self):
        return dict(self.TIME_SLOTS).get(self.time_slot, self.time_slot)

# Запись (связь ManyToMany с TimeSlot)
class Enrollment(models.Model):
    # Связь с пользователем (кто сделал запись)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrollments',
        verbose_name='Пользователь'
    )
    
    # Связь ManyToMany с TimeSlot
    time_slots = models.ManyToManyField(
        TimeSlot,
        related_name='enrollments',
        verbose_name='Выбранные ячейки расписания'
    )
    
    # Дублируем информацию из профиля на случай изменения
    student_name = models.CharField(
        max_length=100,
        verbose_name='Имя студента'
    )
    
    student_phone = models.CharField(
        max_length=20,
        verbose_name='Телефон'
    )
    
    student_email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )
    
    student_comment = models.TextField(
        blank=True,
        verbose_name='Комментарий'
    )

    feedback = models.TextField(
        blank=True,
        verbose_name='Фидбек преподавателя'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    is_approved = models.BooleanField(
        default=False,
        verbose_name='Рассмотрена'
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_enrollments',
        verbose_name='Рассмотрено пользователем'
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата рассмотрения'
    )
    
    # Согласия
    data_consent = models.BooleanField(
        default=False,
        verbose_name='Согласие на обработку персональных данных'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
    
    def __str__(self):
        slots_count = self.time_slots.count()
        username = self.user.username if self.user else "Гость"
        return f"{username} - {self.student_name} - {slots_count} ячейк(а/и)"
    
    @property
    def course(self):
        """Курс из первой выбранной ячейки (все ячейки должны быть с одного курса)"""
        first_slot = self.time_slots.first()
        return first_slot.course if first_slot else None
    
    def save(self, *args, **kwargs):
        """Сохраняем запись и обновляем счетчики в выбранных ячейках"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Увеличиваем счетчики в выбранных ячейках
            for slot in self.time_slots.all():
                if slot.booked_seats < slot.max_seats:
                    slot.booked_seats += 1
                    slot.save()
    
    def delete(self, *args, **kwargs):
        """При удалении уменьшаем счетчики в выбранных ячейках"""
        for slot in self.time_slots.all():
            if slot.booked_seats > 0:
                slot.booked_seats -= 1
                slot.save()
        super().delete(*args, **kwargs)

# Новость
class News(models.Model):
    url = models.URLField(
        verbose_name='Ссылка на новость'
    )
    
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Заголовок'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
    
    def __str__(self):
        return self.title or self.url