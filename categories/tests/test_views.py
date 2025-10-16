# tests/test_views.py

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from categories.models import (
    Category,
    SubCategory,
    CategoryTranslation,
    SubCategoryTranslation
)


class CategoriesAPIViewTest(TestCase):
    """
    CategoriesAPIView (대분류 카테고리 목록 조회)를 테스트하는 클래스
    """

    def setUp(self):
        """
        테스트용 데이터와 API 클라이언트 준비
        """
        self.client = APIClient()

        # 테스트용 카테고리 3개 만들기
        # 카테고리 1: 자연
        self.category1 = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category1,
            lang="ko",
            name="자연"
        )
        CategoryTranslation.objects.create(
            category=self.category1,
            lang="en",
            name="Nature"
        )
        CategoryTranslation.objects.create(
            category=self.category1,
            lang="jp",
            name="自然"
        )
        CategoryTranslation.objects.create(
            category=self.category1,
            lang="cn",
            name="自然"
        )

        # 카테고리 2: 문화
        self.category2 = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category2,
            lang="ko",
            name="문화"
        )
        CategoryTranslation.objects.create(
            category=self.category2,
            lang="en",
            name="Culture"
        )

        # 카테고리 3: 음식
        self.category3 = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category3,
            lang="ko",
            name="음식"
        )
        CategoryTranslation.objects.create(
            category=self.category3,
            lang="en",
            name="Food"
        )

        # 여기만 수정! "categories" → "categories-list"
        self.url = reverse("categories-list")

    # 나머지 테스트 메서드들은 그대로...
    def test_get_categories_success(self):
        """
        카테고리 목록 조회가 성공하는지 테스트
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("categories", response.data)
        self.assertEqual(len(response.data["categories"]), 3)

    def test_get_categories_with_korean(self):
        """
        한국어로 카테고리 목록 조회 테스트
        """
        response = self.client.get(self.url, {"lang": "ko"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        category_names = [cat["name"] for cat in response.data["categories"]]
        self.assertIn("자연", category_names)
        self.assertIn("문화", category_names)
        self.assertIn("음식", category_names)

    def test_get_categories_with_english(self):
        """
        영어로 카테고리 목록 조회 테스트
        """
        response = self.client.get(self.url, {"lang": "en"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        category_names = [cat["name"] for cat in response.data["categories"]]
        self.assertIn("Nature", category_names)
        self.assertIn("Culture", category_names)
        self.assertIn("Food", category_names)

    def test_get_categories_with_japanese(self):
        """
        일본어로 카테고리 목록 조회 테스트
        """
        response = self.client.get(self.url, {"lang": "jp"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data["categories"]

        nature_category = next(cat for cat in categories if cat["id"] == self.category1.id)
        self.assertEqual(nature_category["name"], "自然")

        culture_category = next(cat for cat in categories if cat["id"] == self.category2.id)
        self.assertIsNone(culture_category["name"])

    def test_get_categories_without_lang_parameter(self):
        """
        lang 파라미터 없이 요청하면 기본값 "ko"가 적용되는지 테스트
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        category_names = [cat["name"] for cat in response.data["categories"]]
        self.assertIn("자연", category_names)
        self.assertIn("문화", category_names)

    def test_get_categories_with_unsupported_language(self):
        """
        지원하지 않는 언어 코드로 요청하면 기본값 "ko"가 적용되는지 테스트
        """
        response = self.client.get(self.url, {"lang": "fr"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        category_names = [cat["name"] for cat in response.data["categories"]]
        self.assertIn("자연", category_names)

    def test_get_categories_response_structure(self):
        """
        응답 데이터 구조가 올바른지 테스트
        """
        response = self.client.get(self.url)

        self.assertEqual(len(response.data), 1)
        self.assertIn("categories", response.data)

        self.assertIsInstance(response.data["categories"], list)

        for category in response.data["categories"]:
            self.assertIn("id", category)
            self.assertIn("name", category)
            self.assertEqual(len(category), 2)

    def test_get_categories_when_empty(self):
        """
        카테고리가 하나도 없을 때 빈 리스트를 반환하는지 테스트
        """
        Category.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["categories"], [])
        self.assertEqual(len(response.data["categories"]), 0)


class SubCategoriesAPIViewTest(TestCase):
    """
    SubCategoriesAPIView (서브카테고리 목록 조회)를 테스트하는 클래스
    """

    def setUp(self):
        """
        테스트용 데이터 준비
        """
        self.client = APIClient()

        # 부모 카테고리 만들기
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="자연"
        )

        # 서브카테고리 3개 만들기
        # 서브카테고리 1: 산
        self.subcategory1 = SubCategory.objects.create(
            category=self.category
        )
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
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory1,
            lang="jp",
            name="山"
        )

        # 서브카테고리 2: 바다
        self.subcategory2 = SubCategory.objects.create(
            category=self.category
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory2,
            lang="ko",
            name="바다"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory2,
            lang="en",
            name="Sea"
        )

        # 서브카테고리 3: 강
        self.subcategory3 = SubCategory.objects.create(
            category=self.category
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory3,
            lang="ko",
            name="강"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory3,
            lang="en",
            name="River"
        )

        # 여기만 수정! "subcategories" → "subcategories-list"
        self.url = reverse("subcategories-list", kwargs={"category_id": self.category.id})

    # 나머지 테스트 메서드들은 그대로...
    def test_get_subcategories_success(self):
        """
        서브카테고리 목록 조회가 성공하는지 테스트
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("subcategories", response.data)
        self.assertEqual(len(response.data["subcategories"]), 3)

    def test_get_subcategories_with_korean(self):
        """
        한국어로 서브카테고리 목록 조회 테스트
        """
        response = self.client.get(self.url, {"lang": "ko"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subcategory_names = [sub["name"] for sub in response.data["subcategories"]]
        self.assertIn("산", subcategory_names)
        self.assertIn("바다", subcategory_names)
        self.assertIn("강", subcategory_names)

    def test_get_subcategories_with_english(self):
        """
        영어로 서브카테고리 목록 조회 테스트
        """
        response = self.client.get(self.url, {"lang": "en"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subcategory_names = [sub["name"] for sub in response.data["subcategories"]]
        self.assertIn("Mountain", subcategory_names)
        self.assertIn("Sea", subcategory_names)
        self.assertIn("River", subcategory_names)

    def test_get_subcategories_with_japanese(self):
        """
        일본어로 서브카테고리 목록 조회 테스트
        """
        response = self.client.get(self.url, {"lang": "jp"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subcategories = response.data["subcategories"]

        mountain = next(sub for sub in subcategories if sub["id"] == self.subcategory1.id)
        self.assertEqual(mountain["name"], "山")

        sea = next(sub for sub in subcategories if sub["id"] == self.subcategory2.id)
        self.assertIsNone(sea["name"])

    def test_get_subcategories_without_lang_parameter(self):
        """
        lang 파라미터 없이 요청하면 기본값 "ko"가 적용되는지 테스트
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subcategory_names = [sub["name"] for sub in response.data["subcategories"]]
        self.assertIn("산", subcategory_names)
        self.assertIn("바다", subcategory_names)

    def test_get_subcategories_with_unsupported_language(self):
        """
        지원하지 않는 언어 코드로 요청하면 기본값 "ko"가 적용되는지 테스트
        """
        response = self.client.get(self.url, {"lang": "fr"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subcategory_names = [sub["name"] for sub in response.data["subcategories"]]
        self.assertIn("산", subcategory_names)

    def test_get_subcategories_with_invalid_category_id(self):
        """
        존재하지 않는 카테고리 ID로 요청하면 404 에러가 나는지 테스트
        """
        # 여기도 수정!
        invalid_url = reverse("subcategories-list", kwargs={"category_id": 99999})
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "존재하지 않는 카테고리입니다.")

    def test_get_subcategories_response_structure(self):
        """
        응답 데이터 구조가 올바른지 테스트
        """
        response = self.client.get(self.url)

        self.assertEqual(len(response.data), 1)
        self.assertIn("subcategories", response.data)

        self.assertIsInstance(response.data["subcategories"], list)

        for subcategory in response.data["subcategories"]:
            self.assertIn("id", subcategory)
            self.assertIn("name", subcategory)
            self.assertEqual(len(subcategory), 2)

    def test_get_subcategories_when_empty(self):
        """
        서브카테고리가 하나도 없을 때 빈 리스트를 반환하는지 테스트
        """
        empty_category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=empty_category,
            lang="ko",
            name="빈 카테고리"
        )

        # 여기도 수정!
        empty_url = reverse("subcategories-list", kwargs={"category_id": empty_category.id})
        response = self.client.get(empty_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["subcategories"], [])
        self.assertEqual(len(response.data["subcategories"]), 0)

    def test_subcategories_belong_to_correct_category(self):
        """
        반환된 서브카테고리들이 실제로 요청한 카테고리에 속하는지 테스트
        """
        other_category = Category.objects.create()
        other_subcategory = SubCategory.objects.create(
            category=other_category
        )
        SubCategoryTranslation.objects.create(
            sub_category=other_subcategory,
            lang="ko",
            name="다른 서브카테고리"
        )

        response = self.client.get(self.url)

        self.assertEqual(len(response.data["subcategories"]), 3)

        subcategory_ids = [sub["id"] for sub in response.data["subcategories"]]
        self.assertNotIn(other_subcategory.id, subcategory_ids)