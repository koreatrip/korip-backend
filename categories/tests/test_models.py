from django.test import TestCase
from django.db import IntegrityError
from categories.models import (
    Category, CategoryTranslation,
    SubCategory, SubCategoryTranslation
)


# 카테고리 번역 테스트
class CategoryTranslationTest(TestCase):

    def setUp(self):
        self.nature_category = Category.objects.create()
        self.food_category = Category.objects.create()

    def test_create_category_translation(self):
        translation = CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="ko",
            name="자연"
        )

        self.assertEqual(translation.category, self.nature_category)
        self.assertEqual(translation.lang, "ko")
        self.assertEqual(translation.name, "자연")

    def test_multiple_language_translations(self):
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

        translations = CategoryTranslation.objects.filter(
            category=self.nature_category
        )
        self.assertEqual(translations.count(), 3)

        ko_translation = translations.get(lang="ko")
        en_translation = translations.get(lang="en")
        jp_translation = translations.get(lang="jp")

        self.assertEqual(ko_translation.name, "자연")
        self.assertEqual(en_translation.name, "Nature")
        self.assertEqual(jp_translation.name, "自然")

    def test_unique_category_lang_constraint(self):
        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="ko",
            name="자연"
        )

        with self.assertRaises(IntegrityError):
            CategoryTranslation.objects.create(
                category=self.nature_category,
                lang="ko",
                name="자연2"
            )

    def test_get_category_name_helper_method(self):
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

        ko_name = self.nature_category.get_name("ko")
        en_name = self.nature_category.get_name("en")
        missing_name = self.nature_category.get_name("fr")

        self.assertEqual(ko_name, "자연")
        self.assertEqual(en_name, "Nature")
        self.assertIsNone(missing_name)


# 서브카테고리 번역 테스트
class SubCategoryTranslationTest(TestCase):

    def setUp(self):
        self.nature_category = Category.objects.create()

        self.park_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )
        self.valley_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )

    def test_create_subcategory_translation(self):
        translation = SubCategoryTranslation.objects.create(
            sub_category=self.park_subcategory,
            lang="ko",
            name="국립공원"
        )

        self.assertEqual(translation.sub_category, self.park_subcategory)
        self.assertEqual(translation.lang, "ko")
        self.assertEqual(translation.name, "국립공원")

    def test_subcategory_parent_relationship(self):
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

        subcategories = SubCategory.objects.filter(
            category=self.nature_category
        )
        self.assertEqual(subcategories.count(), 2)

        self.assertEqual(
            self.park_subcategory.category,
            self.nature_category
        )

    def test_get_subcategory_name_helper_method(self):
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

        ko_name = self.park_subcategory.get_name("ko")
        en_name = self.park_subcategory.get_name("en")

        self.assertEqual(ko_name, "국립공원")
        self.assertEqual(en_name, "National Park")


# 카테고리 모델 통합 테스트
class CategoryModelIntegrationTest(TestCase):

    def test_complete_category_structure(self):
        nature_category = Category.objects.create()

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

        park_subcategory = SubCategory.objects.create(
            category=nature_category
        )
        valley_subcategory = SubCategory.objects.create(
            category=nature_category
        )

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

        self.assertEqual(nature_category.get_name("ko"), "자연")
        self.assertEqual(nature_category.get_name("en"), "Nature")

        subcategories = SubCategory.objects.filter(category=nature_category)
        self.assertEqual(subcategories.count(), 2)

        self.assertEqual(park_subcategory.get_name("ko"), "국립공원")
        self.assertEqual(valley_subcategory.get_name("ko"), "계곡")
