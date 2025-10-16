from django.test import TestCase
from categories.models import (
    Category,
    SubCategory,
    CategoryTranslation,
    SubCategoryTranslation
)
from categories.serializers import (
    CategorySerializer,
    SubCategorySerializer,
    SubCategoryListSerializer
)


class CategorySerializerTest(TestCase):
    """
    CategorySerializer를 테스트하는 클래스
    """

    def setUp(self):
        """
        테스트용 카테고리와 번역 데이터 만들기
        """
        # 카테고리 생성
        self.category = Category.objects.create()

        # 여러 언어로 번역 추가
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
        CategoryTranslation.objects.create(
            category=self.category,
            lang="cn",
            name="自然"
        )

    def test_serialize_with_korean(self):
        """
        한국어로 시리얼라이즈했을 때 한국어 이름이 나오는지 테스트
        """
        # context에 language를 "ko"로 전달
        serializer = CategorySerializer(
            self.category,
            context={"language": "ko"}
        )

        # 결과 데이터 확인
        data = serializer.data

        # id가 제대로 나오는지
        self.assertEqual(data["id"], self.category.id)
        # name이 한국어로 나오는지
        self.assertEqual(data["name"], "자연")

    def test_serialize_with_english(self):
        """
        영어로 시리얼라이즈했을 때 영어 이름이 나오는지 테스트
        """
        serializer = CategorySerializer(
            self.category,
            context={"language": "en"}
        )

        data = serializer.data
        self.assertEqual(data["id"], self.category.id)
        self.assertEqual(data["name"], "Nature")

    def test_serialize_with_japanese(self):
        """
        일본어로 시리얼라이즈했을 때 일본어 이름이 나오는지 테스트
        """
        serializer = CategorySerializer(
            self.category,
            context={"language": "jp"}
        )

        data = serializer.data
        self.assertEqual(data["name"], "自然")

    def test_serialize_with_chinese(self):
        """
        중국어로 시리얼라이즈했을 때 중국어 이름이 나오는지 테스트
        """
        serializer = CategorySerializer(
            self.category,
            context={"language": "cn"}
        )

        data = serializer.data
        self.assertEqual(data["name"], "自然")

    def test_serialize_with_default_language(self):
        """
        context에 language를 안 넘기면 기본값 "ko"가 적용되는지 테스트
        """
        # context를 빈 딕셔너리로 전달
        serializer = CategorySerializer(
            self.category,
            context={}
        )

        data = serializer.data
        # 기본값이 "ko"니까 한국어 이름이 나와야 함
        self.assertEqual(data["name"], "자연")

    def test_serialize_without_context(self):
        """
        context를 아예 안 넘기면 기본값 "ko"가 적용되는지 테스트
        """
        serializer = CategorySerializer(self.category)

        data = serializer.data
        self.assertEqual(data["name"], "자연")

    def test_serialize_with_non_existing_language(self):
        """
        존재하지 않는 언어로 요청하면 None이 나오는지 테스트
        """
        serializer = CategorySerializer(
            self.category,
            context={"language": "fr"}  # 프랑스어는 없음
        )

        data = serializer.data
        # 없는 언어면 None이 반환됨
        self.assertIsNone(data["name"])

    def test_serialize_data_structure(self):
        """
        시리얼라이즈된 데이터가 우리가 원하는 구조인지 테스트
        """
        serializer = CategorySerializer(
            self.category,
            context={"language": "ko"}
        )

        data = serializer.data

        # 필수 필드가 다 있는지 확인
        self.assertIn("id", data)
        self.assertIn("name", data)

        # 필드가 정확히 2개만 있는지 (id, name만 있어야 함)
        self.assertEqual(len(data), 2)


class SubCategorySerializerTest(TestCase):
    """
    SubCategorySerializer를 테스트하는 클래스
    """

    def setUp(self):
        """
        테스트용 서브카테고리와 번역 데이터 만들기
        """
        # 부모 카테고리 생성
        self.category = Category.objects.create()

        # 서브카테고리 생성
        self.subcategory = SubCategory.objects.create(
            category=self.category
        )

        # 여러 언어로 번역 추가
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
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory,
            lang="jp",
            name="山"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory,
            lang="cn",
            name="山"
        )

    def test_serialize_with_korean(self):
        """
        한국어로 시리얼라이즈했을 때 한국어 이름이 나오는지 테스트
        """
        serializer = SubCategorySerializer(
            self.subcategory,
            context={"language": "ko"}
        )

        data = serializer.data
        self.assertEqual(data["id"], self.subcategory.id)
        self.assertEqual(data["name"], "산")

    def test_serialize_with_english(self):
        """
        영어로 시리얼라이즈했을 때 영어 이름이 나오는지 테스트
        """
        serializer = SubCategorySerializer(
            self.subcategory,
            context={"language": "en"}
        )

        data = serializer.data
        self.assertEqual(data["name"], "Mountain")

    def test_serialize_with_default_language(self):
        """
        context에 language를 안 넘기면 기본값 "ko"가 적용되는지 테스트
        """
        serializer = SubCategorySerializer(
            self.subcategory,
            context={}
        )

        data = serializer.data
        self.assertEqual(data["name"], "산")

    def test_serialize_data_structure(self):
        """
        시리얼라이즈된 데이터 구조 확인
        """
        serializer = SubCategorySerializer(
            self.subcategory,
            context={"language": "ko"}
        )

        data = serializer.data

        # 필수 필드 확인
        self.assertIn("id", data)
        self.assertIn("name", data)

        # 필드가 정확히 2개만 있는지
        self.assertEqual(len(data), 2)


