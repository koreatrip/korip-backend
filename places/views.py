from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from regions.models import Region, SubRegion
from regions.serializers import SubRegionSerializer
from places.models import Place
from places.serializers import PlaceSerializer
from preferences.models import UserPreference


class PlacesListAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="명소 목록 조회 (데이터 확인용)",
        operation_description="전체 명소 목록을 조회합니다. `category_id`, `region_id`로 필터링 가능합니다.",
        manual_parameters=[
            openapi.Parameter(
                'lang',
                openapi.IN_QUERY,
                description="언어 코드 (기본값: ko)",
                type=openapi.TYPE_STRING,
                default='ko',
                enum=['ko', 'en', 'jp', 'cn']
            ),
            openapi.Parameter(
                'category_id',
                openapi.IN_QUERY,
                description="카테고리 ID(선택)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'region_id',
                openapi.IN_QUERY,
                description="지역 ID(선택)",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: openapi.Response(
                description="명소 목록 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'places': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='명소 ID'),
                                    'content_id': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='외부 컨텐츠 ID'),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='명소명(요청 lang 기준)'),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='설명(요청 lang 기준)'),
                                    'feature': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='특징(요청 lang 기준)'),
                                    'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description='카테고리 ID'),
                                    'sub_category_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description='서브 카테고리 ID'),
                                    'region_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='지역 ID'),
                                    'sub_region_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description='서브지역 ID'),
                                    'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='위도'),
                                    'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='경도'),
                                    'favorite_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='즐겨찾기 수'),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='생성일'),
                                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='수정일'),
                                }
                            )
                        )
                    }
                )
            )
        },
        tags=['명소']
    )

    def get(self, request):
        language = request.query_params.get("lang", "ko")
        queryset = Place.objects.all()
        category_id = request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category=category_id)
        region_id = request.query_params.get("region_id")
        if region_id:
            queryset = queryset.filter(region=region_id)

        # TODO: 한국어 번역 기준 정렬 구현 예정, 현재는 created_at 순으로 임시 처리
        queryset = queryset.order_by("-favorite_count", "-created_at")

        serializer = PlaceSerializer(
            queryset,
            many=True,
            context={"language": language}
        )

        return Response({
            "places": serializer.data
        }, status=status.HTTP_200_OK)

class PlaceTourListAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        language = request.query_params.get("lang", "ko")
        region_id = request.query_params.get("lang", "1")
        most_favoriate_subregion = SubRegion.objects.filter(region_id=region_id).order_by('-favorite_count', 'id')[:4]

        subregion_serializer = SubRegionSerializer(
            most_favoriate_subregion,
            many=True,
            context={"language": language}
        )

        major_places = Place.objects.filter(sub_region=most_favoriate_subregion[0]).order_by('-favorite_count', 'id')[:4]

        place_serializer = PlaceSerializer(
            major_places,
            many=True,
            context={"language": language}
        )

        if request.user.is_authenticated:
            user = request.user
            user_preferences = UserPreference.objects.filter(user_id=user.id)
            # user_recommended_places = 

        return Response(
            {
                "popular_subregions": subregion_serializer.data,
                "major_places": place_serializer.data,
            }, status=status.HTTP_200_OK
        )


class PlaceDetailAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="명소 상세 조회",
        operation_description="명소 ID로 상세 정보를 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'place_id',
                openapi.IN_PATH,
                description="명소 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'lang',
                openapi.IN_QUERY,
                description="언어 코드 (기본값: ko)",
                type=openapi.TYPE_STRING,
                default='ko',
                enum=['ko', 'en', 'jp', 'cn']
            ),
        ],
        responses={
            200: openapi.Response(
                description="명소 상세 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'place': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='명소 ID'),
                                'content_id': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='외부 컨텐츠 ID'),
                                'name': openapi.Schema(type=openapi.TYPE_STRING, description='명소명(요청 lang 기준)'),
                                'description': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='설명(요청 lang 기준)'),
                                'feature': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='특징(요청 lang 기준)'),
                                'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description='카테고리 ID'),
                                'sub_category_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description='서브 카테고리 ID'),
                                'region_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='지역 ID'),
                                'sub_region_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description='서브지역 ID'),
                                'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='위도'),
                                'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='경도'),
                                'favorite_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='즐겨찾기 수'),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='생성일'),
                                'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='수정일'),
                            }
                        )
                    }
                )
            ),
            404: openapi.Response(description="존재하지 않는 명소 ID"),
        },
        tags=['명소']
    )

    def get(self, request, place_id):
        language = request.query_params.get("lang", "ko")
        place = get_object_or_404(Place, id=place_id)

        serializer = PlaceSerializer(
            place,
            context={"language": language}
        )

        return Response({
            "place": serializer.data
        }, status=status.HTTP_200_OK)


class PlacesBySubRegionAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="서브지역별 명소 목록 조회",
        operation_description="특정 서브지역(시군구)의 명소 목록을 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'subregion_id',
                openapi.IN_PATH,
                description="서브지역(시군구) ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'lang',
                openapi.IN_QUERY,
                description="언어 코드 (기본값: ko)",
                type=openapi.TYPE_STRING,
                default='ko',
                enum=['ko', 'en', 'jp', 'cn']
            ),
            openapi.Parameter(
                'sort_type',
                openapi.IN_QUERY,
                description="정렬 타입 (favorite: 즐겨찾기/최신순, name: ID 오름차순)",
                type=openapi.TYPE_STRING,
                enum=['favorite', 'name'],
                default='favorite'
            ),
        ],
        responses={
            200: openapi.Response(
                description="서브지역별 명소 목록 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'places': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='명소 ID'),
                                    'content_id': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='외부 컨텐츠 ID'),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='명소명(요청 lang 기준)'),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='설명(요청 lang 기준)'),
                                    'feature': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='특징(요청 lang 기준)'),
                                    'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description='카테고리 ID'),
                                    'sub_category_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description='서브 카테고리 ID'),
                                    'region_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='지역 ID'),
                                    'sub_region_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description='서브지역 ID'),
                                    'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='위도'),
                                    'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='경도'),
                                    'favorite_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='즐겨찾기 수'),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='생성일'),
                                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='수정일'),
                                }
                            )
                        )
                    }
                )
            )
        },
        tags=['명소']
    )

    def get(self, request, subregion_id):
        language = request.query_params.get("lang", "ko")
        sort_type = request.query_params.get("sort_type", "favorite")
        queryset = Place.objects.filter(sub_region=subregion_id)
        if sort_type == "name":
            queryset = queryset.order_by("id")
        else:
            queryset = queryset.order_by("-favorite_count", "-created_at")

        serializer = PlaceSerializer(
            queryset,
            many=True,
            context={"language": language}
        )

        return Response({
            "places": serializer.data
        }, status=status.HTTP_200_OK)