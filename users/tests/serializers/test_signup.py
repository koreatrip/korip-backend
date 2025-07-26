from django.test import TestCase
from users.serializers.serializers import SignUpSerializer
from users.models import CustomUser
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    EmailError, RequestError
)
from unittest.mock import patch


class SignUpSerializerTest(TestCase):
    @patch("users.serializers.signup.EmailHelper.check_verification_email", return_value=True)
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

    @patch("users.serializers.signup.EmailHelper.check_verification_email", return_value=False)
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
        with patch("users.serializers.signup.EmailHelper.check_verification_email", return_value=True):
            data = {
                "email": "test@example.com",
                "nickname": "tester",
                "password": "123"
            }
            serializer = SignUpSerializer(data=data)
            with self.assertRaises(RequestError) as context:
                serializer.is_valid(raise_exception=True)
            
            self.assertEqual(context.exception.detail['error_code'], ErrorCode.INVALID_PASSWORD.code)