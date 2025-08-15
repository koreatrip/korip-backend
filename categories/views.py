from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from categories.models import Category, SubCategory
from categories.serializers import CategorySerializer, SubCategoryListSerializer


class CategoriesAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="대분류 카테고리 목록 조회",
        manual_parameters=[
            openapi.Parameter(
                "lang",
                openapi.IN_QUERY,
                description="언어 코드 (ko, en, jp, cn)",
                type=openapi.TYPE_STRING,
                default="ko",
                enum=["ko", "en", "jp", "cn"]
            )
        ],
        responses={
            200: openapi.Response(
                description="대분류 카테고리 목록 조회 성공",
                examples={
                    "application/json": {
                        "categories": [
                            {"id": 1, "name": "문화"},
                            {"id": 2, "name": "자연"},
                            {"id": 3, "name": "액티비티"},
                            {"id": 4, "name": "쇼핑"},
                            {"id": 5, "name": "음식"},
                            {"id": 6, "name": "숙박"},
                            {"id": 7, "name": "K-POP"}
                        ]
                    }
                }
            ),
            400: openapi.Response(description="잘못된 요청")
        },
        tags=["카테고리"]
    )
    def get(self, request):
        try:
            language = request.query_params.get("lang", "ko")
            supported_languages = ["ko", "en", "jp", "cn"]

            if language not in supported_languages:
                language = "ko"

            return self._get_categories(request, language)

        except Exception as e:
            return Response({
                "error": f"서버 에러: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_categories(self, request, language):
        try:
            categories = Category.objects.all()

            serializer = CategorySerializer(
                categories,
                many=True,
                context={"language": language}
            )

            return Response({
                "categories": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"카테고리 조회 에러: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubCategoriesAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="서브카테고리 목록 조회",
        manual_parameters=[
            openapi.Parameter(
                "category_id",
                openapi.IN_PATH,
                description="대분류 카테고리 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                "lang",
                openapi.IN_QUERY,
                description="언어 코드 (ko, en, jp, cn)",
                type=openapi.TYPE_STRING,
                default="ko",
                enum=["ko", "en", "jp", "cn"]
            )
        ],
        responses={
            200: openapi.Response(
                description="서브카테고리 목록 조회 성공",
                examples={
                    "application/json": {
                        "subcategories": [
                            {"id": 26, "name": "호텔"},
                            {"id": 27, "name": "펜션"},
                            {"id": 28, "name": "리조트"},
                            {"id": 29, "name": "모텔"}
                        ]
                    }
                }
            ),
            404: openapi.Response(
                description="카테고리를 찾을 수 없음",
                examples={
                    "application/json": {
                        "error": "존재하지 않는 카테고리입니다."
                    }
                }
            ),
            400: openapi.Response(description="잘못된 요청")
        },
        tags=["카테고리"]
    )
    def get(self, request, category_id):
        language = request.query_params.get("lang", "ko")
        supported_languages = ["ko", "en", "jp", "cn"]

        if language not in supported_languages:
            language = "ko"

        return self._get_subcategories(request, language, category_id)

    def _get_subcategories(self, request, language, category_id):
        try:
            category = get_object_or_404(Category, id=category_id)
            subcategories = SubCategory.objects.filter(category=category)

            serializer = SubCategoryListSerializer(
                {},
                context={
                    "language": language,
                    "subcategories_queryset": subcategories
                }
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except Http404:
            return Response({
                "error": "존재하지 않는 카테고리입니다."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": f"서브카테고리 조회 에러: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
