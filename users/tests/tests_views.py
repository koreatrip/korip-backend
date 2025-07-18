from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import CustomUser
from unittest.mock import patch
from rest_framework import status


class SignUpTest(APITestCase):

    @patch("helper.email_helper.EmailHelper.check_verification_email", return_value=True)
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
        self.assertEqual(response.data["message"], "회원가입이 완료되었습니다.")

    @patch("helper.email_helper.EmailHelper.check_verification_email", return_value=False)
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
        self.assertIn("email", response.data)

    @patch("helper.email_helper.EmailHelper.check_verification_email", return_value=True)
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
        self.assertIn("password", response.data)


class SendVerificationCodeTest(APITestCase):

    @patch("helper.email_helper.EmailHelper.send_verification_email", return_value="123456")
    def test_send_verification_email_success(self, mock_send):
        """이메일 발송 성공"""
        url = reverse("verification-email")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "이메일 발송이 완료되었습니다.")

    def test_send_verification_invalid_email_format(self):
        """이메일 발송 실패 (맞지않는 이메일 형식)"""
        url = reverse("verification-email")
        data = {"email": "invalid-email"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_send_verification_existing_user_email(self):
        """이메일 발송 실패 (이미 존재하는 이메일)"""
        CustomUser.objects.create_user(email="test@example.com", password="123")
        url = reverse("verification-email")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    @patch("helper.email_helper.EmailHelper.send_verification_email", return_value=None)
    def test_send_verification_email_fail(self, mock_send):
        """이메일 발송 실패 (예기치 못한 에러)"""
        url = reverse("verification-email")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_message"], "이메일 발송을 실패했습니다.")


class SendVerificationCodeTest(APITestCase):

    @patch("helper.email_helper.EmailHelper.check_verification_code", return_value=True)
    def test_check_verification_code_success(self, mock_check):
        """이메일 인증 성공"""
        url = reverse("verify-code")
        data = {"email": "test@example.com", "code": "123456"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "이메일 인증이 완료되었습니다.")

    @patch("helper.email_helper.EmailHelper.check_verification_code", return_value=False)
    def test_check_verification_code_mismatch(self, mock_check):
        """이메일 인증 실패 (인증 코드 불일치)"""
        url = reverse("verify-code")
        data = {"email": "test@example.com", "code": "000000"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_message"], "이메일 인증번호가 일치하지 않습니다.")

    @patch("helper.email_helper.EmailHelper.check_verification_code", return_value=False)
    def test_check_verification_code_none(self, mock_check):
        """이메일 인증 실패 (인증 시간 초과)"""
        url = reverse("verify-code")
        data = {"email": "test@example.com", "code": "123456"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_message"], "이메일 인증번호가 일치하지 않습니다.")

    def test_check_verification_code_missing_fields(self):
        """이메일 인증 실패 (인증 코드 누락)"""
        url = reverse("verify-code")
        data = {"email": "test@example.com"}  # code 빠짐
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data)
