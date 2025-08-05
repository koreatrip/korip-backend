from django.test import TestCase
from django.contrib.gis.geos import Point
from places.models import Place, PlaceTranslation
from categories.models import Category, CategoryTranslation
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class PlaceModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="문화"
        )

        self.region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="서울"
        )

        self.sub_region = SubRegion.objects.create(
            region=self.region,
            favorite_count=100,
            location=Point(126.9770, 37.5796)
        )
        SubRegionTranslation.objects.create(
            sub_region=self.sub_region,
            lang="ko",
            name="종로구"
        )

    def test_place_creation_with_gis(self):
        place = Place.objects.create(
            content_id="test_001",
            category=self.category,
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9770, 37.5796),
            phone_number="02-1234-5678",
            use_time="09:00~18:00",
            favorite_count=10
        )

        self.assertEqual(place.content_id, "test_001")
        self.assertEqual(place.category, self.category)
        self.assertEqual(place.region, self.region)
        self.assertEqual(place.sub_region, self.sub_region)
        self.assertEqual(place.phone_number, "02-1234-5678")
        self.assertEqual(place.use_time, "09:00~18:00")
        self.assertEqual(place.favorite_count, 10)

        self.assertIsNotNone(place.location)
        self.assertEqual(place.location.x, 126.9770)
        self.assertEqual(place.location.y, 37.5796)

    def test_place_latitude_longitude_properties(self):
        place = Place.objects.create(
            content_id="test_002",
            location=Point(127.0000, 37.0000)
        )

        self.assertEqual(place.latitude, 37.0000)
        self.assertEqual(place.longitude, 127.0000)

    def test_place_with_null_location(self):
        place = Place.objects.create(
            content_id="test_003",
            location=None
        )

        self.assertIsNone(place.location)
        self.assertIsNone(place.latitude)
        self.assertIsNone(place.longitude)

    def test_place_set_coordinates_method(self):
        place = Place.objects.create(content_id="test_004")

        place.set_coordinates(37.5796, 126.9770)

        self.assertIsNotNone(place.location)
        self.assertEqual(place.location.x, 126.9770)
        self.assertEqual(place.location.y, 37.5796)
        self.assertEqual(place.latitude, 37.5796)
        self.assertEqual(place.longitude, 126.9770)

    def test_place_get_coordinates_method(self):
        place = Place.objects.create(
            content_id="test_005",
            location=Point(126.9770, 37.5796)
        )

        coordinates = place.get_coordinates()
        self.assertEqual(coordinates, (37.5796, 126.9770))

        place_no_location = Place.objects.create(
            content_id="test_006",
            location=None
        )
        coordinates_none = place_no_location.get_coordinates()
        self.assertEqual(coordinates_none, (None, None))

    def test_place_str_method(self):
        place = Place.objects.create(
            content_id="test_007",
            location=Point(126.9770, 37.5796)
        )

        str_without_translation = str(place)
        self.assertTrue(
            "test_007" in str_without_translation or f"Place {place.id}" in str_without_translation
        )

        PlaceTranslation.objects.create(
            place=place,
            lang="ko",
            name="테스트 관광지"
        )
        str_with_translation = str(place)
        self.assertIn("테스트 관광지", str_with_translation)

        PlaceTranslation.objects.filter(place=place, lang="ko").update(
            tour_api_content_id="api_test_123"
        )
        place.refresh_from_db()
        str_with_api_id = str(place)
        self.assertIn("테스트 관광지", str_with_api_id)
        self.assertIn("API:api_test_123", str_with_api_id)

    def test_place_region_methods(self):
        place = Place.objects.create(
            content_id="test_008",
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9770, 37.5796)
        )

        self.assertEqual(place.get_region_name("ko"), "서울")
        self.assertEqual(place.get_sub_region_name("ko"), "종로구")

        place_no_region = Place.objects.create(
            content_id="test_009",
            location=Point(126.9770, 37.5796)
        )
        self.assertEqual(place_no_region.get_region_name("ko"), "")
        self.assertEqual(place_no_region.get_sub_region_name("ko"), "")

    def test_place_update_favorite_count(self):
        place = Place.objects.create(
            content_id="test_010",
            location=Point(126.9770, 37.5796),
            favorite_count=5
        )

        try:
            place.update_favorite_count()
        except Exception as e:
            self.fail(f"update_favorite_count 메서드에서 에러 발생: {e}")


