from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone
from .models import Instructor, Course, TimeSlot, Enrollment, News, UserProfile

# Inline для ячеек расписания в админке курса
class TimeSlotInlineForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = '__all__'
    
    def clean(self):
        """Проверяем уникальность ячейки расписания"""
        cleaned_data = super().clean()
        
        if not self.instance.pk:  # Только для новых ячеек
            course = cleaned_data.get('course')
            day_of_week = cleaned_data.get('day_of_week')
            time_slot = cleaned_data.get('time_slot')
            
            if course and day_of_week is not None and time_slot:
                # Проверяем, существует ли уже такая ячейка
                if TimeSlot.objects.filter(
                    course=course,
                    day_of_week=day_of_week,
                    time_slot=time_slot
                ).exists():
                    day_name = dict(TimeSlot.DAYS_OF_WEEK).get(day_of_week, '')
                    time_name = dict(TimeSlot.TIME_SLOTS).get(time_slot, '')
                    
                    raise forms.ValidationError()
        
        return cleaned_data

class TimeSlotInline(admin.TabularInline):
    model = TimeSlot
    form = TimeSlotInlineForm  # Добавляем кастомную форму
    extra = 0
    fields = ['day_of_week', 'time_slot', 'max_seats', 'booked_seats', 'room', 'is_active']
    readonly_fields = ['booked_seats']

