from django.core.cache import cache

import os
from dotenv import load_dotenv

load_dotenv()

CACHE_PAGE_PREFIX = os.getenv('BOOKS_LIST_CACHE_KEY')

CACHE_TIMEOUT = 60 * 60


class CookieAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.COOKIES.get('username') and request.session.get('age'):
            response.set_cookie('username', request.COOKIES['username'], max_age=3600)
        return response


class BookCacheMiddleware:  # Успадкування від MiddlewareMixin видалено, використовуємо новий стиль
    """
    Middleware для повносторінкового кешування сторінок книг.

    Використовує новий (з Django 1.10+) стиль Middleware (з __init__ та __call__).
    Кешує лише успішні відповіді (HTTP 200 OK) і запобігає кешуванню редиректів.
    """

    def __init__(self, get_response):
        """
        Ініціалізація Middleware.

        :param get_response: Функція, яка викликається для отримання відповіді.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Основний метод обробки запиту/відповіді.

        1. Генерує унікальний ключ кешу на основі URL.
        2. Перевіряє кеш: якщо знайдено, повертає кешовану відповідь негайно.
        3. Якщо не знайдено, викликає View для генерації відповіді.
        4. Кешує відповідь (якщо статус 200 OK) і повертає її.

        :param request: Об'єкт HttpRequest.
        :return: Об'єкт HttpResponse.
        """
        if request.path != '/analytics/':
            return self.get_response(request)

        cache_key = CACHE_PAGE_PREFIX + request.path

        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response

        response = self.get_response(request)

        if response.status_code == 200:
            cache.set(cache_key, response, CACHE_TIMEOUT)

        return response
