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
                                "region_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID", example=1, x_nullable=True),
                                "title": openapi.Schema(type=openapi.TYPE_STRING, description="여행 계획 제목", example="성심당 뿌시기 여행"),
                                "start_date": openapi.Schema(type=openapi.TYPE_STRING, description="시작일", example="2025-07-05T10:00:00"),
                                "end_date": openapi.Schema(type=openapi.TYPE_STRING, description="종료일", example="2025-07-07T10:00:00"),
                                "created_at": openapi.Schema(type=openapi.TYPE_STRING, description="생성일", example="2025-07-05T10:00:00"),
                                "updated_at": openapi.Schema(type=openapi.TYPE_STRING, description="수정일", example="2025-07-05T10:00:00"),
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
            "name": openapi.Schema(type=openapi.TYPE_STRING, description="여행 계획 이름", example="여행이름"),
            "subregion_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브지역 ID", example=1),
            "start_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description="시작일", example="2025-07-05"),
            "end_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description="종료일", example="2025-07-07"),
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
        return Response({
            "plans": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = TravelPlanCreateSerializer(data=request.data)
        if serializer.is_valid():
            travel_plan = TravelPlan.objects.create(
                user_id=request.user.id,
                start_date=serializer.validated_data["start_date"],
                end_date=serializer.validated_data["end_date"]
            )

            TravelPlanTranslation.objects.create(
                travel_plan=travel_plan,
                lang="ko",
                title=serializer.validated_data["name"]
            )

            return Response(status=status.HTTP_201_CREATED)

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
                    "region_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID", example=1, x_nullable=True),
                    "plan_places": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="계획 관광지 ID", example=1),
                                "place": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="관광지 ID", example=1),
                                        "category_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="카테고리 ID", example=1),
                                        "subcategory_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브카테고리 ID", example=1),
                                        "region_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID", example=1),
                                        "subregion_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브지역 ID", example=1),
                                        "latitude": openapi.Schema(type=openapi.TYPE_NUMBER, format="double", description="위도", example=37.123456),
                                        "longitude": openapi.Schema(type=openapi.TYPE_NUMBER, format="double", description="경도", example=127.123456),
                                        "phone_number": openapi.Schema(type=openapi.TYPE_STRING, description="전화번호", example="021234567"),
                                        "use_time": openapi.Schema(type=openapi.TYPE_STRING, description="운영시간", example="09:00~18:00"),
                                        "image_url": openapi.Schema(type=openapi.TYPE_STRING, description="이미지 URL", example="https://asdw.ssdwasdasd"),
                                        "address": openapi.Schema(type=openapi.TYPE_STRING, description="주소", example="서울시 강남구 강남동"),
                                        "description": openapi.Schema(type=openapi.TYPE_STRING, description="설명", example="강남 카페 맛집"),
                                        "favorite_count": openapi.Schema(type=openapi.TYPE_INTEGER, description="즐겨찾기 수", example=3),
                                        "created_at": openapi.Schema(type=openapi.TYPE_STRING, description="생성일", example="2025-07-05T10:00:00"),
                                        "updated_at": openapi.Schema(type=openapi.TYPE_STRING, description="수정일", example="2025-07-05T10:00:00"),
                                    }
                                ),
                                "visit_date": openapi.Schema(type=openapi.TYPE_STRING, description="방문일", example="2025-07-05"),
                                "visit_time": openapi.Schema(type=openapi.TYPE_STRING, description="방문시간", example="09:00:00"),
                                "created_at": openapi.Schema(type=openapi.TYPE_STRING, description="생성일", example="2025-07-05T10:00:00"),
                                "updated_at": openapi.Schema(type=openapi.TYPE_STRING, description="수정일", example="2025-07-05T10:00:00"),
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
        return Response(serializer.data, status=status.HTTP_200_OK)

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
