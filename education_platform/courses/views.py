from django.views.generic import DetailView
from django.shortcuts import render, get_object_or_404
from .models import Course, TimeSlot

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        # Получаем все активные слоты для этого курса
        time_slots = course.time_slots.filter(is_active=True)
        
        # Простая структура данных для шаблона
        schedule_data = []
        
        # Дни недели
        days = dict(TimeSlot.DAYS_OF_WEEK)
        # Временные слоты
        times = dict(TimeSlot.TIME_SLOTS)
        
        # Проходим по каждому времени
        for time_code, time_display in times.items():
            row = {
                'time_code': time_code,
                'time_display': time_display,
                'days': {}
            }
            
            # Для каждого дня проверяем есть ли слот
            for day_code, day_name in days.items():
                slot = time_slots.filter(
                    day_of_week=day_code,
                    time_slot=time_code
                ).first()
                
                if slot:
                    row['days'][day_code] = {
                        'id': slot.id,
                        'max_seats': slot.max_seats,
                        'booked_seats': slot.booked_seats,
                        'free_seats': slot.max_seats - slot.booked_seats,
                        'has_free_seats': slot.booked_seats < slot.max_seats,
                        'room': slot.room,
                        'is_active': slot.is_active,
                    }
                else:
                    row['days'][day_code] = None
            
            schedule_data.append(row)
        
        context['schedule_data'] = schedule_data
        context['days'] = days  # Передаем отдельно дни для заголовков
        context['times'] = times  # Передаем отдельно времена
        
        # Передаем ID курса для JavaScript
        context['course_id'] = course.id
        
        return context

# Остальные views остаются как были
def index(request):
    return render(request, 'courses/index.html')

def register_page(request):
    return render(request, 'courses/register.html')

def login_page(request):
    return render(request, 'courses/login.html')

def profile_page(request):
    return render(request, 'courses/profile.html')

def news_page(request):
    return render(request, 'courses/news.html')

def api_test_page(request):
    return render(request, 'courses/api_test.html')