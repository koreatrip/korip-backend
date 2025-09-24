from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import RequestError

from favorites.serializers import (
    FavoritePlaceSerializer, 
    FavoritePlaceListSerializer,
    FavoriteSubRegionSerializer,
    FavoriteSubRegionListSerializer
)
from favorites.models import FavoritePlace, FavoriteSubRegion   
from utils.pagination.favorite_pagination import FavoritePagination
from utils.helper.lang_helper import normalize_lang


class FavoritePlaceAPIView(APIView):

    permission_classes = [IsAuthenticated]
    pagination_class = FavoritePagination
    
    @swagger_auto_schema(
        operation_summary="즐겨찾기 장소 추가/삭제",
        operation_description="특정 장소를 즐겨찾기에 추가하거나 제거합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['place_id'],
            properties={
                'place_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="장소 ID"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="즐겨찾기 추가/삭제 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "is_favorite": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="즐겨찾기 상태"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="결과 메시지"),
                    }
                )
            ),
            400: openapi.Response(description="잘못된 요청"),
            401: openapi.Response(description="인증 필요"),
            404: openapi.Response(description="존재하지 않는 장소")
        },
        tags=["즐겨찾기 - 장소"]
    )
    def post(self, request):
        serializer = FavoritePlaceSerializer(data=request.data)
        
        if not serializer.is_valid():
            raise RequestError(ErrorCode.INVALID_DATA)
        
        result = serializer.toggle_favorite(request.user)
        
        return Response(result, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="즐겨찾기 장소 목록 조회",
        operation_description="사용자의 즐겨찾기 장소 목록을 최신순으로 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                "lang",
                openapi.IN_QUERY,
                description="언어 코드 (기본값: ko)",
                type=openapi.TYPE_STRING,
                default="ko",
                enum=["ko", "en", "jp", "cn"]
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="페이지 번호",
                type=openapi.TYPE_INTEGER,
                default=1
            )
        ],
        responses={
            200: openapi.Response(
                description="즐겨찾기 장소 목록 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="전체 개수"),
                        "next": openapi.Schema(type=openapi.TYPE_STRING, description="다음 페이지 URL"),
                        "previous": openapi.Schema(type=openapi.TYPE_STRING, description="이전 페이지 URL"),
                        "favorite_places": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="장소 ID"),
                                    "content_id": openapi.Schema(type=openapi.TYPE_STRING, description="콘텐츠 ID"),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING, description="장소명"),
                                    "description": openapi.Schema(type=openapi.TYPE_STRING, description="장소 설명"),
                                    "address": openapi.Schema(type=openapi.TYPE_STRING, description="주소"),
                                    "latitude": openapi.Schema(type=openapi.TYPE_NUMBER, description="위도"),
                                    "longitude": openapi.Schema(type=openapi.TYPE_NUMBER, description="경도"),
                                    "phone_number": openapi.Schema(type=openapi.TYPE_STRING, description="전화번호"),
                                    "use_time": openapi.Schema(type=openapi.TYPE_STRING, description="이용시간"),
                                    "link_url": openapi.Schema(type=openapi.TYPE_STRING, description="링크 URL"),
                                    "image_url": openapi.Schema(type=openapi.TYPE_STRING, description="이미지 URL"),
                                    "category": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="카테고리 ID"),
                                            "name": openapi.Schema(type=openapi.TYPE_STRING, description="카테고리명")
                                        }
                                    ),
                                    "sub_category": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브카테고리 ID"),
                                            "name": openapi.Schema(type=openapi.TYPE_STRING, description="서브카테고리명")
                                        }
                                    ),
                                    "region": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID"),
                                            "name": openapi.Schema(type=openapi.TYPE_STRING, description="지역명")
                                        }
                                    ),
                                    "sub_region": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역구 ID"),
                                            "name": openapi.Schema(type=openapi.TYPE_STRING, description="지역구명")
                                        }
                                    ),
                                    "favorite_count": openapi.Schema(type=openapi.TYPE_INTEGER, description="즐겨찾기 수"),
                                    "is_favorite": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="즐겨찾기 여부"),
                                    "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="장소 생성일"),
                                    "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="장소 수정일"),
                                    "favorited_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="즐겨찾기 등록일")
                                }
                            )
                        )
                    }
                )
            ),
            401: openapi.Response(description="인증 필요")
        },
        tags=["즐겨찾기 - 장소"]
    )
    def get(self, request):
        language = normalize_lang(request.query_params.get("lang"))

        favorite_relations = FavoritePlace.objects.filter(user=request.user).select_related('place').prefetch_related('place__translations').order_by('-created_at')
        
        user_favorite_place_ids = set(rel.place.id for rel in favorite_relations)

        paginator = self.pagination_class()
        paginator.results_field_name = "favorite_places"
        page = paginator.paginate_queryset(favorite_relations, request)
        
        favorite_place_serializer = FavoritePlaceListSerializer(
            page,
            many=True,
            context={
                "language": language,
                "user_favorite_place_ids": user_favorite_place_ids
            }
        )

        return paginator.get_paginated_response(favorite_place_serializer.data)
    

