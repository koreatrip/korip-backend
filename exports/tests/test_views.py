from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from users.models import CustomUser
from plans.models import TravelPlan, TravelPlanTranslation, PlanPlace
from places.models import Place, PlaceTranslation
from categories.models import Category, CategoryTranslation
from datetime import date, time


class PlanPdfDataViewTest(TestCase):
    """여행 계획 PDF 데이터 조회 API 테스트"""

    def setUp(self):
        """테스트 시작 전 준비 작업"""
        # API 클라이언트 생성
        self.client = APIClient()

        # 테스트 사용자 생성
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="testpass123",
            nickname="테스트유저"
        )

        # 테스트 여행 계획 생성
        self.travel_plan = TravelPlan.objects.create(
            user_id=self.user.id,
            subregion_id=1,
            start_date=date(2025, 10, 20),
            end_date=date(2025, 10, 22)
        )

        # 여행 계획 번역 데이터 생성
        TravelPlanTranslation.objects.create(
            travel_plan=self.travel_plan,
            lang="ko",
            title="부산 여행",
            description="맛집 투어"
        )

        # 테스트 카테고리 생성
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="자연"
        )

        # 테스트 관광지 생성
        self.place = Place.objects.create(
            category_id=self.category.id,
            region_id=1,
            sub_region_id=1
        )
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="해운대 해수욕장"
        )

        # 여행 계획에 관광지 추가
        PlanPlace.objects.create(
            travel_plan=self.travel_plan,
            place_id=self.place.id,
            visit_date=date(2025, 10, 20),
            visit_time=time(9, 0)
        )

    def test_인증된_사용자_PDF_데이터_조회_성공(self):
        """로그인한 사용자가 자신의 여행 계획 PDF 데이터를 조회할 수 있는지 테스트"""
        # 사용자 로그인
        self.client.force_authenticate(user=self.user)

        # URL 생성
        url = reverse("exports:plan_pdf_data", kwargs={"plan_id": self.travel_plan.id})

        # GET 요청
        response = self.client.get(url)

        # 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 확인
        self.assertEqual(response.data["title"], "부산 여행")
        self.assertEqual(response.data["description"], "맛집 투어")
        self.assertEqual(len(response.data["schedule"]), 1)
        self.assertEqual(response.data["schedule"][0]["day"], 1)
        self.assertEqual(response.data["schedule"][0]["date"], "2025-10-20")
        self.assertEqual(len(response.data["schedule"][0]["places"]), 1)
        self.assertEqual(response.data["schedule"][0]["places"][0]["place_name"], "해운대 해수욕장")

    def test_인증_없이_PDF_데이터_조회_실패(self):
        """로그인하지 않은 사용자는 접근할 수 없는지 테스트"""
        # 로그인 안 함
        url = reverse("exports:plan_pdf_data", kwargs={"plan_id": self.travel_plan.id})

        # GET 요청
        response = self.client.get(url)

        # 401 Unauthorized 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_다른_사용자의_여행_계획_조회_실패(self):
        """다른 사용자의 여행 계획은 조회할 수 없는지 테스트"""
        # 다른 사용자 생성
        other_user = CustomUser.objects.create_user(
            email="other@example.com",
            password="otherpass123",
            nickname="다른유저"
        )

        # 다른 사용자로 로그인
        self.client.force_authenticate(user=other_user)

        # URL 생성
        url = reverse("exports:plan_pdf_data", kwargs={"plan_id": self.travel_plan.id})

        # GET 요청
        response = self.client.get(url)

        # 404 Not Found 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_언어_파라미터_적용(self):
        """lang 파라미터가 제대로 적용되는지 테스트"""
        # 영어 번역 추가
        TravelPlanTranslation.objects.create(
            travel_plan=self.travel_plan,
            lang="en",
            title="Busan Trip",
            description="Food Tour"
        )

        PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Haeundae Beach"
        )

        # 사용자 로그인
        self.client.force_authenticate(user=self.user)

        # URL 생성 (영어로 요청)
        url = reverse("exports:plan_pdf_data", kwargs={"plan_id": self.travel_plan.id})

        # GET 요청
        response = self.client.get(url, {"lang": "en"})

        # 영어 데이터 확인
        self.assertEqual(response.data["title"], "Busan Trip")
        self.assertEqual(response.data["schedule"][0]["places"][0]["place_name"], "Haeundae Beach")


