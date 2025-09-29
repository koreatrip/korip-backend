# exports/views.py - 여행 계획 내보내기 기능들

from django.shortcuts import get_object_or_404, redirect
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from collections import defaultdict
from django.http import JsonResponse
from exports.services.google_calendar import GoogleCalendarService
from users.models import CustomUser

# plans 앱에서 모델들 import
from plans.models import TravelPlan, PlanPlace


class PlanPdfDataView(APIView):
    """여행 계획 PDF 데이터 조회 - PDF 생성용"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="여행 계획 PDF 데이터 조회",
        operation_description="PDF 생성에 필요한 여행 계획 데이터를 JSON으로 반환합니다. PDF 생성 시 사용됩니다.",
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
                description="PDF 데이터 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "title": openapi.Schema(type=openapi.TYPE_STRING, description="여행 계획 제목",
                                                example="하이라이스의 여행일기"),
                        "description": openapi.Schema(type=openapi.TYPE_STRING, description="여행 설명",
                                                      example="성심당 뿌시러 감"),
                        "schedule": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description="일정 목록",
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "day": openapi.Schema(type=openapi.TYPE_INTEGER, description="일차", example=1),
                                    "date": openapi.Schema(type=openapi.TYPE_STRING, description="날짜",
                                                           example="2025-09-06"),
                                    "places": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        description="해당 날짜의 관광지 목록",
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                "time": openapi.Schema(type=openapi.TYPE_STRING, description="시간",
                                                                       example="09:00"),
                                                "place_name": openapi.Schema(type=openapi.TYPE_STRING, description="장소명",
                                                                             example="마라도(마라해양도립공원)"),
                                                "category": openapi.Schema(type=openapi.TYPE_STRING, description="카테고리",
                                                                           example="관광지"),
                                                "place_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="관광지 ID",
                                                                           example=6939)
                                            }
                                        )
                                    )
                                }
                            )
                        ),
                        "created_at": openapi.Schema(type=openapi.TYPE_STRING, description="생성일",
                                                     example="2025-09-05T20:13:00"),
                        "lang": openapi.Schema(type=openapi.TYPE_STRING, description="언어 코드", example="ko")
                    }
                )
            ),
            404: openapi.Response(description="여행 계획을 찾을 수 없음")
        },
        tags=["내보내기"]
    )
    def get(self, request, plan_id):
        travel_plan = get_object_or_404(TravelPlan, id=plan_id, user_id=request.user.id)
        lang = request.GET.get("lang", "ko")

        # 관광지 목록 가져오기
        plan_places = travel_plan.plan_places.all().order_by("visit_date", "visit_time")

        # 날짜별로 그룹화
        places_by_date = defaultdict(list)

        for plan_place in plan_places:
            try:
                # places 앱에서 Place 모델 import
                from places.models import Place, PlaceTranslation
                place = Place.objects.get(id=plan_place.place_id)

                # 다국어 지원 - fallback 로직 (ko → cn → en → jp 순서)
                place_name = "알 수 없는 장소"
                category_name = "기타"

                # Place Translation에서 이름 가져오기 (fallback 로직)
                translation = PlaceTranslation.objects.filter(place=place, lang=lang).first()
                if not translation:
                    # 없으면 중국어로 fallback
                    translation = PlaceTranslation.objects.filter(place=place, lang="cn").first()
                if not translation:
                    # 없으면 영어로 fallback
                    translation = PlaceTranslation.objects.filter(place=place, lang="en").first()
                if not translation:
                    # 없으면 일본어로 fallback
                    translation = PlaceTranslation.objects.filter(place=place, lang="jp").first()

                if translation:
                    place_name = translation.name

                # 카테고리 정보 가져오기
                if place.category_id:
                    try:
                        from categories.models import Category, CategoryTranslation
                        category = Category.objects.get(id=place.category_id)
                        category_translation = CategoryTranslation.objects.filter(
                            category=category, lang=lang
                        ).first()

                        # 카테고리도 fallback 로직 적용
                        if not category_translation:
                            category_translation = CategoryTranslation.objects.filter(
                                category=category, lang="cn"
                            ).first()
                        if not category_translation:
                            category_translation = CategoryTranslation.objects.filter(
                                category=category, lang="en"
                            ).first()
                        if not category_translation:
                            category_translation = CategoryTranslation.objects.filter(
                                category=category, lang="jp"
                            ).first()

                        if category_translation:
                            category_name = category_translation.name
                    except:
                        category_name = "기타"

                # 날짜별로 그룹화
                if plan_place.visit_date:
                    places_by_date[plan_place.visit_date].append({
                        "time": plan_place.visit_time.strftime("%H:%M") if plan_place.visit_time else "",
                        "place_name": place_name,
                        "category": category_name,
                        "place_id": place.id
                    })

            except Place.DoesNotExist:
                # 관광지가 삭제된 경우 빈 시간대로 표시
                if plan_place.visit_date:
                    places_by_date[plan_place.visit_date].append({
                        "time": plan_place.visit_time.strftime("%H:%M") if plan_place.visit_time else "",
                        "place_name": "",
                        "category": "",
                        "place_id": None
                    })

        # 날짜별 일정 정렬 및 구조화
        schedule = []
        sorted_dates = sorted(places_by_date.keys()) if places_by_date else []

        for index, date in enumerate(sorted_dates):
            # 해당 날짜의 관광지들을 시간순으로 정렬
            places = sorted(places_by_date[date], key=lambda x: x["time"] or "00:00")

            schedule.append({
                "day": index + 1,
                "date": date.strftime("%Y-%m-%d"),
                "places": places
            })

        # 여행 계획의 제목과 설명 가져오기 (다국어 지원)
        from plans.models import TravelPlanTranslation

        # 제목과 설명 fallback 로직
        title = "여행 계획"
        description = ""

        plan_translation = TravelPlanTranslation.objects.filter(
            travel_plan=travel_plan, lang=lang
        ).first()

        if not plan_translation:
            plan_translation = TravelPlanTranslation.objects.filter(
                travel_plan=travel_plan, lang="cn"
            ).first()
        if not plan_translation:
            plan_translation = TravelPlanTranslation.objects.filter(
                travel_plan=travel_plan, lang="en"
            ).first()
        if not plan_translation:
            plan_translation = TravelPlanTranslation.objects.filter(
                travel_plan=travel_plan, lang="jp"
            ).first()

        if plan_translation:
            title = plan_translation.title
            description = plan_translation.description

        response_data = {
            "title": title,
            "description": description,
            "schedule": schedule,
            "created_at": travel_plan.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "lang": lang
        }

        return Response(response_data, status=status.HTTP_200_OK)


class GoogleCalendarAuthView(APIView):
    """구글 캘린더 OAuth 인증 시작"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="구글 캘린더 OAuth 인증 시작",
        operation_description="구글 계정으로 로그인하여 캘린더 권한을 받습니다. 이 URL로 접속하면 구글 로그인 페이지로 리디렉션됩니다.",
        responses={
            302: openapi.Response(description="구글 OAuth 페이지로 리디렉션"),
            500: openapi.Response(description="인증 URL 생성 실패")
        },
        tags=["내보내기"]
    )
    def get(self, request):
        try:
            calendar_service = GoogleCalendarService()
            auth_url = calendar_service.get_authorization_url(request.user.id)

            # 구글 로그인 페이지로 리디렉션
            return redirect(auth_url)

        except Exception as e:
            return Response({
                "error": f"인증 URL 생성 실패: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleCalendarCallbackView(APIView):
    """구글 캘린더 OAuth 콜백 처리"""

    @swagger_auto_schema(
        operation_summary="구글 캘린더 OAuth 콜백 처리",
        operation_description="구글 로그인 완료 후 호출되는 콜백 엔드포인트입니다. 액세스 토큰을 받아 사용자 정보를 저장합니다.",
        manual_parameters=[
            openapi.Parameter(
                "code",
                openapi.IN_QUERY,
                description="구글에서 받은 인증 코드",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                "state",
                openapi.IN_QUERY,
                description="사용자 ID가 포함된 state 값",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="인증 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="구글 캘린더 연동 성공"),
                        "google_email": openapi.Schema(type=openapi.TYPE_STRING, example="user@gmail.com")
                    }
                )
            ),
            400: openapi.Response(description="인증 코드 누락 또는 잘못됨"),
            500: openapi.Response(description="인증 처리 실패")
        },
        tags=["내보내기"]
    )
    def get(self, request):
        authorization_code = request.GET.get("code")
        state = request.GET.get("state")

        if not authorization_code or not state:
            return Response({
                "error": "인증 코드 또는 state가 누락되었습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            calendar_service = GoogleCalendarService()
            auth_data = calendar_service.handle_callback(authorization_code, state)

            user_id = auth_data["user_id"]  # handle_callback에서 이미 반환함
            user = CustomUser.objects.get(id=user_id)
            user.google_calendar_token = auth_data["access_token"]
            user.google_calendar_refresh_token = auth_data["refresh_token"]
            user.google_calendar_email = auth_data["google_email"]
            user.save()

            return JsonResponse({
                "message": "구글 캘린더 연동 성공!",
                "google_email": auth_data["google_email"]
            })

        except Exception as e:
            return Response({
                "error": f"인증 처리 실패: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleCalendarSyncView(APIView):
    """여행 계획을 구글 캘린더에 동기화"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="여행 계획을 구글 캘린더에 동기화",
        operation_description="여행 계획의 모든 일정을 구글 캘린더 이벤트로 생성합니다. 사전에 구글 OAuth 인증이 완료되어야 합니다.",
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
                description="캘린더 동기화 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="구글 캘린더에 5개 일정이 추가되었습니다."),
                        "event_count": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
                        "calendar_url": openapi.Schema(type=openapi.TYPE_STRING, example="https://calendar.google.com")
                    }
                )
            ),
            400: openapi.Response(description="구글 인증이 필요하거나 여행 계획이 비어있음"),
            404: openapi.Response(description="여행 계획을 찾을 수 없음"),
            500: openapi.Response(description="캘린더 동기화 실패")
        },
        tags=["내보내기"]
    )
    def post(self, request, plan_id):
        # 여행 계획 존재 확인
        travel_plan = get_object_or_404(TravelPlan, id=plan_id, user_id=request.user.id)

        # 구글 액세스 토큰 확인 (DB에서)
        access_token = request.user.google_calendar_token
        if not access_token:
            return Response({
                "error": "구글 캘린더 인증이 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # PDF 데이터와 같은 형식으로 여행 계획 데이터 가져오기
            lang = request.GET.get("lang", "ko")

            # plan_pdf_data 함수의 로직을 재사용
            plan_places = travel_plan.plan_places.all().order_by("visit_date", "visit_time")
            places_by_date = defaultdict(list)

            for plan_place in plan_places:
                try:
                    from places.models import Place, PlaceTranslation
                    place = Place.objects.get(id=plan_place.place_id)

                    # 다국어 지원 - fallback 로직
                    place_name = "알 수 없는 장소"
                    category_name = "기타"

                    translation = PlaceTranslation.objects.filter(place=place, lang=lang).first()
                    if not translation:
                        translation = PlaceTranslation.objects.filter(place=place, lang="cn").first()
                    if not translation:
                        translation = PlaceTranslation.objects.filter(place=place, lang="en").first()
                    if not translation:
                        translation = PlaceTranslation.objects.filter(place=place, lang="jp").first()

                    if translation:
                        place_name = translation.name

                    # 카테고리 정보
                    if place.category_id:
                        try:
                            from categories.models import Category, CategoryTranslation
                            category = Category.objects.get(id=place.category_id)
                            category_translation = CategoryTranslation.objects.filter(
                                category=category, lang=lang
                            ).first()

                            if not category_translation:
                                category_translation = CategoryTranslation.objects.filter(
                                    category=category, lang="cn"
                                ).first()
                            if not category_translation:
                                category_translation = CategoryTranslation.objects.filter(
                                    category=category, lang="en"
                                ).first()
                            if not category_translation:
                                category_translation = CategoryTranslation.objects.filter(
                                    category=category, lang="jp"
                                ).first()

                            if category_translation:
                                category_name = category_translation.name
                        except:
                            category_name = "기타"

                    # 날짜별로 그룹화
                    if plan_place.visit_date:
                        places_by_date[plan_place.visit_date].append({
                            "time": plan_place.visit_time.strftime("%H:%M") if plan_place.visit_time else "",
                            "place_name": place_name,
                            "category": category_name,
                            "place_id": place.id
                        })

                except Place.DoesNotExist:
                    # 관광지가 삭제된 경우
                    if plan_place.visit_date:
                        places_by_date[plan_place.visit_date].append({
                            "time": plan_place.visit_time.strftime("%H:%M") if plan_place.visit_time else "",
                            "place_name": "",
                            "category": "",
                            "place_id": None
                        })

            # 날짜별 일정 구조화
            schedule = []
            sorted_dates = sorted(places_by_date.keys()) if places_by_date else []

            for index, date in enumerate(sorted_dates):
                places = sorted(places_by_date[date], key=lambda x: x["time"] or "00:00")
                schedule.append({
                    "day": index + 1,
                    "date": date.strftime("%Y-%m-%d"),
                    "places": places
                })

            # 여행 계획 제목과 설명
            from plans.models import TravelPlanTranslation

            title = "여행 계획"
            description = ""

            plan_translation = TravelPlanTranslation.objects.filter(
                travel_plan=travel_plan, lang=lang
            ).first()

            if not plan_translation:
                plan_translation = TravelPlanTranslation.objects.filter(
                    travel_plan=travel_plan, lang="cn"
                ).first()
            if not plan_translation:
                plan_translation = TravelPlanTranslation.objects.filter(
                    travel_plan=travel_plan, lang="en"
                ).first()
            if not plan_translation:
                plan_translation = TravelPlanTranslation.objects.filter(
                    travel_plan=travel_plan, lang="jp"
                ).first()

            if plan_translation:
                title = plan_translation.title
                description = plan_translation.description

            # 구글 캘린더에 동기화할 데이터
            calendar_data = {
                "title": title,
                "description": description,
                "schedule": schedule
            }

            # 일정이 비어있는지 확인
            total_places = sum(len([p for p in day["places"] if p["place_name"]]) for day in schedule)
            if total_places == 0:
                return Response({
                    "error": "동기화할 여행 일정이 없습니다. 먼저 관광지를 추가해주세요."
                }, status=status.HTTP_400_BAD_REQUEST)

            # 구글 캘린더에 이벤트 생성
            calendar_service = GoogleCalendarService()

            try:
                event_ids = calendar_service.create_calendar_events(access_token, calendar_data)
            except Exception as calendar_error:
                # 토큰 만료 시 자동 갱신
                if "refresh the access token" in str(calendar_error) and request.user.google_calendar_refresh_token:
                    try:
                        new_token = calendar_service.refresh_access_token(request.user.google_calendar_refresh_token)
                        request.user.google_calendar_token = new_token
                        request.user.save()
                        event_ids = calendar_service.create_calendar_events(new_token, calendar_data)
                    except Exception:
                        raise Exception("구글 캘린더 재인증이 필요합니다.")
                else:
                    raise calendar_error

            # 성공 응답 반환
            return Response({
                "message": f"구글 캘린더에 {len(event_ids)}개 일정이 추가되었습니다.",
                "event_count": len(event_ids),
                "calendar_url": "https://calendar.google.com"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"캘린더 동기화 실패: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)