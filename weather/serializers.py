from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
from weather.models import WeatherForecast, AirQualityData, WeatherData


class CurrentWeatherSerializer(serializers.Serializer):
    # 현재 날씨 정보

    # 현재 날짜
    current_date = serializers.CharField(help_text="현재 날짜 (MM.DD)")

    # 현재 기온
    temperature = serializers.FloatField(help_text="현재 기온 (°C)")
    weather_condition = serializers.CharField(help_text="날씨 상태 (맑음, 흐림, 비 등)")
    temperature_change = serializers.CharField(help_text="어제 대비 기온 변화 (+2.3°, -0.8° 등)")
    min_temperature = serializers.FloatField(help_text="오늘 최저 기온")
    max_temperature = serializers.FloatField(help_text="오늘 최고 기온")


class TomorrowWeatherSerializer(serializers.Serializer):
    # 내일 날씨 정보

    tomorrow_date = serializers.CharField(help_text="내일 날짜 (MM.DD)")
    min_temperature = serializers.FloatField(help_text="내일 최저 기온")
    max_temperature = serializers.FloatField(help_text="내일 최고 기온")
    morning_condition = serializers.CharField(help_text="오전 날씨 상태")
    morning_precipitation = serializers.IntegerField(help_text="오전 강수확률 (%)")
    afternoon_condition = serializers.CharField(help_text="오후 날씨 상태")
    afternoon_precipitation = serializers.IntegerField(help_text="오후 강수확률 (%)")


class DetailInfoSerializer(serializers.Serializer):
    # 상세 정보

    feels_like = serializers.FloatField(help_text="체감 온도")
    humidity = serializers.IntegerField(help_text="습도 (%)")
    uv_index = serializers.IntegerField(help_text="자외선 지수")
    uv_level = serializers.CharField(help_text="자외선 등급 (보통, 높음 등)")
    wind_speed = serializers.FloatField(help_text="풍속 (m/s)")
    sunrise = serializers.CharField(help_text="일출 시간 (HH:MM)")
    sunset = serializers.CharField(help_text="일몰 시간 (HH:MM)")
    air_quality_status = serializers.CharField(help_text="미세먼지 종합 상태")


class HourlyForecastItemSerializer(serializers.Serializer):
    # 시간별 예보

    time = serializers.CharField(help_text="시간 (N시)")
    weather_condition = serializers.CharField(help_text="날씨 상태")
    temperature = serializers.FloatField(help_text="시간별 기온")
    # 강수확률 (표시되는 시간대만)
    precipitation_probability = serializers.IntegerField(help_text="강수확률 (%)", required=False)


class AirQualityDetailSerializer(serializers.Serializer):
    # 대기질 정보

    # 미세먼지 좋음 PM2.5: 15μg/m³
    pm25_value = serializers.IntegerField(help_text="PM2.5 농도")
    pm25_grade = serializers.CharField(help_text="PM2.5 등급")

    # 초미세먼지 좋음 PM10: 30μg/m³
    pm10_value = serializers.IntegerField(help_text="PM10 농도")
    pm10_grade = serializers.CharField(help_text="PM10 등급")


class TravelTipSerializer(serializers.Serializer):
    # 여행 팁

    tip_message = serializers.CharField(help_text="여행 팁 메시지")


class WeatherResponseSerializer(serializers.Serializer):
    # 완전한 날씨 정보 응답

    # 현재 날씨
    current_weather = CurrentWeatherSerializer(help_text="현재 날씨 정보")
    # 내일 날씨
    tomorrow_weather = TomorrowWeatherSerializer(help_text="내일 날씨 정보")
    # 상세 정보
    detail_info = DetailInfoSerializer(help_text="상세 날씨 정보")
    # 시간별 예보
    hourly_forecast = HourlyForecastItemSerializer(many=True, help_text="시간별 예보 (12시간)")
    # 대기질 정보
    air_quality = AirQualityDetailSerializer(help_text="대기질 상세 정보")
    # 여행 팁
    travel_tip = TravelTipSerializer(help_text="여행 팁")
    # 위치 정보
    location_name = serializers.CharField(help_text="지역명")
    latitude = serializers.FloatField(help_text="위도")
    longitude = serializers.FloatField(help_text="경도")
    # 마지막 업데이트 시간
    last_updated = serializers.DateTimeField(help_text="마지막 업데이트 시간")

class WeatherDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeatherData
        fields = [
            "id",
            "location_name",
            "latitude",
            "longitude",
            "current_temperature",
            "humidity",
            "pm25_value",
            "pm10_value",
            "uv_index",
            "sunrise_time",
            "sunset_time",
            "created_at",
            "updated_at"
        ]


class WeatherForecastSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeatherForecast
        fields = [
            "id",
            "location_name",
            "nx",
            "ny",
            "forecast_date",
            "forecast_time",
            "temperature",
            "humidity",
            "precipitation_probability",
            "precipitation_type",
            "sky_condition",
            "created_at"
        ]


class AirQualityDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirQualityData
        fields = [
            "id",
            "station_name",
            "measurement_date",
            "pm10_value",
            "pm25_value",
            "pm10_grade",
            "pm25_grade",
            "created_at"
        ]
