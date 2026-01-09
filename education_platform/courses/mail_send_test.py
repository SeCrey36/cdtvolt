from django.conf import settings
from django.core.mail import send_mail

send_mail(
    'Тест Gmail',
    'Проверка отправки писем',
    'secretboys3655l@gmail.com',
    ['petya.gorodilov@mail.ru'],  # Куда отправить
    fail_silently=False,
)
print("Проверьте почту (в том числе спам!)")

