from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime

User = get_user_model()


class CustomUserManagerTest(TestCase):
    """CustomUserManager 테스트"""
    
    def test_create_user_success(self):
        """정상적인 유저 생성 테스트"""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            nickname="테스트유저",
            phone_number="010-1234-5678"
        )
        
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.nickname, "테스트유저")
        self.assertEqual(user.phone_number, "010-1234-5678")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_social)
    
    def test_create_user_without_email(self):
        """이메일 없이 유저 생성 시 ValueError 발생"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                email="",
                password="testpass123",
                nickname="테스트유저",
                phone_number="010-1234-5678"
            )
        self.assertEqual(str(context.exception), "이메일은 필수 항목입니다.")
    
    def test_create_user_with_none_email(self):
        """이메일이 None일 때 ValueError 발생"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email=None,
                password="testpass123",
                nickname="테스트유저",
                phone_number="010-1234-5678"
            )
    
    def test_create_user_email_normalization(self):
        """이메일 정규화 테스트"""
        user = User.objects.create_user(
            email="Test@EXAMPLE.COM",
            password="testpass123",
            nickname="테스트유저",
            phone_number="010-1234-5678"
        )
        self.assertEqual(user.email, "Test@example.com")
    
    def test_create_user_with_extra_fields(self):
        """extra_fields 적용 테스트"""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            nickname="테스트유저",
            phone_number="010-1234-5678",
            is_social=True
        )
        self.assertTrue(user.is_social)
    
    def test_create_superuser_success(self):
        """정상적인 슈퍼유저 생성 테스트"""
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
            nickname="관리자",
            phone_number="010-9999-9999"
        )
        
        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_create_superuser_with_is_staff_false(self):
        """is_staff=False로 슈퍼유저 생성 시 ValueError 발생"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                nickname="관리자",
                phone_number="010-9999-9999",
                is_staff=False
            )
        self.assertEqual(str(context.exception), "슈퍼유저는 is_staff=True 이어야 합니다.")
    
    def test_create_superuser_with_is_superuser_false(self):
        """is_superuser=False로 슈퍼유저 생성 시 ValueError 발생"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                nickname="관리자",
                phone_number="010-9999-9999",
                is_superuser=False
            )
        self.assertEqual(str(context.exception), "슈퍼유저는 is_superuser=True 이어야 합니다.")


class CustomUserModelTest(TestCase):
    """CustomUser 모델 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'nickname': '테스트유저',
            'phone_number': '010-1234-5678'
        }
    
    def test_user_creation_with_required_fields(self):
        """필수 필드로 유저 생성 테스트"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.nickname, self.user_data['nickname'])
        self.assertEqual(user.phone_number, self.user_data['phone_number'])
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
    
    def test_user_default_values(self):
        """기본값 설정 확인"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertFalse(user.is_social)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_user_str_method(self):
        """__str__ 메서드 테스트"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])
    
    def test_username_field_is_email(self):
        """USERNAME_FIELD가 이메일인지 확인"""
        self.assertEqual(User.USERNAME_FIELD, 'email')
    
    def test_required_fields_is_empty(self):
        """REQUIRED_FIELDS가 빈 리스트인지 확인"""
        self.assertEqual(User.REQUIRED_FIELDS, [])
    
    def test_password_hashing(self):
        """패스워드 해싱 확인"""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertNotEqual(user.password, self.user_data['password'])
    
    def test_user_inherits_from_abstract_base_user(self):
        """AbstractBaseUser 상속 확인"""
        from django.contrib.auth.models import AbstractBaseUser
        self.assertTrue(issubclass(User, AbstractBaseUser))
    
    def test_user_inherits_from_permissions_mixin(self):
        """PermissionsMixin 상속 확인"""
        from django.contrib.auth.models import PermissionsMixin
        self.assertTrue(issubclass(User, PermissionsMixin))
    
    def test_created_at_auto_now_add(self):
        """created_at 자동 설정 확인"""
        before_creation = timezone.now()
        user = User.objects.create_user(**self.user_data)
        after_creation = timezone.now()
        
        self.assertGreaterEqual(user.created_at, before_creation)
        self.assertLessEqual(user.created_at, after_creation)
    
    def test_updated_at_auto_now(self):
        """updated_at 자동 업데이트 확인"""
        user = User.objects.create_user(**self.user_data)
        original_updated_at = user.updated_at
        
        # 약간의 시간 차이를 두고 업데이트
        import time
        time.sleep(0.01)
        
        user.nickname = "수정된닉네임"
        user.save()
        
        self.assertGreater(user.updated_at, original_updated_at)


class CustomUserDatabaseConstraintTest(TestCase):
    """데이터베이스 제약 조건 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'nickname': '테스트유저',
            'phone_number': '010-1234-5678'
        }
    
    def test_email_unique_constraint(self):
        """이메일 유니크 제약 조건 테스트"""
        # 첫 번째 유저 생성
        User.objects.create_user(**self.user_data)
        
        # 같은 이메일로 두 번째 유저 생성 시도
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email=self.user_data['email'],  # 동일한 이메일
                password='anotherpass123',
                nickname='다른유저',
                phone_number='010-9999-9999'
            )
    
    def test_nickname_max_length_constraint(self):
        """닉네임 최대 길이 제약 조건 테스트"""
        long_nickname = 'a' * 31  # 31자 (max_length=30 초과)
        
        user = User(
            email='test@example.com',
            nickname=long_nickname,
            phone_number='010-1234-5678'
        )
        
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_phone_number_null_constraint(self):
        """전화번호 null 제약 조건 테스트"""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',
                password='testpass123',
                nickname='테스트유저',
                phone_number=None
            )
    
    def test_email_null_constraint(self):
        """이메일 null 제약 조건 테스트 (매니저에서 처리)"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email=None,
                password='testpass123',
                nickname='테스트유저',
                phone_number='010-1234-5678'
            )
    
    def test_nickname_blank_false_constraint(self):
        """닉네임 blank=False 제약 조건 테스트"""
        user = User(
            email='test@example.com',
            nickname='',  # 빈 문자열
            phone_number='010-1234-5678'
        )
        
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_valid_user_creation(self):
        """유효한 데이터로 유저 생성 성공 테스트"""
        user = User.objects.create_user(**self.user_data)
        
        # 생성된 유저가 데이터베이스에 저장되었는지 확인
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())
        self.assertEqual(User.objects.count(), 1)
    
    def test_multiple_users_with_different_emails(self):
        """다른 이메일을 가진 여러 유저 생성 테스트"""
        user1 = User.objects.create_user(
            email='user1@example.com',
            password='pass123',
            nickname='유저1',
            phone_number='010-1111-1111'
        )
        
        user2 = User.objects.create_user(
            email='user2@example.com',
            password='pass123',
            nickname='유저2',
            phone_number='010-2222-2222'
        )
        
        self.assertEqual(User.objects.count(), 2)
        self.assertNotEqual(user1.email, user2.email)