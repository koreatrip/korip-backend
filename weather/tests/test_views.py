# tests/test_weather_views.py

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, Mock
from weather.models import WeatherData


class WeatherByRegionAPITest(APITestCase):

    @patch("weather.views.WeatherAPIClient")
    def test_weather_by_region_seoul(self, mock_client_class):
        # 서울 지역 날씨 조회 테스트
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_weather_by_coordinates.return_value = [
            {
                "forecast_time": "2023-08-13 14:00:00",
                "temperature": 25.0,
                "humidity": 80,
                "precipitation": 0,
                "sky_code": "1",
                "pm25": 15,
                "pm10": 30,
                "uv_index": 5,
                "sunrise_time": "05:30",
                "sunset_time": "19:45"
            }
        ]

        url = reverse("weather:weather_by_region", kwargs={"region_id": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_client.get_weather_by_coordinates.assert_called_once()

    @patch("weather.views.WeatherAPIClient")
    def test_weather_by_region_busan(self, mock_client_class):
        # 부산 지역 날씨 조회 테스트
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_weather_by_coordinates.return_value = [
            {
                "forecast_time": "2023-08-13 14:00:00",
                "temperature": 28.0,
                "humidity": 75,
                "precipitation": 0,
                "sky_code": "1"
            }
        ]

        url = reverse("weather:weather_by_region", kwargs={"region_id": 2})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_weather_by_region_invalid_region(self):
        # 지원하지 않는 지역 테스트
        url = reverse("weather:weather_by_region", kwargs={"region_id": 999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @patch("weather.views.WeatherAPIClient")
    def test_weather_by_region_client_error(self, mock_client_class):
        # WeatherAPIClient 에러 테스트
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_weather_by_coordinates.side_effect = Exception("API 에러")

        url = reverse("weather:weather_by_region", kwargs={"region_id": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)


class WeatherBySubRegionAPITest(APITestCase):

    @patch("weather.views.WeatherAPIClient")
    def test_weather_by_subregion_success(self, mock_client_class):
        # 지역구별 날씨 조회 테스트
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_weather_by_coordinates.return_value = [
            {
                "forecast_time": "2023-08-13 14:00:00",
                "temperature": 26.0,
                "humidity": 85,
                "precipitation": 10,
                "sky_code": "3"
            }
        ]

        url = reverse("weather:weather_by_subregion", kwargs={"region_id": 1, "subregion_id": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_client.get_weather_by_coordinates.assert_called_once()

    def test_weather_by_subregion_invalid_region(self):
        # 잘못된 지역 ID 테스트
        url = reverse("weather:weather_by_subregion", kwargs={"region_id": 999, "subregion_id": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_weather_by_subregion_invalid_subregion(self):
        # 잘못된 지역구 ID 테스트
        url = reverse("weather:weather_by_subregion", kwargs={"region_id": 1, "subregion_id": 999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @patch("weather.views.WeatherAPIClient")
    def test_weather_by_subregion_coordinates_mapping(self, mock_client_class):
        # 지역구 좌표 매핑 테스트
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_weather_by_coordinates.return_value = []

        url = reverse("weather:weather_by_subregion", kwargs={"region_id": 1, "subregion_id": 2})
        response = self.client.get(url)

        # WeatherAPIClient가 호출되었는지 확인
        mock_client.get_weather_by_coordinates.assert_called_once()


class WeatherDataModelTest(TestCase):

    def setUp(self):
        self.valid_data = {
            "location_name": "서울시청",
            "latitude": 37.5665,
            "longitude": 126.9780,
            "current_temperature": 25.0,
            "humidity": 80,
            "pm25_value": 15,
            "pm10_value": 30,
            "uv_index": 5,
            "sunrise_time": "05:30",
            "sunset_time": "19:45"
        }

    def test_create_weather_data_success(self):
        # 정상 데이터로 WeatherData 생성 테스트
        weather = WeatherData.objects.create(**self.valid_data)

        self.assertEqual(weather.location_name, "서울시청")
        self.assertEqual(float(weather.latitude), 37.5665)
        self.assertEqual(float(weather.longitude), 126.9780)
        self.assertEqual(weather.current_temperature, 25.0)
        self.assertEqual(weather.humidity, 80)

    def test_weather_data_str_method(self):
        # __str__ 메서드 테스트
        weather = WeatherData.objects.create(**self.valid_data)
        str_result = str(weather)

        # 실제 형식에 맞춰 검증
        self.assertIn("서울시청", str_result)
        self.assertIn("25.0", str_result)

    def test_weather_data_with_null_values(self):
        # 선택적 필드 null 값 테스트
        minimal_data = {
            "location_name": "테스트 지역",
            "latitude": 35.0,
            "longitude": 127.0,
            "current_temperature": 20.0,
            "humidity": 70
        }
        weather = WeatherData.objects.create(**minimal_data)

        self.assertIsNone(weather.pm25_value)
        self.assertIsNone(weather.pm10_value)
        self.assertIsNone(weather.uv_index)

    def test_weather_data_auto_timestamps(self):
        # 자동 생성 시간 필드 테스트
        weather = WeatherData.objects.create(**self.valid_data)

        self.assertIsNotNone(weather.created_at)
        self.assertIsNotNone(weather.updated_at)

    def test_weather_data_ordering(self):
        # 정렬 테스트 (최신순)
        weather1 = WeatherData.objects.create(**self.valid_data)

        data2 = self.valid_data.copy()
        data2["location_name"] = "부산"
        weather2 = WeatherData.objects.create(**data2)

        weathers = WeatherData.objects.all()
        self.assertEqual(weathers[0], weather2)  # 최신이 첫 번째
        self.assertEqual(weathers[1], weather1)
