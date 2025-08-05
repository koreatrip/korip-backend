from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
from preferences.models import UserPreference
from preferences.services import PreferenceService
from users.models import CustomUser
from categories.models import Category, SubCategory


class PreferenceServiceTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            nickname='tester',
            password='password'
        )
        self.category = Category.objects.create()
        self.subcategories = [
            SubCategory.objects.create(category=self.category) for _ in range(3)
        ]
    
    def test_add_preference_creates_preferences(self):
        """관심사 추가 테스트: 기존 삭제 + 새로 생성"""
        subcategory_ids = [sc.id for sc in self.subcategories[:2]]
        
        result = PreferenceService.add_preference(user_id=self.user.id, subcategory_ids=subcategory_ids)
        
        # 확인 1: 반환값 검증
        self.assertEqual(result['deleted_count'], 0)
        self.assertEqual(result['created_count'], 2)
        self.assertEqual(result['preferences'], subcategory_ids)
        
        # 확인 2: DB에 제대로 반영됐는지
        preferences = UserPreference.objects.filter(user=self.user)
        self.assertEqual(preferences.count(), 2)
        self.assertSetEqual(set(p.subcategory.id for p in preferences), set(subcategory_ids))

    def test_add_preference_deletes_existing(self):
        """기존 관심사가 삭제되는지 테스트"""
        # 기존 관심사 1개 등록
        old_sub = self.subcategories[2]
        UserPreference.objects.create(user=self.user, subcategory=old_sub)

        # 새 관심사로 교체
        new_ids = [self.subcategories[0].id, self.subcategories[1].id]
        result = PreferenceService.add_preference(user_id=self.user.id, subcategory_ids=new_ids)

        # 삭제된 개수 = 1, 새로 생성된 개수 = 2
        self.assertEqual(result['deleted_count'], 1)
        self.assertEqual(UserPreference.objects.filter(user=self.user).count(), 2)



class PreferenceServiceTest(TransactionTestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            nickname='tester',
            password='password'
        )
        self.category = Category.objects.create()
        self.subcategories = [
            SubCategory.objects.create(category=self.category) for _ in range(3)
        ]

    def test_add_preference_rollback_on_error(self):
        """에러 발생 시 트랜잭션 롤백 테스트"""

        # 기존 관심사 1개 등록
        UserPreference.objects.create(user=self.user, subcategory=self.subcategories[0])

        invalid_id = 9999  # 존재하지 않는 subcategory_id

        with self.assertRaises(IntegrityError):
            PreferenceService.add_preference(self.user.id, [invalid_id])

        # ✅ 롤백되어 기존 관심사가 살아있어야 함
        self.assertEqual(UserPreference.objects.filter(user=self.user).count(), 1)
