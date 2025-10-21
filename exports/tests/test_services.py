from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings

from exports.services.google_calendar import GoogleCalendarService


class GoogleCalendarServiceTest(TestCase):
    """구글 캘린더 서비스 테스트"""

    def setUp(self):
        """테스트 시작 전 준비 작업"""
        # GoogleCalendarService 인스턴스 생성
        self.service = GoogleCalendarService()

        # 테스트용 사용자 ID
        self.test_user_id = 123

        # 테스트용 access_token
        self.test_access_token = "test_access_token_12345"

        # 테스트용 refresh_token
        self.test_refresh_token = "test_refresh_token_67890"

    def test_init_설정값_로드(self):
        """서비스 초기화 시 settings 값이 제대로 로드되는지 테스트"""
        # settings에서 값 가져오는지 확인
        self.assertEqual(self.service.client_id, settings.GOOGLE_OAUTH2_CLIENT_ID)
        self.assertEqual(self.service.client_secret, settings.GOOGLE_OAUTH2_CLIENT_SECRET)
        self.assertEqual(self.service.redirect_uri, settings.GOOGLE_OAUTH2_REDIRECT_URI)
        self.assertEqual(self.service.scopes, settings.GOOGLE_CALENDAR_SCOPES)

    @patch("exports.services.google_calendar.Flow")
    def test_get_authorization_url_정상_생성(self, mock_flow):
        """OAuth 인증 URL이 정상적으로 생성되는지 테스트"""
        # Flow.from_client_config 의 반환값을 Mock 으로 설정
        mock_flow_instance = MagicMock()
        mock_flow.from_client_config.return_value = mock_flow_instance

        # authorization_url 메서드가 반환할 값 설정
        expected_url = "https://accounts.google.com/o/oauth2/auth?test=123"
        mock_flow_instance.authorization_url.return_value = (expected_url, "test_state")

        # 함수 실행
        result_url = self.service.get_authorization_url(self.test_user_id)

        # Flow.from_client_config 가 호출되었는지 확인
        mock_flow.from_client_config.assert_called_once()

        # authorization_url 메서드가 올바른 파라미터로 호출되었는지 확인
        mock_flow_instance.authorization_url.assert_called_once_with(
            access_type="offline",
            include_granted_scopes="true",
            state=str(self.test_user_id)
        )

        # 반환된 URL이 예상한 값인지 확인
        self.assertEqual(result_url, expected_url)

    @patch("exports.services.google_calendar.build")
    @patch("exports.services.google_calendar.Flow")
    def test_handle_callback_정상_처리(self, mock_flow, mock_build):
        """OAuth 콜백이 정상적으로 처리되는지 테스트"""
        # Flow Mock 설정
        mock_flow_instance = MagicMock()
        mock_flow.from_client_config.return_value = mock_flow_instance

        # credentials Mock 설정
        mock_credentials = MagicMock()
        mock_credentials.token = self.test_access_token
        mock_credentials.refresh_token = self.test_refresh_token
        mock_credentials.expiry = None
        mock_flow_instance.credentials = mock_credentials

        # Google OAuth2 API Mock 설정
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_userinfo = MagicMock()
        mock_service.userinfo.return_value.get.return_value.execute.return_value = {
            "email": "test@gmail.com"
        }

        # 함수 실행
        test_code = "test_auth_code_123"
        test_state = str(self.test_user_id)
        result = self.service.handle_callback(test_code, test_state)

        # fetch_token 이 호출되었는지 확인
        mock_flow_instance.fetch_token.assert_called_once_with(code=test_code)

        # 반환값 확인
        self.assertEqual(result["user_id"], self.test_user_id)
        self.assertEqual(result["google_email"], "test@gmail.com")
        self.assertEqual(result["access_token"], self.test_access_token)
        self.assertEqual(result["refresh_token"], self.test_refresh_token)
        self.assertIsNone(result["token_expires_at"])

    @patch("exports.services.google_calendar.build")
    @patch("exports.services.google_calendar.Credentials")
    def test_create_calendar_events_정상_생성(self, mock_credentials_class, mock_build):
        """캘린더 이벤트가 정상적으로 생성되는지 테스트"""
        # Credentials Mock
        mock_credentials = MagicMock()
        mock_credentials_class.return_value = mock_credentials

        # Calendar API Mock 설정
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # 이벤트 생성 결과 Mock
        mock_created_event = {"id": "event_123"}
        mock_service.events.return_value.insert.return_value.execute.return_value = mock_created_event

        # 테스트용 여행 계획 데이터
        travel_plan_data = {
            "title": "부산 여행",
            "description": "맛집 투어",
            "schedule": [
                {
                    "date": "2025-10-20",
                    "day": 1,
                    "places": [
                        {
                            "place_name": "해운대 해수욕장",
                            "time": "09:00",
                            "category": "자연"
                        },
                        {
                            "place_name": "광안리",
                            "time": "14:00",
                            "category": "자연"
                        }
                    ]
                }
            ]
        }

        # 함수 실행
        result = self.service.create_calendar_events(self.test_access_token, travel_plan_data)

        # Calendar API build 가 호출되었는지 확인
        mock_build.assert_called_once_with("calendar", "v3", credentials=mock_credentials)

        # 이벤트가 2개 생성되었는지 확인
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "event_123")

    @patch("exports.services.google_calendar.build")
    @patch("exports.services.google_calendar.Credentials")
    def test_create_calendar_events_빈_장소_건너뛰기(self, mock_credentials_class, mock_build):
        """place_name 이나 time 이 없는 경우 건너뛰는지 테스트"""
        # Mock 설정
        mock_credentials = MagicMock()
        mock_credentials_class.return_value = mock_credentials

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # 빈 장소가 포함된 여행 계획
        travel_plan_data = {
            "title": "서울 여행",
            "schedule": [
                {
                    "date": "2025-10-20",
                    "day": 1,
                    "places": [
                        {"place_name": "", "time": "09:00"},  # 빈 이름
                        {"place_name": "경복궁", "time": ""},  # 빈 시간
                        {"place_name": "남산타워", "time": "14:00"}  # 정상
                    ]
                }
            ]
        }

        mock_created_event = {"id": "event_456"}
        mock_service.events.return_value.insert.return_value.execute.return_value = mock_created_event

        # 함수 실행
        result = self.service.create_calendar_events(self.test_access_token, travel_plan_data)

        # 정상적인 장소 1개만 이벤트 생성되었는지 확인
        self.assertEqual(len(result), 1)

    @patch("exports.services.google_calendar.Request")
    @patch("exports.services.google_calendar.Credentials")
    def test_refresh_access_token_정상_갱신(self, mock_credentials_class, mock_request):
        """리프레시 토큰으로 액세스 토큰을 갱신하는지 테스트"""
        # Credentials Mock
        mock_credentials = MagicMock()
        mock_credentials.token = "new_access_token_999"
        mock_credentials_class.return_value = mock_credentials

        # 함수 실행
        result = self.service.refresh_access_token(self.test_refresh_token)

        # Credentials 가 올바른 파라미터로 생성되었는지 확인
        mock_credentials_class.assert_called_once_with(
            token=None,
            refresh_token=self.test_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.service.client_id,
            client_secret=self.service.client_secret
        )

        # refresh 메서드가 호출되었는지 확인
        mock_credentials.refresh.assert_called_once()

        # 새 토큰이 반환되었는지 확인
        self.assertEqual(result, "new_access_token_999")