class FavoriteSubRegionAPIView(APIView):

    permission_classes = [IsAuthenticated]
    pagination_class = FavoritePagination
    
    @swagger_auto_schema(
        operation_summary="즐겨찾기 지역구 추가/삭제",
        operation_description="특정 지역구를 즐겨찾기에 추가하거나 제거합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['sub_region_id'],
            properties={
                'sub_region_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="지역구 ID"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="즐겨찾기 추가/삭제 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "is_favorite": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="즐겨찾기 상태"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="결과 메시지"),
                    }
                )
            ),
            400: openapi.Response(description="잘못된 요청"),
            401: openapi.Response(description="인증 필요"),
            404: openapi.Response(description="존재하지 않는 지역구")
        },
        tags=["즐겨찾기 - 지역구"]
    )
    def post(self, request):
        serializer = FavoriteSubRegionSerializer(data=request.data)
        
        if not serializer.is_valid():
            raise RequestError(ErrorCode.INVALID_DATA)
        
        result = serializer.toggle_favorite(request.user)
        
        return Response(result, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="즐겨찾기 지역구 목록 조회",
        operation_description="사용자의 즐겨찾기 지역구 목록을 최신순으로 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                "lang",
                openapi.IN_QUERY,
                description="언어 코드 (기본값: ko)",
                type=openapi.TYPE_STRING,
                default="ko",
                enum=["ko", "en", "jp", "cn"]
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="페이지 번호",
                type=openapi.TYPE_INTEGER,
                default=1
            )
        ],
        responses={
            200: openapi.Response(
                description="즐겨찾기 지역구 목록 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="전체 개수"),
                        "next": openapi.Schema(type=openapi.TYPE_STRING, description="다음 페이지 URL"),
                        "previous": openapi.Schema(type=openapi.TYPE_STRING, description="이전 페이지 URL"),
                        "favorite_subregions": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역구 ID"),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING, description="지역구명"),
                                    "description": openapi.Schema(type=openapi.TYPE_STRING, description="지역구 설명"),
                                    "features": openapi.Schema(type=openapi.TYPE_STRING, description="지역구 특징"),
                                    "latitude": openapi.Schema(type=openapi.TYPE_NUMBER, description="위도"),
                                    "longitude": openapi.Schema(type=openapi.TYPE_NUMBER, description="경도"),
                                    "favorite_count": openapi.Schema(type=openapi.TYPE_INTEGER, description="즐겨찾기 수"),
                                    "is_favorite": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="즐겨찾기 여부"),
                                    "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="지역구 생성일"),
                                    "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="지역구 수정일"),
                                    "favorited_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="즐겨찾기 등록일")
                                }
                            )
                        )
                    }
                )
            ),
            401: openapi.Response(description="인증 필요")
        },
        tags=["즐겨찾기 - 지역구"]
    )
    def get(self, request):
        language = normalize_lang(request.query_params.get("lang"))

        favorite_relations = FavoriteSubRegion.objects.filter(user=request.user).select_related('sub_region').prefetch_related('sub_region__translations').order_by('-created_at')

        user_favorite_subregion_ids = set(rel.sub_region.id for rel in favorite_relations)

        paginator = self.pagination_class()
        paginator.results_field_name = "favorite_subregions"
        page = paginator.paginate_queryset(favorite_relations, request)
        
        favorite_subregion_serializer = FavoriteSubRegionListSerializer(
            page,
            many=True,
            context={
                "language": language,
                "user_favorite_subregion_ids": user_favorite_subregion_ids
            }
        )

        return paginator.get_paginated_response(favorite_subregion_serializer.data)