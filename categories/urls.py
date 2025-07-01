from django.urls import path
from categories.views import (
    CategoriesAPIView,
    SubCategoriesAPIView,
    SubCategoryCreateAPIView,
    CategoryTranslationAPIView
)

urlpatterns = [
    path("", CategoriesAPIView.as_view(), name="categories-list"),
    path("subcategories/", SubCategoryCreateAPIView.as_view(), name="subcategories-create"),
    path("<int:category_id>/subcategories/", SubCategoriesAPIView.as_view(), name="subcategories-list"),
    path("<int:category_id>/translations/<str:lang>/", CategoryTranslationAPIView.as_view(),
         name="category-translation-update"),
]
