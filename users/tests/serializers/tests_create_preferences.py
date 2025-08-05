from django.test import TestCase
from categories.models import Category, SubCategory
from users.serializers.create_preferences import CreatePreferenceSerializer


class CreatePreferenceSerializerTest(TestCase):
    
    def setUp(self):
        self.serializer_class = CreatePreferenceSerializer
        self.category = Category.objects.create()
        self.subcategory1 = SubCategory.objects.create(id=1, category=self.category)
        self.subcategory2 = SubCategory.objects.create(id=2, category=self.category)
        self.subcategory3 = SubCategory.objects.create(id=3, category=self.category)
    
    def test_valid_preferences(self):
        """유효한 preferences 데이터 테스트"""
        data = {"preferences": [1, 2, 3]}
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['preferences'], [1, 2, 3])
    
    def test_duplicate_preferences_removed(self):
        """중복된 preferences 제거 테스트"""
        data = {"preferences": [1, 2, 2, 3, 1]}
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())
        # 중복이 제거되어야 함
        validated = serializer.validated_data['preferences']
        self.assertEqual(len(validated), 3)
        self.assertIn(1, validated)
        self.assertIn(2, validated)
        self.assertIn(3, validated)
    
    def test_empty_preferences(self):
        """빈 preferences 리스트 테스트"""
        data = {"preferences": []}
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('preferences', serializer.errors)
    
    def test_too_many_preferences(self):
        """10개 이상의 preferences 테스트"""
        # 10개 서브카테고리 생성
        for i in range(4, 15):
            SubCategory.objects.create(id=i, category=self.category)
        
        data = {"preferences": list(range(1, 12))}  # 11개
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('preferences', serializer.errors)
    
    def test_non_existing_subcategory(self):
        """존재하지 않는 서브카테고리 ID 테스트"""
        data = {"preferences": [1, 2, 999]}
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('preferences', serializer.errors)
    
    def test_invalid_preference_values(self):
        """잘못된 타입의 preference 값 테스트"""
        data = {"preferences": [200, 3]}
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('preferences', serializer.errors)