class SubCategoryListSerializerTest(TestCase):
    """
    SubCategoryListSerializer를 테스트하는 클래스
    이 시리얼라이저는 여러 개의 서브카테고리를 리스트로 반환해
    """

    def setUp(self):
        """
        테스트용 카테고리와 여러 서브카테고리 만들기
        """
        # 부모 카테고리 생성
        self.category = Category.objects.create()

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

    def test_serialize_multiple_subcategories_korean(self):
        """
        여러 서브카테고리를 한국어로 시리얼라이즈하는 테스트
        """
        # 모든 서브카테고리 쿼리셋 가져오기
        subcategories_queryset = SubCategory.objects.filter(
            category=self.category
        )

        # 시리얼라이저에 빈 객체와 context 전달
        # SubCategoryListSerializer는 인스턴스 없이 context만 사용해
        serializer = SubCategoryListSerializer(
            {},  # 빈 객체
            context={
                "language": "ko",
                "subcategories_queryset": subcategories_queryset
            }
        )

        data = serializer.data

        # subcategories 키가 있는지 확인
        self.assertIn("subcategories", data)

        # 서브카테고리가 3개 들어있는지 확인
        self.assertEqual(len(data["subcategories"]), 3)

        # 각 서브카테고리의 이름 확인
        names = [sub["name"] for sub in data["subcategories"]]
        self.assertIn("산", names)
        self.assertIn("바다", names)
        self.assertIn("강", names)

    def test_serialize_multiple_subcategories_english(self):
        """
        여러 서브카테고리를 영어로 시리얼라이즈하는 테스트
        """
        subcategories_queryset = SubCategory.objects.filter(
            category=self.category
        )

        serializer = SubCategoryListSerializer(
            {},
            context={
                "language": "en",
                "subcategories_queryset": subcategories_queryset
            }
        )

        data = serializer.data

        # 영어 이름들 확인
        names = [sub["name"] for sub in data["subcategories"]]
        self.assertIn("Mountain", names)
        self.assertIn("Sea", names)
        self.assertIn("River", names)

    def test_serialize_with_empty_queryset(self):
        """
        빈 쿼리셋을 전달했을 때 빈 리스트가 나오는지 테스트
        """
        # 빈 쿼리셋 생성
        empty_queryset = SubCategory.objects.none()

        serializer = SubCategoryListSerializer(
            {},
            context={
                "language": "ko",
                "subcategories_queryset": empty_queryset
            }
        )

        data = serializer.data

        # 빈 리스트가 나와야 함
        self.assertEqual(data["subcategories"], [])
        self.assertEqual(len(data["subcategories"]), 0)

    def test_serialize_without_queryset(self):
        """
        쿼리셋을 context에 안 넘기면 빈 리스트가 나오는지 테스트
        """
        serializer = SubCategoryListSerializer(
            {},
            context={"language": "ko"}
            # subcategories_queryset를 안 넘김
        )

        data = serializer.data

        # 빈 리스트가 나와야 함
        self.assertEqual(data["subcategories"], [])

    def test_serialize_data_structure(self):
        """
        시리얼라이즈된 데이터가 올바른 구조인지 테스트
        """
        subcategories_queryset = SubCategory.objects.filter(
            category=self.category
        )

        serializer = SubCategoryListSerializer(
            {},
            context={
                "language": "ko",
                "subcategories_queryset": subcategories_queryset
            }
        )

        data = serializer.data

        # subcategories 키만 있어야 함
        self.assertEqual(len(data), 1)
        self.assertIn("subcategories", data)

        # subcategories는 리스트여야 함
        self.assertIsInstance(data["subcategories"], list)

        # 각 서브카테고리는 id와 name을 가져야 함
        for subcategory in data["subcategories"]:
            self.assertIn("id", subcategory)
            self.assertIn("name", subcategory)
            self.assertEqual(len(subcategory), 2)

    def test_serialize_with_default_language(self):
        """
        language를 context에 안 넘기면 기본값 "ko"가 적용되는지 테스트
        """
        subcategories_queryset = SubCategory.objects.filter(
            category=self.category
        )

        serializer = SubCategoryListSerializer(
            {},
            context={
                # language를 안 넘김
                "subcategories_queryset": subcategories_queryset
            }
        )

        data = serializer.data

        # 한국어 이름들이 나와야 함
        names = [sub["name"] for sub in data["subcategories"]]
        self.assertIn("산", names)
        self.assertIn("바다", names)
        self.assertIn("강", names)