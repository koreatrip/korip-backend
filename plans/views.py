# plans/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from plans.models import TravelPlan, TravelPlanTranslation, PlanPlace
from plans.serializers import (
    TravelPlanListSerializer,
    TravelPlanDetailSerializer,
    TravelPlanCreateSerializer,
    PlanPlaceListCreateSerializer
)


def get_user_favorite_places(user_id, lang="ko"):
    """사용자의 즐겨찾기 관광지 목록 가져오기"""
    from favorites.models import FavoritePlace
    from places.models import Place, PlaceTranslation

    favorite_places = []
    favorite_relations = FavoritePlace.objects.filter(user_id=user_id).select_related('place')

    for favorite in favorite_relations:
        place = favorite.place

        try:
            translation = PlaceTranslation.objects.get(place=place, lang=lang)
            place_name = translation.name
            place_address = translation.address
            place_description = translation.description
        except PlaceTranslation.DoesNotExist:
            place_name = ""
            place_address = ""
            place_description = ""

        favorite_places.append({
            "place_id": place.id,
            "content_id": place.content_id,
            "name": place_name,
            "address": place_address,
            "description": place_description,
            "latitude": float(place.latitude) if place.latitude else None,
            "longitude": float(place.longitude) if place.longitude else None,
            "phone_number": place.phone_number,
            "use_time": place.use_time,
            "link_url": place.link_url,
            "favorite_count": place.favorite_count,
            "favorited_at": favorite.created_at
        })

    favorite_places.sort(key=lambda x: x["favorited_at"], reverse=True)
    return favorite_places


def get_user_favorite_regions(user_id, lang="ko"):
    """사용자의 즐겨찾기 지역 목록 가져오기"""
    from favorites.models import FavoritePlace, FavoriteSubRegion
    from regions.models import SubRegion, SubRegionTranslation
    from collections import defaultdict

    # 방법 1: 즐겨찾기한 관광지를 기반으로 지역 그룹화
    favorite_places = FavoritePlace.objects.filter(user_id=user_id).select_related('place')
    region_counts = defaultdict(int)
    region_info = {}

    for favorite in favorite_places:
        place = favorite.place

        if hasattr(place, 'region') and place.region:
            region_id = place.region.id
        elif hasattr(place, 'region_id') and place.region_id:
            region_id = place.region_id
        else:
            continue

        if hasattr(place, 'sub_region') and place.sub_region:
            subregion_id = place.sub_region.id
        elif hasattr(place, 'sub_region_id') and place.sub_region_id:
            subregion_id = place.sub_region_id
        else:
            continue

        region_counts[subregion_id] += 1

        if subregion_id not in region_info:
            try:
                subregion = SubRegion.objects.get(id=subregion_id)

                try:
                    translation = SubRegionTranslation.objects.get(
                        sub_region=subregion, lang=lang
                    )
                    region_name = translation.name
                    region_description = translation.description
                except SubRegionTranslation.DoesNotExist:
                    region_name = ""
                    region_description = ""

                region_info[subregion_id] = {
                    "subregion_id": subregion_id,
                    "region_id": region_id,
                    "name": region_name,
                    "description": region_description,
                    "favorite_places_count": 0
                }
            except SubRegion.DoesNotExist:
                continue

    for subregion_id, count in region_counts.items():
        if subregion_id in region_info:
            region_info[subregion_id]["favorite_places_count"] = count

    # 방법 2: 직접 즐겨찾기한 지역구들 추가 (FavoriteSubRegion 사용)
    favorite_subregions = FavoriteSubRegion.objects.filter(user_id=user_id).select_related('sub_region')

    for favorite in favorite_subregions:
        subregion = favorite.sub_region
        subregion_id = subregion.id

        try:
            translation = SubRegionTranslation.objects.get(
                sub_region=subregion, lang=lang
            )
            region_name = translation.name
            region_description = translation.description
        except SubRegionTranslation.DoesNotExist:
            region_name = ""
            region_description = ""

        # 기존에 관광지 기반으로 추가된 지역이 아니면 새로 추가
        if subregion_id not in region_info:
            region_info[subregion_id] = {
                "subregion_id": subregion_id,
                "region_id": subregion.region.id,
                "name": region_name,
                "description": region_description,
                "favorite_places_count": 0  # 직접 즐겨찾기한 지역구는 0
            }

    favorite_regions = list(region_info.values())
    favorite_regions.sort(key=lambda x: x["favorite_places_count"], reverse=True)

    return favorite_regions


