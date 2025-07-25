from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from categories.models import Category, CategoryTranslation, SubCategory, SubCategoryTranslation


# 카테고리 API 테스트
class CategoryAPITest(APITestCase):

    def setUp(self):
        self.nature_category = Category.objects.create()
        self.food_category = Category.objects.create()

        # 카테고리 번역 생성
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

        CategoryTranslation.objects.create(
            category=self.food_category,
            lang="ko",
            name="음식"
        )
        CategoryTranslation.objects.create(
            category=self.food_category,
            lang="en",
            name="Food"
        )

        # 서브카테고리 생성
        self.park_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )
        self.valley_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )
        self.korean_food_subcategory = SubCategory.objects.create(
            category=self.food_category
        )

        # 서브카테고리 번역 생성
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

        SubCategoryTranslation.objects.create(
            sub_category=self.valley_subcategory,
            lang="ko",
            name="계곡"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.valley_subcategory,
            lang="en",
            name="Valley"
        )

        SubCategoryTranslation.objects.create(
            sub_category=self.korean_food_subcategory,
            lang="ko",
            name="한식"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.korean_food_subcategory,
            lang="en",
            name="Korean Food"
        )

    # 한국어로 카테고리 목록 조회 테스트
    def test_get_categories_with_korean_language(self):
        url = "/api/categories/?lang=ko"
        response = self.client.get(url, follow=True)

        # 응답 성공 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 구조 확인
        self.assertIn("categories", response.data)
        categories = response.data["categories"]

        # 카테고리 개수 확인
        self.assertEqual(len(categories), 2)

        # 첫 번째 카테고리 확인 (자연)
        nature_category = categories[0]
        self.assertEqual(nature_category["id"], self.nature_category.id)
        self.assertEqual(nature_category["name"], "자연")  # 한국어로 조회됨

        # 서브카테고리 항상 포함 확인
        self.assertIn("subcategories", nature_category)
        subcategories = nature_category["subcategories"]
        self.assertEqual(len(subcategories), 2)

        # 서브카테고리 이름도 한국어로 확인
        subcategory_names = [sub["name"] for sub in subcategories]
        self.assertIn("국립공원", subcategory_names)
        self.assertIn("계곡", subcategory_names)

    # 영어로 카테고리 목록 조회 테스트
    def test_get_categories_with_english_language(self):
        url = "/api/categories/?lang=en"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data["categories"]

        # 영어 이름으로 조회됨
        nature_category = categories[0]
        self.assertEqual(nature_category["name"], "Nature")

        # 서브카테고리도 영어로
        subcategories = nature_category["subcategories"]
        subcategory_names = [sub["name"] for sub in subcategories]
        self.assertIn("National Park", subcategory_names)
        self.assertIn("Valley", subcategory_names)

    # 언어 파라미터 없이 카테고리 목록 조회 테스트
    def test_get_categories_without_language_parameter(self):
        url = "/api/categories/"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data["categories"]
        nature_category = categories[0]

        # 기본값이 한국어여야 함
        self.assertEqual(nature_category["name"], "자연")

    # 지원하지 않는 언어로 조회 테스트
    def test_get_categories_with_unsupported_language(self):
        url = "/api/categories/?lang=fr"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data["categories"]
        nature_category = categories[0]

        # 지원하지 않는 언어면 기본값(한국어)
        self.assertEqual(nature_category["name"], "자연")


# 서브카테고리 API 테스트
class SubCategoryAPITest(APITestCase):

    def setUp(self):
        self.nature_category = Category.objects.create()
        self.food_category = Category.objects.create()

        # 카테고리 번역
        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="ko",
            name="자연"
        )

        # 서브카테고리 생성
        self.park_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )
        self.valley_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )

        # 서브카테고리 번역
        SubCategoryTranslation.objects.create(
            sub_category=self.park_subcategory,
            lang="ko",
            name="공원"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.park_subcategory,
            lang="en",
            name="Park"
        )

        SubCategoryTranslation.objects.create(
            sub_category=self.valley_subcategory,
            lang="ko",
            name="계곡"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.valley_subcategory,
            lang="en",
            name="Valley"
        )

    # 특정 카테고리의 서브카테고리 조회 테스트
    def test_get_subcategories_by_category_id(self):
        url = f"/api/categories/{self.nature_category.id}/subcategories/?lang=ko"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("subcategories", response.data)
        subcategories = response.data["subcategories"]

        self.assertEqual(len(subcategories), 2)

        subcategory_names = [sub["name"] for sub in subcategories]
        self.assertIn("공원", subcategory_names)
        self.assertIn("계곡", subcategory_names)

    # 영어로 서브카테고리 조회 테스트
    def test_get_subcategories_with_english_language(self):
        url = f"/api/categories/{self.nature_category.id}/subcategories/?lang=en"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subcategories = response.data["subcategories"]
        subcategory_names = [sub["name"] for sub in subcategories]
        self.assertIn("Park", subcategory_names)
        self.assertIn("Valley", subcategory_names)

    # 존재하지 않는 카테고리의 서브카테고리 조회 테스트
    def test_get_subcategories_with_invalid_category_id(self):
        url = "/api/categories/9999/subcategories/?lang=ko"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    # 서브카테고리가 없는 카테고리 조회 테스트
    def test_get_subcategories_for_category_without_subcategories(self):
        url = f"/api/categories/{self.food_category.id}/subcategories/?lang=ko"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subcategories = response.data["subcategories"]
        self.assertEqual(len(subcategories), 0)