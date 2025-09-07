from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
from weather.models import WeatherForecast, AirQualityData, Weather


class CurrentWeatherSerializer(serializers.Serializer):
    # 현재 날씨 정보
    current_date = serializers.CharField(help_text="현재 날짜 (MM.DD)")
    temperature = serializers.FloatField(help_text="현재 기온 (°C)")
    weather_condition = serializers.CharField(help_text="날씨 상태 (맑음, 흐림, 비 등)")
    temperature_change = serializers.CharField(help_text="아침 대비 기온 변화 (아침보다 2.3°↑)")
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
    precipitation_probability = serializers.IntegerField(help_text="강수확률 (%)", required=False)


class AirQualityDetailSerializer(serializers.Serializer):
    # 대기질 정보
    pm25_value = serializers.IntegerField(help_text="PM2.5 농도")
    pm25_grade = serializers.CharField(help_text="PM2.5 등급")
    pm10_value = serializers.IntegerField(help_text="PM10 농도")
    pm10_grade = serializers.CharField(help_text="PM10 등급")


class TravelTipSerializer(serializers.Serializer):
    # 여행 팁
    tip_message = serializers.CharField(help_text="여행 팁 메시지")


class WeatherResponseSerializer(serializers.Serializer):
    # 완전한 날씨 정보 응답
    current_weather = CurrentWeatherSerializer(help_text="현재 날씨 정보")
    tomorrow_weather = TomorrowWeatherSerializer(help_text="내일 날씨 정보")
    detail_info = DetailInfoSerializer(help_text="상세 날씨 정보")
    hourly_forecast = HourlyForecastItemSerializer(many=True, help_text="시간별 예보 (24시간)")
    air_quality = AirQualityDetailSerializer(help_text="대기질 상세 정보")
    travel_tip = TravelTipSerializer(help_text="여행 팁")
    location_name = serializers.CharField(help_text="지역명")
    latitude = serializers.FloatField(help_text="위도")
    longitude = serializers.FloatField(help_text="경도")
    last_updated = serializers.DateTimeField(help_text="마지막 업데이트 시간")


# 모델 직렬화용 Serializer들
class WeatherSerializer(serializers.ModelSerializer):
    # Weather 모델 직렬화 (메인 날씨 정보)
    region_name = serializers.CharField(source="region.get_name", read_only=True)
    sub_region_name = serializers.CharField(source="sub_region.get_name", read_only=True)

    class Meta:
        model = Weather
        fields = [
            "id",
            "region",
            "sub_region",
            "region_name",
            "sub_region_name",
            "temperature",
            "min_temperature",
            "max_temperature",
            "humidity",
            "precipitation",
            "sky_code",
            "precipitation_type",
            "wind_speed",
            "wind_direction",
            "feels_like_temperature",
            "uv_index",
            "sunrise_time",
            "sunset_time",
            "pm25",
            "pm10",
            "morning_temperature",
            "temperature_change_text",
            "forecast_time",
            "created_at",
            "updated_at"
        ]


class WeatherForecastSerializer(serializers.ModelSerializer):
    # WeatherForecast 모델 직렬화 (시간별 예보)
    region_name = serializers.CharField(source="region.get_name", read_only=True)
    sub_region_name = serializers.CharField(source="sub_region.get_name", read_only=True)

    class Meta:
        model = WeatherForecast
        fields = [
            "id",
            "region",
            "sub_region",
            "region_name",
            "sub_region_name",
            "nx",
            "ny",
            "forecast_date",
            "forecast_time",
            "temperature",
            "humidity",
            "precipitation_probability",
            "precipitation_type",
            "sky_condition",
            "wind_speed",
            "wind_direction",
            "created_at"
        ]


class AirQualityDataSerializer(serializers.ModelSerializer):
    # AirQualityData 모델 직렬화 (대기질 정보)
    region_name = serializers.CharField(source="region.get_name", read_only=True)
    sub_region_name = serializers.CharField(source="sub_region.get_name", read_only=True)

    class Meta:
        model = AirQualityData
        fields = [
            "id",
            "region",
            "sub_region",
            "region_name",
            "sub_region_name",
            "station_name",
            "measurement_date",
            "pm10_value",
            "pm25_value",
            "pm10_grade",
            "pm25_grade",
            "created_at"
        ]