class PlaceTranslationModelTest(TestCase):

    def setUp(self):
        self.place = Place.objects.create(
            content_id="translation_test",
            location=Point(126.9770, 37.5796)
        )

    def test_place_translation_creation(self):
        translation = PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="테스트 관광지",
            description="테스트용 관광지입니다",
            address="서울특별시 종로구"
        )

        self.assertEqual(translation.place, self.place)
        self.assertEqual(translation.lang, "ko")
        self.assertEqual(translation.name, "테스트 관광지")
        self.assertEqual(translation.description, "테스트용 관광지입니다")
        self.assertEqual(translation.address, "서울특별시 종로구")

    def test_place_translation_str_method(self):
        translation = PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Test Tourist Spot"
        )

        str_result = str(translation)
        self.assertEqual(str_result, "Test Tourist Spot (en)")

    def test_place_translation_with_tour_api_content_id(self):
        translation = PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="테스트 관광지",
            tour_api_content_id="123456"
        )

        self.assertEqual(translation.tour_api_content_id, "123456")

        str_result = str(translation)
        self.assertIn("API:123456", str_result)

    def test_place_get_translation_methods(self):
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="한국 관광지",
            description="한국어 설명",
            address="서울특별시 종로구"
        )

        PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Korean Tourist Spot",
            description="English description",
            address="Jongno-gu, Seoul"
        )

        self.assertEqual(self.place.get_name("ko"), "한국 관광지")
        self.assertEqual(self.place.get_description("ko"), "한국어 설명")
        self.assertEqual(self.place.get_address("ko"), "서울특별시 종로구")

        self.assertEqual(self.place.get_name("en"), "Korean Tourist Spot")
        self.assertEqual(self.place.get_description("en"), "English description")
        self.assertEqual(self.place.get_address("en"), "Jongno-gu, Seoul")

        self.assertEqual(self.place.get_name("jp"), "")
        self.assertEqual(self.place.get_description("jp"), "")
        self.assertEqual(self.place.get_address("jp"), "")

    def test_place_get_tour_api_content_id_method(self):
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="한국 관광지",
            tour_api_content_id="ko_123456"
        )

        PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Korean Tourist Spot",
            tour_api_content_id="en_789012"
        )

        PlaceTranslation.objects.create(
            place=self.place,
            lang="jp",
            name="テスト観光地",
            tour_api_content_id="translation_test"
        )

        self.assertEqual(self.place.get_tour_api_content_id("ko"), "ko_123456")
        self.assertEqual(self.place.get_tour_api_content_id("en"), "en_789012")
        self.assertEqual(self.place.get_tour_api_content_id("jp"), "translation_test")

    def test_place_translation_utility_methods(self):
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="한국 관광지"
        )
        PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Korean Tourist Spot"
        )

        available_languages = self.place.get_available_languages()
        self.assertIn("ko", available_languages)
        self.assertIn("en", available_languages)
        self.assertEqual(len(available_languages), 2)

        self.assertTrue(self.place.has_translation("ko"))
        self.assertTrue(self.place.has_translation("en"))
        self.assertFalse(self.place.has_translation("jp"))

    def test_place_translation_unique_constraint(self):
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="첫 번째 번역"
        )

        with self.assertRaises(Exception):
            PlaceTranslation.objects.create(
                place=self.place,
                lang="ko",
                name="두 번째 번역"
            )
