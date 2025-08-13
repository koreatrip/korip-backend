# weather/urls.py
# 올바른 계층 구조 날씨 API - 지역 > 지역구

from django.urls import path
from weather.views import (
    WeatherByRegionAPI,
    WeatherBySubRegionAPI,
)

# 앱 이름 설정
app_name = "weather"

urlpatterns = [
    path("region/<int:region_id>/", WeatherByRegionAPI.as_view(), name="weather_by_region"),
    path("region/<int:region_id>/subregion/<int:subregion_id>/", WeatherBySubRegionAPI.as_view(), name="weather_by_subregion"),
]