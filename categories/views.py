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


class CategoriesAPIView(APIView):
    """카테고리 목록 조회/생성 API (새로운 번역 구조)"""

    def get(self, request):
        """카테고리 목록을 언어별로 조회"""
        # 언어 파라미터 처리
        language = request.query_params.get("lang", "ko")
        supported_languages = ["ko", "en", "jp", "cn"]

        if language not in supported_languages:
            language = "ko"  # 기본값

        # 카테고리 목록 조회 (서브카테고리 포함)
        categories = Category.objects.prefetch_related("subcategories").all()

        # 새로운 번역 구조 시리얼라이저 사용
        serializer = CategorySerializer(
            categories,
            many=True,
            language=language
        )

        return Response({
            "categories": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """번역과 함께 카테고리 생성"""
        serializer = CategoryCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "error": "잘못된 데이터입니다.",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 번역 데이터 검증
        translations_data = serializer.validated_data["translations"]

        if not translations_data:
            return Response({
                "error": "최소 하나의 번역이 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 카테고리 생성
        category = Category.objects.create()

        # 번역들 생성
        created_translations = []
        for translation_data in translations_data:
            if translation_data["name"].strip():  # 빈 이름 체크
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
            # 유효한 번역이 없으면 카테고리 삭제
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
    """특정 카테고리의 서브카테고리 목록 조회 API"""

    def get(self, request, category_id):
        """특정 카테고리의 서브카테고리 목록을 언어별로 조회"""
        # 카테고리 존재 확인
        category = get_object_or_404(Category, id=category_id)

        # 언어 파라미터 처리
        language = request.query_params.get("lang", "ko")
        supported_languages = ["ko", "en", "jp", "cn"]

        if language not in supported_languages:
            language = "ko"  # 기본값

        # 해당 카테고리의 서브카테고리들 조회
        subcategories = SubCategory.objects.filter(category=category)

        # 서브카테고리 목록 시리얼라이저 사용
        serializer = SubCategoryListSerializer(
            {},  # 빈 객체 (실제 데이터는 subcategories_queryset에서)
            language=language,
            subcategories_queryset=subcategories
        )

        return Response(
            serializer.data,  # {"subcategories": [...]}
            status=status.HTTP_200_OK
        )


class SubCategoryCreateAPIView(APIView):
    """서브카테고리 생성 API"""

    def post(self, request):
        """번역과 함께 서브카테고리 생성"""
        serializer = SubCategoryCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "error": "잘못된 데이터입니다.",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 카테고리 존재 확인
        category_id = serializer.validated_data["category_id"]
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({
                "error": "존재하지 않는 카테고리입니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 번역 데이터 검증
        translations_data = serializer.validated_data["translations"]

        if not translations_data:
            return Response({
                "error": "최소 하나의 번역이 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 서브카테고리 생성
        subcategory = SubCategory.objects.create(category=category)

        # 번역들 생성
        created_translations = []
        for translation_data in translations_data:
            if translation_data["name"].strip():  # 빈 이름 체크
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
            # 유효한 번역이 없으면 서브카테고리 삭제
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
    """카테고리 번역 수정 API"""

    def patch(self, request, category_id, lang):
        """특정 언어의 카테고리 번역 수정"""
        # 카테고리 존재 확인
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({
                "error": "존재하지 않는 카테고리입니다."
            }, status=status.HTTP_404_NOT_FOUND)

        # 번역 존재 확인
        try:
            translation = CategoryTranslation.objects.get(
                category=category,
                lang=lang
            )
        except CategoryTranslation.DoesNotExist:
            return Response({
                "error": f"{lang} 언어의 번역이 존재하지 않습니다."
            }, status=status.HTTP_404_NOT_FOUND)

        # 새로운 이름 검증
        new_name = request.data.get("name")
        if not new_name or not new_name.strip():
            return Response({
                "error": "이름은 필수입니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 번역 수정
        translation.name = new_name.strip()
        translation.save()

        return Response({
            "id": translation.id,
            "category_id": category.id,
            "lang": translation.lang,
            "name": translation.name,
            "message": f"{lang} 번역이 성공적으로 수정되었습니다."
        }, status=status.HTTP_200_OK)
