from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.gis.geos import Point
from unittest.mock import patch, Mock
from places.models import Place, PlaceTranslation
from categories.models import Category, CategoryTranslation, SubCategory, SubCategoryTranslation
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class SyncTourApiCommandTest(TestCase):
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

    def _get_mock_api_data(self):
        return [
            {
                "contentid": "126508",
                "title": "경복궁",
                "addr1": "서울특별시 종로구 사직로 161",
                "mapx": "126.9770171326",
                "mapy": "37.5788408279",
                "cat1": "A02",
                "cat2": "A0201",
                "cat3": "A02010100",
                "areacode": "1",
                "sigungucode": "1",
                "tel": "02-3700-3900"
            }
        ]

    def _get_mock_processed_data(self):
        return {
            "content_id": "126508",
            "title": "경복궁",
            "address": "서울특별시 종로구 사직로 161",
            "latitude": "37.5788408279",
            "longitude": "126.9770171326",
            "category_id": self.category.id,
            "sub_category_id": self.sub_category.id,
            "region_name": "서울",
            "subregion_name": "종로구",
            "tel": "02-3700-3900"
        }

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    @patch("places.services.category_mapper.CategoryMapper.process_tour_api_place")
    def test_command_basic_execution(self, mock_process, mock_get_area):
        mock_get_area.return_value = self._get_mock_api_data()
        mock_process.return_value = self._get_mock_processed_data()

        call_command("sync_tour_api", "--limit", "1", "--area-code", "1")

        places = Place.objects.all()
        self.assertEqual(places.count(), 1)

        place = places.first()
        self.assertEqual(place.content_id, "126508")
        self.assertEqual(place.category, self.category)
        self.assertEqual(place.sub_category, self.sub_category)
        self.assertEqual(place.region, self.region)
        self.assertEqual(place.sub_region, self.sub_region)

        translations = PlaceTranslation.objects.filter(place=place)
        self.assertEqual(translations.count(), 1)

        translation = translations.first()
        self.assertEqual(translation.name, "경복궁")
        self.assertEqual(translation.lang, "ko")

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    @patch("places.services.category_mapper.CategoryMapper.process_tour_api_place")
    def test_dry_run_mode(self, mock_process, mock_get_area):
        mock_get_area.return_value = self._get_mock_api_data()
        mock_process.return_value = self._get_mock_processed_data()

        call_command("sync_tour_api", "--limit", "1", "--dry-run")

        self.assertEqual(Place.objects.count(), 0)
        self.assertEqual(PlaceTranslation.objects.count(), 0)

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    @patch("places.services.category_mapper.CategoryMapper.process_tour_api_place")
    def test_force_update_existing_place(self, mock_process, mock_get_area):
        existing_place = Place.objects.create(
            content_id="126508",
            location=Point(126.9770, 37.5788),
            phone_number="old-phone"
        )

        mock_get_area.return_value = self._get_mock_api_data()
        mock_process.return_value = self._get_mock_processed_data()

        call_command("sync_tour_api", "--limit", "1", "--force-update")

        existing_place.refresh_from_db()
        self.assertEqual(existing_place.phone_number, "02-3700-3900")
        self.assertEqual(existing_place.category, self.category)

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    @patch("places.services.category_mapper.CategoryMapper.process_tour_api_place")
    def test_skip_existing_place_without_force_update(self, mock_process, mock_get_area):
        existing_place = Place.objects.create(
            content_id="126508",
            location=Point(126.9770, 37.5788),
            phone_number="old-phone"
        )

        mock_get_area.return_value = self._get_mock_api_data()
        mock_process.return_value = self._get_mock_processed_data()

        call_command("sync_tour_api", "--limit", "1")

        existing_place.refresh_from_db()
        self.assertEqual(existing_place.phone_number, "old-phone")

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    def test_api_returns_empty_data(self, mock_get_area):
        mock_get_area.return_value = []

        call_command("sync_tour_api", "--limit", "1")

        self.assertEqual(Place.objects.count(), 0)

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    def test_api_returns_none(self, mock_get_area):
        mock_get_area.return_value = None

        call_command("sync_tour_api", "--limit", "1")

        self.assertEqual(Place.objects.count(), 0)

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    @patch("places.services.category_mapper.CategoryMapper.process_tour_api_place")
    def test_place_without_region_data(self, mock_process, mock_get_area):
        mock_data = self._get_mock_processed_data()
        mock_data["region_name"] = None
        mock_data["subregion_name"] = None

        mock_get_area.return_value = self._get_mock_api_data()
        mock_process.return_value = mock_data

        call_command("sync_tour_api", "--limit", "1")

        place = Place.objects.first()
        self.assertIsNotNone(place)
        self.assertIsNone(place.region)
        self.assertIsNone(place.sub_region)

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    @patch("places.services.category_mapper.CategoryMapper.process_tour_api_place")
    def test_place_without_category_data(self, mock_process, mock_get_area):
        mock_data = self._get_mock_processed_data()
        mock_data["category_id"] = None
        mock_data["sub_category_id"] = None

        mock_get_area.return_value = self._get_mock_api_data()
        mock_process.return_value = mock_data

        call_command("sync_tour_api", "--limit", "1")

        place = Place.objects.first()
        self.assertIsNotNone(place)
        self.assertIsNone(place.category)
        self.assertIsNone(place.sub_category)

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    @patch("places.services.category_mapper.CategoryMapper.process_tour_api_place")
    def test_place_with_invalid_coordinates(self, mock_process, mock_get_area):
        mock_data = self._get_mock_processed_data()
        mock_data["latitude"] = "invalid"
        mock_data["longitude"] = "invalid"

        mock_get_area.return_value = self._get_mock_api_data()
        mock_process.return_value = mock_data

        call_command("sync_tour_api", "--limit", "1")

        place = Place.objects.first()
        self.assertIsNotNone(place)
        self.assertIsNone(place.location)

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    @patch("places.services.category_mapper.CategoryMapper.process_tour_api_place")
    def test_command_with_area_code_filter(self, mock_process, mock_get_area):
        mock_get_area.return_value = self._get_mock_api_data()
        mock_process.return_value = self._get_mock_processed_data()

        call_command("sync_tour_api", "--area-code", "1", "--limit", "1")

        mock_get_area.assert_called_once_with(
            area_code="1",
            page_no=1,
            num_of_rows=1
        )

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    @patch("places.services.category_mapper.CategoryMapper.process_tour_api_place")
    def test_command_with_page_option(self, mock_process, mock_get_area):
        mock_get_area.return_value = self._get_mock_api_data()
        mock_process.return_value = self._get_mock_processed_data()

        call_command("sync_tour_api", "--page", "2", "--limit", "10")

        mock_get_area.assert_called_once_with(
            area_code=None,
            page_no=2,
            num_of_rows=10
        )

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    @patch("places.services.category_mapper.CategoryMapper.process_tour_api_place")
    def test_command_with_limit_exceeding_maximum(self, mock_process, mock_get_area):
        mock_get_area.return_value = self._get_mock_api_data()
        mock_process.return_value = self._get_mock_processed_data()

        call_command("sync_tour_api", "--limit", "2000")

        mock_get_area.assert_called_once_with(
            area_code=None,
            page_no=1,
            num_of_rows=1000
        )

    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    @patch("places.services.category_mapper.CategoryMapper.process_tour_api_place")
    def test_error_handling_during_processing(self, mock_process, mock_get_area):
        mock_get_area.return_value = self._get_mock_api_data()
        mock_process.side_effect = Exception("Processing error")

        call_command("sync_tour_api", "--limit", "1")

        self.assertEqual(Place.objects.count(), 0)

    def test_filter_stats_option(self):
        try:
            call_command("sync_tour_api", "--filter-stats")
        except Exception:
            pass

    @patch("places.services.tour_api_client.TourAPIClient.test_connection")
    @patch("places.services.tour_api_client.TourAPIClient.get_area_list")
    def test_api_connection_test_failure(self, mock_get_area, mock_test_connection):
        mock_test_connection.return_value = False
        mock_get_area.return_value = []

        call_command("sync_tour_api", "--limit", "1")

        mock_test_connection.assert_called_once_with(from_command=True)

    def test_command_help(self):
        try:
            call_command("sync_tour_api", "--help")
        except SystemExit as e:
            self.assertEqual(e.code, 0)


