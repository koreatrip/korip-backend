# 카테고리 매핑 테스트

from django.test import TestCase
from places.services.category_mapper import CategoryMapper
from categories.models import Category, SubCategory, CategoryTranslation, SubCategoryTranslation


class CategoryMapperTest(TestCase):
    def setUp(self):
        self.mapper = CategoryMapper()
        self.setup_test_categories()

    def setup_test_categories(self):
        self.culture_category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.culture_category,
            lang="ko",
            name="문화"
        )

        self.museum_subcategory = SubCategory.objects.create(
            category=self.culture_category
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.museum_subcategory,
            lang="ko",
            name="박물관"
        )

        self.history_subcategory = SubCategory.objects.create(
            category=self.culture_category
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.history_subcategory,
            lang="ko",
            name="역사"
        )

        self.food_category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.food_category,
            lang="ko",
            name="음식"
        )

        self.korean_food_subcategory = SubCategory.objects.create(
            category=self.food_category
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.korean_food_subcategory,
            lang="ko",
            name="한식"
        )

        self.nature_category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.nature_category,
            lang="ko",
            name="자연"
        )

        self.mountain_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.mountain_subcategory,
            lang="ko",
            name="산"
        )

        self.sea_subcategory = SubCategory.objects.create(
            category=self.nature_category
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.sea_subcategory,
            lang="ko",
            name="바다"
        )

        self.activity_category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.activity_category,
            lang="ko",
            name="액티비티"
        )

        self.shopping_category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.shopping_category,
            lang="ko",
            name="쇼핑"
        )

    def test_mapper_initialization(self):
        self.assertIn("VE", self.mapper.category_mapping)
        self.assertIn("FD", self.mapper.category_mapping)
        self.assertIn("VN", self.mapper.category_mapping)
        self.assertIn("RS", self.mapper.category_mapping)
        self.assertIn("SH", self.mapper.category_mapping)

        self.assertEqual(self.mapper.category_mapping["VE"], "문화")
        self.assertEqual(self.mapper.category_mapping["FD"], "음식")
        self.assertEqual(self.mapper.category_mapping["VN"], "자연")
        self.assertEqual(self.mapper.category_mapping["RS"], "액티비티")
        self.assertEqual(self.mapper.category_mapping["SH"], "쇼핑")

    def test_category_mapping_success(self):
        test_cases = [
            ("VE", "문화"),
            ("FD", "음식"),
            ("VN", "자연"),
            ("RS", "액티비티"),
            ("SH", "쇼핑"),
            ("EV", "문화"),
        ]

        for code, expected in test_cases:
            with self.subTest(code=code):
                result = self.mapper.map_category(code)
                self.assertEqual(result, expected)

    def test_subcategory_mapping_success(self):
        test_cases = [
            ("VE", "VE07", "문화"),
            ("FD", "FD01", "음식"),
            ("VN", "VN01", "자연"),
            ("RS", "RS03", "액티비티"),
            ("SH", "SH01", "쇼핑"),
        ]

        for lclssystm1, lclssystm2, expected in test_cases:
            with self.subTest(code=f"{lclssystm1}-{lclssystm2}"):
                result = self.mapper.map_category(lclssystm1, lclssystm2)
                self.assertEqual(result, expected)

    def test_detailed_category_mapping_success(self):
        test_cases = [
            ("VE", "VE07", "VE070100", "문화"),
            ("VE", "VE07", "VE070600", "문화"),
            ("FD", "FD01", "FD010100", "음식"),
            ("VN", "VN01", "VN010400", "자연"),
            ("RS", "RS03", "RS030100", "액티비티"),
            ("SH", "SH01", "SH010100", "쇼핑"),
        ]

        for lclssystm1, lclssystm2, lclssystm3, expected in test_cases:
            with self.subTest(code=f"{lclssystm1}-{lclssystm2}-{lclssystm3}"):
                result = self.mapper.map_category(lclssystm1, lclssystm2, lclssystm3)
                self.assertEqual(result, expected)

    def test_detailed_category_priority(self):
        lclssystm1 = "VE"
        lclssystm2 = "VE07"
        lclssystm3 = "VE070100"

        result = self.mapper.map_category(lclssystm1, lclssystm2, lclssystm3)
        self.assertEqual(result, "문화")

    def test_mapping_failure_cases(self):
        test_cases = [
            ("XX", None, None),
            ("XX", "XX01", None),
            ("XX", "XX01", "XX010100"),
            (None, None, None),
            ("", "", ""),
        ]

        for lclssystm1, lclssystm2, lclssystm3 in test_cases:
            with self.subTest(code=f"{lclssystm1}-{lclssystm2}-{lclssystm3}"):
                result = self.mapper.map_category(lclssystm1, lclssystm2, lclssystm3)
                self.assertIsNone(result)

    def test_partial_mapping_success(self):
        result = self.mapper.map_category("XX", "VE07")
        self.assertEqual(result, "문화")

    def test_subcategory_mapping_with_details(self):
        test_cases = [
            ("VE", "VE07", "VE070100", ("문화", "박물관")),
            ("VE", "VE07", "VE070600", ("문화", "미술관")),
            ("FD", "FD01", None, ("음식", "한식")),
            ("VN", "VN01", "VN010400", ("자연", "산")),
            ("RS", "RS03", "RS030100", ("액티비티", "동물원")),
            ("SH", "SH01", "SH010100", ("쇼핑", "전통시장")),
        ]

        for lclssystm1, lclssystm2, lclssystm3, expected in test_cases:
            with self.subTest(code=f"{lclssystm1}-{lclssystm2}-{lclssystm3}"):
                result = self.mapper.map_subcategory(lclssystm1, lclssystm2, lclssystm3)
                self.assertEqual(result, expected)

    def test_subcategory_without_subcategory(self):
        test_cases = [
            ("VE", "VE05", None),
            ("EV", "EV01", None),
            ("C01", None, None),
        ]

        for lclssystm1, lclssystm2, lclssystm3 in test_cases:
            with self.subTest(code=f"{lclssystm1}-{lclssystm2}-{lclssystm3}"):
                result = self.mapper.map_subcategory(lclssystm1, lclssystm2, lclssystm3)
                self.assertEqual(result[0], "문화")
                self.assertIsNone(result[1])

    def test_get_category_ids_success(self):
        category_id, subcategory_id = self.mapper.get_category_ids("문화", "박물관")

        self.assertEqual(category_id, self.culture_category.id)
        self.assertEqual(subcategory_id, self.museum_subcategory.id)

    def test_get_category_ids_main_only(self):
        category_id, subcategory_id = self.mapper.get_category_ids("문화")

        self.assertEqual(category_id, self.culture_category.id)
        self.assertIsNone(subcategory_id)

    def test_get_category_ids_nonexistent(self):
        test_cases = [
            ("존재하지않는카테고리", None),
            ("문화", "존재하지않는서브카테고리"),
            (None, None),
            ("", ""),
        ]

        for category_name, subcategory_name in test_cases:
            with self.subTest(category=category_name, subcategory=subcategory_name):
                category_id, subcategory_id = self.mapper.get_category_ids(category_name, subcategory_name)

                if category_name in ["문화", "음식", "자연", "액티비티", "쇼핑"]:
                    self.assertIsNotNone(category_id)
                else:
                    self.assertIsNone(category_id)

                if subcategory_name in ["박물관", "한식"]:
                    self.assertIsNotNone(subcategory_id)
                else:
                    self.assertIsNone(subcategory_id)

    def test_region_mapping_initialization(self):
        self.assertIn("1", self.mapper.region_mapping)
        self.assertIn("2", self.mapper.region_mapping)
        self.assertIn("6", self.mapper.region_mapping)
        self.assertIn("31", self.mapper.region_mapping)
        self.assertIn("39", self.mapper.region_mapping)

        self.assertEqual(self.mapper.region_mapping["1"]["region_name"], "서울")
        self.assertEqual(self.mapper.region_mapping["2"]["region_name"], "인천")
        self.assertEqual(self.mapper.region_mapping["6"]["region_name"], "부산")
        self.assertEqual(self.mapper.region_mapping["31"]["region_name"], "경기")
        self.assertEqual(self.mapper.region_mapping["39"]["region_name"], "제주")

    def test_region_mapping_success(self):
        test_cases = [
            ("1", "1", ("서울", "종로구")),
            ("6", "9", ("부산", "해운대구")),
            ("31", "28", ("경기", "용인시 처인구")),
            ("39", "1", ("제주", "제주시")),
            ("2", "1", ("인천", "중구")),
        ]

        for areacode, sigungucode, expected in test_cases:
            with self.subTest(area=areacode, sigungu=sigungucode):
                result = self.mapper.map_region(areacode, sigungucode)
                self.assertEqual(result, expected)

    def test_get_region_ids_success(self):
        test_cases = [
            ("서울", "종로구"),
            ("부산", "해운대구"),
            ("경기", "용인시 처인구"),
        ]

        for region_name, subregion_name in test_cases:
            with self.subTest(region=region_name, subregion=subregion_name):
                region_id, subregion_id = self.mapper.get_region_ids(region_name, subregion_name)

    def test_get_region_ids_nonexistent(self):
        test_cases = [
            ("존재하지않는지역", "존재하지않는지역구"),
            (None, None),
            ("", ""),
        ]

        for region_name, subregion_name in test_cases:
            with self.subTest(region=region_name, subregion=subregion_name):
                region_id, subregion_id = self.mapper.get_region_ids(region_name, subregion_name)
                self.assertIsNone(region_id)
                self.assertIsNone(subregion_id)

    def test_tour_api_data_processing_with_region(self):
        sample_data = {
            "contentid": "126508",
            "title": "경복궁",
            "addr1": "서울특별시 종로구 사직로 161",
            "mapx": "126.9769616297",
            "mapy": "37.5788408161",
            "lclsSystm1": "VE",
            "lclsSystm2": "VE01",
            "lclsSystm3": "VE010100",
            "contenttypeid": "12",
            "tel": "02-3700-3900",
            "firstimage": "http://example.com/gyeongbok.jpg",
            "areacode": "1",
            "sigungucode": "1",
        }

        processed = self.mapper.process_tour_api_place(sample_data)

        self.assertEqual(processed["content_id"], "126508")
        self.assertEqual(processed["title"], "경복궁")
        self.assertEqual(processed["category_id"], self.culture_category.id)
        self.assertEqual(processed["sub_category_id"], self.history_subcategory.id)
        self.assertEqual(processed["latitude"], 37.5788408161)
        self.assertEqual(processed["longitude"], 126.9769616297)

    def test_multiple_region_tour_api_data_processing(self):
        test_cases = [
            {
                "data": {
                    "contentid": "100001",
                    "title": "해운대해수욕장",
                    "addr1": "부산광역시 해운대구 우동",
                    "mapx": "129.1599340493",
                    "mapy": "35.1581665783",
                    "lclsSystm1": "VN",
                    "lclsSystm2": "VN01",
                    "lclsSystm3": "VN010800",
                    "areacode": "6",
                    "sigungucode": "9",
                },
                "expected": {
                    "category_id": self.nature_category.id,
                    "sub_category_id": self.sea_subcategory.id,
                    "region_name": "부산",
                    "subregion_name": "해운대구",
                }
            },
            {
                "data": {
                    "contentid": "100002",
                    "title": "에버랜드",
                    "addr1": "경기도 용인시 처인구",
                    "mapx": "127.2035865",
                    "mapy": "37.2943395",
                    "lclsSystm1": "RS",
                    "lclsSystm2": "RS04",
                    "lclsSystm3": "RS040100",
                    "areacode": "31",
                    "sigungucode": "28",
                },
                "expected": {
                    "category_id": self.activity_category.id,
                    "sub_category_id": None,
                    "region_name": "경기",
                    "subregion_name": "용인시 처인구",
                }
            },
            {
                "data": {
                    "contentid": "100003",
                    "title": "한라산",
                    "addr1": "제주특별자치도 제주시",
                    "mapx": "126.5",
                    "mapy": "33.3",
                    "lclsSystm1": "VN",
                    "lclsSystm2": "VN01",
                    "lclsSystm3": "VN010400",
                    "areacode": "39",
                    "sigungucode": "1",
                },
                "expected": {
                    "category_id": self.nature_category.id,
                    "sub_category_id": self.mountain_subcategory.id,
                    "region_name": "제주",
                    "subregion_name": "제주시",
                }
            }
        ]

        for i, test_case in enumerate(test_cases):
            with self.subTest(case=i):
                processed = self.mapper.process_tour_api_place(test_case["data"])
                expected = test_case["expected"]

                self.assertEqual(processed["category_id"], expected["category_id"])
                self.assertEqual(processed["sub_category_id"], expected["sub_category_id"])

    def test_mapping_statistics_with_region(self):
        stats = self.mapper.get_mapping_statistics()

        self.assertIn("region_mappings", stats)
        self.assertIn("supported_regions", stats)
        self.assertEqual(stats["region_mappings"], 5)
        supported_regions = stats["supported_regions"]
        self.assertIn("서울", supported_regions)
        self.assertIn("부산", supported_regions)
        self.assertIn("경기", supported_regions)
        self.assertIn("제주", supported_regions)
        self.assertIn("인천", supported_regions)
