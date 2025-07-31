from django.test import TestCase
from users.serializers.auth.login import LoginSerializer
from users.models import CustomUser
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    RequestError, 
    AuthenticationError
)


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