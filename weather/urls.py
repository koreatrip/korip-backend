
from django.urls import path
from weather.views import WeatherAPI

app_name = "weather"

urlpatterns = [
    path("region/<int:region_id>/", WeatherAPI.as_view(), name="weather_by_region"),
]