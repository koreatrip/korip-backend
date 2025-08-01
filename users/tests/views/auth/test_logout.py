from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from users.models import CustomUser
from rest_framework import status
from exceptions.error_code import ErrorCode


class LogoutTest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            nickname="tester"
        )
        self.logout_url = reverse("logout-user")

    def test_logout_success(self):
        """로그아웃 성공"""
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.logout_url, {"refresh_token": str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_fail_invalid_token(self):
        """로그아웃 실패 - 잘못된 리프레시 토큰"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.logout_url, {"refresh_token": "invalid.token"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_code"], ErrorCode.INVALID_REFRESH_TOKEN.code)