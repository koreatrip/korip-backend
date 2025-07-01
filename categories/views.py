from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from categories.models import Category, SubCategory
from categories.serializers import (
    CategorySerializer,
    SubCategoryListSerializer,
    CategoryCreateSerializer,
    SubCategoryCreateSerializer
)
from categories.models import (
    Category, SubCategory,
    CategoryTranslation, SubCategoryTranslation
)


# 카테고리 목록 조회/생성 API
class CategoriesAPIView(APIView):

    def get(self, request):
        language = request.query_params.get("lang", "ko")
        supported_languages = ["ko", "en", "jp", "cn"]

        if language not in supported_languages:
            language = "ko"  # 기본값

        # 카테고리 목록 조회 (서브카테고리 포함)
        categories = Category.objects.prefetch_related("subcategories").all()

        serializer = CategorySerializer(
            categories,
            many=True,
            language=language
        )

        return Response({
            "categories": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "error": "잘못된 데이터입니다.",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        translations_data = serializer.validated_data["translations"]

        if not translations_data:
            return Response({
                "error": "최소 하나의 번역이 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        category = Category.objects.create()

        created_translations = []
        for translation_data in translations_data:
            if translation_data["name"].strip():
                translation = CategoryTranslation.objects.create(
                    category=category,
                    lang=translation_data["lang"],
                    name=translation_data["name"]
                )
                created_translations.append({
                    "lang": translation.lang,
                    "name": translation.name
                })

        if not created_translations:
            category.delete()
            return Response({
                "error": "유효한 번역이 없습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "id": category.id,
            "translations": created_translations,
            "message": "카테고리가 성공적으로 생성되었습니다."
        }, status=status.HTTP_201_CREATED)


class SubCategoriesAPIView(APIView):

    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        language = request.query_params.get("lang", "ko")
        supported_languages = ["ko", "en", "jp", "cn"]

        if language not in supported_languages:
            language = "ko"

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


class SubCategoryCreateAPIView(APIView):

    def post(self, request):
        serializer = SubCategoryCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "error": "잘못된 데이터입니다.",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        category_id = serializer.validated_data["category_id"]
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({
                "error": "존재하지 않는 카테고리입니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        translations_data = serializer.validated_data["translations"]

        if not translations_data:
            return Response({
                "error": "최소 하나의 번역이 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        subcategory = SubCategory.objects.create(category=category)

        created_translations = []
        for translation_data in translations_data:
            if translation_data["name"].strip():
                translation = SubCategoryTranslation.objects.create(
                    sub_category=subcategory,
                    lang=translation_data["lang"],
                    name=translation_data["name"]
                )
                created_translations.append({
                    "lang": translation.lang,
                    "name": translation.name
                })

        if not created_translations:
            subcategory.delete()
            return Response({
                "error": "유효한 번역이 없습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "id": subcategory.id,
            "category_id": category.id,
            "translations": created_translations,
            "message": "서브카테고리가 성공적으로 생성되었습니다."
        }, status=status.HTTP_201_CREATED)


class CategoryTranslationAPIView(APIView):

    def patch(self, request, category_id, lang):

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({
                "error": "존재하지 않는 카테고리입니다."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            translation = CategoryTranslation.objects.get(
                category=category,
                lang=lang
            )
        except CategoryTranslation.DoesNotExist:
            return Response({
                "error": f"{lang} 언어의 번역이 존재하지 않습니다."
            }, status=status.HTTP_404_NOT_FOUND)

        new_name = request.data.get("name")
        if not new_name or not new_name.strip():
            return Response({
                "error": "이름은 필수입니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        translation.name = new_name.strip()
        translation.save()

        return Response({
            "id": translation.id,
            "category_id": category.id,
            "lang": translation.lang,
            "name": translation.name,
            "message": f"{lang} 번역이 성공적으로 수정되었습니다."
        }, status=status.HTTP_200_OK)
