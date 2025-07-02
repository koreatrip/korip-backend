from rest_framework.test import APITestCase
from rest_framework import status
import json
from categories.models import Category, CategoryTranslation, SubCategory, SubCategoryTranslation


# 카테고리 생성 API 테스트
class CategoryCreateAPITest(APITestCase):

# 여러 언어 번역과 함께 카테고리 생성 테스트
    def test_create_category_with_multiple_translations(self):
        url = "/api/categories/"
        data = {
            "translations": [
                {"lang": "ko", "name": "액티비티"},
                {"lang": "en", "name": "Activity"},
                {"lang": "jp", "name": "アクティビティ"},
                {"lang": "cn", "name": "活动"}
            ]
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )

        # 응답 성공 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 응답 데이터 확인
        self.assertIn("id", response.data)
        self.assertIn("translations", response.data)

        # 카테고리가 생성되었는지 확인
        category_id = response.data["id"]
        category = Category.objects.get(id=category_id)
        self.assertIsNotNone(category)

        # 번역이 모두 생성되었는지 확인
        translations = CategoryTranslation.objects.filter(category=category)
        self.assertEqual(translations.count(), 4)

        # 각 언어별 번역 확인
        ko_translation = translations.get(lang="ko")
        en_translation = translations.get(lang="en")
        jp_translation = translations.get(lang="jp")
        cn_translation = translations.get(lang="cn")

        self.assertEqual(ko_translation.name, "액티비티")
        self.assertEqual(en_translation.name, "Activity")
        self.assertEqual(jp_translation.name, "アクティビティ")
        self.assertEqual(cn_translation.name, "活动")

        # 헬퍼 메서드로도 확인
        self.assertEqual(category.get_name("ko"), "액티비티")
        self.assertEqual(category.get_name("en"), "Activity")

# 일부 언어 번역만으로 카테고리 생성 테스트
    def test_create_category_with_partial_translations(self):
        url = "/api/categories/"
        data = {
            "translations": [
                {"lang": "ko", "name": "스포츠"},
                {"lang": "en", "name": "Sports"}
                # 일본어, 중국어 번역 없음
            ]
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 번역이 2개만 생성되었는지 확인
        category_id = response.data["id"]
        category = Category.objects.get(id=category_id)
        translations = CategoryTranslation.objects.filter(category=category)
        self.assertEqual(translations.count(), 2)

        # 존재하는 번역 확인
        self.assertEqual(category.get_name("ko"), "스포츠")
        self.assertEqual(category.get_name("en"), "Sports")

        # 존재하지 않는 번역은 None
        self.assertIsNone(category.get_name("jp"))
        self.assertIsNone(category.get_name("cn"))

# 번역 없이 카테고리 생성 시도 테스트
    def test_create_category_without_translations(self):
        url = "/api/categories/"
        data = {
            "translations": []
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )

        # 실패해야 함 (최소 한 개 번역은 필요)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

# 잘못된 데이터로 카테고리 생성 시도 테스트
    def test_create_category_with_invalid_data(self):
        url = "/api/categories/"
        data = {
            "translations": [
                {"lang": "ko", "name": ""},  # 빈 이름
                {"lang": "en"}  # 이름 필드 없음
            ]
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# 서브카테고리 생성 API 테스트
class SubCategoryCreateAPITest(APITestCase):

    def setUp(self):
        self.nature_category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="ko",
            name="자연"
        )

    def test_create_subcategory_with_translations(self):
        url = "/api/categories/subcategories/"
        data = {
            "category_id": self.nature_category.id,
            "translations": [
                {"lang": "ko", "name": "등산"},
                {"lang": "en", "name": "Hiking"},
                {"lang": "jp", "name": "ハイキング"}
            ]
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        subcategory_id = response.data["id"]
        subcategory = SubCategory.objects.get(id=subcategory_id)
        self.assertEqual(subcategory.category, self.nature_category)

        translations = SubCategoryTranslation.objects.filter(sub_category=subcategory)
        self.assertEqual(translations.count(), 3)

        self.assertEqual(subcategory.get_name("ko"), "등산")
        self.assertEqual(subcategory.get_name("en"), "Hiking")
        self.assertEqual(subcategory.get_name("jp"), "ハイキング")

    def test_create_subcategory_with_invalid_category(self):
        url = "/api/categories/subcategories/"
        data = {
            "category_id": 9999,
            "translations": [
                {"lang": "ko", "name": "등산"}
            ]
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

# 카테고리 ID 없이 서브카테고리 생성 시도 테스트
    def test_create_subcategory_without_category_id(self):
        url = "/api/categories/subcategories/"
        data = {
            "translations": [
                {"lang": "ko", "name": "등산"}
            ]
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# 번역 수정 API 테스트
class TranslationUpdateAPITest(APITestCase):

    def setUp(self):
        self.nature_category = Category.objects.create()

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

# 특정 언어 번역만 수정 테스트
    def test_update_specific_language_translation(self):
        url = f"/api/categories/{self.nature_category.id}/translations/ko/"
        data = {
            "name": "자연환경"
        }

        response = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.nature_category.get_name("ko"), "자연환경")

        self.assertEqual(self.nature_category.get_name("en"), "Nature")

# 존재하지 않는 번역 수정 시도 테스트
    def test_update_nonexistent_translation(self):
        url = f"/api/categories/{self.nature_category.id}/translations/fr/"
        data = {
            "name": "Nature"
        }

        response = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# 존재하지 않는 카테고리의 번역 수정 시도 테스트
    def test_update_translation_with_invalid_category(self):
        url = "/api/categories/9999/translations/ko/"
        data = {
            "name": "새로운 이름"
        }

        response = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
