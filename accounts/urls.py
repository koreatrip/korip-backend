from django.urls import path
from . import views

urlpatterns = [
    path('languages/', views.LanguageAPI.as_view(), name='language-api'),
]