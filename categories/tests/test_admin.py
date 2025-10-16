from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from categories.models import (
    Category,
    SubCategory,
    CategoryTranslation,
    SubCategoryTranslation
)
from categories.admin import (
    CategoryAdmin,
    SubCategoryAdmin,
    CategoryTranslationAdmin,
    SubCategoryTranslationAdmin
)

User = get_user_model()


class CategoryAdminTest(TestCase):
    """
    CategoryAdmin을 테스트하는 클래스
    """

    def setUp(self):
        """
        테스트용 데이터 준비
        """
        self.site = AdminSite()
        self.admin = CategoryAdmin(Category, self.site)
        self.superuser = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123"
        )

        self.client = Client()
        self.client.force_login(self.superuser)

        # 테스트용 카테고리 생성
        self.category = Category.objects.create()
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

    def test_list_display(self):
        """
        list_display가 올바르게 설정되었는지 테스트
        """
        expected = ["id", "get_korean_name", "get_english_name", "created_at"]
        self.assertEqual(list(self.admin.list_display), expected)

    def test_list_display_links(self):
        """
        list_display_links가 올바르게 설정되었는지 테스트
        """
        expected = ["id", "get_korean_name"]
        self.assertEqual(list(self.admin.list_display_links), expected)

    def test_search_fields(self):
        """
        search_fields가 올바르게 설정되었는지 테스트
        """
        expected = ["translations__name"]
        self.assertEqual(list(self.admin.search_fields), expected)

    def test_ordering(self):
        """
        ordering이 올바르게 설정되었는지 테스트
        """
        expected = ["id"]
        self.assertEqual(list(self.admin.ordering), expected)

    def test_get_korean_name(self):
        """
        get_korean_name 메서드가 한국어 이름을 반환하는지 테스트
        """
        korean_name = self.admin.get_korean_name(self.category)
        self.assertEqual(korean_name, "자연")

    def test_get_korean_name_without_translation(self):
        """
        한국어 번역이 없을 때 "-"를 반환하는지 테스트
        """
        category_no_ko = Category.objects.create()
        korean_name = self.admin.get_korean_name(category_no_ko)
        self.assertEqual(korean_name, "-")

    def test_get_english_name(self):
        """
        get_english_name 메서드가 영어 이름을 반환하는지 테스트
        """
        english_name = self.admin.get_english_name(self.category)
        self.assertEqual(english_name, "Nature")

    def test_get_english_name_without_translation(self):
        """
        영어 번역이 없을 때 "-"를 반환하는지 테스트
        """
        category_no_en = Category.objects.create()
        english_name = self.admin.get_english_name(category_no_en)
        self.assertEqual(english_name, "-")

    def test_inlines(self):
        """
        CategoryTranslationInline이 설정되어 있는지 테스트
        """
        self.assertEqual(len(self.admin.inlines), 1)
        self.assertEqual(self.admin.inlines[0].model, CategoryTranslation)

    def test_admin_changelist_view(self):
        """
        관리자 목록 페이지가 제대로 로드되는지 테스트
        """
        url = "/admin/categories/category/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "자연")

    def test_admin_search(self):
        """
        관리자 페이지에서 검색이 제대로 작동하는지 테스트
        """
        url = "/admin/categories/category/?q=자연"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "자연")


