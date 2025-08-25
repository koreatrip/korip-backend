from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from regions.models import Region, SubRegion
from weather.models import Weather
from weather.services.weather_api_client import WeatherAPIClient
from weather.exceptions import WeatherAPIError
from datetime import datetime, timedelta
import pytz


class Command(BaseCommand):
    help = "기상청 API에서 날씨 데이터를 수집하여 DB에 저장합니다"

    def add_arguments(self, parser):
        parser.add_argument("--region_id", type=int, help="특정 지역 ID만 업데이트")
        parser.add_argument("--force", action="store_true", help="강제로 업데이트")
        parser.add_argument("--dry_run", action="store_true", help="시뮬레이션만 실행")
        parser.add_argument("--all", action="store_true", help="전체 지역 날씨 데이터 수집")

    def handle(self, *args, **options):
        self.stdout.write("날씨 데이터 동기화를 시작합니다...")

        try:
            weather_client = WeatherAPIClient()
            self.stdout.write("기상청 API 클라이언트 초기화 완료")
        except Exception as e:
            raise CommandError(f"API 클라이언트 초기화 실패: {e}")

        regions = self._get_regions_to_process(options.get("region_id"))

        if not regions:
            self.stdout.write("처리할 지역이 없습니다.")
            return

        self.stdout.write(f"총 {len(regions)}개 지역을 처리합니다.")

        success_count = 0
        error_count = 0

        for region in regions:
            try:
                saved_count = self._process_region_weather_efficient(
                    region,
                    weather_client,
                    options.get("force", False),
                    options.get("dry_run", False)
                )
                success_count += 1
                self.stdout.write(f"  {self._get_region_name(region)} 처리 완료 ({saved_count}개 저장)")
            except Exception as e:
                error_count += 1
                self.stdout.write(f"  {self._get_region_name(region)} 처리 실패: {e}")

        if success_count > 0 and not options.get("dry_run", False):
            self._cleanup_old_weather_data()

        self.stdout.write(
            f"\n날씨 데이터 동기화 완료!\n"
            f"성공: {success_count}개 지역\n"
            f"실패: {error_count}개 지역"
        )

    def _get_regions_to_process(self, region_id=None):
        if region_id:
            try:
                return [Region.objects.get(id=region_id)]
            except Region.DoesNotExist:
                raise CommandError(f"지역 ID {region_id}를 찾을 수 없습니다")
        else:
            return Region.objects.all()

    def _get_region_name(self, region):
        try:
            if hasattr(region, 'get_name'):
                return region.get_name('ko')
            elif hasattr(region, 'name'):
                return region.name
            else:
                return str(region)
        except:
            return str(region)

    def _process_region_weather_efficient(self, region, weather_client, force=False, dry_run=False):
        self.stdout.write(f"{self._get_region_name(region)} 날씨 데이터 수집 중...")

        subregions = getattr(region, 'subregions', None)

        if not subregions or not subregions.exists():
            self.stdout.write(f"  {self._get_region_name(region)}에 서브지역이 없습니다.")
            return 0

        representative_subregion = self._get_representative_subregion(subregions.all())

        if not representative_subregion:
            self.stdout.write(f"  대표 지역을 찾을 수 없습니다.")
            return 0

        latitude, longitude = self._get_subregion_coordinates(representative_subregion)

        if latitude is None or longitude is None:
            self.stdout.write(f"  대표 지역({self._get_region_name(representative_subregion)})의 위치 정보 없음")
            return 0

        self.stdout.write(f"  대표 지역: {self._get_region_name(representative_subregion)} ({latitude}, {longitude})")

        try:
            weather_data = weather_client.get_weather_by_coordinates(latitude, longitude)

            if not weather_data:
                self.stdout.write(f"  날씨 데이터 없음")
                return 0

            if dry_run:
                self.stdout.write(f"  {len(weather_data)}개 예보 × {subregions.count()}개 지역구 시뮬레이션 완료")
                return len(weather_data) * subregions.count()

            total_saved = 0
            for subregion in subregions.all():
                saved_count = self._save_weather_data(region, subregion, weather_data)
                total_saved += saved_count
                self.stdout.write(f"    {self._get_region_name(subregion)}: {saved_count}개 저장")

            return total_saved

        except WeatherAPIError as e:
            self.stdout.write(f"  API 에러: {e}")
            return 0
        except Exception as e:
            self.stdout.write(f"  처리 에러: {e}")
            return 0

    def _get_representative_subregion(self, subregions):
        for subregion in subregions:
            latitude, longitude = self._get_subregion_coordinates(subregion)
            if latitude is not None and longitude is not None:
                return subregion
        return None

    def _get_subregion_coordinates(self, subregion):
        latitude = None
        longitude = None

        if hasattr(subregion, "latitude") and hasattr(subregion, "longitude"):
            latitude = subregion.latitude
            longitude = subregion.longitude
        elif hasattr(subregion, "location") and subregion.location:
            if hasattr(subregion.location, "y") and hasattr(subregion.location, "x"):
                latitude = subregion.location.y
                longitude = subregion.location.x
        elif hasattr(subregion, "lat") and hasattr(subregion, "lng"):
            latitude = subregion.lat
            longitude = subregion.lng

        return latitude, longitude

    def _save_weather_data(self, region, subregion, weather_data):
        saved_count = 0
        morning_temp = None

        # 최저기온을 아침 기온으로 사용
        for forecast in weather_data:
            min_temp = forecast.get("min_temperature")
            if min_temp is not None:
                morning_temp = min_temp
                self.stdout.write(f"  아침 기준: 최저기온 {morning_temp}도")
                break

        if morning_temp is None:
            self.stdout.write("  최저기온 데이터를 찾을 수 없습니다")

        kst = pytz.timezone("Asia/Seoul")

        with transaction.atomic():
            for forecast in weather_data:
                try:
                    forecast_time = datetime.strptime(
                        forecast["forecast_time"],
                        "%Y-%m-%d %H:%M:%S"
                    )
                    forecast_time = kst.localize(forecast_time)

                    # 아침 기온(최저기온) 대비 계산
                    current_temp = forecast.get("temperature")
                    temperature_change_text = None

                    if morning_temp is not None and current_temp is not None:
                        temp_diff = current_temp - morning_temp
                        if abs(temp_diff) >= 0.1:
                            if temp_diff > 0:
                                temperature_change_text = f"아침보다 {temp_diff:.1f}°↑"
                            else:
                                temperature_change_text = f"아침보다 {abs(temp_diff):.1f}°↓"
                        else:
                            temperature_change_text = "아침과 비슷"

                    weather, created = Weather.objects.update_or_create(
                        region=region,
                        sub_region=subregion,
                        forecast_time=forecast_time,
                        defaults={
                            "temperature": forecast.get("temperature"),
                            "humidity": forecast.get("humidity"),
                            "precipitation": forecast.get("precipitation"),
                            "sky_code": forecast.get("sky_code"),
                            "precipitation_type": forecast.get("precipitation_type"),
                            "wind_speed": forecast.get("wind_speed"),
                            "wind_direction": forecast.get("wind_direction"),
                            "uv_index": forecast.get("uv_index"),
                            "feels_like_temperature": forecast.get("feels_like_temperature"),
                            "pm25": forecast.get("pm25"),
                            "pm10": forecast.get("pm10"),
                            "sunrise_time": forecast.get("sunrise_time"),
                            "sunset_time": forecast.get("sunset_time"),
                            "min_temperature": forecast.get("min_temperature"),
                            "max_temperature": forecast.get("max_temperature"),
                            "temperature_change_text": temperature_change_text,
                            "morning_temperature": morning_temp,
                        }
                    )
                    saved_count += 1

                except Exception as e:
                    continue

        return saved_count

    def _cleanup_old_weather_data(self):
        from datetime import timedelta
        seven_days_ago = timezone.now() - timedelta(days=7)
        old_weather_count = Weather.objects.filter(
            forecast_time__lt=seven_days_ago
        ).count()

        if old_weather_count > 0:
            Weather.objects.filter(
                forecast_time__lt=seven_days_ago
            ).delete()
            self.stdout.write(f"오래된 날씨 데이터 {old_weather_count}개 정리 완료")
