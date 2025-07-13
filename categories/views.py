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


# 카테고리 목록 API
class CategoriesAPIView(APIView):
    def get(self, request):
        language = request.query_params.get("lang", "ko")
        supported_languages = ["ko", "en", "jp", "cn"]

        if language not in supported_languages:
            language = "ko"

        # 카테고리 목록만 조회
        return self._get_categories(request, language)

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


# 서브카테고리 목록 API
class SubCategoriesAPIView(APIView):
    def get(self, request, category_id):
        language = request.query_params.get("lang", "ko")
        supported_languages = ["ko", "en", "jp", "cn"]

        if language not in supported_languages:
            language = "ko"

        # 서브카테고리 목록 조회
        return self._get_subcategories(request, language, category_id)

    def _get_subcategories(self, request, language, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
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
