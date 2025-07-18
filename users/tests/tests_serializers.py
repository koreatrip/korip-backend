from django.test import TestCase
from users.serializers import (
    SignUpSerializer,
    SendVerificationCodeSerializer,
    CheckVerificationCodeSerializer
)
from users.models import CustomUser
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
        """회워가입 실패 (이메일 인증X)"""
        data = {
            "email": "test@example.com",
            "nickname": "tester",
            "password": "SecurePass123!"
        }
        serializer = SignUpSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_weak_password(self):
        """회워가입 실패 (너무 짧은 비밀번호)"""
        with patch("users.serializers.EmailHelper.check_verification_email", return_value=True):
            data = {
                "email": "test@example.com",
                "nickname": "tester",
                "password": "123"  # 너무 약한 비밀번호
            }
            serializer = SignUpSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("password", serializer.errors)


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
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


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
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_missing_fields(self):
        """이메일 인증 실패 (코드 누락)"""
        data = {"email": "test@example.com"}  # code 빠짐
        serializer = CheckVerificationCodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)
