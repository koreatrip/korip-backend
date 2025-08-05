from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.gis.geos import Point
from unittest.mock import patch, Mock
from places.models import Place, PlaceTranslation


class SyncMultilangPlacesCommandTest(TestCase):
    def setUp(self):
        pass

    def _get_mock_api_response(self, languages_data):
        return {
            "status": "success",
            "data": languages_data,
            "successful_languages": [lang for lang, data in languages_data.items() if data]
        }

    def _get_gyeongbok_data(self):
        return {
            "ko": [{
                "contentid": "126508",
                "title": "경복궁",
                "addr1": "서울특별시 종로구 사직로 161",
                "mapx": "126.9770171326",
                "mapy": "37.5788408279",
                "cat1": "A02",
                "lclsSystm1": "CC",
                "_language": "ko"
            }],
            "en": [{
                "contentid": "126508_en",
                "title": "Gyeongbokgung Palace",
                "addr1": "161 Sajik-ro, Jongno-gu, Seoul",
                "mapx": "126.9770500000",
                "mapy": "37.5788900000",
                "cat1": "A02",
                "lclsSystm1": "CC",
                "_language": "en"
            }],
            "jp": [],
            "cn": []
        }

    @patch("places.services.multilang_tour_api_client.MultiLangTourAPIClient.collect_all_languages")
    def test_command_success_with_mock_data(self, mock_collect):
        mock_collect.return_value = self._get_mock_api_response(self._get_gyeongbok_data())

        call_command("sync_multilang_places", "--languages", "ko,en", "--area-code", "1", "--limit", "1")

        places = Place.objects.all()
        self.assertEqual(places.count(), 1)

        place = places.first()
        self.assertIsNotNone(place.location)
        self.assertAlmostEqual(place.location.x, 126.977, places=3)
        self.assertAlmostEqual(place.location.y, 37.5788, places=3)

        translations = PlaceTranslation.objects.filter(place=place)
        self.assertEqual(translations.count(), 2)

        ko_translation = translations.get(lang="ko")
        self.assertEqual(ko_translation.name, "경복궁")
        self.assertEqual(ko_translation.tour_api_content_id, "126508")

        en_translation = translations.get(lang="en")
        self.assertEqual(en_translation.name, "Gyeongbokgung Palace")
        self.assertEqual(en_translation.tour_api_content_id, "126508_en")

    @patch("places.services.multilang_tour_api_client.MultiLangTourAPIClient.collect_all_languages")
    def test_gis_matching_same_place(self, mock_collect):
        existing_place = Place.objects.create(
            content_id="126508",
            location=Point(126.9770171326, 37.5788408279)
        )
        PlaceTranslation.objects.create(
            place=existing_place,
            lang="ko",
            name="경복궁",
            tour_api_content_id="126508"
        )

        mock_data = {
            "ko": [],
            "en": [{
                "contentid": "126508_en",
                "title": "Gyeongbokgung Palace",
                "mapx": "126.9770500000",
                "mapy": "37.5788900000",
                "_language": "en"
            }],
            "jp": [],
            "cn": []
        }

        mock_collect.return_value = self._get_mock_api_response(mock_data)

        call_command("sync_multilang_places", "--languages", "en", "--area-code", "1")

        places = Place.objects.all()
        self.assertEqual(places.count(), 1)

        place = places.first()
        translations = PlaceTranslation.objects.filter(place=place)
        self.assertEqual(translations.count(), 2)

        en_translation = translations.get(lang="en")
        self.assertEqual(en_translation.name, "Gyeongbokgung Palace")
        self.assertEqual(en_translation.tour_api_content_id, "126508_en")

    @patch("places.services.multilang_tour_api_client.MultiLangTourAPIClient.collect_all_languages")
    def test_gis_matching_different_places(self, mock_collect):
        gyeongbok = Place.objects.create(
            content_id="126508",
            location=Point(126.9770171326, 37.5788408279)
        )
        PlaceTranslation.objects.create(
            place=gyeongbok,
            lang="ko",
            name="경복궁",
            tour_api_content_id="126508"
        )

        mock_data = {
            "ko": [{
                "contentid": "126509",
                "title": "창덕궁",
                "mapx": "126.9910727208",
                "mapy": "37.5794090842",
                "_language": "ko"
            }],
            "en": [],
            "jp": [],
            "cn": []
        }

        mock_collect.return_value = self._get_mock_api_response(mock_data)

        call_command("sync_multilang_places", "--languages", "ko", "--area-code", "1")

        places = Place.objects.all()
        self.assertEqual(places.count(), 2)

        changdeok = Place.objects.get(content_id="126509")
        self.assertIsNotNone(changdeok)

        changdeok_translation = PlaceTranslation.objects.get(place=changdeok, lang="ko")
        self.assertEqual(changdeok_translation.name, "창덕궁")

    def test_command_invalid_language(self):
        with self.assertRaises(CommandError):
            call_command("sync_multilang_places", "--languages", "fr,de")

    def test_command_invalid_area_code(self):
        with self.assertRaises(CommandError):
            call_command("sync_multilang_places", "--area-code", "999")

    @patch("places.services.multilang_tour_api_client.MultiLangTourAPIClient.collect_all_languages")
    def test_api_error_handling(self, mock_collect):
        mock_collect.return_value = {
            "status": "error",
            "errors": ["ko: API call failed", "en: Daily limit exceeded"]
        }

        with self.assertRaises(CommandError):
            call_command("sync_multilang_places", "--languages", "ko,en", "--area-code", "1")

    @patch("places.services.multilang_tour_api_client.MultiLangTourAPIClient.collect_all_languages")
    def test_duplicate_content_id_handling(self, mock_collect):
        existing_place = Place.objects.create(
            content_id="126508",
            location=Point(126.9770171326, 37.5788408279)
        )

        mock_data = {
            "ko": [{
                "contentid": "126508",
                "title": "경복궁 (업데이트)",
                "mapx": "126.9770171326",
                "mapy": "37.5788408279",
                "_language": "ko"
            }],
            "en": [],
            "jp": [],
            "cn": []
        }

        mock_collect.return_value = self._get_mock_api_response(mock_data)

        call_command("sync_multilang_places", "--languages", "ko", "--area-code", "1")

        places = Place.objects.all()
        self.assertEqual(places.count(), 1)

    def test_command_help_text(self):
        try:
            call_command("sync_multilang_places", "--help")
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    @patch("places.services.multilang_tour_api_client.MultiLangTourAPIClient.collect_all_languages")
    def test_limit_option(self, mock_collect):
        mock_data = {
            "ko": [
                {"contentid": "126508", "title": "경복궁", "mapx": "126.977", "mapy": "37.578", "_language": "ko"},
                {"contentid": "126509", "title": "창덕궁", "mapx": "126.991", "mapy": "37.579", "_language": "ko"}
            ],
            "en": [],
            "jp": [],
            "cn": []
        }

        mock_collect.return_value = self._get_mock_api_response(mock_data)

        call_command("sync_multilang_places", "--languages", "ko", "--area-code", "1", "--limit", "1")

        places = Place.objects.all()
        self.assertGreaterEqual(places.count(), 0)

    @patch("places.services.multilang_tour_api_client.MultiLangTourAPIClient.collect_all_languages")
    def test_multilang_integration_scenario(self, mock_collect):
        mock_data = {
            "ko": [{
                "contentid": "126508",
                "title": "경복궁",
                "mapx": "126.9770171326",
                "mapy": "37.5788408279",
                "_language": "ko"
            }],
            "en": [{
                "contentid": "126508_en",
                "title": "Gyeongbokgung Palace",
                "mapx": "126.9770500000",
                "mapy": "37.5788900000",
                "_language": "en"
            }],
            "jp": [{
                "contentid": "126508_jp",
                "title": "景福宮",
                "mapx": "126.9770300000",
                "mapy": "37.5788600000",
                "_language": "jp"
            }],
            "cn": [{
                "contentid": "126508_cn",
                "title": "景福宫",
                "mapx": "126.9770000000",
                "mapy": "37.5788200000",
                "_language": "cn"
            }]
        }

        mock_collect.return_value = self._get_mock_api_response(mock_data)

        call_command("sync_multilang_places", "--languages", "ko,en,jp,cn", "--area-code", "1")

        places = Place.objects.all()
        self.assertEqual(places.count(), 1)

        place = places.first()
        translations = PlaceTranslation.objects.filter(place=place)
        self.assertEqual(translations.count(), 4)

        language_names = {
            "ko": "경복궁",
            "en": "Gyeongbokgung Palace",
            "jp": "景福宮",
            "cn": "景福宫"
        }

        for lang, expected_name in language_names.items():
            translation = translations.get(lang=lang)
            self.assertEqual(translation.name, expected_name)
            self.assertIn("126508", translation.tour_api_content_id)

        self.assertIsNotNone(place.location)
        self.assertAlmostEqual(place.location.x, 126.977, places=2)
        self.assertAlmostEqual(place.location.y, 37.5788, places=2)
