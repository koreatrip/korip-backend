from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from categories.models import Category, CategoryTranslation, SubCategory, SubCategoryTranslation


class CategoryAPITest(APITestCase):

    def setUp(self):
        self.nature_category = Category.objects.create()
        self.food_category = Category.objects.create()

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

        self.park_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )
        self.valley_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )
        self.korean_food_subcategory = SubCategory.objects.create(
            category=self.food_category
        )

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

    def test_get_categories_with_korean_language(self):
        url = "/api/categories/?lang=ko"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("categories", response.data)
        categories = response.data["categories"]

        self.assertEqual(len(categories), 2)

        nature_category = categories[0]
        self.assertEqual(nature_category["id"], self.nature_category.id)
        self.assertEqual(nature_category["name"], "자연")

        self.assertNotIn("subcategories", nature_category)

        food_category = categories[1]
        self.assertEqual(food_category["id"], self.food_category.id)
        self.assertEqual(food_category["name"], "음식")
        self.assertNotIn("subcategories", food_category)

    def test_get_categories_with_english_language(self):
        url = "/api/categories/?lang=en"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data["categories"]

        nature_category = categories[0]
        self.assertEqual(nature_category["name"], "Nature")

        self.assertNotIn("subcategories", nature_category)

    def test_get_categories_without_language_parameter(self):
        url = "/api/categories/"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data["categories"]
        nature_category = categories[0]

        self.assertEqual(nature_category["name"], "자연")

        expected_fields = {"id", "name"}
        actual_fields = set(nature_category.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_get_categories_with_unsupported_language(self):
        url = "/api/categories/?lang=fr"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        categories = response.data["categories"]
        nature_category = categories[0]

        self.assertEqual(nature_category["name"], "자연")

    def test_categories_response_structure(self):
        url = "/api/categories/?lang=ko"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_structure = {
            "categories": [
                {"id": self.nature_category.id, "name": "자연"},
                {"id": self.food_category.id, "name": "음식"}
            ]
        }

        self.assertEqual(response.data, expected_structure)


class SubCategoryAPITest(APITestCase):

    def setUp(self):
        self.nature_category = Category.objects.create()
        self.food_category = Category.objects.create()

        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="ko",
            name="자연"
        )

        self.park_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )
        self.valley_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )

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

    def test_get_subcategories_with_english_language(self):
        url = f"/api/categories/{self.nature_category.id}/subcategories/?lang=en"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subcategories = response.data["subcategories"]
        subcategory_names = [sub["name"] for sub in subcategories]
        self.assertIn("Park", subcategory_names)
        self.assertIn("Valley", subcategory_names)

    def test_get_subcategories_with_invalid_category_id(self):
        url = "/api/categories/9999/subcategories/?lang=ko"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_get_subcategories_for_category_without_subcategories(self):
        url = f"/api/categories/{self.food_category.id}/subcategories/?lang=ko"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subcategories = response.data["subcategories"]
        self.assertEqual(len(subcategories), 0)

    def test_subcategories_response_structure(self):
        url = f"/api/categories/{self.nature_category.id}/subcategories/?lang=ko"
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_structure = {
            "subcategories": [
                {"id": self.park_subcategory.id, "name": "공원"},
                {"id": self.valley_subcategory.id, "name": "계곡"}
            ]
        }

        self.assertEqual(response.data, expected_structure)
