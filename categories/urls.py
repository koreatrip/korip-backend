from django.urls import path
from categories.views import CategoriesAPIView, SubCategoriesAPIView

urlpatterns = [
    path("", CategoriesAPIView.as_view(), name="categories-list"),
    path("/<int:category_id>/subcategories", SubCategoriesAPIView.as_view(), name="subcategories-list"),
]
