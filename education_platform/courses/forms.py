from django import forms
from django.db import models
from .models import Enrollment, TimeSlot

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student_name', 'student_phone', 'student_email', 'student_comment', 'data_consent']
        widgets = {
            'student_name': forms.TextInput(attrs={'placeholder': 'Ваше имя'}),
            'student_phone': forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'}),
            'student_email': forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
            'student_comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Комментарий...'}),
        }
        labels = {
            'student_name': 'Имя',
            'student_phone': 'Телефон',
            'student_email': 'Email',
            'student_comment': 'Комментарий',
            'data_consent': 'Согласие на обработку данных',
        }
    
    # Поле для выбора ячеек
    time_slots = forms.ModelMultipleChoiceField(
        queryset=TimeSlot.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label='Выберите дни и время',
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        
        if self.course:
            # Фильтруем только активные ячейки этого курса со свободными местами
            self.fields['time_slots'].queryset = TimeSlot.objects.filter(
                course=self.course,
                is_active=True
            ).filter(booked_seats__lt=models.F('max_seats'))
    
    def clean_time_slots(self):
        slots = self.cleaned_data.get('time_slots')
        
        if not slots:
            raise forms.ValidationError("Выберите хотя бы одно время для занятий")
        
        # Проверяем доступность каждого слота
        unavailable_slots = []
        for slot in slots:
            if slot.booked_seats >= slot.max_seats:
                unavailable_slots.append(f"{slot.get_day_of_week_display()} {slot.get_time_display()}")
        
        if unavailable_slots:
            raise forms.ValidationError(
                f"На следующие занятия места закончились: {', '.join(unavailable_slots)}"
            )
        
        return slots