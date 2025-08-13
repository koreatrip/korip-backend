# tests/test_weather_models.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from weather.models import WeatherData


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
        # __str__ 메서드 테스트 (실제 형식에 맞춰 수정)
        weather = WeatherData.objects.create(**self.valid_data)
        str_result = str(weather)

        # 실제 형식: "서울시청 - 25.0℃ (2025-08-13 04:24)"
        self.assertIn("서울시청", str_result)
        self.assertIn("25.0", str_result)
        self.assertTrue("℃" in str_result or "°C" in str_result)

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

    def test_weather_data_latitude_precision(self):
        # 위도 정밀도 테스트 (float 비교로 수정)
        data = self.valid_data.copy()
        data["latitude"] = 37.56656789
        weather = WeatherData.objects.create(**data)

        self.assertEqual(float(weather.latitude), 37.56656789)

    def test_weather_data_longitude_precision(self):
        # 경도 정밀도 테스트 (float 비교로 수정)
        data = self.valid_data.copy()
        data["longitude"] = 126.97801234
        weather = WeatherData.objects.create(**data)

        self.assertEqual(float(weather.longitude), 126.97801234)

    def test_weather_data_humidity_range(self):
        # 습도 범위 테스트 (0-100%)
        data = self.valid_data.copy()

        # 정상 범위
        data["humidity"] = 0
        weather1 = WeatherData.objects.create(**data)
        self.assertEqual(weather1.humidity, 0)

        data["humidity"] = 100
        weather2 = WeatherData.objects.create(**data)
        self.assertEqual(weather2.humidity, 100)

    def test_weather_data_temperature_negative(self):
        # 음수 기온 테스트
        data = self.valid_data.copy()
        data["current_temperature"] = -15.5
        weather = WeatherData.objects.create(**data)

        self.assertEqual(weather.current_temperature, -15.5)

    def test_weather_data_ordering(self):
        # 정렬 테스트 (최신순)
        weather1 = WeatherData.objects.create(**self.valid_data)

        data2 = self.valid_data.copy()
        data2["location_name"] = "부산"
        weather2 = WeatherData.objects.create(**data2)

        weathers = WeatherData.objects.all()
        self.assertEqual(weathers[0], weather2)  # 최신이 첫 번째
        self.assertEqual(weathers[1], weather1)

    def test_weather_data_db_table_name(self):
        # DB 테이블명 확인
        self.assertEqual(WeatherData._meta.db_table, "weather_data")
