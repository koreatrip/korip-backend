from django.test import TestCase
from django.db import IntegrityError
from django.contrib.gis.geos import Point
from places.models import Place, PlaceTranslation
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation
from categories.models import Category, CategoryTranslation, SubCategory, SubCategoryTranslation


class PlaceTranslationModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="문화"
        )

        self.sub_category = SubCategory.objects.create(category=self.category)
        SubCategoryTranslation.objects.create(
            sub_category=self.sub_category,
            lang="ko",
            name="궁궐"
        )

        self.region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="서울"
        )

        self.sub_region = SubRegion.objects.create(
            region=self.region,
            favorite_count=0,
            location=Point(126.9780, 37.5665)
        )
        SubRegionTranslation.objects.create(
            sub_region=self.sub_region,
            lang="ko",
            name="종로구"
        )

        self.place = Place.objects.create(
            content_id="test_place_translation",
            category=self.category,
            sub_category=self.sub_category,
            location=Point(126.9780, 37.5665),
            phone_number="02-1234-5678",
            use_time="09:00-18:00",
            region=self.region,
            sub_region=self.sub_region,
            link_url="https://example.com",
            favorite_count=0
        )

    def test_place_translation_creation(self):
        translation = PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁",
            description="조선시대 궁궐",
            address="서울특별시 종로구"
        )

        self.assertEqual(translation.place, self.place)
        self.assertEqual(translation.lang, "ko")
        self.assertEqual(translation.name, "경복궁")
        self.assertEqual(translation.description, "조선시대 궁궐")
        self.assertEqual(translation.address, "서울특별시 종로구")

    def test_place_translation_str_method(self):
        translation = PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Gyeongbokgung Palace"
        )

        str_result = str(translation)
        self.assertEqual(str_result, "Gyeongbokgung Palace (en)")

    def test_place_translation_with_tour_api_content_id(self):
        translation = PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁",
            tour_api_content_id="126508"
        )

        str_result = str(translation)
        self.assertIn("API:126508", str_result)

    def test_place_translation_unique_constraint(self):
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁",
            description="조선 왕조의 법궁"
        )

        with self.assertRaises(IntegrityError):
            PlaceTranslation.objects.create(
                place=self.place,
                lang="ko",
                name="다른 이름",
                description="다른 설명"
            )

    def test_place_translation_optional_fields(self):
        translation = PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Test Place"
        )

        self.assertEqual(translation.name, "Test Place")
        self.assertEqual(translation.description, "")
        self.assertEqual(translation.address, "")

    def test_place_translation_language_choices(self):
        valid_languages = ["ko", "en", "jp", "cn"]

        for lang in valid_languages:
            translation = PlaceTranslation.objects.create(
                place=self.place,
                lang=lang,
                name=f"Test Name {lang}"
            )
            self.assertEqual(translation.lang, lang)

    def test_place_translation_cascade_delete(self):
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁"
        )
        PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Gyeongbokgung Palace"
        )

        self.assertEqual(PlaceTranslation.objects.filter(place=self.place).count(), 2)

        place_id = self.place.id
        self.place.delete()
        self.assertEqual(PlaceTranslation.objects.filter(place_id=place_id).count(), 0)


class PlaceModelTranslationMethodTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="문화"
        )

        self.sub_category = SubCategory.objects.create(category=self.category)
        SubCategoryTranslation.objects.create(
            sub_category=self.sub_category,
            lang="ko",
            name="궁궐"
        )

        self.region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="서울"
        )

        self.sub_region = SubRegion.objects.create(
            region=self.region,
            favorite_count=0,
            location=Point(126.9780, 37.5665)
        )
        SubRegionTranslation.objects.create(
            sub_region=self.sub_region,
            lang="ko",
            name="종로구"
        )

        self.place = Place.objects.create(
            content_id="translation_methods_test",
            category=self.category,
            sub_category=self.sub_category,
            location=Point(126.9780, 37.5665),
            region=self.region,
            sub_region=self.sub_region
        )

        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="덕수궁",
            description="대한제국 황궁",
            address="서울특별시 중구"
        )
        PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Deoksugung Palace",
            description="Imperial palace of Korean Empire",
            address="Jung-gu, Seoul"
        )

    def test_get_name_method(self):
        self.assertEqual(self.place.get_name("ko"), "덕수궁")
        self.assertEqual(self.place.get_name("en"), "Deoksugung Palace")
        self.assertEqual(self.place.get_name("jp"), "")  # 없는 언어는 빈 문자열

    def test_get_description_method(self):
        self.assertEqual(self.place.get_description("ko"), "대한제국 황궁")
        self.assertEqual(self.place.get_description("en"), "Imperial palace of Korean Empire")
        self.assertEqual(self.place.get_description("jp"), "")

    def test_get_address_method(self):
        self.assertEqual(self.place.get_address("ko"), "서울특별시 중구")
        self.assertEqual(self.place.get_address("en"), "Jung-gu, Seoul")
        self.assertEqual(self.place.get_address("jp"), "")

    def test_get_available_languages_method(self):
        available_languages = self.place.get_available_languages()
        self.assertIn("ko", available_languages)
        self.assertIn("en", available_languages)
        self.assertEqual(len(available_languages), 2)

    def test_get_tour_api_content_id_method(self):
        PlaceTranslation.objects.filter(place=self.place, lang="ko").update(
            tour_api_content_id="126518"
        )

        tour_api_id = self.place.get_tour_api_content_id("ko")
        self.assertEqual(tour_api_id, "126518")

        tour_api_id_empty = self.place.get_tour_api_content_id("jp")
        self.assertEqual(tour_api_id_empty, "")

    def test_place_without_translations(self):
        place_no_translation = Place.objects.create(
            content_id="no_translation",
            location=Point(127.0000, 37.0000)
        )

        self.assertEqual(place_no_translation.get_name("ko"), "")
        self.assertEqual(place_no_translation.get_description("ko"), "")
        self.assertEqual(place_no_translation.get_address("ko"), "")
        self.assertEqual(len(place_no_translation.get_available_languages()), 0)