class GoogleCalendarAuthViewTest(TestCase):
    """구글 캘린더 인증 시작 API 테스트"""

    def setUp(self):
        """테스트 시작 전 준비 작업"""
        self.client = APIClient()

        # 테스트 사용자 생성
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="testpass123",
            nickname="테스트유저"
        )

    @patch("exports.views.GoogleCalendarService")
    def test_인증_URL_생성_및_리디렉션(self, mock_service_class):
        """구글 인증 URL이 생성되고 리디렉션되는지 테스트"""
        # Mock 설정
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_authorization_url.return_value = "https://accounts.google.com/o/oauth2/auth?test=123"

        # 사용자 로그인
        self.client.force_authenticate(user=self.user)

        # URL 생성
        url = reverse("exports:google_calendar_auth")

        # GET 요청
        response = self.client.get(url)

        # 302 리디렉션 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # 리디렉션 URL 확인
        self.assertIn("https://accounts.google.com", response.url)

        # get_authorization_url 이 호출되었는지 확인
        mock_service.get_authorization_url.assert_called_once_with(self.user.id)

    def test_인증_없이_접근_실패(self):
        """로그인하지 않은 사용자는 접근할 수 없는지 테스트"""
        url = reverse("exports:google_calendar_auth")

        # GET 요청
        response = self.client.get(url)

        # 401 Unauthorized 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GoogleCalendarCallbackViewTest(TestCase):
    """구글 캘린더 OAuth 콜백 처리 API 테스트"""

    def setUp(self):
        """테스트 시작 전 준비 작업"""
        self.client = APIClient()

        # 테스트 사용자 생성
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="testpass123",
            nickname="테스트유저"
        )

    @patch("exports.views.GoogleCalendarService")
    def test_콜백_처리_성공(self, mock_service_class):
        """OAuth 콜백이 정상적으로 처리되는지 테스트"""
        # Mock 설정
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.handle_callback.return_value = {
            "user_id": self.user.id,
            "google_email": "user@gmail.com",
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token"
        }

        # URL 생성
        url = reverse("exports:google_calendar_callback")

        # GET 요청 (구글에서 리디렉션되는 형태)
        response = self.client.get(url, {
            "code": "test_auth_code_123",
            "state": str(self.user.id)
        })

        # 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 확인
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["google_email"], "user@gmail.com")

        # DB에 토큰이 저장되었는지 확인
        self.user.refresh_from_db()
        self.assertEqual(self.user.google_calendar_token, "test_access_token")
        self.assertEqual(self.user.google_calendar_refresh_token, "test_refresh_token")
        self.assertEqual(self.user.google_calendar_email, "user@gmail.com")

    def test_code_누락_시_실패(self):
        """code 파라미터가 없으면 실패하는지 테스트"""
        url = reverse("exports:google_calendar_callback")

        # state만 있고 code는 없음
        response = self.client.get(url, {"state": "123"})

        # 400 Bad Request 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class GoogleCalendarSyncViewTest(TestCase):
    """구글 캘린더 동기화 API 테스트"""

    def setUp(self):
        """테스트 시작 전 준비 작업"""
        self.client = APIClient()

        # 테스트 사용자 생성 (구글 토큰 포함)
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="testpass123",
            nickname="테스트유저"
        )
        self.user.google_calendar_token = "test_access_token"
        self.user.google_calendar_refresh_token = "test_refresh_token"
        self.user.save()

        # 테스트 여행 계획 생성
        self.travel_plan = TravelPlan.objects.create(
            user_id=self.user.id,
            subregion_id=1,
            start_date=date(2025, 10, 20),
            end_date=date(2025, 10, 22)
        )

        TravelPlanTranslation.objects.create(
            travel_plan=self.travel_plan,
            lang="ko",
            title="제주도 여행",
            description="휴양"
        )

        # 테스트 카테고리 생성
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="자연"
        )

        # 테스트 관광지 생성
        self.place = Place.objects.create(
            category_id=self.category.id,
            region_id=1,
            sub_region_id=1
        )
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="한라산"
        )

        # 여행 계획에 관광지 추가
        PlanPlace.objects.create(
            travel_plan=self.travel_plan,
            place_id=self.place.id,
            visit_date=date(2025, 10, 20),
            visit_time=time(9, 0)
        )

    @patch("exports.views.GoogleCalendarService")
    def test_캘린더_동기화_성공(self, mock_service_class):
        """구글 캘린더에 일정이 정상적으로 동기화되는지 테스트"""
        # Mock 설정
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.create_calendar_events.return_value = ["event_123", "event_456"]

        # 사용자 로그인
        self.client.force_authenticate(user=self.user)

        # URL 생성
        url = reverse("exports:google_calendar_sync", kwargs={"plan_id": self.travel_plan.id})

        # POST 요청
        response = self.client.post(url)

        # 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 확인
        self.assertIn("message", response.data)
        self.assertIn("event_count", response.data)
        self.assertEqual(response.data["event_count"], 2)

        # create_calendar_events 가 호출되었는지 확인
        mock_service.create_calendar_events.assert_called_once()

    def test_구글_토큰_없으면_실패(self):
        """구글 토큰이 없으면 동기화할 수 없는지 테스트"""
        # 토큰 제거
        self.user.google_calendar_token = None
        self.user.save()

        # 사용자 로그인
        self.client.force_authenticate(user=self.user)

        # URL 생성
        url = reverse("exports:google_calendar_sync", kwargs={"plan_id": self.travel_plan.id})

        # POST 요청
        response = self.client.post(url)

        # 400 Bad Request 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_인증_없이_접근_실패(self):
        """로그인하지 않은 사용자는 접근할 수 없는지 테스트"""
        url = reverse("exports:google_calendar_sync", kwargs={"plan_id": self.travel_plan.id})

        # POST 요청
        response = self.client.post(url)

        # 401 Unauthorized 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_빈_여행_계획_동기화_실패(self):
        """관광지가 없는 여행 계획은 동기화할 수 없는지 테스트"""
        # 관광지 삭제
        PlanPlace.objects.all().delete()

        # 사용자 로그인
        self.client.force_authenticate(user=self.user)

        # URL 생성
        url = reverse("exports:google_calendar_sync", kwargs={"plan_id": self.travel_plan.id})

        # POST 요청
        response = self.client.post(url)

        # 400 Bad Request 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)