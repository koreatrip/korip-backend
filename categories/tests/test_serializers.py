from django.test import TestCase
from categories.models import Category, SubCategory, CategoryTranslation, SubCategoryTranslation
from categories.serializers import (
    CategorySerializer,
    SubCategoryListSerializer,
    CategoryCreateSerializer,
    SubCategoryCreateSerializer
)


class CategorySerializerTest(TestCase):
    """카테고리 시리얼라이저 테스트"""

    def setUp(self):
        """테스트용 데이터 준비"""
        # 카테고리 생성
        self.category = Category.objects.create()

        # 다국어 번역 생성
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="자연"
        )
        CategoryTranslation.objects.create(
            category=self.category,
            lang="en",
            name="Nature"
        )
        CategoryTranslation.objects.create(
            category=self.category,
            lang="jp",
            name="自然"
        )

        # 서브카테고리 생성
        self.subcategory = SubCategory.objects.create(category=self.category)
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory,
            lang="ko",
            name="산"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory,
            lang="en",
            name="Mountain"
        )

    def test_category_serializer_with_korean_language(self):
        """카테고리 시리얼라이저 한국어 테스트"""
        serializer = CategorySerializer(
            [self.category],
            many=True,
            language="ko"
        )

        data = serializer.data
        self.assertEqual(len(data), 1)

        category_data = data[0]
        self.assertEqual(category_data["id"], self.category.id)
        self.assertEqual(category_data["name"], "자연")
        self.assertIn("subcategories", category_data)

        # 서브카테고리 확인
        subcategories = category_data["subcategories"]
        self.assertEqual(len(subcategories), 1)
        self.assertEqual(subcategories[0]["name"], "산")

    def test_category_serializer_with_english_language(self):
        """카테고리 시리얼라이저 영어 테스트"""
        serializer = CategorySerializer(
            [self.category],
            many=True,
            language="en"
        )

        data = serializer.data
        category_data = data[0]

        self.assertEqual(category_data["name"], "Nature")

        # 서브카테고리도 영어로 표시되는지 확인
        subcategories = category_data["subcategories"]
        self.assertEqual(subcategories[0]["name"], "Mountain")

    def test_category_serializer_with_missing_translation(self):
        """번역이 없는 언어로 요청 시 테스트"""
        serializer = CategorySerializer(
            [self.category],
            many=True,
            language="cn"  # 중국어 번역 없음
        )

        data = serializer.data
        category_data = data[0]

        # 번역이 없으면 빈 문자열이나 None 반환
        self.assertIn(category_data["name"], [None, ""])

    def test_category_serializer_with_japanese_language(self):
        """카테고리 시리얼라이저 일본어 테스트"""
        serializer = CategorySerializer(
            [self.category],
            many=True,
            language="jp"
        )

        data = serializer.data
        category_data = data[0]

        self.assertEqual(category_data["name"], "自然")


