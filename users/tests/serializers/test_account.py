from django.test import TestCase
from users.serializers.account import (
    FindAccountSerializer,
    ChangePasswordSerializer,
)
from users.models import CustomUser
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import RequestError


class FindAccountSerializerTest(TestCase):

    def test_valid_phone_number(self):
        data = {'phone_number': '01012345678'}
        serializer = FindAccountSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['phone_number'], '01012345678')

    def test_blank_phone_number(self):
        data = {'phone_number': ''}
        serializer = FindAccountSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)

    def test_missing_phone_number(self):
        data = {}
        serializer = FindAccountSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)


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