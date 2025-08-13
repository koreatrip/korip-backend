# tests/test_weather_serializers.py

from django.test import TestCase
from rest_framework.test import APITestCase
from weather.serializers import (
    WeatherDataSerializer, CurrentWeatherSerializer,
    TomorrowWeatherSerializer, DetailInfoSerializer,
    HourlyForecastItemSerializer, AirQualityDetailSerializer,
    TravelTipSerializer, WeatherResponseSerializer
)
from weather.models import WeatherData


class WeatherDataSerializerTest(TestCase):

    def setUp(self):
        self.weather_data = WeatherData.objects.create(
            location_name="서울시청",
            latitude=37.5665,
            longitude=126.9780,
            current_temperature=25.0,
            humidity=80,
            pm25_value=15,
            pm10_value=30,
            uv_index=5,
            sunrise_time="05:30",
            sunset_time="19:45"
        )

    def test_weather_data_serializer_fields(self):
        # WeatherDataSerializer 필드 테스트
        serializer = WeatherDataSerializer(self.weather_data)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("location_name", data)
        self.assertIn("latitude", data)
        self.assertIn("longitude", data)
        self.assertIn("current_temperature", data)
        self.assertIn("humidity", data)

    def test_weather_data_serializer_values(self):
        # WeatherDataSerializer 값 테스트
        serializer = WeatherDataSerializer(self.weather_data)
        data = serializer.data

        self.assertEqual(data["location_name"], "서울시청")
        self.assertEqual(float(data["latitude"]), 37.5665)
        self.assertEqual(float(data["longitude"]), 126.9780)
        self.assertEqual(data["current_temperature"], 25.0)
        self.assertEqual(data["humidity"], 80)


class CurrentWeatherSerializerTest(TestCase):

    def test_current_weather_serializer_valid_data(self):
        # 정상 데이터 직렬화 테스트
        data = {
            "current_date": "08.13",
            "temperature": 25.0,
            "weather_condition": "맑음",
            "temperature_change": "+2.3°",
            "min_temperature": 19.0,
            "max_temperature": 30.0
        }

        serializer = CurrentWeatherSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["temperature"], 25.0)

    def test_current_weather_serializer_invalid_data(self):
        # 잘못된 데이터 직렬화 테스트
        data = {
            "current_date": "08.13",
            "temperature": "invalid",  # 숫자가 아님
            "weather_condition": "맑음"
        }

        serializer = CurrentWeatherSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("temperature", serializer.errors)


class TomorrowWeatherSerializerTest(TestCase):

    def test_tomorrow_weather_serializer_valid_data(self):
        # 내일 날씨 직렬화 테스트
        data = {
            "tomorrow_date": "08.14",
            "min_temperature": 18.0,
            "max_temperature": 32.0,
            "morning_condition": "맑음",
            "morning_precipitation": 0,
            "afternoon_condition": "구름",
            "afternoon_precipitation": 20
        }

        serializer = TomorrowWeatherSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_tomorrow_weather_serializer_precipitation_range(self):
        # 강수확률 범위 테스트
        data = {
            "tomorrow_date": "08.14",
            "min_temperature": 18.0,
            "max_temperature": 32.0,
            "morning_condition": "맑음",
            "morning_precipitation": 150,  # 100 초과
            "afternoon_condition": "구름",
            "afternoon_precipitation": -10  # 0 미만
        }

        serializer = TomorrowWeatherSerializer(data=data)
        # 기본 IntegerField는 범위 검증 안함
        self.assertTrue(serializer.is_valid())


class DetailInfoSerializerTest(TestCase):

    def test_detail_info_serializer_complete_data(self):
        # 완전한 상세 정보 테스트
        data = {
            "feels_like": 23.5,
            "humidity": 85,
            "uv_index": 7,
            "uv_level": "높음",
            "wind_speed": 2.5,
            "sunrise": "05:15",
            "sunset": "19:40",
            "air_quality_status": "보통"
        }

        serializer = DetailInfoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["feels_like"], 23.5)
        self.assertEqual(serializer.validated_data["uv_index"], 7)


class HourlyForecastItemSerializerTest(TestCase):

    def test_hourly_forecast_item_required_fields(self):
        # 필수 필드만 있는 시간별 예보 테스트
        data = {
            "time": "14시",
            "weather_icon": "sunny",
            "weather_condition": "맑음",
            "temperature": 28.0
        }

        serializer = HourlyForecastItemSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_hourly_forecast_item_with_precipitation(self):
        # 강수확률 포함 시간별 예보 테스트
        data = {
            "time": "16시",
            "weather_icon": "rainy",
            "weather_condition": "비",
            "temperature": 22.0,
            "precipitation_probability": 80
        }

        serializer = HourlyForecastItemSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["precipitation_probability"], 80)


class AirQualityDetailSerializerTest(TestCase):

    def test_air_quality_detail_serializer(self):
        # 대기질 정보 직렬화 테스트
        data = {
            "pm25_value": 15,
            "pm25_grade": "좋음",
            "pm10_value": 30,
            "pm10_grade": "보통"
        }

        serializer = AirQualityDetailSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["pm25_value"], 15)


class TravelTipSerializerTest(TestCase):

    def test_travel_tip_serializer(self):
        # 여행 팁 직렬화 테스트
        data = {
            "tip_message": "아이 활동하기 좋은 날씨입니다."
        }

        serializer = TravelTipSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["tip_message"], "아이 활동하기 좋은 날씨입니다.")


class WeatherResponseSerializerTest(TestCase):

    def test_weather_response_serializer_complete(self):
        # 완전한 날씨 응답 데이터 테스트
        data = {
            "current_weather": {
                "current_date": "08.13",
                "temperature": 25.0,
                "weather_condition": "맑음",
                "temperature_change": "+1.2°",
                "min_temperature": 19.0,
                "max_temperature": 30.0
            },
            "tomorrow_weather": {
                "tomorrow_date": "08.14",
                "min_temperature": 18.0,
                "max_temperature": 32.0,
                "morning_condition": "맑음",
                "morning_precipitation": 0,
                "afternoon_condition": "구름",
                "afternoon_precipitation": 20
            },
            "detail_info": {
                "feels_like": 23.5,
                "humidity": 85,
                "uv_index": 7,
                "uv_level": "높음",
                "wind_speed": 2.5,
                "sunrise": "05:15",
                "sunset": "19:40",
                "air_quality_status": "보통"
            },
            "hourly_forecast": [
                {
                    "time": "14시",
                    "weather_icon": "sunny",
                    "weather_condition": "맑음",
                    "temperature": 28.0
                }
            ],
            "air_quality": {
                "pm25_value": 15,
                "pm25_grade": "좋음",
                "pm10_value": 30,
                "pm10_grade": "보통"
            },
            "travel_tip": {
                "tip_message": "야외 활동하기 좋은 날씨입니다."
            },
            "location_name": "서울시청",
            "latitude": 37.5665,
            "longitude": 126.9780,
            "last_updated": "2023-08-13T14:30:00Z"
        }

        serializer = WeatherResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_weather_response_serializer_missing_fields(self):
        # 필수 필드 누락 테스트
        data = {
            "current_weather": {
                "current_date": "08.13",
                "temperature": 25.0
                # 필수 필드들 누락
            }
        }

        serializer = WeatherResponseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("current_weather", serializer.errors)
