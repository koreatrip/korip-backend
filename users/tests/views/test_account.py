from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import CustomUser
from rest_framework import status
from exceptions.error_code import ErrorCode


class AccountTest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            nickname="tester"
        )
        self.login_url = reverse("login-user")
        self.logout_url = reverse("logout-user")
        self.token_refresh_url = reverse("reissue-token")
        self.change_pw_url = reverse("change-pwd")
    
    def test_change_password_success(self):
        """비밀번호 변경 성공"""
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "TestPass123!",
            "new_password": "NewPass456!"
        }
        response = self.client.post(self.change_pw_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_fail_wrong_current(self):
        """비밀번호 변경 실패 - 현재 비밀번호 불일치"""
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "WrongPass123!",
            "new_password": "NewPass456!"
        }
        response = self.client.post(self.change_pw_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_code"], ErrorCode.MISSMATCHED_PASSWORD.code)
