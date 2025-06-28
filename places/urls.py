from django.urls import path
from .views import ThemesAPIView

urlpatterns = [
    path('themes/', ThemesAPIView.as_view(), name='themes-list'),
]
