from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models.functions import Lower
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from categories.models import Category
from regions.models import Region, SubRegion
from regions.serializers import RegionSerializer, SubRegionSerializer
from places.models import Place
from places.serializers import PlaceSerializer
from utils.pagination.custom_pagination import CustomPagination


class PlacesListAPIView(APIView):
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

class PlaceTourListAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="지역별 둘러보기 조회",
        operation_description=(
            "지역의 정보, 서브지역 정보, 인기 시·군·구(4)와 주요 명소(4)를 반환합니다. "
            "인증(Authorization: Bearer <JWT>) 상태라면 관심사 기반 추천 명소(3)도 포함됩니다."
        ),
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
                'region_id',
                openapi.IN_QUERY,
                description="지역 ID (기본값: 1)",
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                'subregion_id',
                openapi.IN_QUERY,
                description="특정 시·군·구 ID (미지정 시 인기 1위 시·군·구 기준으로 주요 명소 반환)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer <JWT> 형식으로 전달 시 user_recommended_places 포함",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: openapi.Response(
                description="관광지 홈 블록 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=['region', 'subregion', 'weather', 'popular_subregions', 'major_places'],
                    properties={
                        'region': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='지역 정보',
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='지역 ID'),
                                'name': openapi.Schema(type=openapi.TYPE_STRING, description='지역명(요청 lang 기준)'),
                                'description': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='설명(요청 lang 기준)'),
                                'feature': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='특징(요청 lang 기준)'),
                                'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='위도'),
                                'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='경도'),
                                'favorite_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='즐겨찾기 수'),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='생성일'),
                                'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='수정일'),
                            }
                        ),
                        'subregion': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='요청된 서브지역 정보 (subregion_id 지정 시 해당 서브지역, 미지정 시 인기 1위 서브지역)',
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='서브지역 ID'),
                                'name': openapi.Schema(type=openapi.TYPE_STRING, description='서브지역명(요청 lang 기준)'),
                                'description': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='설명(요청 lang 기준)'),
                                'feature': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='특징(요청 lang 기준)'),
                                'region_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='지역 ID'),
                                'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='위도'),
                                'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='경도'),
                                'favorite_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='즐겨찾기 수'),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='생성일'),
                                'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='수정일'),
                            }
                        ),
                        'popular_subregions': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='인기 서브지역 목록 (즐겨찾기 순으로 정렬된 상위 4개)',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='시·군·구 ID'),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='시·군·구명(요청 lang 기준)'),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='설명(요청 lang 기준)'),
                                    'feature': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='특징(요청 lang 기준)'),
                                    'region_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='지역 ID'),
                                    'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='위도'),
                                    'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, format='double', nullable=True, description='경도'),
                                    'favorite_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='즐겨찾기 수'),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='생성일'),
                                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='수정일'),
                                }
                            )
                        ),
                        'major_places': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='주요 명소 목록 (선택된 서브지역의 즐겨찾기 순으로 정렬된 상위 4개)',
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
                        ),
                        'user_recommended_places': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='사용자 관심사 기반 추천 명소 (인증된 사용자에게만 제공, 상위 3개)',
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
                        ),
                    }
                ),
                examples={
                    "application/json": {
                        "region": {
                            "id": 1,
                            "name": "서울특별시",
                            "description": "대한민국의 수도",
                            "feature": "한강이 도심을 가로지르며 흐르는 천만 인구의 메가시티로, 경복궁과 창덕궁 같은 조선왕조의 찬란한 궁궐 문화유산이 강남의 현대적 마천루와 어우러져 전통과 현대가 조화롭게 공존하는 글로벌 도시입니다. 명동, 홍대, 이태원 등 각기 다른 매력을 가진 지역들과 N서울타워, 한강공원, 동대문디자인플라자 등의 랜드마크가 있어 연간 수천만 명의 관광객이 찾는 아시아 최고의 관광 도시 중 하나입니다.",
                            "favorite_count": 1500
                        },
                        "subregion": {
                            "id": 1,
                            "name": "강남구",
                            "description": "서울의 대표적인 번화가",
                            "feature": "쇼핑과 엔터테인먼트의 중심지",
                            "region_id": 1,
                            "favorite_count": 120,
                            "latitude": 37.5172,
                            "longitude": 127.0473
                        },
                        "popular_subregions": [
                            {"id": 3, "name": "강북구", "region_id": 1, "favorite_count": 120},
                            {"id": 13, "name": "마포구", "region_id": 1, "favorite_count": 98},
                            {"id": 5, "name": "관악구", "region_id": 1, "favorite_count": 76},
                            {"id": 1, "name": "강남구", "region_id": 1, "favorite_count": 72}
                        ],
                        "major_places": [
                            {"id": 101, "name": "북한산 국립공원", "region_id": 1, "sub_region_id": 3, "favorite_count": 55},
                            {"id": 102, "name": "OO 박물관", "region_id": 1, "sub_region_id": 3, "favorite_count": 41},
                            {"id": 103, "name": "△△ 공원", "region_id": 1, "sub_region_id": 3, "favorite_count": 38},
                            {"id": 104, "name": "◇◇ 전시관", "region_id": 1, "sub_region_id": 3, "favorite_count": 32}
                        ],
                        "user_recommended_places": [
                            {"id": 202, "name": "추천 명소 A", "region_id": 1, "sub_region_id": 5, "favorite_count": 20},
                            {"id": 203, "name": "추천 명소 B", "region_id": 1, "sub_region_id": 8, "favorite_count": 18},
                            {"id": 204, "name": "추천 명소 C", "region_id": 1, "sub_region_id": 12, "favorite_count": 16}
                        ]
                    }
                }
            )
        },
        tags=['명소']
    )

    def get(self, request):
        language = request.query_params.get("lang", "ko")
        region_id = request.query_params.get("region_id", "1")
        region = Region.objects.filter(id=region_id).first()

        region_serializer = RegionSerializer(region, context={"language": language})

        most_favoriate_subregion_ids = list(SubRegion.objects.filter(region=region).order_by('-favorite_count', 'id')[:4])

        subregion_serializer = SubRegionSerializer(
            most_favoriate_subregion_ids,
            many=True,
            context={"language": language}
        )

        request_subregion_id = request.query_params.get("subregion_id", "")
        
        if request_subregion_id == "":
            first_subregion = most_favoriate_subregion_ids[0] if most_favoriate_subregion_ids else None
            request_subregion = first_subregion
            major_places = Place.objects.filter(sub_region=first_subregion).order_by('-favorite_count', 'id').prefetch_related('translations')[:4]
        else:
            major_places = Place.objects.filter(sub_region=int(request_subregion_id)).order_by('-favorite_count', 'id').prefetch_related('translations')[:4]            
            request_subregion = SubRegion.objects.filter(id=request_subregion_id).filter().first()

        request_subregion_serializer = SubRegionSerializer(request_subregion, context={"language": language})

        place_serializer = PlaceSerializer(
            major_places,
            many=True,
            context={"language": language}
        )

        if request.user.is_authenticated:
            pref_ids = list(
                request.user.preferences.values_list('subcategory_id', flat=True)
            )
            user_recommended_places = Place.objects.filter(
                sub_category_id__in=pref_ids,region_id=region_id
                ).order_by('-favorite_count', 'id')[:3]
            
            user_recommended_serializer = PlaceSerializer(
                user_recommended_places,
                many=True,
                context={"language": language}
            )

            return Response(
                {
                    "region": region_serializer.data,
                    "subregion": request_subregion_serializer.data,
                    "popular_subregions": subregion_serializer.data,
                    "major_places": place_serializer.data,
                    "user_recommended_places": user_recommended_serializer.data
                }, status=status.HTTP_200_OK
            )

        return Response(
            {
                "region": region_serializer.data,
                "subregion": request_subregion_serializer.data,
                "popular_subregions": subregion_serializer.data,
                "major_places": place_serializer.data,
            }, status=status.HTTP_200_OK
        )


