from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import Mock, patch
from users.models import CustomUser, LoginType


class SocialLoginAPIViewTest(TestCase):
    """SocialLoginAPIView 필수 테스트"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('social-login-user')
        self.valid_phone_number = "8201012345678",
        self.valid_code = "4/0AeaYSHBqFw8xQwNxYz9h4KqJ5K5K5K5K5K5K5K5K5K5K5K5K5K5"

    @patch('users.views.auth.social_login.get_provider')
    def test_successful_login_new_user(self, mock_get_provider):
        """새 사용자 소셜 로그인 성공 테스트"""
        mock_provider = Mock()
        mock_provider.get_token.return_value = "mock_access_token"
        mock_provider.get_user_info.return_value = {
            "email": "newuser@example.com",
            "name": "New User",
            "sub": "123456789",
            "login_type": LoginType.GOOGLE
        }
        mock_get_provider.return_value = mock_provider

        data = {
            "phone_number": self.valid_phone_number,
            "code": self.valid_code
        }
        
        response = self.client.post(f"{self.url}?provider=google", data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
        
        # 새 사용자가 생성되었는지 확인
        user = CustomUser.objects.get(email="newuser@example.com")
        self.assertEqual(user.nickname, "New User")
        self.assertTrue(user.is_social)

    @patch('users.views.auth.social_login.get_provider')
    def test_successful_login_existing_user(self, mock_get_provider):
        """기존 사용자 소셜 로그인 성공 테스트"""        
        mock_provider = Mock()
        mock_provider.get_token.return_value = "mock_access_token"
        mock_provider.get_user_info.return_value = {
            "email": "existing@example.com",
            "name": "Updated Name",
            "sub": "123456789",
            "login_type": LoginType.GOOGLE
        }
        mock_get_provider.return_value = mock_provider

        data = {
            "phone_number": self.valid_phone_number,
            "code": self.valid_code
        }
        
        response = self.client.post(f"{self.url}?provider=google", data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
        
        # 기존 사용자 정보가 유지되는지 확인
        self.assertEqual(CustomUser.objects.filter(email="existing@example.com").count(), 1)

    def test_unsupported_provider(self):
        """지원하지 않는 제공자 테스트"""
        data = {
            "phone_number": self.valid_phone_number,
            "code": self.valid_code
        }
        
        response = self.client.post(f"{self.url}?provider=facebook", data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_provider_parameter(self):
        """provider 파라미터 누락 테스트"""
        data = {
            "phone_number": self.valid_phone_number,
            "code": self.valid_code
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_code_field(self):
        """code 필드 누락 테스트"""
        data = {}
        
        response = self.client.post(f"{self.url}?provider=google", data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data)

    def test_empty_code_field(self):
        """빈 code 필드 테스트"""
        data = {
            "phone_number": self.valid_phone_number,
            "code": ""
        }
        
        response = self.client.post(f"{self.url}?provider=google", data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_phone_number_field(self):
        """phone_number 필드 누락 테스트"""
        data = {
            "code": self.valid_code
        }
        response = self.client.post(f"{self.url}?provider=google", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data)

    def test_empty_phone_number_field(self):
        """빈 phone_number 필드 테스트"""
        data = {
            "phone_number": "",
            "code": self.valid_code
        }
        response = self.client.post(f"{self.url}?provider=google", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data)

    @patch('utils.oauth.factory.get_provider')
    def test_invalid_oauth_code(self, mock_get_provider):
        """유효하지 않은 OAuth 코드 테스트"""
        mock_provider = Mock()
        mock_provider.get_token.side_effect = Exception("Invalid authorization code")
        mock_get_provider.return_value = mock_provider

        data = {
            "phone_number": self.valid_phone_number,
            "code": "invalid_code"
        }
        
        with self.assertRaises(Exception):
            response = self.client.post(f"{self.url}?provider=google", data)
