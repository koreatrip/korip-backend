from django.test import TestCase
from categories.models import Category, SubCategory, CategoryTranslation, SubCategoryTranslation
from categories.serializers import CategorySerializer, SubCategoryListSerializer


class CategorySerializerTest(TestCase):

    def setUp(self):
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
        CategoryTranslation.objects.create(
            category=self.category,
            lang="jp",
            name="自然"
        )

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
        serializer = CategorySerializer(
            [self.category],
            many=True,
            context={"language": "ko"}
        )

        data = serializer.data
        self.assertEqual(len(data), 1)

        category_data = data[0]
        self.assertEqual(category_data["id"], self.category.id)
        self.assertEqual(category_data["name"], "자연")

        self.assertNotIn("subcategories", category_data)

        expected_fields = {"id", "name"}
        actual_fields = set(category_data.keys())
        self.assertEqual(actual_fields, expected_fields)

    def test_category_serializer_with_english_language(self):
        serializer = CategorySerializer(
            [self.category],
            many=True,
            context={"language": "en"}
        )

        data = serializer.data
        category_data = data[0]

        self.assertEqual(category_data["name"], "Nature")
        self.assertNotIn("subcategories", category_data)

    def test_category_serializer_with_japanese_language(self):
        serializer = CategorySerializer(
            [self.category],
            many=True,
            context={"language": "jp"}
        )

        data = serializer.data
        category_data = data[0]

        self.assertEqual(category_data["name"], "自然")
        self.assertNotIn("subcategories", category_data)

    def test_category_serializer_with_missing_translation(self):
        serializer = CategorySerializer(
            [self.category],
            many=True,
            context={"language": "cn"}
        )

        data = serializer.data
        category_data = data[0]

        self.assertIn(category_data["name"], [None, ""])
        self.assertNotIn("subcategories", category_data)

    def test_category_serializer_default_language(self):
        serializer = CategorySerializer(
            [self.category],
            many=True,
            context={}
        )

        data = serializer.data
        category_data = data[0]

        self.assertEqual(category_data["name"], "자연")
        self.assertNotIn("subcategories", category_data)

    def test_multiple_categories_serialization(self):
        food_category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=food_category,
            lang="ko",
            name="음식"
        )

        categories = [self.category, food_category]
        serializer = CategorySerializer(
            categories,
            many=True,
            context={"language": "ko"}
        )

        data = serializer.data
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]["name"], "자연")
        self.assertNotIn("subcategories", data[0])

        self.assertEqual(data[1]["name"], "음식")
        self.assertNotIn("subcategories", data[1])


class SubCategoryListSerializerTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create()

        self.subcategory1 = SubCategory.objects.create(category=self.category)
        self.subcategory2 = SubCategory.objects.create(category=self.category)

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
            sub_category=self.subcategory2,
            lang="ko",
            name="바다"
        )

    def test_subcategory_list_serializer_korean(self):
        subcategories = SubCategory.objects.filter(category=self.category)

        serializer = SubCategoryListSerializer(
            {},
            context={
                "language": "ko",
                "subcategories_queryset": subcategories
            }
        )

        data = serializer.data
        self.assertIn("subcategories", data)

        subcategories_data = data["subcategories"]
        self.assertEqual(len(subcategories_data), 2)

        names = [sub["name"] for sub in subcategories_data]
        self.assertIn("산", names)
        self.assertIn("바다", names)

        for sub in subcategories_data:
            expected_fields = {"id", "name"}
            actual_fields = set(sub.keys())
            self.assertEqual(actual_fields, expected_fields)

    def test_subcategory_list_serializer_english(self):
        subcategories = SubCategory.objects.filter(category=self.category)

        serializer = SubCategoryListSerializer(
            {},
            context={
                "language": "en",
                "subcategories_queryset": subcategories
            }
        )

        data = serializer.data
        subcategories_data = data["subcategories"]

        mountain_data = next((sub for sub in subcategories_data
                              if sub["name"] == "Mountain"), None)
        self.assertIsNotNone(mountain_data)

        sea_data = next((sub for sub in subcategories_data
                         if sub["id"] == self.subcategory2.id), None)
        self.assertIsNotNone(sea_data)
        self.assertIn(sea_data["name"], [None, ""])

    def test_empty_subcategories_queryset(self):
        empty_queryset = SubCategory.objects.none()

        serializer = SubCategoryListSerializer(
            {},
            context={
                "language": "ko",
                "subcategories_queryset": empty_queryset
            }
        )

        data = serializer.data
        self.assertEqual(data["subcategories"], [])

    def test_subcategory_list_serializer_response_structure(self):
        subcategories = SubCategory.objects.filter(category=self.category)

        serializer = SubCategoryListSerializer(
            {},
            context={
                "language": "ko",
                "subcategories_queryset": subcategories
            }
        )

        data = serializer.data

        self.assertEqual(set(data.keys()), {"subcategories"})

        for sub in data["subcategories"]:
            self.assertEqual(set(sub.keys()), {"id", "name"})

    def test_subcategory_list_serializer_without_queryset(self):
        serializer = SubCategoryListSerializer(
            {},
            context={
                "language": "ko",
                "subcategories_queryset": None
            }
        )

        data = serializer.data
        self.assertEqual(data["subcategories"], [])