class PlaceDetailAPIView(APIView):
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
    

class PlacesBySubRegionAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

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
                'category_id',
                openapi.IN_QUERY,
                description="카테고리 ID (선택사항)",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="페이지 번호 (기본값: 1)",
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="페이지당 항목 수",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={
            200: openapi.Response(
                description="서브지역별 명소 목록 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='총 명소 수'),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='다음 페이지 URL'),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='이전 페이지 URL'),
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
            ),
            404: openapi.Response(
                description="서브지역을 찾을 수 없음",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='오류 메시지')
                    }
                )
            )
        },
        tags=['명소']
    )

    def get(self, request, subregion_id):
        category_id = request.query_params.get("category_id", "")
        language = request.query_params.get("lang", "ko")
        
        queryset = Place.objects.filter(
            sub_region_id=subregion_id
        ).order_by('-favorite_count', 'id').prefetch_related('translations')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = PlaceSerializer(
                page,
                many=True,
                context={"language": language}
            )
            # 페이지네이션 응답에서 results를 places로 변경
            paginated_response = paginator.get_paginated_response(serializer.data)
            if 'results' in paginated_response.data:
                paginated_response.data['places'] = paginated_response.data.pop('results')
            return paginated_response

        serializer = PlaceSerializer(
            queryset,
            many=True,
            context={"language": language}
        )

        return Response({
            "places": serializer.data
        }, status=status.HTTP_200_OK)


class PlacesByCategoryIdAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_summary="카테고리별 명소 목록 조회",
        operation_description="특정 카테고리의 명소 목록을 즐겨찾기 높은 순으로 조회합니다.",
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
                description="언어 코드 (기본값: ko)",
                type=openapi.TYPE_STRING,
                default='ko',
                enum=['ko', 'en', 'jp', 'cn']
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="페이지 번호 (기본값: 1)",
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="페이지당 항목 수",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={
            200: openapi.Response(
                description="카테고리별 명소 목록 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='총 명소 수'),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='다음 페이지 URL'),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='이전 페이지 URL'),
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
            ),
            404: openapi.Response(
                description="카테고리를 찾을 수 없음",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='오류 메시지')
                    }
                )
            )
        },
        tags=['명소']
    )

    def get(self, request, category_id):
        language = request.query_params.get("lang", "ko")
        
        # 카테고리 존재 여부 확인 (선택사항 - 필요에 따라 추가)
        get_object_or_404(Category, id=category_id)
        
        queryset = Place.objects.filter(category_id=category_id).order_by('-favorite_count', 'id').prefetch_related('translations')
        
        # 빈 결과에 대한 처리
        if not queryset.exists():
            return Response({
                'count': 0,
                'next': None,
                'previous': None,
                'places': []
            }, status=status.HTTP_200_OK)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = PlaceSerializer(
                page,
                many=True,
                context={"language": language}
            )

            paginated_response = paginator.get_paginated_response(serializer.data)
            if 'results' in paginated_response.data:
                paginated_response.data['places'] = paginated_response.data.pop('results')
            return paginated_response
        
        serializer = PlaceSerializer(   
            queryset,
            many=True,
            context={"language": language}
        )

        return Response({
            "places": serializer.data
        }, status=status.HTTP_200_OK)


class PlacesBySubCategoryIdAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_summary="서브 카테고리별 명소 목록 조회",
        operation_description="특정 서브 카테고리의 명소 목록을 즐겨찾기 높은 순으로 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                "subcategory_id",
                openapi.IN_PATH,
                description="서브 카테고리 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
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
                description="페이지 번호 (기본값: 1)",
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="페이지당 항목 수",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={
            200: openapi.Response(
                description="서브 카테고리별 명소 목록 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="총 명소 수"),
                        "next": openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description="다음 페이지 URL"),
                        "previous": openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description="이전 페이지 URL"),
                        "places": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="명소 ID"),
                                    "content_id": openapi.Schema(type=openapi.TYPE_STRING, nullable=True,
                                                                 description="외부 컨텐츠 ID"),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING, description="명소명(요청 lang 기준)"),
                                    "description": openapi.Schema(type=openapi.TYPE_STRING, nullable=True,
                                                                  description="설명(요청 lang 기준)"),
                                    "feature": openapi.Schema(type=openapi.TYPE_STRING, nullable=True,
                                                              description="특징(요청 lang 기준)"),
                                    "category_id": openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True,
                                                                  description="카테고리 ID"),
                                    "sub_category_id": openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True,
                                                                      description="서브 카테고리 ID"),
                                    "region_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID"),
                                    "sub_region_id": openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True,
                                                                    description="서브지역 ID"),
                                    "latitude": openapi.Schema(type=openapi.TYPE_NUMBER, format="double", nullable=True,
                                                               description="위도"),
                                    "longitude": openapi.Schema(type=openapi.TYPE_NUMBER, format="double",
                                                                nullable=True, description="경도"),
                                    "favorite_count": openapi.Schema(type=openapi.TYPE_INTEGER, description="즐겨찾기 수"),
                                    "created_at": openapi.Schema(type=openapi.TYPE_STRING,
                                                                 format=openapi.FORMAT_DATETIME, description="생성일"),
                                    "updated_at": openapi.Schema(type=openapi.TYPE_STRING,
                                                                 format=openapi.FORMAT_DATETIME, description="수정일"),
                                }
                            )
                        )
                    }
                )
            ),
            404: openapi.Response(
                description="서브 카테고리를 찾을 수 없음",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING, description="오류 메시지")
                    }
                )
            )
        },
        tags=["명소"]
    )
    def get(self, request, subcategory_id):
        language = request.query_params.get("lang", "ko")

        from categories.models import SubCategory
        get_object_or_404(SubCategory, id=subcategory_id)

        queryset = Place.objects.filter(
            sub_category_id=subcategory_id
        ).order_by("-favorite_count", "id").prefetch_related("translations")

        # 빈 결과에 대한 처리
        if not queryset.exists():
            return Response({
                "count": 0,
                "next": None,
                "previous": None,
                "places": []
            }, status=status.HTTP_200_OK)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = PlaceSerializer(
                page,
                many=True,
                context={"language": language}
            )

            paginated_response = paginator.get_paginated_response(serializer.data)
            if "results" in paginated_response.data:
                paginated_response.data["places"] = paginated_response.data.pop("results")
            return paginated_response

        serializer = PlaceSerializer(
            queryset,
            many=True,
            context={"language": language}
        )

        return Response({
            "places": serializer.data
        }, status=status.HTTP_200_OK)