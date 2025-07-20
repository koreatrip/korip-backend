# categories/views.py - 완전한 버전 (SubCategoriesAPIView 포함)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
    @swagger_auto_schema(
        operation_summary="카테고리 목록 조회",
        operation_description="전체 카테고리 목록을 조회합니다. 언어 파라미터를 통해 다국어 지원이 가능합니다.",
        manual_parameters=[
            openapi.Parameter(
                'lang',
                openapi.IN_QUERY,
                description="언어 코드 (ko, en, jp, cn)",
                type=openapi.TYPE_STRING,
                default='ko',
                enum=['ko', 'en', 'jp', 'cn']
            )
        ],
        responses={
            200: openapi.Response(
                description="카테고리 목록 조회 성공",
                examples={
                    "application/json": {
                        "categories": [
                            {
                                "id": 1,
                                "name": "여행",
                                "subcategories": [
                                    {
                                        "id": 1,
                                        "name": "국내여행"
                                    },
                                    {
                                        "id": 2,
                                        "name": "해외여행"
                                    }
                                ]
                            }
                        ]
                    }
                }
            ),
            400: openapi.Response(
                description="잘못된 요청"
            )
        },
        tags=['카테고리']
    )
    def get(self, request):
        try:
            language = request.query_params.get("lang", "ko")
            supported_languages = ["ko", "en", "jp", "cn"]

            if language not in supported_languages:
                language = "ko"

            # 카테고리 목록만 조회
            return self._get_categories(request, language)

        except Exception as e:
            return Response({
                "error": f"서버 에러: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_categories(self, request, language):
        try:
            categories = Category.objects.prefetch_related("subcategories").all()

            # Context 방식 사용
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
    @swagger_auto_schema(
        operation_summary="서브카테고리 목록 조회",
        operation_description="특정 카테고리의 서브카테고리 목록을 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'category_id',
                openapi.IN_PATH,
                description="카테고리 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'lang',
                openapi.IN_QUERY,
                description="언어 코드 (ko, en, jp, cn)",
                type=openapi.TYPE_STRING,
                default='ko',
                enum=['ko', 'en', 'jp', 'cn']
            )
        ],
        responses={
            200: openapi.Response(
                description="서브카테고리 목록 조회 성공",
                examples={
                    "application/json": {
                        "subcategories": [
                            {
                                "id": 1,
                                "name": "국내여행"
                            },
                            {
                                "id": 2,
                                "name": "해외여행"
                            }
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
            400: openapi.Response(
                description="잘못된 요청"
            )
        },
        tags=['카테고리']
    )
    def get(self, request, category_id):
        try:
            language = request.query_params.get("lang", "ko")
            supported_languages = ["ko", "en", "jp", "cn"]

            if language not in supported_languages:
                language = "ko"

            # 서브카테고리 목록 조회
            return self._get_subcategories(request, language, category_id)

        except Exception as e:
            return Response({
                "error": f"서버 에러: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            context={
                "language": language,
                "subcategories_queryset": subcategories
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
