from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import CustomUser
from rest_framework import status
from exceptions.error_code import ErrorCode


class LoginTest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            nickname="tester"
        )
        self.login_url = reverse("login-user")

    def test_login_success(self):
        """로그인 성공"""
        data = {
            "email": "test@example.com",
            "password": "TestPass123!"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_login_fail_wrong_password(self):
        """로그인 실패 - 비밀번호 오류"""
        data = {
            "email": "test@example.com",
            "password": "WrongPass"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_code"], ErrorCode.INVALID_USER_INFO.code)