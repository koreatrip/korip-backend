from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone
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

    def test_first_login_sets_last_login_and_returns_flag_true(self):
        """첫 로그인: last_login = None -> not None, first_login=True"""
        self.assertIsNone(self.user.last_login)  # 초기값은 None

        data = {"email": "test@example.com", "password": "TestPass123!"}
        res = self.client.post(self.login_url, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["first_login"])  # 첫 로그인 플래그만 확인
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)  # 시간값 자체 비교 X

    def test_second_login_returns_flag_false_and_last_login_exists(self):
        """두 번째 로그인: first_login=False, last_login은 계속 존재"""
        data = {"email": "test@example.com", "password": "TestPass123!"}

        # 1차 로그인
        self.client.post(self.login_url, data)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)

        # 2차 로그인
        res2 = self.client.post(self.login_url, data)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertFalse(res2.data["first_login"])  # 재로그인 플래그만 확인
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)  # 존재 여부만 확인
