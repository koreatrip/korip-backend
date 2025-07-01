from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from categories.models import Category, CategoryTranslation, SubCategory, SubCategoryTranslation


class CategoryAPITest(APITestCase):
    """카테고리 API 테스트 (새로운 번역 구조)"""

    def setUp(self):
        """테스트용 데이터 준비"""
        # 카테고리 생성
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

    def test_get_categories_with_korean_language(self):
        """한국어로 카테고리 목록 조회 테스트"""
        url = "/api/categories/?lang=ko"
        response = self.client.get(url)

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

        # 서브카테고리 포함 확인
        self.assertIn("subcategories", nature_category)
        subcategories = nature_category["subcategories"]
        self.assertEqual(len(subcategories), 2)  # 국립공원, 계곡

        # 서브카테고리 이름도 한국어로 확인
        subcategory_names = [sub["name"] for sub in subcategories]
        self.assertIn("국립공원", subcategory_names)
        self.assertIn("계곡", subcategory_names)

        # 두 번째 카테고리 확인 (음식)
        food_category = categories[1]
        self.assertEqual(food_category["name"], "음식")
        self.assertEqual(len(food_category["subcategories"]), 1)  # 한식
        self.assertEqual(food_category["subcategories"][0]["name"], "한식")

    def test_get_categories_with_english_language(self):
        """영어로 카테고리 목록 조회 테스트"""
        url = "/api/categories/?lang=en"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data["categories"]

        # 영어 이름으로 조회됨 확인
        nature_category = categories[0]
        self.assertEqual(nature_category["name"], "Nature")  # 영어로 조회됨

        # 서브카테고리도 영어로 확인
        subcategory_names = [sub["name"] for sub in nature_category["subcategories"]]
        self.assertIn("National Park", subcategory_names)
        self.assertIn("Valley", subcategory_names)

        # 음식 카테고리도 영어로 확인
        food_category = categories[1]
        self.assertEqual(food_category["name"], "Food")
        self.assertEqual(food_category["subcategories"][0]["name"], "Korean Food")

    def test_get_categories_with_japanese_language(self):
        """일본어로 카테고리 목록 조회 테스트"""
        url = "/api/categories/?lang=jp"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data["categories"]

        # 일본어 번역이 있는 카테고리는 일본어로, 없는 건 None 또는 빈 값
        nature_category = categories[0]
        self.assertEqual(nature_category["name"], "自然")  # 일본어로 조회됨

        # 음식 카테고리는 일본어 번역이 없으므로 None이거나 빈 값
        food_category = categories[1]
        self.assertIsNone(food_category["name"])  # 또는 빈 문자열

    def test_get_categories_without_language_parameter(self):
        """언어 파라미터 없이 조회 시 기본값(한국어) 사용 테스트"""
        url = "/api/categories/"  # lang 파라미터 없음
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data["categories"]

        # 기본값으로 한국어가 사용되어야 함
        nature_category = categories[0]
        self.assertEqual(nature_category["name"], "자연")  # 한국어로 조회됨

    def test_get_categories_with_invalid_language(self):
        """존재하지 않는 언어 코드로 조회 시 기본값(한국어) 사용 테스트"""
        url = "/api/categories/?lang=fr"  # 프랑스어 (지원하지 않는 언어)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data["categories"]

        # 지원하지 않는 언어의 경우 기본값(한국어) 반환
        nature_category = categories[0]
        self.assertEqual(nature_category["name"], "자연")  # 기본값으로 한국어 사용

        food_category = categories[1]
        self.assertEqual(food_category["name"], "음식")  # 기본값으로 한국어 사용


class SubCategoryAPITest(APITestCase):
    """서브카테고리 API 테스트"""

    def setUp(self):
        """테스트용 데이터 준비"""
        # 카테고리 생성
        self.nature_category = Category.objects.create()

        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="ko",
            name="자연"
        )

        # 서브카테고리들 생성
        self.park_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )
        self.valley_subcategory = SubCategory.objects.create(
            category=self.nature_category
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

    def test_get_subcategories_by_category_id(self):
        """특정 카테고리의 서브카테고리 목록 조회 테스트"""
        url = f"/api/categories/{self.nature_category.id}/subcategories/?lang=ko"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 구조 확인
        self.assertIn("subcategories", response.data)
        subcategories = response.data["subcategories"]

        # 서브카테고리 개수 확인
        self.assertEqual(len(subcategories), 2)

        # 서브카테고리 이름 확인 (한국어)
        subcategory_names = [sub["name"] for sub in subcategories]
        self.assertIn("국립공원", subcategory_names)
        self.assertIn("계곡", subcategory_names)

    def test_get_subcategories_with_english_language(self):
        """영어로 서브카테고리 목록 조회 테스트"""
        url = f"/api/categories/{self.nature_category.id}/subcategories/?lang=en"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subcategories = response.data["subcategories"]

        # 영어 번역이 있는 것은 영어로, 없는 것은 None
        park_subcategory = next(sub for sub in subcategories if sub["name"] == "National Park")
        self.assertIsNotNone(park_subcategory)

        valley_subcategory = next(sub for sub in subcategories if sub["name"] is None)
        self.assertIsNotNone(valley_subcategory)  # 계곡은 영어 번역이 없어서 None

    def test_get_subcategories_with_nonexistent_category(self):
        """존재하지 않는 카테고리의 서브카테고리 조회 테스트"""
        url = "/api/categories/9999/subcategories/?lang=ko"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
