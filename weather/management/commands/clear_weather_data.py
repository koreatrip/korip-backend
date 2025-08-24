from django.core.management.base import BaseCommand
from weather.models import Weather, WeatherForecast


class Command(BaseCommand):
    help = "모든 날씨 데이터 삭제"

    def handle(self, *args, **options):
        weather_count = Weather.objects.count()
        forecast_count = WeatherForecast.objects.count()

        Weather.objects.all().delete()
        WeatherForecast.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"삭제 완료: Weather {weather_count}개, WeatherForecast {forecast_count}개"
            )
        )
