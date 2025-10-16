from django.test import TestCase
from django.db import IntegrityError
from categories.models import (
    Category,
    SubCategory,
    CategoryTranslation,
    SubCategoryTranslation
)


class CategoryModelTest(TestCase):
    """
    Category 모델을 테스트하는 클래스
    TestCase를 상속받으면 테스트용 데이터베이스를 자동으로 만들어줌
    """

    def setUp(self):
        """
        각 테스트 메서드가 실행되기 전에 자동으로 실행되는 메서드
        테스트에 필요한 기본 데이터를 여기서 만들어 줌
        """
        # 카테고리 하나 만들기
        self.category = Category.objects.create()

        # 카테고리에 한국어 번역 추가
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="자연"
        )

        # 카테고리에 영어 번역 추가
        CategoryTranslation.objects.create(
            category=self.category,
            lang="en",
            name="Nature"
        )

    def test_category_creation(self):
        """
        카테고리가 제대로 생성되는지 테스트
        """
        # 카테고리가 데이터베이스에 저장되었는지 확인
        self.assertIsNotNone(self.category.id)

        # created_at이 자동으로 설정되었는지 확인
        self.assertIsNotNone(self.category.created_at)

        # updated_at이 자동으로 설정되었는지 확인
        self.assertIsNotNone(self.category.updated_at)

    def test_category_str_method(self):
        """
        카테고리의 __str__ 메서드가 제대로 작동하는지 테스트
        한국어 이름을 반환
        """
        # __str__을 호출했을 때 한국어 이름이 나와야 함
        self.assertEqual(str(self.category), "자연")

    def test_category_str_method_without_korean(self):
        """
        한국어 번역이 없을 때 __str__ 메서드 테스트
        "Category {id}" 형식으로 반환
        """
        # 한국어 번역이 없는 새 카테고리 만들기
        category_no_ko = Category.objects.create()

        # __str__을 호출했을 때 "Category {id}" 형식이어야 함
        expected = f"Category {category_no_ko.id}"
        self.assertEqual(str(category_no_ko), expected)

    def test_get_name_korean(self):
        """
        get_name 메서드가 한국어 이름을 제대로 가져오는지 테스트
        """
        name = self.category.get_name("ko")
        self.assertEqual(name, "자연")

    def test_get_name_english(self):
        """
        get_name 메서드가 영어 이름을 제대로 가져오는지 테스트
        """
        name = self.category.get_name("en")
        self.assertEqual(name, "Nature")

    def test_get_name_not_exists(self):
        """
        없는 언어로 get_name을 호출했을 때 None을 반환하는지 테스트
        """
        name = self.category.get_name("jp")
        self.assertIsNone(name)

    def test_category_translation_unique_together(self):
        """
        같은 카테고리에 같은 언어 코드가 중복되지 않는지 테스트
        unique_together 제약조건이 작동하는지 확인
        """
        # 이미 "ko"가 있는데 또 "ko"를 추가하려고 하면 에러가 나야 함
        with self.assertRaises(IntegrityError):
            CategoryTranslation.objects.create(
                category=self.category,
                lang="ko",
                name="중복 자연"
            )


