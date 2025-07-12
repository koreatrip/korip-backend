from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from categories.models import (
    Category, SubCategory,
    CategoryTranslation, SubCategoryTranslation
)
from categories.serializers import (
    CategorySerializer,
    SubCategoryListSerializer
)


# 통합 카테고리 API - 조회 전용
class CategoriesAPIView(APIView):
    def get(self, request):
        language = request.query_params.get("lang", "ko")
        supported_languages = ["ko", "en", "jp", "cn"]

        if language not in supported_languages:
            language = "ko"

        request_type = request.query_params.get("type", "categories")
        # 서브카테고리 목록 조회
        if request_type == "subcategories":
            return self._get_subcategories(request, language)
        else:
            # 카테고리 목록 조회
            return self._get_categories(request, language)

# 카테고리 목록 조회
    def _get_categories(self, request, language):
        categories = Category.objects.prefetch_related("subcategories").all()

        serializer = CategorySerializer(
            categories,
            many=True,
            language=language
        )

        return Response({
            "categories": serializer.data
        }, status=status.HTTP_200_OK)

# 서브카테고리 목록 조회
    def _get_subcategories(self, request, language):
        category_id = request.query_params.get("category_id")

        if not category_id:
            return Response({
                "error": "category_id 파라미터가 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            category_id = int(category_id)
            category = Category.objects.get(id=category_id)
        except (ValueError, Category.DoesNotExist):
            return Response({
                "error": "존재하지 않는 카테고리입니다."
            }, status=status.HTTP_404_NOT_FOUND)

        subcategories = SubCategory.objects.filter(category=category)

        serializer = SubCategoryListSerializer(
            {},
            language=language,
            subcategories_queryset=subcategories
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