# Форма для курса
class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
    
    create_default_slots = forms.BooleanField(
        required=False,
        initial=True,
        label='Создать стандартные ячейки расписания',
        help_text='Автоматически создать 5 ячеек: Пн-Пт с 10:00 до 12:00'
    )
    
    default_seats = forms.IntegerField(
        initial=10,
        min_value=1,
        required=False,
        label='Количество мест в каждой ячейке'
    )

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    list_display = ['title', 'get_instructors', 'is_active', 'time_slots_count', 'enrollments_count']
    list_filter = ['is_active', 'instructors']
    search_fields = ['title', 'description']
    filter_horizontal = ['instructors']
    inlines = [TimeSlotInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'image', 'instructors', 'price', 'duration_minutes', 'is_active')
        }),
        ('Настройки расписания', {
            'fields': ('create_default_slots', 'default_seats'),
            'classes': ('collapse',),
            'description': 'Настройки доступны только при создании нового курса'
        }),
    )
    
    def get_instructors(self, obj):
        return obj.get_instructors_names()
    get_instructors.short_description = 'Преподаватели'
    
    def time_slots_count(self, obj):
        count = obj.time_slots.count()
        return format_html(
            '<a href="{}?course__id__exact={}">{}</a>',
            reverse('admin:courses_timeslot_changelist'),
            obj.id,
            count
        )
    time_slots_count.short_description = 'Ячейки'
    
    def enrollments_count(self, obj):
        # Считаем записи через ячейки этого курса
        count = Enrollment.objects.filter(time_slots__course=obj).distinct().count()
        return format_html(
            '<a href="{}?time_slots__course__id__exact={}">{}</a>',
            reverse('admin:courses_enrollment_changelist'),
            obj.id,
            count
        )
    enrollments_count.short_description = 'Записи'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        if not change and form.cleaned_data.get('create_default_slots', True):
            default_seats = form.cleaned_data.get('default_seats', 10)
            
            standard_slots = [
                (0, '10-12'),
                (1, '10-12'),
                (2, '10-12'),
                (3, '10-12'),
                (4, '10-12'),
            ]
            
            created_count = 0
            for day, time in standard_slots:
                if not TimeSlot.objects.filter(course=obj, day_of_week=day, time_slot=time).exists():
                    TimeSlot.objects.create(
                        course=obj,
                        day_of_week=day,
                        time_slot=time,
                        max_seats=default_seats,
                        booked_seats=0,
                        room='',
                        is_active=True
                    )
                    created_count += 1
            
            if created_count > 0:
                messages.success(request, f'Создано {created_count} стандартных ячеек')

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'courses_count']
    search_fields = ['name', 'user__username', 'user__email']
    
    def courses_count(self, obj):
        return obj.courses.count()
    courses_count.short_description = 'Курсы'

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['course_link', 'day_display', 'time_display', 'seats_info', 'enrollments_link', 'is_active']
    list_filter = ['course', 'day_of_week', 'is_active']
    search_fields = ['course__title', 'room']
    readonly_fields = ['booked_seats', 'free_seats_info']
    
    fieldsets = (
        ('Основное', {
            'fields': ('course', 'day_of_week', 'time_slot', 'room', 'is_active')
        }),
        ('Места', {
            'fields': ('max_seats', 'booked_seats', 'free_seats_info')
        }),
    )
    
    def course_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:courses_course_change', args=[obj.course.id]),
            obj.course.title
        )
    course_link.short_description = 'Курс'
    
    def day_display(self, obj):
        return obj.get_day_of_week_display()
    day_display.short_description = 'День'
    
    def time_display(self, obj):
        return obj.get_time_display()
    time_display.short_description = 'Время'
    
    def seats_info(self, obj):
        free = obj.max_seats - obj.booked_seats
        if free > 5:
            color = 'green'
        elif free > 0:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{}/{}</span>',
            color, obj.booked_seats, obj.max_seats
        )
    seats_info.short_description = 'Занято/Всего'
    
    def enrollments_link(self, obj):
        count = obj.enrollments.count()
        return format_html(
            '<a href="{}?time_slots__id__exact={}">{}</a>',
            reverse('admin:courses_enrollment_changelist'),
            obj.id,
            count
        )
    enrollments_link.short_description = 'Записи'
    
    def free_seats_info(self, obj):
        free = obj.max_seats - obj.booked_seats
        return format_html(
            '<strong>Свободно: {}</strong> из {}',
            free, obj.max_seats
        )
    free_seats_info.short_description = 'Свободные места'

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'course_info', 'slots_info', 'is_approved', 'created_at', 'enrollment_actions']
    list_filter = ['is_approved', 'created_at', 'time_slots__course']
    search_fields = ['student_name', 'student_phone', 'student_email']
    readonly_fields = ['created_at', 'approved_at', 'selected_slots_display']
    filter_horizontal = ['time_slots']
    
    fieldsets = (
        ('Информация о студенте', {
            'fields': ('student_name', 'student_phone', 'student_email', 'student_comment', 'data_consent')
        }),
        ('Выбранные ячейки расписания', {
            'fields': ('time_slots', 'selected_slots_display'),
            'description': 'Студент может выбрать несколько дней/времён'
        }),
        ('Статус', {
            'fields': ('is_approved', 'approved_by', 'approved_at', 'feedback', 'created_at')
        }),
    )
    
    def course_info(self, obj):
        course = obj.course
        if course:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:courses_course_change', args=[course.id]),
                course.title
            )
        return '-'
    course_info.short_description = 'Курс'
    
    def slots_info(self, obj):
        slots = obj.time_slots.all()
        if slots:
            slots_list = []
            for slot in slots:
                slots_list.append(f"{slot.get_day_of_week_display()} {slot.get_time_display()}")
            return ', '.join(slots_list)
        return '-'
    slots_info.short_description = 'Выбранные слоты'
    
    def selected_slots_display(self, obj):
        """Отображение выбранных слотов в форме"""
        slots = obj.time_slots.all()
        if not slots:
            return 'Нет выбранных слотов'
        
        html = '<ul>'
        for slot in slots:
            html += format_html(
                '<li>{} - {} (мест: {}/{})</li>',
                slot.get_day_of_week_display(),
                slot.get_time_display(),
                slot.booked_seats,
                slot.max_seats
            )
        html += '</ul>'
        return format_html(html)
    selected_slots_display.short_description = 'Выбранные слоты'
    
    def enrollment_actions(self, obj):
        return format_html(
            '<a href="{}">✏️</a>',
            reverse('admin:courses_enrollment_change', args=[obj.id])
        )
    enrollment_actions.short_description = 'Действия'
    
    def save_model(self, request, obj, form, change):
        # Получаем старые и новые слоты
        if change:
            old_slots = set(Enrollment.objects.get(pk=obj.pk).time_slots.all())
        else:
            old_slots = set()
        
        new_slots = set(obj.time_slots.all())
        
        # Сохраняем объект
        super().save_model(request, obj, form, change)
        
        # Обновляем счетчики мест
        # Уменьшаем счетчики в старых слотах, которых нет в новых
        for slot in old_slots - new_slots:
            if slot.booked_seats > 0:
                slot.booked_seats -= 1
                slot.save()
        
        # Увеличиваем счетчики в новых слотах, которых не было в старых
        for slot in new_slots - old_slots:
            if slot.booked_seats < slot.max_seats:
                slot.booked_seats += 1
                slot.save()
        
        # Если подтверждаем запись
        if 'is_approved' in form.changed_data and obj.is_approved:
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
            obj.save()

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title_or_url', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    
    def title_or_url(self, obj):
        return obj.title or obj.url
    title_or_url.short_description = 'Новость'
    
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'email_confirmed', 'created_at')
    list_filter = ('email_confirmed', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    
    fieldsets = (
        ('Основное', {
            'fields': ('user', 'phone')
        }),
        ('Подтверждение email', {
            'fields': ('email_confirmed', 'email_confirmation_token', 'email_confirmation_sent_at')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
