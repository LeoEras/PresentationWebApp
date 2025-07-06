# presentation/urls.py

from django.urls import path
from . import views

app_name = "presentation"

urlpatterns = [
    path('', views.home, name='home'),
]