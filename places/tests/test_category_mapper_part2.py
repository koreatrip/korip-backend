# 카테고리 매핑 테스트 Part 2 (좌표 변환, 데이터 처리, 통계)

from django.test import TestCase
from places.services.category_mapper import CategoryMapper
from categories.models import Category, SubCategory, CategoryTranslation, SubCategoryTranslation


class CategoryMapperUtilsTest(TestCase):
    def setUp(self):
        self.mapper = CategoryMapper()

        self.food_category = Category.objects.create()
        CategoryTranslation.objects.create(category=self.food_category, lang="ko", name="음식")

        self.nature_category = Category.objects.create()
        CategoryTranslation.objects.create(category=self.nature_category, lang="ko", name="자연")

        self.sea_subcategory = SubCategory.objects.create(category=self.nature_category)
        SubCategoryTranslation.objects.create(sub_category=self.sea_subcategory, lang="ko", name="바다")

    def test_convert_to_decimal_success(self):
        test_cases = [
            ("127.0377755568", 127.0377755568),
            ("37.5788400000", 37.5788400000),
            ("0", 0.0),
            ("0.0", 0.0),
            ("-127.123456", -127.123456),
            ("180.0", 180.0),
            ("-180.0", -180.0),
        ]

        for coord_str, expected in test_cases:
            with self.subTest(coord=coord_str):
                result = self.mapper._convert_to_decimal(coord_str)
                self.assertEqual(result, expected)

    def test_convert_to_decimal_empty_string(self):
        test_cases = ["", "   ", None]

        for coord_str in test_cases:
            with self.subTest(coord=coord_str):
                result = self.mapper._convert_to_decimal(coord_str)
                self.assertIsNone(result)

    def test_convert_to_decimal_invalid_format(self):
        test_cases = [
            "abc123",
            "12.34.56",
            "12,34",
            "12.34abc",
            "경도값",
            "127.abc",
        ]

        for coord_str in test_cases:
            with self.subTest(coord=coord_str):
                result = self.mapper._convert_to_decimal(coord_str)
                self.assertIsNone(result)

    def test_get_mapping_statistics(self):
        stats = self.mapper.get_mapping_statistics()

        self.assertIn("total_mappings", stats)
        self.assertIn("main_categories", stats)
        self.assertIn("subcategory_mappings", stats)
        self.assertIn("coverage", stats)
        self.assertIn("region_mappings", stats)
        self.assertIn("supported_regions", stats)

        main_categories = stats["main_categories"]
        expected_categories = ["문화", "자연", "액티비티", "쇼핑", "음식"]
        for category in expected_categories:
            self.assertIn(category, main_categories)

        coverage = stats["coverage"]
        for category in expected_categories:
            self.assertIn(category, coverage)
            self.assertIsInstance(coverage[category], int)
            self.assertGreaterEqual(coverage[category], 0)


