from rest_framework.test import APITestCase
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from exceptions.error_code import ErrorCode


class SignUpTest(APITestCase):

    @patch("utils.helper.email_helper.EmailHelper.check_verification_email", return_value=True)
    def test_signup_success(self, mock_check):
        """회원가입 성공"""
        url = reverse("sign-up-user")
        data = {
            "email": "test@example.com",
            "nickname": "tester",
            "phone_number": "01012345678",
            "password": "securePass123!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], data["email"])
        self.assertEqual(response.data["name"], data["nickname"])

    @patch("utils.helper.email_helper.EmailHelper.check_verification_email", return_value=False)
    def test_signup_email_not_verified(self, mock_check):
        """회원가입 실패 (이메일 인증X)"""
        url = reverse("sign-up-user")
        data = {
            "email": "test@example.com",
            "nickname": "tester",
            "phone_number": "01012345678",
            "password": "securePass123!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_code"], ErrorCode.EMAIL_NOT_CERTIFIED.code)
        self.assertEqual(response.data["error_message"], ErrorCode.EMAIL_NOT_CERTIFIED.message)

    @patch("utils.helper.email_helper.EmailHelper.check_verification_email", return_value=True)
    def test_signup_password_too_short(self, mock_check):
        """회원가입 실패 (너무 짧은 비밀번호)"""
        url = reverse("sign-up-user")
        data = {
            "email": "test@example.com",
            "nickname": "tester",
            "phone_number": "01012345678",
            "password": "123"  # too short
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_code"], ErrorCode.INVALID_PASSWORD.code)
        self.assertEqual(response.data["error_message"], ErrorCode.INVALID_PASSWORD.message)