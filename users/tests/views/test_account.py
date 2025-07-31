from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import CustomUser
from rest_framework import status
from exceptions.error_code import ErrorCode
from users.models import LoginType


class FindAccountTest(APITestCase):

    def setUp(self):
        """테스트 데이터 설정"""
        self.url = reverse('find-account')  # URL name에 맞게 수정 필요
        self.phone_number = "010-1234-5678"
        
        # 테스트용 사용자 생성
        self.user1 = CustomUser.objects.create_user(
            email="john@example.com",
            phone_number=self.phone_number,
            nickname="john",
            login_type=LoginType.EMAIL
        )
        
        self.user2 = CustomUser.objects.create_user(
            email="john@gmail.com",
            phone_number=self.phone_number,
            nickname="john2",
            login_type=LoginType.GOOGLE
        )
        
        # 다른 전화번호 사용자
        self.user3 = CustomUser.objects.create_user(
            email="jane@example.com",
            phone_number="010-9999-9999",
            nickname="jane",
            login_type=LoginType.EMAIL
        )

    def test_find_account_success_multiple_accounts(self):
        """성공: 같은 전화번호로 여러 계정 찾기"""
        data = {"phone_number": self.phone_number}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accounts', response.data)
        self.assertEqual(len(response.data['accounts']), 2)
        
        # 이메일 마스킹 확인
        emails = [account['email'] for account in response.data['accounts']]
        self.assertIn('jo**@example.com', emails)
        self.assertIn('jo**@gmail.com', emails)
        
        # 로그인 타입 확인
        login_types = [account['login_type'] for account in response.data['accounts']]
        self.assertIn('email', login_types)
        self.assertIn('google', login_types)

    def test_find_account_success_single_account(self):
        """성공: 단일 계정 찾기"""
        data = {"phone_number": "010-9999-9999"}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['accounts']), 1)
        self.assertEqual(response.data['accounts'][0]['email'], 'ja**@example.com')

    def test_find_account_not_found(self):
        """실패: 존재하지 않는 전화번호"""
        data = {"phone_number": "010-0000-0000"}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_code", response.data)
        self.assertEqual(response.data["error_code"], ErrorCode.ACCOUNT_NOT_FOUND.code)


    def test_find_account_invalid_phone_number_empty(self):
        """실패: 빈 전화번호"""
        data = {"phone_number": ""}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data)

    def test_find_account_missing_phone_number(self):
        """실패: 전화번호 필드 누락"""
        data = {}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data)

    def test_email_masking_logic(self):
        """이메일 마스킹 로직 테스트"""
        from users.views.account import FindAccountAPIView
        
        view = FindAccountAPIView()
        
        # 다양한 이메일 마스킹 테스트
        test_cases = [
            ("a@test.com", "a@test.com"),
            ("ab@test.com", "a*@test.com"),
            ("abc@test.com", "ab*@test.com"),
            ("john@example.com", "jo**@example.com"),
            ("verylongname@gmail.com", "ve********@gmail.com"),
        ]
        
        for original, expected in test_cases:
            with self.subTest(email=original):
                result = view._mask_email(original)
                self.assertEqual(result, expected)

    def test_email_masking_no_at_symbol(self):
        """이메일에 @ 기호가 없는 경우"""
        from users.views.account import FindAccountAPIView
        
        view = FindAccountAPIView()
        result = view._mask_email("invalidemail")
        self.assertEqual(result, "invalidemail")


class ChangePasswordTest(APITestCase):

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