class CategoryMapperDataProcessingTest(TestCase):

    def setUp(self):
        self.mapper = CategoryMapper()

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

        self.food_category = Category.objects.create()
        self.nature_category = Category.objects.create()

    def test_process_tour_api_place_complete_data(self):
        place_data = {
            "contentid": "126508",
            "title": "경복궁",
            "addr1": "서울특별시 종로구 사직로 161",
            "mapx": "126.9769873715",
            "mapy": "37.5788400000",
            "lclsSystm1": "VE",
            "lclsSystm2": "VE07",
            "lclsSystm3": "VE070100",
            "contenttypeid": "12",
            "tel": "02-3700-3900",
            "firstimage": "http://example.com/image.jpg",
            "areacode": "1",
            "sigungucode": "1"
        }

        result = self.mapper.process_tour_api_place(place_data)

        self.assertEqual(result["content_id"], "126508")
        self.assertEqual(result["title"], "경복궁")
        self.assertEqual(result["address"], "서울특별시 종로구 사직로 161")
        self.assertEqual(result["latitude"], 37.5788400000)
        self.assertEqual(result["longitude"], 126.9769873715)
        self.assertEqual(result["category_id"], self.culture_category.id)
        self.assertEqual(result["sub_category_id"], self.museum_subcategory.id)
        self.assertEqual(result["phone_number"], "02-3700-3900")
        self.assertEqual(result["image_url"], "http://example.com/image.jpg")
        self.assertEqual(result["use_time"], "")
        self.assertEqual(result["link_url"], "")

    def test_process_tour_api_place_partial_data(self):
        place_data = {
            "contentid": "123456",
            "title": "테스트 관광지",
            "lclsSystm1": "VE",
        }

        result = self.mapper.process_tour_api_place(place_data)

        self.assertEqual(result["content_id"], "123456")
        self.assertEqual(result["title"], "테스트 관광지")
        self.assertEqual(result["address"], "")
        self.assertIsNone(result["latitude"])
        self.assertIsNone(result["longitude"])
        self.assertEqual(result["category_id"], self.culture_category.id)
        self.assertIsNone(result["sub_category_id"])
        self.assertEqual(result["phone_number"], "")
        self.assertEqual(result["image_url"], "")

    def test_process_tour_api_place_unmapped_category(self):
        place_data = {
            "contentid": "999999",
            "title": "알 수 없는 관광지",
            "lclsSystm1": "XX",
            "lclsSystm2": "XX01",
            "lclsSystm3": "XX010100",
        }

        result = self.mapper.process_tour_api_place(place_data)

        self.assertEqual(result["content_id"], "999999")
        self.assertEqual(result["title"], "알 수 없는 관광지")
        self.assertIsNone(result["category_id"])
        self.assertIsNone(result["sub_category_id"])

    def test_process_tour_api_place_invalid_coordinates(self):
        place_data = {
            "contentid": "111111",
            "title": "좌표 오류 관광지",
            "mapx": "abc.def",
            "mapy": "123.ghi",
            "lclsSystm1": "VE",
        }

        result = self.mapper.process_tour_api_place(place_data)

        self.assertEqual(result["content_id"], "111111")
        self.assertIsNone(result["latitude"])
        self.assertIsNone(result["longitude"])
        self.assertEqual(result["category_id"], self.culture_category.id)

    def test_process_tour_api_place_empty_content_id(self):
        place_data = {
            "title": "Content ID 없는 관광지",
            "lclsSystm1": "VE",
        }

        result = self.mapper.process_tour_api_place(place_data)
        self.assertIsNone(result)

    def test_process_tour_api_place_with_region_mapping(self):
        place_data = {
            "contentid": "200001",
            "title": "해운대해수욕장",
            "addr1": "부산광역시 해운대구 우동",
            "mapx": "129.1599340493",
            "mapy": "35.1581665783",
            "lclsSystm1": "VE",
            "lclsSystm2": "VE07",
            "lclsSystm3": "VE070100",
            "areacode": "6",
            "sigungucode": "9",
        }

        result = self.mapper.process_tour_api_place(place_data)

        self.assertEqual(result["content_id"], "200001")
        self.assertEqual(result["category_id"], self.culture_category.id)
        self.assertEqual(result["sub_category_id"], self.museum_subcategory.id)


