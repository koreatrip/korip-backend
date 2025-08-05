from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from unittest.mock import Mock, patch
from users.models import CustomUser
from categories.models import Category, SubCategory
from preferences.models import UserPreference

User = get_user_model()


class UserPreferenceModelTest(TestCase):
    """UserPreference 모델 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            nickname='testuser',
            password='testpass123'
        )
        
        # SubCategory Mock 객체 생성 (실제 모델이 없을 경우를 대비)
        test_category = Category.objects.create()
        self.subcategory = SubCategory.objects.create(category=test_category)
    
    def test_create_user_preference(self):
        """사용자 관심사 생성 테스트"""            
        preference = UserPreference.objects.create(
            user=self.user,
            subcategory=self.subcategory
        )
        
        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.subcategory, self.subcategory)
        self.assertIsNotNone(preference.created_at)
    
    def test_str_method(self):
        """__str__ 메서드 테스트"""
        preference = UserPreference.objects.create(
            user=self.user,
            subcategory=self.subcategory
        )
        
        expected = f"{self.user.nickname} - {self.subcategory}"
        self.assertIn(self.user.nickname, str(preference))
    
    def test_meta_options(self):
        """Meta 옵션 테스트"""
        self.assertEqual(UserPreference._meta.db_table, "user_preference")
        self.assertEqual(UserPreference._meta.verbose_name, "사용자 관심사")
        self.assertEqual(UserPreference._meta.verbose_name_plural, "사용자 관심사")
    
    def test_unique_together_constraint(self):
        """unique_together 제약조건 테스트"""           
        # 첫 번째 관심사 생성
        UserPreference.objects.create(
            user=self.user,
            subcategory=self.subcategory
        )
        
        # 같은 사용자, 같은 서브카테고리로 중복 생성 시도
        with self.assertRaises(IntegrityError):
            UserPreference.objects.create(
                user=self.user,
                subcategory=self.subcategory
            )
    
    def test_foreign_key_relationships(self):
        """외래키 관계 테스트"""
        preference = UserPreference.objects.create(
            user=self.user,
            subcategory=self.subcategory
        )
        
        # Related name 테스트
        self.assertIn(preference, self.user.preferences.all())
    
    def test_cascade_delete_user(self):
        """사용자 삭제 시 CASCADE 동작 테스트"""
        preference = UserPreference.objects.create(
            user=self.user,
            subcategory_id=1
        )
        
        preference_id = preference.id
        
        # 사용자 삭제
        self.user.delete()
        
        # 관련 UserPreference도 삭제되었는지 확인
        with self.assertRaises(UserPreference.DoesNotExist):
            UserPreference.objects.get(id=preference_id)
    
    def test_created_at_auto_field(self):
        """created_at 자동 설정 테스트"""
        before_creation = timezone.now()
        preference = UserPreference.objects.create(
            user=self.user,
            subcategory=self.subcategory
        )
        after_creation = timezone.now()
        
        self.assertGreaterEqual(preference.created_at, before_creation)
        self.assertLessEqual(preference.created_at, after_creation)


class UserPreferenceQueryTest(TestCase):
    """UserPreference 쿼리 및 성능 테스트"""
    
    def setUp(self):
        """대량 테스트 데이터 생성"""
        self.users = []
        for i in range(5):
            user = CustomUser.objects.create_user(
                email=f'user{i}@example.com',
                nickname=f'user{i}',
                password='testpass123'
            )
            self.users.append(user)
        
        test_category = Category.objects.create()
        self.subcategory = SubCategory.objects.create(category=test_category)
        self.subcategories = [
            SubCategory.objects.create(category=test_category)
            for _ in range(3)
        ]
    
    def test_bulk_preference_creation(self):
        """대량 관심사 생성 테스트"""
        preferences = []
        for user in self.users:
            for subcategory in self.subcategories:  
                preferences.append(UserPreference(
                    user=user,
                    subcategory=subcategory
                ))
        
        UserPreference.objects.bulk_create(preferences)
        
        # 총 15개의 관심사가 생성되었는지 확인 (5명 * 3개)
        self.assertEqual(UserPreference.objects.count(), 15)
    
    def test_user_preferences_query(self):
        """사용자별 관심사 조회 테스트"""
        # 첫 번째 사용자에게만 관심사 추가
        UserPreference.objects.create(
            user=self.users[0],
            subcategory=self.subcategory
        )
        
        # 사용자별 관심사 조회
        user_prefs = self.users[0].preferences.all()
        self.assertEqual(user_prefs.count(), 1)
        
        # 다른 사용자는 관심사가 없어야 함
        other_user_prefs = self.users[1].preferences.all()
        self.assertEqual(other_user_prefs.count(), 0)
    
    def test_subcategory_user_count(self):
        """서브카테고리별 사용자 수 조회 테스트"""
        # 여러 사용자가 같은 카테고리 선택
        for user in self.users[:3]:  # 처음 3명만
            UserPreference.objects.create(
                user=user,
                subcategory=self.subcategory
            )
        
        # 특정 서브카테고리를 선택한 사용자 수 확인
        user_count = UserPreference.objects.filter(subcategory_id=self.subcategory.id).count()
        self.assertEqual(user_count, 3)
