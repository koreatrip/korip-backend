from rest_framework import status
from rest_framework.views import APIView
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
    PlanPlaceListCreateSerializer,
    TravelPlanUpdateSerializer,
    SinglePlaceAddSerializer
)


class PlanListCreateAPIView(APIView):
    """여행 계획 목록 조회 및 생성 API"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
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
                                    "region_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID",
                                                                example=1,
                                                                x_nullable=True),
                                    "title": openapi.Schema(type=openapi.TYPE_STRING, description="여행 계획 제목",
                                                            example="성심당 뿌시기 여행"),
                                    "description": openapi.Schema(type=openapi.TYPE_STRING, description="여행 설명",
                                                                  example="대전 맛집 탐방"),
                                    "subregion_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브지역 ID",
                                                                   example=1),
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
    def get(self, request):
        """여행 계획 목록 조회"""
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

    @swagger_auto_schema(
        operation_summary="여행 계획 생성",
        operation_description="새로운 여행 계획을 생성합니다. lang 파라미터로 언어를 지정할 수 있습니다.",
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
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "subregion_id"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="여행 계획 이름", example="하이라이스의 여행일기"),
                "subregion_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브지역 ID", example=1),
            }
        ),
        responses={
            201: openapi.Response(description="여행 계획 생성 성공"),
            400: openapi.Response(description="잘못된 요청")
        },
        tags=["여행계획"]
    )
    def post(self, request):
        """여행 계획 생성"""
        lang = request.GET.get("lang", "ko")

        serializer = TravelPlanCreateSerializer(data=request.data)
        if serializer.is_valid():
            travel_plan = serializer.save(user_id=request.user.id, lang=lang)
            return Response({"id": travel_plan.id}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlanDetailAPIView(APIView):
    """여행 계획 상세 조회, 관광지 추가, 수정 및 삭제 API"""
    permission_classes = [IsAuthenticated]

    def get_object(self, plan_id, user_id):
        """여행 계획 객체 가져오기"""
        return get_object_or_404(TravelPlan, id=plan_id, user_id=user_id)

    @swagger_auto_schema(
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
                        "title": openapi.Schema(type=openapi.TYPE_STRING, description="여행 계획 제목",
                                                example="하이라이스의 여행일기"),
                        "description": openapi.Schema(type=openapi.TYPE_STRING, description="여행 설명",
                                                      example="대전 맛집 탐방"),
                        "region_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID", example=1,
                                                    x_nullable=True),
                        "subregion_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브지역 ID", example=1),
                        "start_date": openapi.Schema(type=openapi.TYPE_STRING, description="시작일 (어드민 전용)",
                                                     example="2025-07-05", x_nullable=True),
                        "end_date": openapi.Schema(type=openapi.TYPE_STRING, description="종료일 (어드민 전용)",
                                                   example="2025-07-07", x_nullable=True),
                        "created_at": openapi.Schema(type=openapi.TYPE_STRING, description="생성일",
                                                     example="2025-07-05T10:00:00"),
                        "updated_at": openapi.Schema(type=openapi.TYPE_STRING, description="수정일",
                                                     example="2025-07-05T10:00:00"),
                    }
                )
            )
        },
        tags=["여행일정"]
    )
    def get(self, request, plan_id):
        """여행 계획 상세 조회"""
        travel_plan = self.get_object(plan_id, request.user.id)
        lang = request.GET.get("lang", "ko")

        serializer = TravelPlanDetailSerializer(
            travel_plan,
            context={"lang": lang}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="여행 계획에 관광지 추가",
        operation_description="여행 계획에 관광지 하나를 추가합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["place_id"],
            properties={
                "place_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="추가할 관광지 ID",
                    example=1234
                )
            }
        ),
        responses={
            201: openapi.Response(description="관광지 추가 성공"),
            400: openapi.Response(description="잘못된 요청")
        },
        tags=["여행일정"]
    )
    def post(self, request, plan_id):
        """여행 계획에 관광지 추가"""
        travel_plan = self.get_object(plan_id, request.user.id)

        serializer = SinglePlaceAddSerializer(data=request.data)

        if serializer.is_valid():
            place_id = serializer.validated_data["place_id"]

            if PlanPlace.objects.filter(travel_plan=travel_plan, place_id=place_id).exists():
                return Response(
                    {"error": "이미 일정에 추가된 관광지입니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            PlanPlace.objects.create(
                travel_plan=travel_plan,
                place_id=place_id,
                visit_date=None,
                visit_time=None
            )

            lang = request.GET.get("lang", "ko")
            detail_serializer = TravelPlanDetailSerializer(travel_plan, context={"lang": lang})

            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="여행 계획 전체 수정",
        operation_description="여행 계획의 제목, 설명, 날짜, 관광지 일정을 수정합니다. 모든 필드는 선택사항입니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="여행 계획 제목", example="새로운 여행 제목"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, description="여행 설명", example="수정된 여행 설명"),
                "start_date": openapi.Schema(type=openapi.TYPE_STRING, description="시작일", example="2025-09-07"),
                "end_date": openapi.Schema(type=openapi.TYPE_STRING, description="종료일", example="2025-09-09"),
                "places": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="관광지 일정 (선택사항)",
                    example=[
                        # 9월 7일
                        {"place_id": None, "visit_date": "2025-09-07", "visit_time": "09:00"},
                        {"place_id": 5690, "visit_date": "2025-09-07", "visit_time": "11:00"},
                        {"place_id": None, "visit_date": "2025-09-07", "visit_time": "13:00"},
                        {"place_id": None, "visit_date": "2025-09-07", "visit_time": "15:00"},
                        {"place_id": None, "visit_date": "2025-09-07", "visit_time": "17:00"},
                        {"place_id": None, "visit_date": "2025-09-07", "visit_time": "19:00"},
                        {"place_id": None, "visit_date": "2025-09-07", "visit_time": "21:00"},
                        {"place_id": None, "visit_date": "2025-09-07", "visit_time": "23:00"},
                        # 9월 8일
                        {"place_id": None, "visit_date": "2025-09-08", "visit_time": "09:00"},
                        {"place_id": None, "visit_date": "2025-09-08", "visit_time": "11:00"},
                        {"place_id": None, "visit_date": "2025-09-08", "visit_time": "13:00"},
                        {"place_id": None, "visit_date": "2025-09-08", "visit_time": "15:00"},
                        {"place_id": None, "visit_date": "2025-09-08", "visit_time": "17:00"},
                        {"place_id": None, "visit_date": "2025-09-08", "visit_time": "19:00"},
                        {"place_id": None, "visit_date": "2025-09-08", "visit_time": "21:00"},
                        {"place_id": None, "visit_date": "2025-09-08", "visit_time": "23:00"},
                        # 9월 9일
                        {"place_id": None, "visit_date": "2025-09-09", "visit_time": "09:00"},
                        {"place_id": None, "visit_date": "2025-09-09", "visit_time": "11:00"},
                        {"place_id": None, "visit_date": "2025-09-09", "visit_time": "13:00"},
                        {"place_id": None, "visit_date": "2025-09-09", "visit_time": "15:00"},
                        {"place_id": None, "visit_date": "2025-09-09", "visit_time": "17:00"},
                        {"place_id": None, "visit_date": "2025-09-09", "visit_time": "19:00"},
                        {"place_id": None, "visit_date": "2025-09-09", "visit_time": "21:00"},
                        {"place_id": None, "visit_date": "2025-09-09", "visit_time": "23:00"}
                    ],
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        required=["place_id", "visit_date", "visit_time"],
                        properties={
                            "place_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="관광지 ID", example=5690,
                                                       x_nullable=True),
                            "visit_date": openapi.Schema(type=openapi.TYPE_STRING, description="방문일",
                                                         example="2025-09-07"),
                            "visit_time": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="방문시간",
                                example="11:00",
                                enum=["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00", "23:00"]
                            )
                        }
                    )
                )
            }
        ),
        responses={
            200: openapi.Response(description="수정 성공"),
            400: openapi.Response(description="잘못된 요청")
        },
        tags=["여행일정"]
    )

    def patch(self, request, plan_id):
        """여행 계획 전체 수정"""
        travel_plan = self.get_object(plan_id, request.user.id)

        serializer = PlanPlaceListCreateSerializer(data=request.data)

        if serializer.is_valid():
            PlanPlace.objects.filter(travel_plan=travel_plan).delete()

            visit_dates = []
            for place_data in serializer.validated_data["places"]:
                if place_data["place_id"]:
                    PlanPlace.objects.create(
                        travel_plan=travel_plan,
                        place_id=place_data["place_id"],
                        visit_date=place_data["visit_date"],
                        visit_time=place_data["visit_time"]
                    )
                    visit_dates.append(place_data["visit_date"])

            if visit_dates:
                travel_plan.start_date = min(visit_dates)
                travel_plan.end_date = max(visit_dates)
                travel_plan.save()

            lang = request.GET.get("lang", "ko")
            detail_serializer = TravelPlanDetailSerializer(travel_plan, context={"lang": lang})

            return Response(detail_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="여행 계획 삭제",
        operation_description="특정 여행 계획을 삭제합니다.",
        responses={
            204: "삭제 성공",
            404: "여행 계획을 찾을 수 없음"
        },
        tags=["여행계획"]
    )
    def delete(self, request, plan_id):
        """여행 계획 삭제"""
        travel_plan = self.get_object(plan_id, request.user.id)
        travel_plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RemovePlaceFromPlanAPIView(APIView):
    """여행 일정에서 관광지 제거 API"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="여행 일정에서 관광지 제거",
        operation_description="여행 일정에서 특정 관광지를 제거합니다.",
        responses={
            204: "삭제 성공",
            404: "관광지를 찾을 수 없음"
        },
        tags=["여행일정"]
    )
    def delete(self, request, plan_id, place_id):
        """여행 계획에서 특정 관광지 제거"""
        travel_plan = get_object_or_404(TravelPlan, id=plan_id, user_id=request.user.id)

        deleted_count = PlanPlace.objects.filter(
            travel_plan=travel_plan,
            place_id=place_id
        ).delete()

        if deleted_count[0] == 0:
            return Response(
                {"error": "해당 관광지가 일정에 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