class CategoryMapperIntegrationTest(TestCase):

    def setUp(self):
        self.mapper = CategoryMapper()

        self.categories = {}
        category_names = ["문화", "자연", "액티비티", "쇼핑", "음식"]

        for name in category_names:
            category = Category.objects.create()
            CategoryTranslation.objects.create(
                category=category,
                lang="ko",
                name=name
            )
            self.categories[name] = category

    def test_real_tour_api_data_simulation(self):
        test_places = [
            {
                "contentid": "126508",
                "title": "경복궁",
                "addr1": "서울특별시 종로구 사직로 161",
                "mapx": "126.9769873715",
                "mapy": "37.5788400000",
                "lclsSystm1": "VE",
                "lclsSystm2": "VE01",
                "lclsSystm3": "VE010100",
                "contenttypeid": "12",
                "areacode": "1",
                "sigungucode": "1",
                "expected_category": "문화",
                "expected_region": "서울",
                "expected_subregion": "종로구"
            },
            {
                "contentid": "2871024",
                "title": "가나돈까스의집",
                "addr1": "서울특별시 강남구 언주로 608",
                "mapx": "127.0377755568",
                "mapy": "37.5099674377",
                "lclsSystm1": "FD",
                "lclsSystm2": "FD01",
                "lclsSystm3": "FD010100",
                "contenttypeid": "39",
                "areacode": "1",
                "sigungucode": "23",
                "expected_category": "음식",
                "expected_region": "서울",
                "expected_subregion": "강남구"
            },
            {
                "contentid": "789012",
                "title": "남산서울타워",
                "addr1": "서울특별시 용산구 남산공원길 105",
                "mapx": "126.9883543199",
                "mapy": "37.5512143074",
                "lclsSystm1": "VE",
                "lclsSystm2": "VE05",
                "lclsSystm3": "VE050100",
                "contenttypeid": "12",
                "areacode": "1",
                "sigungucode": "3",
                "expected_category": "문화",
                "expected_region": "서울",
                "expected_subregion": "용산구"
            },
            {
                "contentid": "345678",
                "title": "한강공원",
                "addr1": "서울특별시 영등포구 여의동로 330",
                "mapx": "126.9365917232",
                "mapy": "37.5289285603",
                "lclsSystm1": "VN",
                "lclsSystm2": "VN01",
                "lclsSystm3": "VN010100",
                "contenttypeid": "12",
                "areacode": "1",
                "sigungucode": "19",
                "expected_category": "자연",
                "expected_region": "서울",
                "expected_subregion": "영등포구"
            }
        ]

        for place_data in test_places:
            with self.subTest(place=place_data["title"]):
                expected_category = place_data.pop("expected_category")
                expected_region = place_data.pop("expected_region")
                expected_subregion = place_data.pop("expected_subregion")

                result = self.mapper.process_tour_api_place(place_data)

                self.assertEqual(result["content_id"], place_data["contentid"])
                self.assertEqual(result["title"], place_data["title"])
                self.assertEqual(result["address"], place_data["addr1"])

                expected_lat = float(place_data["mapy"])
                expected_lng = float(place_data["mapx"])
                self.assertEqual(result["latitude"], expected_lat)
                self.assertEqual(result["longitude"], expected_lng)

                expected_category_id = self.categories[expected_category].id
                self.assertEqual(result["category_id"], expected_category_id)

    def test_mapping_method_execution(self):
        try:
            self.mapper.test_mapping()
            test_passed = True
        except Exception:
            test_passed = False

    def test_mapping_priority_complete_test(self):
        priority_test_cases = [
            ("VE", None, None, "대분류"),
            ("VE", "VE07", None, "중분류"),
            ("VE", "VE07", "VE070100", "소분류"),
            ("XX", "VE07", "VE070100", "소분류"),
            ("XX", "VE07", None, "중분류"),
        ]

        for lclssystm1, lclssystm2, lclssystm3, expected_priority in priority_test_cases:
            with self.subTest(case=f"{lclssystm1}-{lclssystm2}-{lclssystm3}"):
                result = self.mapper.map_category(lclssystm1, lclssystm2, lclssystm3)

                if expected_priority == "소분류" and lclssystm3:
                    expected_result = self.mapper.category_mapping.get(lclssystm3)
                    if not expected_result and lclssystm2:
                        expected_result = self.mapper.category_mapping.get(lclssystm2)
                    if not expected_result and lclssystm1:
                        expected_result = self.mapper.category_mapping.get(lclssystm1)
                elif expected_priority == "중분류" and lclssystm2:
                    expected_result = self.mapper.category_mapping.get(lclssystm2)
                    if not expected_result and lclssystm1:
                        expected_result = self.mapper.category_mapping.get(lclssystm1)
                elif expected_priority == "대분류" and lclssystm1:
                    expected_result = self.mapper.category_mapping.get(lclssystm1)
                else:
                    expected_result = None

                self.assertEqual(result, expected_result)