class SubCategoryAdminTest(TestCase):
    """
    SubCategoryAdmin을 테스트하는 클래스
    """

    def setUp(self):
        """
        테스트용 데이터 준비
        """
        self.site = AdminSite()
        self.admin = SubCategoryAdmin(SubCategory, self.site)

        self.superuser = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123"
        )

        self.client = Client()
        self.client.force_login(self.superuser)

        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="자연"
        )

        self.subcategory = SubCategory.objects.create(
            category=self.category
        )
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

    def test_list_display(self):
        """
        list_display가 올바르게 설정되었는지 테스트
        """
        expected = ["id", "get_korean_name", "get_english_name", "category", "created_at"]
        self.assertEqual(list(self.admin.list_display), expected)

    def test_list_display_links(self):
        """
        list_display_links가 올바르게 설정되었는지 테스트
        """
        expected = ["id", "get_korean_name"]
        self.assertEqual(list(self.admin.list_display_links), expected)

    def test_list_filter(self):
        """
        list_filter가 올바르게 설정되었는지 테스트
        """
        expected = ["category"]
        self.assertEqual(list(self.admin.list_filter), expected)

    def test_search_fields(self):
        """
        search_fields가 올바르게 설정되었는지 테스트
        """
        expected = ["translations__name"]
        self.assertEqual(list(self.admin.search_fields), expected)

    def test_ordering(self):
        """
        ordering이 올바르게 설정되었는지 테스트
        """
        expected = ["category", "id"]
        self.assertEqual(list(self.admin.ordering), expected)

    def test_get_korean_name(self):
        """
        get_korean_name 메서드가 한국어 이름을 반환하는지 테스트
        """
        korean_name = self.admin.get_korean_name(self.subcategory)
        self.assertEqual(korean_name, "산")

    def test_get_korean_name_without_translation(self):
        """
        한국어 번역이 없을 때 "-"를 반환하는지 테스트
        """
        subcategory_no_ko = SubCategory.objects.create(category=self.category)
        korean_name = self.admin.get_korean_name(subcategory_no_ko)
        self.assertEqual(korean_name, "-")

    def test_get_english_name(self):
        """
        get_english_name 메서드가 영어 이름을 반환하는지 테스트
        """
        english_name = self.admin.get_english_name(self.subcategory)
        self.assertEqual(english_name, "Mountain")

    def test_get_english_name_without_translation(self):
        """
        영어 번역이 없을 때 "-"를 반환하는지 테스트
        """
        subcategory_no_en = SubCategory.objects.create(category=self.category)
        english_name = self.admin.get_english_name(subcategory_no_en)
        self.assertEqual(english_name, "-")

    def test_inlines(self):
        """
        SubCategoryTranslationInline이 설정되어 있는지 테스트
        """
        self.assertEqual(len(self.admin.inlines), 1)
        self.assertEqual(self.admin.inlines[0].model, SubCategoryTranslation)

    def test_admin_changelist_view(self):
        """
        관리자 목록 페이지가 제대로 로드되는지 테스트
        """
        url = "/admin/categories/subcategory/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "산")

    def test_admin_filter_by_category(self):
        """
        카테고리별 필터링이 제대로 작동하는지 테스트
        """
        other_category = Category.objects.create()
        other_subcategory = SubCategory.objects.create(
            category=other_category
        )
        SubCategoryTranslation.objects.create(
            sub_category=other_subcategory,
            lang="ko",
            name="호텔"
        )

        url = f"/admin/categories/subcategory/?category__id__exact={self.category.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "산")
        self.assertNotContains(response, "호텔")


class CategoryTranslationAdminTest(TestCase):
    """
    CategoryTranslationAdmin을 테스트하는 클래스
    """

    def setUp(self):
        """
        테스트용 데이터 준비
        """
        self.site = AdminSite()
        self.admin = CategoryTranslationAdmin(CategoryTranslation, self.site)
        self.superuser = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123"
        )

        self.client = Client()
        self.client.force_login(self.superuser)

        self.category = Category.objects.create()
        self.translation = CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="자연"
        )

    def test_list_display(self):
        """
        list_display가 올바르게 설정되었는지 테스트
        """
        expected = ["id", "category", "lang", "name", "created_at"]
        self.assertEqual(list(self.admin.list_display), expected)

    def test_list_filter(self):
        """
        list_filter가 올바르게 설정되었는지 테스트
        """
        expected = ["lang"]
        self.assertEqual(list(self.admin.list_filter), expected)

    def test_search_fields(self):
        """
        search_fields가 올바르게 설정되었는지 테스트
        """
        expected = ["name"]
        self.assertEqual(list(self.admin.search_fields), expected)

    def test_ordering(self):
        """
        ordering이 올바르게 설정되었는지 테스트
        """
        expected = ["category", "lang"]
        self.assertEqual(list(self.admin.ordering), expected)

    def test_admin_changelist_view(self):
        """
        관리자 목록 페이지가 제대로 로드되는지 테스트
        """
        url = "/admin/categories/categorytranslation/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "자연")

    def test_admin_filter_by_language(self):
        """
        언어별 필터링이 제대로 작동하는지 테스트
        """
        CategoryTranslation.objects.create(
            category=self.category,
            lang="en",
            name="Nature"
        )

        url = "/admin/categories/categorytranslation/?lang__exact=ko"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "자연")
        self.assertNotContains(response, "Nature")


