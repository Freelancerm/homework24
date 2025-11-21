from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('greeting/', views.greeting_view, name='greeting'),
    path('logout/',views.logout_view, name='logout'),
    path('benchmark/', views.benchmark_view, name='benchmark'),
    path('cached/', views.cached_view, name='cached'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('raw/', views.raw_sql_view, name='raw_sql'),
    path('import/', views.start_import_view, name='import'),
]