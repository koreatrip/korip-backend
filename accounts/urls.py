from django.urls import path
from .views import LanguageListAPI, LanguageSelectAPI

urlpatterns = [
    path('languages/', LanguageListAPI.as_view(), name='language-list'),
    path('language/', LanguageSelectAPI.as_view(), name='language-select'),
]