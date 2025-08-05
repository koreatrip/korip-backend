from django.test import TestCase
from unittest.mock import Mock, patch
from places.services.tour_api_client import TourAPIClient


class TourAPIClientTest(TestCase):

    def setUp(self):
        self.client = TourAPIClient()

    def test_client_initialization(self):
        self.assertEqual(self.client.base_url, "http://apis.data.go.kr/B551011/KorService2")
        self.assertEqual(self.client.mobile_os, "ETC")
        self.assertEqual(self.client.mobile_app, "KORIP")
        self.assertEqual(self.client.response_type, "json")
        self.assertEqual(self.client.request_delay, 1)

    @patch("places.services.tour_api_client.requests.get")
    def test_make_request_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {
                "header": {"resultCode": "0000", "resultMsg": "OK"},
                "body": {"items": {"item": [{"test": "data"}]}}
            }
        }
        mock_get.return_value = mock_response
        result = self.client._make_request("test_endpoint", {"param1": "value1"})

        self.assertIsNotNone(result)
        self.assertEqual(result["items"]["item"][0]["test"], "data")

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("serviceKey", call_args[1]["params"])
        self.assertIn("param1", call_args[1]["params"])

    @patch("places.services.tour_api_client.requests.get")
    def test_make_request_api_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {
                "header": {"resultCode": "9999", "resultMsg": "API 에러"},
                "body": {}
            }
        }
        mock_get.return_value = mock_response
        result = self.client._make_request("test_endpoint", {})
        self.assertIsNone(result)

    @patch("places.services.tour_api_client.requests.get")
    def test_make_request_network_error(self, mock_get):
        mock_get.side_effect = Exception("네트워크 에러")
        result = self.client._make_request("test_endpoint", {})
        self.assertIsNone(result)

    @patch("places.services.tour_api_client.TourAPIClient._make_request")
    def test_get_area_list_success(self, mock_make_request):
        mock_make_request.return_value = {
            "items": {
                "item": [
                    {"contentid": "123", "title": "테스트 관광지1"},
                    {"contentid": "456", "title": "테스트 관광지2"}
                ]
            }
        }

        result = self.client.get_area_list(area_code="1", num_of_rows=10)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "테스트 관광지1")
        self.assertEqual(result[1]["title"], "테스트 관광지2")
        mock_make_request.assert_called_once_with(
            "areaBasedList2",
            {"numOfRows": 10, "pageNo": 1, "areaCode": "1"},
            "ko"
        )

    @patch("places.services.tour_api_client.TourAPIClient._make_request")
    def test_get_area_list_empty_result(self, mock_make_request):
        mock_make_request.return_value = {"items": {"item": []}}
        result = self.client.get_area_list()
        self.assertEqual(result, [])

    @patch("places.services.tour_api_client.TourAPIClient._make_request")
    def test_get_area_list_api_failure(self, mock_make_request):
        mock_make_request.return_value = None
        result = self.client.get_area_list()
        self.assertEqual(result, [])

    @patch("places.services.tour_api_client.TourAPIClient._make_request")
    def test_get_category_codes_success(self, mock_make_request):
        mock_make_request.return_value = {
            "items": {
                "item": [
                    {"lclsSystm1Cd": "VE", "lclsSystm1Nm": "문화관광"},
                    {"lclsSystm1Cd": "FD", "lclsSystm1Nm": "음식"}
                ]
            }
        }

        result = self.client.get_category_codes()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["lclsSystm1Cd"], "VE")
        self.assertEqual(result[1]["lclsSystm1Cd"], "FD")
        mock_make_request.assert_called_once_with(
            "lclsSystmCode2",
            {"numOfRows": 1000, "pageNo": 1, "lclsSystmListYn": "Y"},
            "ko"
        )

    @patch("places.services.tour_api_client.TourAPIClient._make_request")
    def test_get_area_codes_success(self, mock_make_request):
        mock_make_request.return_value = {
            "items": {
                "item": [
                    {"code": "1", "name": "서울"},
                    {"code": "2", "name": "인천"}
                ]
            }
        }

        result = self.client.get_area_codes()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "서울")
        mock_make_request.assert_called_once_with(
            "areaCode2",
            {"numOfRows": 100, "pageNo": 1},
            "ko"
        )

    def test_connection_test_success(self):
        result = self.client.test_connection(from_command=False)
        self.assertFalse(result)

    def test_connection_test_failure(self):
        result = self.client.test_connection(from_command=False)
        self.assertFalse(result)


class TourAPIClientIntegrationTest(TestCase):

    def setUp(self):
        self.client = TourAPIClient()

    @patch("places.services.tour_api_client.requests.get")
    @patch("places.services.tour_api_client.time.sleep")
    def test_full_flow_simulation(self, mock_sleep, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {
                "header": {"resultCode": "0000", "resultMsg": "OK"},
                "body": {
                    "items": {
                        "item": [
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
                                "tel": "02-3700-3900"
                            }
                        ]
                    }
                }
            }
        }
        mock_get.return_value = mock_response
        places = self.client.get_area_list(area_code="1", num_of_rows=1)
        self.assertEqual(len(places), 1)
        place = places[0]
        self.assertEqual(place["contentid"], "126508")
        self.assertEqual(place["title"], "경복궁")
        self.assertEqual(place["lclsSystm1"], "VE")

        mock_get.assert_called_once()
        call_args = mock_get.call_args

        self.assertIn("areaBasedList2", call_args[0][0])

        params = call_args[1]["params"]
        self.assertEqual(params["areaCode"], "1")
        self.assertEqual(params["numOfRows"], 1)
        self.assertIn("serviceKey", params)