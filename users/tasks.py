import random
from celery import shared_task
from django.core.mail import send_mail


@shared_task
def process_user_data(user_id):
    print(f"Фоновая обработка данных пользователя ID: {user_id}")
    return f"Данные пользователя {user_id} успешно обработаны"


@shared_task
def clear_expired_data():
    print("Запуск очистки устаревших данных по расписанию...")
    return "Очистка завершена"


@shared_task
def send_welcome_email(user_email):
    send_mail(
        subject="Добро пожаловать!",
        message="Спасибо за регистрацию на нашем проекте!",
        from_email="noreply@example.com",
        recipient_list=[user_email],
        fail_silently=True,
    )
    return f"Письмо успешно отправлено на {user_email}"
