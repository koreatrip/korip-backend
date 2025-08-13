"""
3시간마다 기상청 API에서 날씨 데이터를 수집해서 DB에 저장하는 Command

python manage.py sync_weather
python manage.py sync_weather --region_id=1  # 특정 지역만
python manage.py sync_weather --force        # 강제 업데이트
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from regions.models import Region, SubRegion
from weather.models import Weather
from weather.services.weather_api_client import WeatherAPIClient
from weather.exceptions import WeatherAPIError
import time


class Command(BaseCommand):
    help = "기상청 API에서 날씨 데이터를 수집하여 DB에 저장합니다"

    def add_arguments(self, parser):
        # 선택적 인자들
        parser.add_argument(
            "--region_id",
            type=int,
            help="특정 지역 ID만 업데이트 (지정하지 않으면 모든 지역)"
        )

        parser.add_argument(
            "--force",
            action="store_true",
            help="최근 업데이트 여부와 관계없이 강제로 업데이트"
        )

        parser.add_argument(
            "--dry_run",
            action="store_true",
            help="실제 저장하지 않고 시뮬레이션만 실행"
        )

    def handle(self, *args, **options):
        # 메인 실행 함수
        self.stdout.write(
            self.style.SUCCESS("날씨 데이터 동기화를 시작합니다...")
        )

        # WeatherAPIClient 초기화 (환경변수 자동 로드)
        try:
            weather_client = WeatherAPIClient()  # .env.local의 USE_HTTPS=False 자동 적용
            self.stdout.write("기상청 API 클라이언트 초기화 완료 (환경변수 기반)")
        except Exception as e:
            raise CommandError(f"API 클라이언트 초기화 실패: {e}")

        # 처리할 지역들 가져오기
        regions = self._get_regions_to_process(options.get("region_id"))

        if not regions:
            self.stdout.write(
                self.style.WARNING("처리할 지역이 없습니다.")
            )
            return

        self.stdout.write(f"총 {len(regions)}개 지역을 처리합니다.")

        # 각 지역별로 날씨 데이터 수집
        success_count = 0
        error_count = 0

        for region in regions:
            try:
                self._process_region_weather(
                    region,
                    weather_client,
                    options.get("force", False),
                    options.get("dry_run", False)
                )
                success_count += 1
                self.stdout.write(f"  {region.get_name('ko')} 처리 완료")

                # API 호출 간격 (API 부하 방지)
                time.sleep(0.5)

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"  {region.get_name('ko')} 처리 실패: {e}")
                )

        # 오래된 데이터 정리
        if success_count > 0:
            self._cleanup_old_weather_data()

        # 결과 요약
        self.stdout.write(
            self.style.SUCCESS(
                f"\n날씨 데이터 동기화 완료!\n"
                f"성공: {success_count}개 지역\n"
                f"실패: {error_count}개 지역"
            )
        )

    def _get_regions_to_process(self, region_id=None):
        # 처리할 지역 목록 가져오기
        if region_id:
            # 특정 지역만 처리
            try:
                return [Region.objects.get(id=region_id)]
            except Region.DoesNotExist:
                raise CommandError(f"지역 ID {region_id}를 찾을 수 없습니다")
        else:
            # 모든 지역 처리 (서브지역이 있는 지역만)
            return Region.objects.filter(subregions__isnull=False).distinct()

    def _process_region_weather(self, region, weather_client, force=False, dry_run=False):
        # 특정 지역의 날씨 데이터 처리
        self.stdout.write(f"{region.get_name('ko')} 날씨 데이터 수집 중...")

        # 해당 지역의 서브지역들 가져오기
        subregions = region.subregions.all()

        if not subregions:
            self.stdout.write(f"  {region.get_name('ko')}에 서브지역이 없습니다.")
            return

        for subregion in subregions:
            self._process_subregion_weather(subregion, weather_client, force, dry_run)

    def _process_subregion_weather(self, subregion, weather_client, force=False, dry_run=False):
        # 서브지역의 날씨 데이터 처리
        try:
            # 서브지역에 위도/경도가 있는지 확인
            latitude = None
            longitude = None

            # 여러 가능한 속성명 시도
            if hasattr(subregion, "latitude") and hasattr(subregion, "longitude"):
                latitude = subregion.latitude
                longitude = subregion.longitude
            elif hasattr(subregion, "location") and subregion.location:
                # GeoDjango Point 필드인 경우
                if hasattr(subregion.location, "y") and hasattr(subregion.location, "x"):
                    latitude = subregion.location.y
                    longitude = subregion.location.x
            elif hasattr(subregion, "lat") and hasattr(subregion, "lng"):
                latitude = subregion.lat
                longitude = subregion.lng

            # 위치 정보 유효성 확인
            if latitude is None or longitude is None:
                self.stdout.write(f"    {subregion.get_name('ko')}: 위치 정보 없음")
                return

            # 위도/경도 범위 확인
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                self.stdout.write(f"    {subregion.get_name('ko')}: 잘못된 좌표 ({latitude}, {longitude})")
                return

            # 최근 업데이트 확인 (force가 아닌 경우)
            if not force and self._is_recently_updated(subregion):
                self.stdout.write(f"    {subregion.get_name('ko')}: 최근 업데이트됨 (스킵)")
                return

            self.stdout.write(f"    {subregion.get_name('ko')} ({latitude}, {longitude}) 처리 중...")

            # 기상청 API 호출
            weather_data = weather_client.get_weather_by_coordinates(latitude, longitude)

            if not weather_data:
                self.stdout.write(f"      날씨 데이터 없음")
                return

            # DB에 저장
            if not dry_run:
                saved_count = self._save_weather_data(subregion.region, weather_data)
                self.stdout.write(f"      {saved_count}개 예보 저장 완료")
            else:
                self.stdout.write(f"      {len(weather_data)}개 예보 시뮬레이션 완료")

        except WeatherAPIError as e:
            self.stdout.write(f"      API 에러: {e}")
        except Exception as e:
            self.stdout.write(f"      처리 에러: {e}")

    def _is_recently_updated(self, subregion):
        # 최근 3시간 이내에 업데이트되었는지 확인
        from datetime import timedelta

        three_hours_ago = timezone.now() - timedelta(hours=3)

        recent_weather = Weather.objects.filter(
            region=subregion.region,
            created_at__gte=three_hours_ago
        ).exists()

        return recent_weather

    def _save_weather_data(self, region, weather_data):
        # 날씨 데이터를 DB에 저장
        saved_count = 0

        with transaction.atomic():
            for forecast in weather_data:
                try:
                    # 예보 시간 파싱
                    forecast_time = timezone.datetime.strptime(
                        forecast["forecast_time"],
                        "%Y-%m-%d %H:%M:%S"
                    )
                    forecast_time = timezone.make_aware(forecast_time)

                    # 중복 체크 및 생성/업데이트 (모든 필드 포함)
                    weather, created = Weather.objects.update_or_create(
                        region=region,
                        forecast_time=forecast_time,
                        defaults={
                            # 기본 날씨 정보
                            "temperature": forecast.get("temperature"),
                            "humidity": forecast.get("humidity"),
                            "precipitation": forecast.get("precipitation"),
                            "sky_code": forecast.get("sky_code"),
                            "precipitation_type": forecast.get("precipitation_type"),
                            "wind_speed": forecast.get("wind_speed"),
                            "wind_direction": forecast.get("wind_direction"),

                            # 생활기상지수
                            "uv_index": forecast.get("uv_index"),
                            "feels_like_temperature": forecast.get("feels_like_temperature"),

                            # 대기질 정보
                            "pm25_value": forecast.get("pm25"),
                            "pm10_value": forecast.get("pm10"),

                            # 일출/일몰 정보
                            "sunrise_time": forecast.get("sunrise_time"),
                            "sunset_time": forecast.get("sunset_time"),

                            # 최저/최고 기온
                            "min_temperature": forecast.get("min_temperature"),
                            "max_temperature": forecast.get("max_temperature"),
                        }
                    )

                    saved_count += 1

                    # 생성/업데이트 로그
                    action = "생성됨" if created else "업데이트됨"
                    self.stdout.write(f"        {forecast_time.strftime('%Y-%m-%d %H:%M')} 예보 {action}")

                except Exception as e:
                    self.stdout.write(f"        예보 저장 실패: {e}")
                    continue

        return saved_count

    def _cleanup_old_weather_data(self):
        # 7일 이상 된 오래된 날씨 데이터 정리
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
        else:
            self.stdout.write("정리할 오래된 데이터 없음")
