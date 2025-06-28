from django.test import TestCase
from django.core.exceptions import ValidationError
from places.models import Category, SubCategory
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json


class CategoryModelTest(TestCase):

    def test_category_creation_with_multilingual_fields(self):
        category = Category.objects.create(
            name_ko="음식",
            name_en="Food",
            name_jp="食べ物",
            name_cn="美食"
        )

        self.assertEqual(category.name_ko, "음식")
        self.assertEqual(category.name_en, "Food")
        self.assertEqual(category.name_jp, "食べ物")
        self.assertEqual(category.name_cn, "美食")
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)

    def test_category_str_method_returns_korean_name(self):
        category = Category.objects.create(
            name_ko="자연",
            name_en="Nature",
            name_jp="自然",
            name_cn="自然"
        )

        self.assertEqual(str(category), "자연")

    def test_category_required_fields(self):

        category = Category.objects.create(
            name_ko="음식",
            name_en="Food",
            name_jp="食べ物",
            name_cn="美食"
        )
        self.assertIsNotNone(category.id)

        empty_category = Category.objects.create(
            name_ko="",
            name_en="Food",
            name_jp="食べ物",
            name_cn="美食"
        )
        self.assertEqual(empty_category.name_ko, "")


class SubCategoryModelTest(TestCase):

    def setUp(self):
        self.food_category = Category.objects.create(
            name_ko="음식",
            name_en="Food",
            name_jp="食べ物",
            name_cn="美食"
        )

        self.nature_category = Category.objects.create(
            name_ko="자연",
            name_en="Nature",
            name_jp="自然",
            name_cn="自然"
        )

    def test_subcategory_creation_with_multilingual_fields(self):
        subcategory = SubCategory.objects.create(
            name_ko="한식",
            name_en="Korean Food",
            name_jp="韓国料理",
            name_cn="韩式料理",
            category=self.food_category
        )

        self.assertEqual(subcategory.name_ko, "한식")
        self.assertEqual(subcategory.name_en, "Korean Food")
        self.assertEqual(subcategory.name_jp, "韓国料理")
        self.assertEqual(subcategory.name_cn, "韩式料理")
        self.assertEqual(subcategory.category, self.food_category)

    def test_subcategory_str_method_returns_korean_name(self):
        subcategory = SubCategory.objects.create(
            name_ko="산",
            name_en="Mountain",
            name_jp="山",
            name_cn="山",
            category=self.nature_category
        )

        self.assertEqual(str(subcategory), "산")

    def test_subcategory_foreign_key_relationship(self):
        korean_food = SubCategory.objects.create(
            name_ko="한식",
            name_en="Korean Food",
            name_jp="韓国料理",
            name_cn="韩式料理",
            category=self.food_category
        )

        chinese_food = SubCategory.objects.create(
            name_ko="중식",
            name_en="Chinese Food",
            name_jp="中華料理",
            name_cn="中式料理",
            category=self.food_category
        )

        food_subcategories = self.food_category.subcategories.all()
        self.assertEqual(food_subcategories.count(), 2)
        self.assertIn(korean_food, food_subcategories)
        self.assertIn(chinese_food, food_subcategories)

    def test_subcategory_without_category_should_fail(self):
        with self.assertRaises(Exception):
            SubCategory.objects.create(
                name_ko="한식",
                name_en="Korean Food"
            )


class CategoryAPITest(APITestCase):

    def setUp(self):
        self.food_category = Category.objects.create(
            name_ko="음식",
            name_en="Food",
            name_jp="食べ物",
            name_cn="美食"
        )

        self.nature_category = Category.objects.create(
            name_ko="자연",
            name_en="Nature",
            name_jp="自然",
            name_cn="自然"
        )

        self.korean_food = SubCategory.objects.create(
            name_ko="한식",
            name_en="Korean Food",
            name_jp="韓国料理",
            name_cn="韩式料理",
            category=self.food_category
        )

        self.mountain = SubCategory.objects.create(
            name_ko="산",
            name_en="Mountain",
            name_jp="山",
            name_cn="山",
            category=self.nature_category
        )

    def test_get_themes_default_korean(self):
        url = '/places/themes/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('themes', response.data)

        themes = response.data['themes']
        self.assertEqual(len(themes), 2)

        food_theme = themes[0]
        self.assertEqual(food_theme['name'], '음식')
        self.assertEqual(len(food_theme['subcategories']), 1)
        self.assertEqual(food_theme['subcategories'][0]['name'], '한식')

    def test_get_themes_with_language_parameter(self):
        url = '/places/themes/?lang=en'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        themes = response.data['themes']

        food_theme = themes[0]
        self.assertEqual(food_theme['name'], 'Food')
        self.assertEqual(food_theme['subcategories'][0]['name'], 'Korean Food')

    def test_get_themes_with_japanese_language(self):
        url = '/places/themes/?lang=jp'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        themes = response.data['themes']

        food_theme = themes[0]
        self.assertEqual(food_theme['name'], '食べ物')
        self.assertEqual(food_theme['subcategories'][0]['name'], '韓国料理')

    def test_get_themes_with_chinese_language(self):
        url = '/places/themes/?lang=cn'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        themes = response.data['themes']

        food_theme = themes[0]
        self.assertEqual(food_theme['name'], '美食')
        self.assertEqual(food_theme['subcategories'][0]['name'], '韩式料理')

    def test_get_themes_with_invalid_language_defaults_to_korean(self):
        url = '/places/themes/?lang=invalid'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        themes = response.data['themes']

        food_theme = themes[0]
        self.assertEqual(food_theme['name'], '음식')