class SubCategoryTranslationAdminTest(TestCase):
    """
    SubCategoryTranslationAdmin을 테스트하는 클래스
    """

    def setUp(self):
        """
        테스트용 데이터 준비
        """
        self.site = AdminSite()
        self.admin = SubCategoryTranslationAdmin(SubCategoryTranslation, self.site)
        self.superuser = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123"
        )

        self.client = Client()
        self.client.force_login(self.superuser)

        self.category = Category.objects.create()
        self.subcategory = SubCategory.objects.create(
            category=self.category
        )
        self.translation = SubCategoryTranslation.objects.create(
            sub_category=self.subcategory,
            lang="ko",
            name="산"
        )

    def test_list_display(self):
        """
        list_display가 올바르게 설정되었는지 테스트
        """
        expected = ["id", "sub_category", "lang", "name", "created_at"]
        self.assertEqual(list(self.admin.list_display), expected)

    def test_list_filter(self):
        """
        list_filter가 올바르게 설정되었는지 테스트
        """
        expected = ["lang"]
        self.assertEqual(list(self.admin.list_filter), expected)

    def test_search_fields(self):
        """
        search_fields가 올바르게 설정되었는지 테스트
        """
        expected = ["name"]
        self.assertEqual(list(self.admin.search_fields), expected)

    def test_ordering(self):
        """
        ordering이 올바르게 설정되었는지 테스트
        """
        expected = ["sub_category", "lang"]
        self.assertEqual(list(self.admin.ordering), expected)

    def test_admin_changelist_view(self):
        """
        관리자 목록 페이지가 제대로 로드되는지 테스트
        """
        url = "/admin/categories/subcategorytranslation/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "산")

    def test_admin_filter_by_language(self):
        """
        언어별 필터링이 제대로 작동하는지 테스트
        """
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory,
            lang="en",
            name="Mountain"
        )

        url = "/admin/categories/subcategorytranslation/?lang__exact=ko"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "산")
        self.assertNotContains(response, "Mountain")


class InlineAdminTest(TestCase):
    """
    Inline 설정을 테스트하는 클래스
    """

    def setUp(self):
        """
        테스트용 데이터 준비
        """
        self.site = AdminSite()
        self.category_admin = CategoryAdmin(Category, self.site)
        self.subcategory_admin = SubCategoryAdmin(SubCategory, self.site)

    def test_category_translation_inline_settings(self):
        """
        CategoryTranslationInline의 설정이 올바른지 테스트
        """
        inline = self.category_admin.inlines[0]

        self.assertEqual(inline.model, CategoryTranslation)
        self.assertEqual(inline.extra, 1)
        self.assertEqual(inline.max_num, 4)

    def test_subcategory_translation_inline_settings(self):
        """
        SubCategoryTranslationInline의 설정이 올바른지 테스트
        """
        inline = self.subcategory_admin.inlines[0]

        self.assertEqual(inline.model, SubCategoryTranslation)
        self.assertEqual(inline.extra, 1)
        self.assertEqual(inline.max_num, 4)
