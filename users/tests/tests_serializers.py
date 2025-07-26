from django.test import TestCase
from django.contrib.auth.hashers import make_password
from users.serializers import (
    SignUpSerializer,
    SendVerificationCodeSerializer,
    CheckVerificationCodeSerializer,
    LoginSerializer, 
    ChangePasswordSerializer,
)
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from users.serializers import CustomTokenObtainPairSerializer
from users.models import CustomUser
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    EmailError, RequestError, 
    AuthenticationError, UserError,
)
from unittest.mock import patch

class SignUpSerializerTest(TestCase):
    @patch("users.serializers.EmailHelper.check_verification_email", return_value=True)
    def test_valid_data(self, mock_check):
        """회원가입 성공 (이메일 인증 완료, 강력한 비밀번호)"""
        data = {
            "email": "test@example.com",
            "nickname": "tester",
            "phone_number": "01012345678",
            "password": "SecurePass123!"
        }
        serializer = SignUpSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, data["email"])
        self.assertTrue(CustomUser.objects.filter(email="test@example.com").exists())

    @patch("users.serializers.EmailHelper.check_verification_email", return_value=False)
    def test_email_not_verified(self, mock_check):
        """회원가입 실패 (이메일 인증X)"""
        data = {
            "email": "test@example.com",
            "nickname": "tester",
            "password": "SecurePass123!"
        }
        serializer = SignUpSerializer(data=data)
        with self.assertRaises(EmailError) as context:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(context.exception.detail['error_code'], ErrorCode.EMAIL_NOT_CERTIFIED.code)

    def test_weak_password(self):
        """회원가입 실패 (너무 약한 비밀번호)"""
        with patch("users.serializers.EmailHelper.check_verification_email", return_value=True):
            data = {
                "email": "test@example.com",
                "nickname": "tester",
                "password": "123"
            }
            serializer = SignUpSerializer(data=data)
            with self.assertRaises(RequestError) as context:
                serializer.is_valid(raise_exception=True)
            
            self.assertEqual(context.exception.detail['error_code'], ErrorCode.INVALID_PASSWORD.code)


class SendVerificationCodeSerializerTest(TestCase):
    def test_valid_email(self):
        """이메일 발송 성공 (미가입 이메일)"""
        data = {"email": "new@example.com"}
        serializer = SendVerificationCodeSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_existing_email(self):
        """이메일 발송 실패 (이미 존재하는 이메일)"""
        CustomUser.objects.create_user(email="test@example.com", password="12345678")
        data = {"email": "test@example.com"}
        serializer = SendVerificationCodeSerializer(data=data)
        
        with self.assertRaises(EmailError) as context:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(context.exception.detail['error_code'], ErrorCode.EMAIL_ALREADY_REGISTERED.code)


class CheckVerificationCodeSerializerTest(TestCase):
    def test_valid_email_and_code(self):
        """이메일 인증 성공 (미가입 이메일, 코드 일치)"""
        data = {"email": "new@example.com", "code": "123456"}
        serializer = CheckVerificationCodeSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_existing_email_error(self):
        """이메일 인증 실패 (이미 존재하는 이메일)"""
        CustomUser.objects.create_user(email="test@example.com", password="pass")
        data = {"email": "test@example.com", "code": "123456"}
        serializer = CheckVerificationCodeSerializer(data=data)

        with self.assertRaises(EmailError) as context:
            serializer.is_valid(raise_exception=True)
        
        self.assertEqual(context.exception.detail['error_code'], ErrorCode.EMAIL_ALREADY_REGISTERED.code)

    def test_missing_fields(self):
        """이메일 인증 실패 (코드 누락)"""
        data = {"email": "test@example.com"}  # code 누락
        serializer = CheckVerificationCodeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)


class CustomTokenObtainPairSerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="jwtuser@example.com",
            password="TestPass123!",
            nickname="jwt_tester",
            phone_number="01012345678",
            is_social=False
        )
        self.factory = APIRequestFactory()

    def test_token_contains_custom_claims(self):
        """JWT 토큰에 커스텀 클레임 포함 확인"""
        token = CustomTokenObtainPairSerializer.get_token(self.user)
        self.assertEqual(token["email"], self.user.email)
        self.assertEqual(token["nickname"], self.user.nickname)
        self.assertEqual(token["is_social"], self.user.is_social)

    def test_token_response_contains_user_info(self):
        """JWT 응답에 사용자 정보 포함 확인"""
        data = {
            "email": "jwtuser@example.com",
            "password": "TestPass123!"
        }
        request = self.factory.post("/api/users/login/", data)
        serializer = CustomTokenObtainPairSerializer(data=data, context={"request": Request(request)})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        token_data = serializer.validated_data

        self.assertIn("access", token_data)
        self.assertIn("refresh", token_data)

        user_data = token_data["user"]
        self.assertEqual(user_data["id"], self.user.id)
        self.assertEqual(user_data["email"], self.user.email)
        self.assertEqual(user_data["name"], self.user.nickname)
        self.assertEqual(user_data["phone_number"], self.user.phone_number)
        self.assertEqual(user_data["is_social"], self.user.is_social)

    def test_token_invalid_credentials(self):
        """JWT 발급 실패 (잘못된 비밀번호)"""
        data = {
            "email": "jwtuser@example.com",
            "password": "WrongPass"
        }
        request = self.factory.post("/api/users/login/", data)
        serializer = CustomTokenObtainPairSerializer(data=data, context={"request": Request(request)})

        with self.assertRaises(AuthenticationFailed) as context:
            serializer.is_valid(raise_exception=True)

        self.assertEqual(str(context.exception), "지정된 자격 증명에 해당하는 활성화된 사용자를 찾을 수 없습니다")


class LoginSerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="login@example.com",
            password="TestPass123!",
            nickname="login_user"
        )

    def test_login_success(self):
        """로그인 성공"""
        data = {"email": "login@example.com", "password": "TestPass123!"}
        serializer = LoginSerializer(data=data, context={"request": None})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_login_fail_wrong_password(self):
        """로그인 실패 (잘못된 비밀번호)"""
        data = {"email": "login@example.com", "password": "WrongPass"}
        serializer = LoginSerializer(data=data, context={"request": None})
        with self.assertRaises(AuthenticationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(context.exception.detail["error_code"], ErrorCode.INVALID_USER_INFO.code)

    def test_login_fail_inactive(self):
        """로그인 실패 (비활성화된 계정)"""
        self.user.is_active = False
        self.user.save()
        data = {"email": "login@example.com", "password": "TestPass123!"}
        serializer = LoginSerializer(data=data, context={"request": None})
        with self.assertRaises(AuthenticationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(context.exception.detail["error_code"], ErrorCode.INVALID_USER_INFO.code)


    def test_login_fail_missing_email_field(self):
        """로그인 실패 (이메일 필드 누락 - RequestError)"""
        data = {"password": "TestPass123!"}
        serializer = LoginSerializer(data=data, context={"request": None})
        with self.assertRaises(RequestError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(context.exception.detail["error_code"], ErrorCode.MISSING_CREDENTIALS.code)

    def test_login_fail_missing_password_field(self):
        """로그인 실패 (비밀번호 필드 누락 - RequestError)"""
        data = {"email": "login@example.com"}
        serializer = LoginSerializer(data=data, context={"request": None})
        with self.assertRaises(RequestError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(context.exception.detail["error_code"], ErrorCode.MISSING_CREDENTIALS.code)


class ChangePasswordSerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="changepw@example.com",
            password="OldPass123!",
            nickname="pw_user"
        )

    def _mock_request(self):
        class DummyRequest:
            user = self.user
        return DummyRequest()

    def test_change_password_success(self):
        """비밀번호 변경 성공"""
        data = {
            "current_password": "OldPass123!",
            "new_password": "NewSecure123!"
        }
        serializer = ChangePasswordSerializer(data=data, context={"request": self._mock_request()})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_change_password_same_as_current(self):
        """비밀번호 변경 실패 (현재 비밀번호와 동일)"""
        data = {
            "current_password": "OldPass123!",
            "new_password": "OldPass123!"
        }
        serializer = ChangePasswordSerializer(data=data, context={"request": self._mock_request()})
        with self.assertRaises(RequestError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(context.exception.detail["error_code"], ErrorCode.SAME_CURRENT_PASSWORD.code)

    def test_change_password_weak(self):
        """비밀번호 변경 실패 (너무 약한 새 비밀번호)"""
        data = {
            "current_password": "OldPass123!",
            "new_password": "123"
        }
        serializer = ChangePasswordSerializer(data=data, context={"request": self._mock_request()})
        with self.assertRaises(RequestError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(context.exception.detail["error_code"], ErrorCode.INVALID_PASSWORD.code)
