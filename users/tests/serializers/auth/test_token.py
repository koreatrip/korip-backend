from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed
from users.serializers.serializers import CustomTokenObtainPairSerializer
from users.models import CustomUser


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