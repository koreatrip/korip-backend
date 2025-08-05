from django.test import TestCase
from unittest.mock import patch, Mock
from places.services.multilang_tour_api_client import MultiLangTourAPIClient


class MultiLangTourAPIClientTest(TestCase):
    def setUp(self):
        self.client = MultiLangTourAPIClient()

    def test_init_with_default_settings(self):
        self.assertEqual(self.client.base_url, "http://apis.data.go.kr/B551011/KorService2")
        self.assertIn("pcaidHGQK", self.client.service_key)
        self.assertEqual(self.client.mobile_os, "ETC")
        self.assertEqual(self.client.mobile_app, "KORIP")

    def test_supported_languages(self):
        expected_languages = ["ko", "en", "jp", "cn"]
        self.assertEqual(self.client.supported_languages, expected_languages)

    @patch("places.services.multilang_tour_api_client.requests.get")
    def test_get_places_by_language_korean_success(self, mock_get):
        mock_response_data = {
            "response": {
                "header": {"resultCode": "0000", "resultMsg": "OK"},
                "body": {
                    "items": {
                        "item": [
                            {
                                "contentid": "126508",
                                "title": "경복궁",
                                "addr1": "서울특별시 종로구 사직로 161",
                                "mapx": "126.9770171326",
                                "mapy": "37.5788408279",
                                "cat1": "A02",
                                "cat2": "A0201",
                                "cat3": "A02010100",
                                "lclsSystm1": "CC",
                                "lclsSystm2": "CC01",
                                "lclsSystm3": "CC010200"
                            }
                        ]
                    }
                }
            }
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_places_by_language(area_code=1, lang="ko", num_of_rows=10)

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["data"]), 1)

        place_data = result["data"][0]
        self.assertEqual(place_data["contentid"], "126508")
        self.assertEqual(place_data["title"], "경복궁")
        self.assertEqual(place_data["_language"], "ko")

    @patch("places.services.multilang_tour_api_client.requests.get")
    def test_get_places_by_language_api_error(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API 호출 실패")
        mock_get.return_value = mock_response

        result = self.client.get_places_by_language(area_code=1, lang="ko")

        self.assertEqual(result["status"], "error")
        self.assertIn("API 호출 실패", result["error"])

    def test_get_places_by_language_unsupported_language(self):
        result = self.client.get_places_by_language(area_code=1, lang="fr")

        self.assertEqual(result["status"], "error")
        self.assertIn("지원하지 않는 언어", result["error"])

    @patch("places.services.multilang_tour_api_client.requests.get")
    def test_collect_all_languages_success(self, mock_get):
        korean_data = {
            "response": {
                "header": {"resultCode": "0000", "resultMsg": "OK"},
                "body": {
                    "items": {
                        "item": [
                            {
                                "contentid": "126508",
                                "title": "경복궁",
                                "mapx": "126.9770171326",
                                "mapy": "37.5788408279"
                            }
                        ]
                    }
                }
            }
        }

        english_data = {
            "response": {
                "header": {"resultCode": "0000", "resultMsg": "OK"},
                "body": {
                    "items": {
                        "item": [
                            {
                                "contentid": "126508_en",
                                "title": "Gyeongbokgung Palace",
                                "mapx": "126.9770500000",
                                "mapy": "37.5788900000"
                            }
                        ]
                    }
                }
            }
        }

        call_count = 0

        def mock_get_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None

            if call_count == 1:
                mock_response.json.return_value = korean_data
            elif call_count == 2:
                mock_response.json.return_value = english_data
            else:
                empty_data = {
                    "response": {
                        "header": {"resultCode": "0000", "resultMsg": "OK"},
                        "body": {"items": {"item": []}}
                    }
                }
                mock_response.json.return_value = empty_data

            return mock_response

        mock_get.side_effect = mock_get_side_effect
        result = self.client.collect_all_languages(area_code=1, num_of_rows=10)

        self.assertEqual(result["status"], "success")
        self.assertIn("ko", result["data"])
        self.assertIn("en", result["data"])

        ko_places = result["data"]["ko"]
        self.assertEqual(len(ko_places), 1)
        self.assertEqual(ko_places[0]["title"], "경복궁")
        self.assertEqual(ko_places[0]["_language"], "ko")

        en_places = result["data"]["en"]
        self.assertEqual(len(en_places), 1)
        self.assertEqual(en_places[0]["title"], "Gyeongbokgung Palace")
        self.assertEqual(en_places[0]["_language"], "en")

    def test_build_api_url_korean(self):
        url = self.client._build_api_url("ko", "areaBasedList2", {
            "areaCode": 1,
            "numOfRows": 10,
            "pageNo": 1
        })

        self.assertIn("KorService2/areaBasedList2", url)
        self.assertIn("areaCode=1", url)
        self.assertIn("numOfRows=10", url)

    def test_build_api_url_english(self):
        url = self.client._build_api_url("en", "areaBasedList2", {
            "areaCode": 1,
            "numOfRows": 10
        })

        self.assertIn("EngService2/areaBasedList2", url)

    def test_add_language_metadata(self):
        sample_data = [
            {"contentid": "126508", "title": "경복궁"},
            {"contentid": "126509", "title": "창덕궁"}
        ]

        result = self.client._add_language_metadata(sample_data, "ko")

        for item in result:
            self.assertEqual(item["_language"], "ko")

        self.assertEqual(result[0]["title"], "경복궁")
        self.assertEqual(result[1]["title"], "창덕궁")

    def test_extract_items_from_response_success(self):
        response_data = {
            "response": {
                "header": {"resultCode": "0000", "resultMsg": "OK"},
                "body": {
                    "items": {
                        "item": [
                            {"contentid": "126508", "title": "경복궁"},
                            {"contentid": "126509", "title": "창덕궁"}
                        ]
                    }
                }
            }
        }

        items = self.client._extract_items_from_response(response_data)

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["title"], "경복궁")
        self.assertEqual(items[1]["title"], "창덕궁")

    def test_extract_items_from_response_empty(self):
        response_data = {
            "response": {
                "header": {"resultCode": "0000", "resultMsg": "OK"},
                "body": {"items": {"item": []}}
            }
        }

        items = self.client._extract_items_from_response(response_data)
        self.assertEqual(len(items), 0)

    def test_extract_items_from_response_error(self):
        response_data = {
            "response": {
                "header": {"resultCode": "9999", "resultMsg": "서비스 오류"},
                "body": {}
            }
        }

        items = self.client._extract_items_from_response(response_data)
        self.assertEqual(len(items), 0)

    def test_api_call_limit_tracking(self):
        initial_count = self.client.api_call_count

        result = self.client.get_places_by_language(area_code=1, lang="fr")

        self.assertEqual(self.client.api_call_count, initial_count)
        self.assertEqual(result["status"], "error")

    def test_api_usage_stats(self):
        stats = self.client.get_api_usage_stats()

        self.assertIn("total_calls", stats)
        self.assertIn("daily_limit", stats)
        self.assertIn("remaining_calls_total", stats)
        self.assertIn("usage_percentage", stats)
        self.assertEqual(stats["daily_limit"], 1000)

    def test_api_counter_reset(self):
        self.client.api_call_count = 50
        self.client.reset_api_counter()
        self.assertEqual(self.client.api_call_count, 0)