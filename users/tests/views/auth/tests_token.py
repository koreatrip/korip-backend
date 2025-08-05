from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from users.models import CustomUser
from rest_framework import status
from exceptions.error_code import ErrorCode


class TokenTest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            nickname="tester"
        )
        self.token_refresh_url = reverse("reissue-token")

    def test_token_refresh_success(self):
        """토큰 갱신 성공"""
        refresh = RefreshToken.for_user(self.user)
        # 'refresh' 필드로 보내야 함
        response = self.client.post(self.token_refresh_url, {"refresh": str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

    def test_token_refresh_fail(self):
        """토큰 갱신 실패 - 잘못된 토큰"""
        response = self.client.post(self.token_refresh_url, {"refresh": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error_code", response.data)
        self.assertEqual(response.data["error_code"], ErrorCode.INVALID_REFRESH_TOKEN.code)