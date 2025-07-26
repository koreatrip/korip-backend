from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from users.models import CustomUser
from unittest.mock import patch
from rest_framework import status
from exceptions.error_code import ErrorCode


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
        self.assertEqual(response.data["email"], data["email"])
        self.assertEqual(response.data["name"], data["nickname"])

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
        self.assertEqual(response.data["error_code"], ErrorCode.EMAIL_NOT_CERTIFIED.code)
        self.assertEqual(response.data["error_message"], ErrorCode.EMAIL_NOT_CERTIFIED.message)

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
        self.assertEqual(response.data["error_code"], ErrorCode.INVALID_PASSWORD.code)
        self.assertEqual(response.data["error_message"], ErrorCode.INVALID_PASSWORD.message)


class SendVerificationCodeTest(APITestCase):

    @patch("helper.email_helper.EmailHelper.send_verification_email", return_value="123456")
    def test_send_verification_email_success(self, mock_send):
        """이메일 발송 성공"""
        url = reverse("verification-email")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_verification_invalid_email_format(self):
        """이메일 발송 실패 (잘못된 이메일 형식)"""
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
        self.assertEqual(response.data["error_code"], ErrorCode.EMAIL_ALREADY_REGISTERED.code)
        self.assertEqual(response.data["error_message"], ErrorCode.EMAIL_ALREADY_REGISTERED.message)

    @patch("helper.email_helper.EmailHelper.send_verification_email", return_value=None)
    def test_send_verification_email_fail(self, mock_send):
        """이메일 발송 실패 (실패 예외)"""
        url = reverse("verification-email")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_code"], ErrorCode.EMAIL_NOT_CERTIFIED.code)
        self.assertEqual(response.data["error_message"], ErrorCode.EMAIL_NOT_CERTIFIED.message)


class CheckVerificationCodeTest(APITestCase):

    @patch("helper.email_helper.EmailHelper.check_verification_code", return_value=True)
    def test_check_verification_code_success(self, mock_check):
        """이메일 인증 성공"""
        url = reverse("verify-code")
        data = {"email": "test@example.com", "code": "123456"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("helper.email_helper.EmailHelper.check_verification_code", return_value=False)
    def test_check_verification_code_fail(self, mock_check):
        """이메일 인증 실패 (불일치 또는 만료)"""
        url = reverse("verify-code")
        data = {"email": "test@example.com", "code": "000000"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_code"], ErrorCode.EMAIL_CERTIFICATION_FAIL.code)
        self.assertEqual(response.data["error_message"], ErrorCode.EMAIL_CERTIFICATION_FAIL.message)

    def test_check_verification_code_missing_fields(self):
        """이메일 인증 실패 (코드 누락)"""
        url = reverse("verify-code")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data)


class AuthTokenTest(APITestCase):

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
