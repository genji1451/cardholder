from django.urls import path
from . import views

urlpatterns = [
    path('sheets/import/', views.SheetsImportView.as_view(), name='sheets-import'),
]
