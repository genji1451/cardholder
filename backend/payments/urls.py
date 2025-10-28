from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create-order/', views.create_order, name='create_order'),
    path('robokassa/result/', views.robokassa_result, name='robokassa_result'),
    path('status/<uuid:order_id>/', views.payment_status, name='payment_status'),
    path('success/', views.payment_success, name='payment_success'),
    path('fail/', views.payment_fail, name='payment_fail'),
]
