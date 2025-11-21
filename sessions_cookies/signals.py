from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Book
import os
from dotenv import load_dotenv

load_dotenv()

BOOKS_LIST_CACHE_KEY = os.getenv('BOOKS_LIST_CACHE_KEY')


@receiver(post_save, sender=Book)
def clear_books_list_cache_on_save(sender, instance, **kwargs):
    """ Очищує кеш зі списком книг при додаванні або зміні книги. """
    cache.delete(BOOKS_LIST_CACHE_KEY)
    cache_key = BOOKS_LIST_CACHE_KEY + '/analytics/'
    cache.delete(cache_key)
    print(f"Кеш очищено.Книга '{instance.title}' була збережена/оновлена.")


@receiver(post_delete, sender=Book)
def clear_books_list_cache_on_delete(sender, instance, **kwargs):
    """ Очищує кеш зі списком книг при видаленні книги. """
    cache.delete(BOOKS_LIST_CACHE_KEY)
    cache_key = BOOKS_LIST_CACHE_KEY + '/analytics/'
    cache.delete(cache_key)
    print(f"Кеш очищено.Книга '{instance.title}' була видалена. ")
