from django.test import TestCase
from users.serializers.serializers import (
    SendVerificationCodeSerializer,
    CheckVerificationCodeSerializer
)
from users.models import CustomUser
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import EmailError


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