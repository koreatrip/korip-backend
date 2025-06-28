from django.urls import path
from categories.views import CategoriesAPIView

urlpatterns = [
    path("", CategoriesAPIView.as_view(), name="categories-list"),
]
