import time
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Avg, Count
from django.core.cache import cache
from .models import Book, Author, Review
from .tasks import import_books_task
from django.views.decorators.cache import never_cache
from django.conf import settings


# --- СЕСІЇ ТА COOKIES ---

@never_cache
def login_view(request):
    """
    Обробник для сторінки входу користувача.

    Обробляє POST-запит для встановлення сесії та cookie.
    Якщо ім'я користувача надано:
    1. Зберігає 'age' у сесії.
    2. Встановлює cookie 'username' з терміном життя 1 година.
    3. Перенаправляє користувача на сторінку привітання ('greeting').
    Якщо це GET-запит або дані неповні, рендерить форму входу.

    :param request: Об'єкт HttpRequest.
    :return: HttpResponse (render або redirect).
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')

        if name:
            request.session['age'] = age
            response = redirect('greeting')
            response.set_cookie('username', name, max_age=3600)
            return response

    return render(request, 'sessions_cookies/login.html')


@never_cache
def greeting_view(request):
    """
    Обробник для сторінки привітання.

    Отримує ім'я ('username') з cookie та вік ('age') з сесії.
    Якщо вік відсутній у сесії (користувач не автентифікований),
    перенаправляє на сторінку входу ('login').

    :param request: Об'єкт HttpRequest.
    :return: HttpResponse (render або redirect).
    """
    name = request.COOKIES.get('username')
    age = request.session.get('age')

    if age is None:
        return redirect('login')

    return render(request, 'sessions_cookies/greeting.html', {'name': name, 'age': age})


@never_cache
def logout_view(request):
    """
    Обробник для виходу користувача з системи.

    Очищає автентифікаційні дані:
    1. Видаляє cookie 'username'.
    2. Видаляє ключ 'age' із сесії.
    3. Повністю очищає об'єкт сесії та видаляє cookie сесії.
    Перенаправляє користувача на сторінку входу ('login').

    :param request: Об'єкт HttpRequest.
    :return: HttpResponseRedirect до 'login'.
    """
    response = redirect('login')

    if 'username' in request.COOKIES:
        response.delete_cookie('username')

    if 'age' in request.session:
        del request.session['age']

    request.session.flush()
    response.delete_cookie(settings.SESSION_COOKIE_NAME)

    return response


# --- ОПТИМІЗАЦІЯ ---

def benchmark_view(request):
    """
    Обробник для демонстрації проблеми N+1 та її вирішення.

    Вимірює час виконання:
    1. 'Поганого запиту' (N+1): Ітерація та окреме отримання пов'язаних даних.
    2. 'Хорошого запиту': Використання select_related('author') та prefetch_related('reviews')
       для зменшення кількості запитів до БД.

    Створює тестові дані, якщо книги відсутні.
    Розраховує прискорення ('speedup') хорошого запиту порівняно з поганим.

    :param request: Об'єкт HttpRequest.
    :return: HttpResponse з результатами вимірювання часу.
    """
    if not Book.objects.exists():
        a = Author.objects.create(name="Test Author")
        for i in range(100):
            b = Book.objects.create(title=f"Book {i}", author=a, rating=4.5)
            Review.objects.create(book=b, text="Super", stars=5)

    # Поганий запит (N+1)
    start = time.time()
    books_bad = list(Book.objects.all())
    for b in books_bad:
        _ = b.author.name
        _ = list(b.reviews.all())
    time_bad = time.time() - start

    # Хороший запит
    start = time.time()
    books_good = list(Book.objects.select_related('author').prefetch_related('reviews').all())
    for b in books_good:
        _ = b.author.name
        _ = list(b.reviews.all())
    time_good = time.time() - start

    if time_good > 0:
        speedup = time_bad / time_good
    else:
        speedup = 0

    return render(request, 'sessions_cookies/benchmark.html', {
        'time_bad': time_bad,
        'time_good': time_good,
        'speedup': speedup,
    })


# --- КЕШУВАННЯ ---

def cached_view(request):
    """
    Обробник для демонстрації об'єктного кешування (Low-Level Cache API).

    1. Намагається отримати список книг за ключем 'books_list' з кешу.
    2. Якщо книги відсутні у кеші:
        a) Виконує запит до БД з оптимізацією (select_related).
        b) Зберігає результат у кеші на 15 хвилин.
    Вимірює час виконання.

    :param request: Об'єкт HttpRequest.
    :return: HttpResponse з відображенням списку книг та статусу кешування.

    """
    start_time = time.time()

    books = cache.get('books_list')
    is_cached = True

    if not books:
        is_cached = False
        books = Book.objects.select_related('author').all()
        cache.set('books_list', books, 60 * 15)  # 15 хвилин

    end_time = time.time()
    execution_time = end_time - start_time

    return render(request, 'sessions_cookies/cached.html', {
        'books': books,
        'is_cached': is_cached,
        'count': len(books),
        'execution_time': execution_time,
    })


# --- АНАЛІТИКА ТА RAW SQL ---

def analytics_view(request):
    """
    Обробник для відображення статистики та аналітики книг.

    Використовує агрегаційні функції Django ORM (Avg, Count) для:
    1. Підрахунку загальної кількості відгуків (total_reviews) для кожної книги.
    2. Розрахунку середнього рейтингу (avg_rating) на основі зірок відгуків.
    Результат сортується за кількістю відгуків у порядку спадання.

    :param request: Об'єкт HttpRequest.
    :return: HttpResponse з результатами агрегації.
    """
    # Агрегація
    stats = Book.objects.annotate(
        total_reviews=Count('reviews'),
        avg_rating=Avg('reviews__stars'),
    ).order_by('-total_reviews')
    return render(request, 'sessions_cookies/analytics.html', {'stats': stats})


def raw_sql_view(request):
    """
    Обробник для демонстрації використання безпечного Raw SQL.

    Використовує Book.objects.raw() для виконання прямого SQL-запиту
    з параметризованим введенням (запобігання SQL-ін'єкціям).
    Отримує книги, рейтинг яких вищий за 3, обмежуючи результат 5 книгами.

    :param request: Об'єкт HttpRequest.
    :return: HttpResponse з відображенням результатів Raw SQL.

    """
    limit = 5
    # Безпечний RAW SQL
    books = Book.objects.raw("SELECT * FROM sessions_cookies_book WHERE rating > %s LIMIT %s", [3, limit])
    return render(request, 'sessions_cookies/raw_sql.html', {'books': books})


# --- CELERY TRIGGER ---

def start_import_view(request):
    """
    Обробник для запуску асинхронного завдання Celery.

    Викликає функцію 'import_books_task.delay()' для виконання імпорту
    у фоновому режимі. Негайно повертає відповідь користувачу зі статусом завдання.

    :param request: Об'єкт HttpRequest.
    :return: HttpResponse з ID запущеного завдання Celery (task_id).
    """
    # Запуск асинхронного завдання
    task = import_books_task.delay('admin@example.com')
    return render(request, 'sessions_cookies/import_status.html', {'task_id': task.id})
