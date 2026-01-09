import smtplib
import ssl

print("=== Тест SMTP для Gmail (порт 465) ===")

try:
    # Создаем SSL контекст (можно небезопасный для теста)
    context = ssl._create_unverified_context()
    
    # Сразу SSL соединение (порт 465)
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=10)
    print("SSL соединение установлено сразу")
    
    server.quit()
    print("Порт 465 готов к использованию")
    
except Exception as e:
    print(f"Ошибка: {e}")