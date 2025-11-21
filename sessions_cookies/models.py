from django.db import models


class Author(models.Model):
    """
    Модель, що представляє автора книги.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        """
        Повертає строкове представлення об'єкта (ім'я автора).
        """
        return self.name


class Book(models.Model):
    """
    Модель, що представляє книгу.

    Містить інформацію про назву, автора, рейтинг та дату публікації.
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    rating = models.FloatField(default=0.0, db_index=True)
    published_date = models.DateField(auto_now_add=True)

    def __str__(self):
        """
        Повертає строкове представлення об'єкта (назва книги).
        """
        return self.title


class Review(models.Model):
    """
    Модель, що представляє відгук користувача про певну книгу.
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    stars = models.IntegerField(default=5)

    def __str__(self):
        return f"Рейтинг книги: {self.book.title}"