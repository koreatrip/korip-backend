from django.urls import path
from categories.views import CategoriesAPIView

# 모든 카테고리 관련 기능을 하나의 엔드포인트에서 쿼리 파라미터로 처리
urlpatterns = [
    path("", CategoriesAPIView.as_view(), name="categories-list"),
]
