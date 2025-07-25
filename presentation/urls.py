# presentation/urls.py

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "presentation"

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('presentation/<int:pk>/', views.presentation_detail, name='detail'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)