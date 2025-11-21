from django.apps import AppConfig


class SessionsCookiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sessions_cookies'

    def ready(self):
        """ Імпортуємо наші сигнали при готовності додатку. """
        from . import signals
