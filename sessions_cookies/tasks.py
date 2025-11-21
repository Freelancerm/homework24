from celery import shared_task
from .models import Book, Author
import time


@shared_task
def import_books_task(email_to_notify):
    """
    Фонова задача Celery для імітації довготривалого процесу імпорту книг.

    Ця задача виконується асинхронно, не блокуючи основний потік веб-сервера.
    Після завершення імітації імпорту, вона додає тестові дані до бази даних.

    :param email_to_notify: Електронна адреса, на яку має бути відправлено
                            повідомлення про завершення імпорту.
    :type email_to_notify: str
    :return: Строка-підтвердження про успішне завершення імпорту.
    :rtype: str

    :Keyword Args:
        * Emulation: Затримка 5 секунд для імітації тривалого процесу.
        * DB Operations: Створює автора 'Celery Robot' та дві нові книги.
        * Logging: Виводить повідомлення про завершення та успішне відправлення
                   сповіщення у консоль.
    """
    # Емуляція довгого імпорту (5 секунд)
    time.sleep(5)

    # Створення тестових даних
    author, _ = Author.objects.get_or_create(name='Celery Robot')
    Book.objects.create(title="Imported Book 1", author=author, rating=5.0)
    Book.objects.create(title="Imported Book 2", author=author, rating=4.0)

    # Вивід у консоль
    print(f"EMAIL успішно відправлено на адресу: {email_to_notify}. Імпорт завершено!")

    return "Імпорт завершено"