class CategoryCreateSerializerTest(TestCase):
    """카테고리 생성 시리얼라이저 테스트"""

    def test_valid_create_data(self):
        """유효한 카테고리 생성 데이터 테스트"""
        data = {
            "translations": [
                {"lang": "ko", "name": "액티비티"},
                {"lang": "en", "name": "Activity"},
                {"lang": "jp", "name": "アクティビティ"}
            ]
        }

        serializer = CategoryCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        validated_data = serializer.validated_data
        self.assertIn("translations", validated_data)
        self.assertEqual(len(validated_data["translations"]), 3)

    def test_empty_translations(self):
        """빈 번역 리스트 테스트 (실패해야 함)"""
        data = {
            "translations": []
        }

        serializer = CategoryCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())  # 빈 번역은 실패해야 함
        self.assertIn("translations", serializer.errors)

    def test_invalid_language_code(self):
        """잘못된 언어 코드 테스트"""
        data = {
            "translations": [
                {"lang": "invalid", "name": "테스트"}
            ]
        }

        serializer = CategoryCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("translations", serializer.errors)

    def test_empty_translation_name(self):
        """빈 번역 이름 테스트"""
        data = {
            "translations": [
                {"lang": "ko", "name": ""},
                {"lang": "en", "name": "Valid Name"}
            ]
        }

        serializer = CategoryCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_missing_translation_name(self):
        """번역 이름 필드 누락 테스트"""
        data = {
            "translations": [
                {"lang": "ko"},  # name 필드 없음
                {"lang": "en", "name": "Valid Name"}
            ]
        }

        serializer = CategoryCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_duplicate_language_codes(self):
        """중복 언어 코드 테스트"""
        data = {
            "translations": [
                {"lang": "ko", "name": "첫 번째"},
                {"lang": "ko", "name": "두 번째"},  # 중복
                {"lang": "en", "name": "English"}
            ]
        }

        serializer = CategoryCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class SubCategoryCreateSerializerTest(TestCase):
    """서브카테고리 생성 시리얼라이저 테스트"""

    def setUp(self):
        """테스트용 카테고리 생성"""
        self.category = Category.objects.create()

    def test_valid_subcategory_create_data(self):
        """유효한 서브카테고리 생성 데이터 테스트"""
        data = {
            "category_id": self.category.id,
            "translations": [
                {"lang": "ko", "name": "등산"},
                {"lang": "en", "name": "Hiking"}
            ]
        }

        serializer = SubCategoryCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        validated_data = serializer.validated_data
        self.assertEqual(validated_data["category_id"], self.category.id)
        self.assertEqual(len(validated_data["translations"]), 2)

    def test_missing_category_id(self):
        """카테고리 ID 누락 테스트"""
        data = {
            "translations": [
                {"lang": "ko", "name": "등산"}
            ]
        }

        serializer = SubCategoryCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("category_id", serializer.errors)

    def test_invalid_category_id_type(self):
        """잘못된 카테고리 ID 타입 테스트"""
        data = {
            "category_id": "not_a_number",
            "translations": [
                {"lang": "ko", "name": "등산"}
            ]
        }

        serializer = SubCategoryCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("category_id", serializer.errors)


class SubCategoryListSerializerTest(TestCase):
    """서브카테고리 목록 시리얼라이저 테스트"""

    def setUp(self):
        """테스트용 데이터 준비"""
        # 카테고리 생성
        self.category = Category.objects.create()

        # 서브카테고리들 생성
        self.subcategory1 = SubCategory.objects.create(category=self.category)
        self.subcategory2 = SubCategory.objects.create(category=self.category)

        # 첫 번째 서브카테고리 번역
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory1,
            lang="ko",
            name="산"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory1,
            lang="en",
            name="Mountain"
        )

        # 두 번째 서브카테고리 번역
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory2,
            lang="ko",
            name="바다"
        )

    def test_subcategory_list_serializer_korean(self):
        """서브카테고리 목록 시리얼라이저 한국어 테스트"""
        subcategories = SubCategory.objects.filter(category=self.category)

        serializer = SubCategoryListSerializer(
            {},  # 빈 객체
            language="ko",
            subcategories_queryset=subcategories
        )

        data = serializer.data
        self.assertIn("subcategories", data)

        subcategories_data = data["subcategories"]
        self.assertEqual(len(subcategories_data), 2)

        # 이름 확인
        names = [sub["name"] for sub in subcategories_data]
        self.assertIn("산", names)
        self.assertIn("바다", names)

    def test_subcategory_list_serializer_english(self):
        """서브카테고리 목록 시리얼라이저 영어 테스트"""
        subcategories = SubCategory.objects.filter(category=self.category)

        serializer = SubCategoryListSerializer(
            {},
            language="en",
            subcategories_queryset=subcategories
        )

        data = serializer.data
        subcategories_data = data["subcategories"]

        # 첫 번째 서브카테고리는 영어 번역 있음
        mountain_data = next((sub for sub in subcategories_data
                              if sub["name"] == "Mountain"), None)
        self.assertIsNotNone(mountain_data)

        # 두 번째 서브카테고리는 영어 번역 없음 (None 또는 빈 문자열)
        sea_data = next((sub for sub in subcategories_data
                         if sub["id"] == self.subcategory2.id), None)
        self.assertIsNotNone(sea_data)
        self.assertIn(sea_data["name"], [None, ""])

    def test_empty_subcategories_queryset(self):
        """빈 서브카테고리 쿼리셋 테스트"""
        empty_queryset = SubCategory.objects.none()

        serializer = SubCategoryListSerializer(
            {},
            language="ko",
            subcategories_queryset=empty_queryset
        )

        data = serializer.data
        self.assertEqual(data["subcategories"], [])