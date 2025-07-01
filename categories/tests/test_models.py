from django.test import TestCase
from django.db import IntegrityError
from categories.models import (
    Category, CategoryTranslation,
    SubCategory, SubCategoryTranslation
)


class CategoryTranslationTest(TestCase):
    """카테고리 번역 테스트"""

    def setUp(self):
        """테스트용 데이터 준비"""
        # 카테고리 생성 (이름 정보 없이)
        self.nature_category = Category.objects.create()
        self.food_category = Category.objects.create()

    def test_create_category_translation(self):
        """카테고리 번역 생성 테스트"""
        # 자연 카테고리 한국어 번역 생성
        translation = CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="ko",
            name="자연"
        )

        # 생성된 번역 확인
        self.assertEqual(translation.category, self.nature_category)
        self.assertEqual(translation.lang, "ko")
        self.assertEqual(translation.name, "자연")

    def test_multiple_language_translations(self):
        """여러 언어 번역 테스트"""
        # 한 카테고리에 여러 언어 번역 추가
        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="ko",
            name="자연"
        )
        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="en",
            name="Nature"
        )
        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="jp",
            name="自然"
        )

        # 모든 번역이 제대로 생성되었는지 확인
        translations = CategoryTranslation.objects.filter(
            category=self.nature_category
        )
        self.assertEqual(translations.count(), 3)

        # 각 언어별 번역 확인
        ko_translation = translations.get(lang="ko")
        en_translation = translations.get(lang="en")
        jp_translation = translations.get(lang="jp")

        self.assertEqual(ko_translation.name, "자연")
        self.assertEqual(en_translation.name, "Nature")
        self.assertEqual(jp_translation.name, "自然")

    def test_unique_category_lang_constraint(self):
        """카테고리 + 언어 조합 유일성 테스트"""
        # 첫 번째 번역 생성
        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="ko",
            name="자연"
        )

        # 같은 카테고리, 같은 언어로 중복 번역 시도
        with self.assertRaises(IntegrityError):
            CategoryTranslation.objects.create(
                category=self.nature_category,
                lang="ko",  # 같은 언어
                name="자연2"  # 다른 이름이지만 중복이라 에러 발생해야 함
            )

    def test_get_category_name_helper_method(self):
        """카테고리 이름 조회 헬퍼 메서드 테스트"""
        # 번역 데이터 생성
        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="ko",
            name="자연"
        )
        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="en",
            name="Nature"
        )

        # 헬퍼 메서드로 언어별 이름 조회
        ko_name = self.nature_category.get_name("ko")
        en_name = self.nature_category.get_name("en")
        missing_name = self.nature_category.get_name("fr")  # 없는 언어

        self.assertEqual(ko_name, "자연")
        self.assertEqual(en_name, "Nature")
        self.assertIsNone(missing_name)  # 없는 번역은 None 반환


class SubCategoryTranslationTest(TestCase):
    """서브카테고리 번역 테스트"""

    def setUp(self):
        """테스트용 데이터 준비"""
        # 부모 카테고리 생성
        self.nature_category = Category.objects.create()

        # 서브카테고리 생성
        self.park_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )
        self.valley_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )

    def test_create_subcategory_translation(self):
        """서브카테고리 번역 생성 테스트"""
        translation = SubCategoryTranslation.objects.create(
            sub_category=self.park_subcategory,
            lang="ko",
            name="국립공원"
        )

        self.assertEqual(translation.sub_category, self.park_subcategory)
        self.assertEqual(translation.lang, "ko")
        self.assertEqual(translation.name, "국립공원")

    def test_subcategory_parent_relationship(self):
        """서브카테고리-부모카테고리 관계 테스트"""
        # 서브카테고리 번역 생성
        SubCategoryTranslation.objects.create(
            sub_category=self.park_subcategory,
            lang="ko",
            name="국립공원"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.valley_subcategory,
            lang="ko",
            name="계곡"
        )

        # 부모 카테고리에 속한 서브카테고리들 확인
        subcategories = SubCategory.objects.filter(
            category=self.nature_category
        )
        self.assertEqual(subcategories.count(), 2)

        # 서브카테고리에서 부모 카테고리 접근 확인
        self.assertEqual(
            self.park_subcategory.category,
            self.nature_category
        )

    def test_get_subcategory_name_helper_method(self):
        """서브카테고리 이름 조회 헬퍼 메서드 테스트"""
        # 번역 데이터 생성
        SubCategoryTranslation.objects.create(
            sub_category=self.park_subcategory,
            lang="ko",
            name="국립공원"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.park_subcategory,
            lang="en",
            name="National Park"
        )

        # 헬퍼 메서드로 언어별 이름 조회
        ko_name = self.park_subcategory.get_name("ko")
        en_name = self.park_subcategory.get_name("en")

        self.assertEqual(ko_name, "국립공원")
        self.assertEqual(en_name, "National Park")


class CategoryModelIntegrationTest(TestCase):
    """카테고리 모델 통합 테스트"""

    def test_complete_category_structure(self):
        """전체 카테고리 구조 테스트"""
        # 1. 대분류 생성
        nature_category = Category.objects.create()

        # 2. 대분류 번역 생성
        CategoryTranslation.objects.create(
            category=nature_category,
            lang="ko",
            name="자연"
        )
        CategoryTranslation.objects.create(
            category=nature_category,
            lang="en",
            name="Nature"
        )

        # 3. 소분류 생성
        park_subcategory = SubCategory.objects.create(
            category=nature_category
        )
        valley_subcategory = SubCategory.objects.create(
            category=nature_category
        )

        # 4. 소분류 번역 생성
        SubCategoryTranslation.objects.create(
            sub_category=park_subcategory,
            lang="ko",
            name="국립공원"
        )
        SubCategoryTranslation.objects.create(
            sub_category=valley_subcategory,
            lang="ko",
            name="계곡"
        )

        # 5. 전체 구조 검증
        # 대분류 이름 확인
        self.assertEqual(nature_category.get_name("ko"), "자연")
        self.assertEqual(nature_category.get_name("en"), "Nature")

        # 소분류 개수 확인
        subcategories = SubCategory.objects.filter(category=nature_category)
        self.assertEqual(subcategories.count(), 2)

        # 소분류 이름 확인
        self.assertEqual(park_subcategory.get_name("ko"), "국립공원")
        self.assertEqual(valley_subcategory.get_name("ko"), "계곡")
