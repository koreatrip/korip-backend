from django.urls import path
from categories.views import (
    CategoriesAPIView,
    SubCategoriesAPIView,
    SubCategoryCreateAPIView,
    CategoryTranslationAPIView
)

urlpatterns = [
    # 카테고리 목록 조회/생성
    # GET /api/categories/ - 목록 조회
    # POST /api/categories/ - 카테고리 생성
    path("", CategoriesAPIView.as_view(), name="categories-list"),

    # 서브카테고리 생성
    # POST /api/categories/subcategories/ - 서브카테고리 생성
    path("subcategories/", SubCategoryCreateAPIView.as_view(), name="subcategories-create"),

    # 특정 카테고리의 서브카테고리 목록 조회
    # GET /api/categories/{category_id}/subcategories/ - 서브카테고리 목록
    path("<int:category_id>/subcategories/", SubCategoriesAPIView.as_view(), name="subcategories-list"),

    # 특정 언어 번역 수정
    # PATCH /api/categories/{category_id}/translations/{lang}/ - 번역 수정
    path("<int:category_id>/translations/<str:lang>/", CategoryTranslationAPIView.as_view(),
         name="category-translation-update"),
]
