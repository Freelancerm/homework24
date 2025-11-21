from django.contrib import admin
from .models import Author, Book, Review
from django.db.models import Count


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Конфігурація адміністративного інтерфейсу для моделі Book (Книга).

    Дозволяє відображення, пошук, фільтрацію та редагування книг.
    Включає спеціальне поле для підрахунку кількості відгуків.
    """
    list_display = ('title', 'author', 'rating', 'display_review_count', 'published_date')
    search_fields = ('title', 'author__name')
    list_filter = ('rating', 'author', 'published_date')
    list_editable = ('rating',)

    def get_queryset(self, request):
        """
        Повертає QuerySet для відображення у списку.

        Анотує QuerySet додатковим полем '_review_count',
        яке містить кількість відгуків для кожної книги.
        """
        queryset = super().get_queryset(request).annotate(
            _review_count=Count('reviews')
        )
        return queryset

    def display_review_count(self, obj):
        """
        Повертає значення анотованого поля _review_count.

        Використовується як колонка у list_display.

        :param obj: Екземпляр моделі Book.
        :return: Кількість відгуків (int)
        """
        return obj._review_count

    display_review_count.short_description = 'Відгуки'
    display_review_count.admin_order_field = '_review_count'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """
    Конфігурація адміністративного інтерфейсу для моделі Author (Автор).
    """
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Конфігурація адміністративного інтерфейсу для моделі Review (Відгук).
    """
    list_display = ('book', 'stars', 'text')
    list_filter = ('stars',)
    search_fields = ('text', 'book__title')