@swagger_auto_schema(
    method="get",
    operation_summary="내 여행 일정 목록 조회",
    operation_description="로그인한 사용자의 여행 계획 목록을 조회합니다.",
    manual_parameters=[
        openapi.Parameter(
            "lang",
            openapi.IN_QUERY,
            description="언어 코드 (기본값: ko)",
            type=openapi.TYPE_STRING,
            default="ko",
            enum=["ko", "en", "jp", "cn"]
        )
    ],
    responses={
        200: openapi.Response(
            description="여행 계획 목록 조회 성공",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "plans": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="계획 ID", example=1),
                                "region_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID", example=1,
                                                            x_nullable=True),
                                "title": openapi.Schema(type=openapi.TYPE_STRING, description="여행 계획 제목",
                                                        example="성심당 뿌시기 여행"),
                                "description": openapi.Schema(type=openapi.TYPE_STRING, description="여행 설명",
                                                              example="대전 맛집 탐방"),
                                "destination": openapi.Schema(type=openapi.TYPE_STRING, description="선택한 여행지명",
                                                              example="대전"),
                                "subregion_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브지역 ID",
                                                               example=1),
                                "start_date": openapi.Schema(type=openapi.TYPE_STRING, description="시작일",
                                                             example="2025-07-05T10:00:00"),
                                "end_date": openapi.Schema(type=openapi.TYPE_STRING, description="종료일",
                                                           example="2025-07-07T10:00:00"),
                                "created_at": openapi.Schema(type=openapi.TYPE_STRING, description="생성일",
                                                             example="2025-07-05T10:00:00"),
                                "updated_at": openapi.Schema(type=openapi.TYPE_STRING, description="수정일",
                                                             example="2025-07-05T10:00:00"),
                            }
                        )
                    )
                }
            )
        )
    },
    tags=["여행계획"]
)
@swagger_auto_schema(
    method="post",
    operation_summary="여행 계획 생성",
    operation_description="새로운 여행 계획을 생성합니다.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["name", "subregion_id", "start_date", "end_date"],
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING, description="여행 계획 이름", example="하이라이스의 여행일기"),
            "description": openapi.Schema(type=openapi.TYPE_STRING, description="여행 설명", example="성심당 뿌시러 감"),
            "destination": openapi.Schema(type=openapi.TYPE_STRING, description="선택한 여행지명",
                                          example="지역명을 검색해보세요 (예: 서울)"),
            "subregion_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브지역 ID", example=1),
            "start_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description="시작일",
                                         example="2025-07-05"),
            "end_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description="종료일",
                                       example="2025-07-07"),
        }
    ),
    responses={
        201: openapi.Response(description="여행 계획 생성 성공"),
        400: openapi.Response(description="잘못된 요청")
    },
    tags=["여행계획"]
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def plan_list_create(request):
    """여행 계획 목록 조회 및 생성"""
    if request.method == "GET":
        lang = request.GET.get("lang", "ko")
        travel_plans = TravelPlan.objects.filter(user_id=request.user.id)
        serializer = TravelPlanListSerializer(
            travel_plans,
            many=True,
            context={"lang": lang}
        )

        favorite_places = get_user_favorite_places(request.user.id, lang)
        favorite_regions = get_user_favorite_regions(request.user.id, lang)

        return Response({
            "plans": serializer.data,
            "favorite_places": favorite_places,
            "favorite_regions": favorite_regions
        }, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = TravelPlanCreateSerializer(data=request.data)
        if serializer.is_valid():
            travel_plan = serializer.save(user_id=request.user.id)
            return Response({"id": travel_plan.id}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="내 여행 일정 상세 조회",
    operation_description="여행 계획의 상세 정보를 조회합니다.",
    manual_parameters=[
        openapi.Parameter(
            "lang",
            openapi.IN_QUERY,
            description="언어 코드 (기본값: ko)",
            type=openapi.TYPE_STRING,
            default="ko",
            enum=["ko", "en", "jp", "cn"]
        )
    ],
    responses={
        200: openapi.Response(
            description="여행 계획 상세 조회 성공",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="계획 ID", example=1),
                    "title": openapi.Schema(type=openapi.TYPE_STRING, description="여행 계획 제목", example="하이라이스의 여행일기"),
                    "description": openapi.Schema(type=openapi.TYPE_STRING, description="여행 설명", example="대전 맛집 탐방"),
                    "destination": openapi.Schema(type=openapi.TYPE_STRING, description="선택한 여행지명", example="대전"),
                    "region_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID", example=1,
                                                x_nullable=True),
                    "subregion_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브지역 ID", example=1),
                    "start_date": openapi.Schema(type=openapi.TYPE_STRING, description="시작일", example="2025-07-05"),
                    "end_date": openapi.Schema(type=openapi.TYPE_STRING, description="종료일", example="2025-07-07"),
                    "plan_places": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="계획 관광지 ID", example=1),
                                "place": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="관광지 ID",
                                                             example=1),
                                        "category_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="카테고리 ID",
                                                                      example=1),
                                        "subcategory_id": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                         description="서브카테고리 ID", example=1),
                                        "region_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID",
                                                                    example=1),
                                        "subregion_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브지역 ID",
                                                                       example=1),
                                        "latitude": openapi.Schema(type=openapi.TYPE_NUMBER, format="double",
                                                                   description="위도", example=37.123456),
                                        "longitude": openapi.Schema(type=openapi.TYPE_NUMBER, format="double",
                                                                    description="경도", example=127.123456),
                                        "phone_number": openapi.Schema(type=openapi.TYPE_STRING, description="전화번호",
                                                                       example="021234567"),
                                        "use_time": openapi.Schema(type=openapi.TYPE_STRING, description="운영시간",
                                                                   example="09:00~18:00"),
                                        "image_url": openapi.Schema(type=openapi.TYPE_STRING, description="이미지 URL",
                                                                    example="https://asdw.ssdwasdasd"),
                                        "address": openapi.Schema(type=openapi.TYPE_STRING, description="주소",
                                                                  example="서울시 강남구 강남동"),
                                        "description": openapi.Schema(type=openapi.TYPE_STRING, description="설명",
                                                                      example="강남 카페 맛집"),
                                        "favorite_count": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                         description="즐겨찾기 수", example=3),
                                        "created_at": openapi.Schema(type=openapi.TYPE_STRING, description="생성일",
                                                                     example="2025-07-05T10:00:00"),
                                        "updated_at": openapi.Schema(type=openapi.TYPE_STRING, description="수정일",
                                                                     example="2025-07-05T10:00:00"),
                                    }
                                ),
                                "visit_date": openapi.Schema(type=openapi.TYPE_STRING, description="방문일",
                                                             example="2025-07-05"),
                                "visit_time": openapi.Schema(type=openapi.TYPE_STRING, description="방문시간",
                                                             example="09:00:00"),
                                "created_at": openapi.Schema(type=openapi.TYPE_STRING, description="생성일",
                                                             example="2025-07-05T10:00:00"),
                                "updated_at": openapi.Schema(type=openapi.TYPE_STRING, description="수정일",
                                                             example="2025-07-05T10:00:00"),
                            }
                        )
                    ),
                    "created_at": openapi.Schema(type=openapi.TYPE_STRING, description="생성일",
                                                 example="2025-07-05T10:00:00"),
                    "updated_at": openapi.Schema(type=openapi.TYPE_STRING, description="수정일",
                                                 example="2025-07-05T10:00:00"),
                }
            )
        )
    },
    tags=["여행계획"]
)
@swagger_auto_schema(
    methods=["post", "put"],
    operation_summary="여행 일정 관광지 추가/수정",
    operation_description="여행 계획에 관광지들을 추가하거나 수정합니다.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["places"],
        properties={
            "places": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=["place_id", "visit_date", "visit_time"],
                    properties={
                        "place_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="관광지 ID", example=1),
                        "visit_date": openapi.Schema(type=openapi.TYPE_STRING, description="방문일", example="2025-07-05"),
                        "visit_time": openapi.Schema(type=openapi.TYPE_STRING, description="방문시간", example="09:00"),
                    }
                )
            )
        }
    ),
    responses={
        200: openapi.Response(description="수정 성공"),
        201: openapi.Response(description="추가 성공"),
        400: openapi.Response(description="잘못된 요청")
    },
    tags=["여행계획"]
)
@api_view(["GET", "POST", "PUT"])
@permission_classes([IsAuthenticated])
def plan_detail(request, plan_id):
    """여행 계획 상세 조회, 관광지 추가 및 수정"""
    travel_plan = get_object_or_404(TravelPlan, id=plan_id, user_id=request.user.id)

    if request.method == "GET":
        lang = request.GET.get("lang", "ko")
        serializer = TravelPlanDetailSerializer(
            travel_plan,
            context={"lang": lang}
        )

        favorite_places = get_user_favorite_places(request.user.id, lang)
        favorite_regions = get_user_favorite_regions(request.user.id, lang)

        response_data = serializer.data.copy()
        response_data.update({
            "favorite_places": favorite_places,
            "favorite_regions": favorite_regions
        })

        return Response(response_data, status=status.HTTP_200_OK)

    elif request.method in ["POST", "PUT"]:
        serializer = PlanPlaceListCreateSerializer(data=request.data)
        if serializer.is_valid():
            PlanPlace.objects.filter(travel_plan=travel_plan).delete()

            for place_data in serializer.validated_data["places"]:
                PlanPlace.objects.create(
                    travel_plan=travel_plan,
                    place_id=place_data["place_id"],
                    visit_date=place_data["visit_date"],
                    visit_time=place_data["visit_time"]
                )

            status_code = status.HTTP_201_CREATED if request.method == "POST" else status.HTTP_200_OK
            return Response(status=status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
