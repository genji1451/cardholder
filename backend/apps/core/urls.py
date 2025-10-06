from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api_root'),
    path('health/', views.health_check, name='health_check'),
    path('init/', views.init_database, name='init_database'),
    path('migrate/', views.run_migrations, name='run_migrations'),
    path('auth/telegram/', views.telegram_auth, name='telegram_auth'),
    path('auth/me/', views.current_user, name='current_user'),
    path('auth/subscription/', views.check_telegram_subscription, name='check_subscription'),
]