class SubCategoryModelTest(TestCase):
    """
    SubCategory 모델을 테스트하는 클래스
    """

    def setUp(self):
        """
        서브카테고리 테스트를 위한 기본 데이터 세팅
        """
        # 부모 카테고리 만들기
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="자연"
        )

        # 서브카테고리 만들기
        self.subcategory = SubCategory.objects.create(
            category=self.category
        )

        # 서브카테고리에 한국어 번역 추가
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory,
            lang="ko",
            name="산"
        )

        # 서브카테고리에 영어 번역 추가
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory,
            lang="en",
            name="Mountain"
        )

    def test_subcategory_creation(self):
        """
        서브카테고리가 제대로 생성되는지 테스트
        """
        self.assertIsNotNone(self.subcategory.id)
        self.assertIsNotNone(self.subcategory.created_at)
        self.assertIsNotNone(self.subcategory.updated_at)

    def test_subcategory_category_relation(self):
        """
        서브카테고리와 카테고리의 관계가 제대로 설정되었는지 테스트
        """
        # 서브카테고리의 부모 카테고리가 맞는지 확인
        self.assertEqual(self.subcategory.category, self.category)

        # 카테고리에서 서브카테고리를 가져올 수 있는지 확인 (역참조)
        subcategories = self.category.subcategories.all()
        self.assertIn(self.subcategory, subcategories)
        self.assertEqual(subcategories.count(), 1)

    def test_subcategory_str_method(self):
        """
        서브카테고리의 __str__ 메서드가 제대로 작동하는지 테스트
        """
        self.assertEqual(str(self.subcategory), "산")

    def test_subcategory_str_method_without_korean(self):
        """
        한국어 번역이 없을 때 __str__ 메서드 테스트
        """
        subcategory_no_ko = SubCategory.objects.create(
            category=self.category
        )
        expected = f"SubCategory {subcategory_no_ko.id}"
        self.assertEqual(str(subcategory_no_ko), expected)

    def test_subcategory_get_name_korean(self):
        """
        서브카테고리의 get_name 메서드가 한국어 이름을 제대로 가져오는지 테스트
        """
        name = self.subcategory.get_name("ko")
        self.assertEqual(name, "산")

    def test_subcategory_get_name_english(self):
        """
        서브카테고리의 get_name 메서드가 영어 이름을 제대로 가져오는지 테스트
        """
        name = self.subcategory.get_name("en")
        self.assertEqual(name, "Mountain")

    def test_subcategory_get_name_not_exists(self):
        """
        없는 언어로 get_name을 호출했을 때 None을 반환하는지 테스트
        """
        name = self.subcategory.get_name("cn")
        self.assertIsNone(name)

    def test_subcategory_translation_unique_together(self):
        """
        같은 서브카테고리에 같은 언어 코드가 중복되지 않는지 테스트
        """
        with self.assertRaises(IntegrityError):
            SubCategoryTranslation.objects.create(
                sub_category=self.subcategory,
                lang="ko",
                name="중복 산"
            )

    def test_cascade_delete(self):
        """
        카테고리를 삭제하면 서브카테고리도 함께 삭제되는지 테스트
        on_delete=models.CASCADE가 제대로 작동하는지 확인
        """
        category_id = self.category.id
        subcategory_id = self.subcategory.id

        # 카테고리 삭제
        self.category.delete()

        # 서브카테고리도 같이 삭제되었는지 확인
        with self.assertRaises(SubCategory.DoesNotExist):
            SubCategory.objects.get(id=subcategory_id)


class CategoryTranslationModelTest(TestCase):
    """
    CategoryTranslation 모델을 테스트하는 클래스
    """

    def setUp(self):
        """
        번역 테스트를 위한 기본 데이터 세팅
        """
        self.category = Category.objects.create()
        self.translation = CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="문화"
        )

    def test_translation_creation(self):
        """
        번역이 제대로 생성되는지 테스트
        """
        self.assertIsNotNone(self.translation.id)
        self.assertEqual(self.translation.lang, "ko")
        self.assertEqual(self.translation.name, "문화")

    def test_translation_str_method(self):
        """
        번역의 __str__ 메서드가 제대로 작동하는지 테스트
        "{category_id} - {lang}: {name}" 형식이어야 함
        """
        expected = f"{self.category.id} - ko: 문화"
        self.assertEqual(str(self.translation), expected)

    def test_translation_relation(self):
        """
        번역과 카테고리의 관계가 제대로 설정되었는지 테스트
        """
        # 번역에서 카테고리로 접근
        self.assertEqual(self.translation.category, self.category)

        # 카테고리에서 번역으로 접근 (역참조)
        translations = self.category.translations.all()
        self.assertIn(self.translation, translations)


class SubCategoryTranslationModelTest(TestCase):
    """
    SubCategoryTranslation 모델을 테스트하는 클래스
    """

    def setUp(self):
        """
        서브카테고리 번역 테스트를 위한 기본 데이터 세팅
        """
        self.category = Category.objects.create()
        self.subcategory = SubCategory.objects.create(
            category=self.category
        )
        self.translation = SubCategoryTranslation.objects.create(
            sub_category=self.subcategory,
            lang="ko",
            name="해변"
        )

    def test_translation_creation(self):
        """
        서브카테고리 번역이 제대로 생성되는지 테스트
        """
        self.assertIsNotNone(self.translation.id)
        self.assertEqual(self.translation.lang, "ko")
        self.assertEqual(self.translation.name, "해변")

    def test_translation_str_method(self):
        """
        서브카테고리 번역의 __str__ 메서드가 제대로 작동하는지 테스트
        """
        expected = f"{self.subcategory.id} - ko: 해변"
        self.assertEqual(str(self.translation), expected)

    def test_translation_relation(self):
        """
        번역과 서브카테고리의 관계가 제대로 설정되었는지 테스트
        """
        # 번역에서 서브카테고리로 접근
        self.assertEqual(self.translation.sub_category, self.subcategory)

        # 서브카테고리에서 번역으로 접근 (역참조)
        translations = self.subcategory.translations.all()
        self.assertIn(self.translation, translations)