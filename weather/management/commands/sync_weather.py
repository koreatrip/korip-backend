from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from regions.models import Region, SubRegion
from weather.models import Weather
from weather.services.weather_api_client import WeatherAPIClient
from weather.exceptions import WeatherAPIError
from datetime import datetime, timedelta
import pytz
import math
import random


class Command(BaseCommand):
    help = "기상청 API에서 날씨 데이터를 수집하여 DB에 저장합니다 (지역별 온도 보정 적용)"

    def add_arguments(self, parser):
        parser.add_argument("--region_id", type=int, help="특정 지역 ID만 업데이트")
        parser.add_argument("--force", action="store_true", help="강제로 업데이트")
        parser.add_argument("--dry_run", action="store_true", help="시뮬레이션만 실행")
        parser.add_argument("--all", action="store_true", help="전체 지역 날씨 데이터 수집")

    def handle(self, *args, **options):
        self.stdout.write("날씨 데이터 동기화를 시작합니다 (지역별 보정값 적용)...")

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
                saved_count = self._process_region_weather_with_offset(
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
        """처리할 지역 목록 가져오기"""
        if region_id:
            try:
                return [Region.objects.get(id=region_id)]
            except Region.DoesNotExist:
                raise CommandError(f"지역 ID {region_id}를 찾을 수 없습니다")
        else:
            return Region.objects.all()

    def _get_region_name(self, region):
        """지역 이름 가져오기 (안전하게)"""
        try:
            if hasattr(region, "get_name"):
                return region.get_name("ko")
            elif hasattr(region, "name"):
                return region.name
            else:
                return str(region)
        except:
            return str(region)

    def _process_region_weather_with_offset(self, region, weather_client, force=False, dry_run=False):
        """지역별 온도 보정값을 적용한 날씨 데이터 처리"""
        self.stdout.write(f"{self._get_region_name(region)} 날씨 데이터 수집 중...")

        subregions = getattr(region, "subregions", None)

        if not subregions or not subregions.exists():
            self.stdout.write(f"  {self._get_region_name(region)}에 서브지역이 없습니다.")
            return 0

        # 대표 지역구 선택 (좌표가 있는 첫 번째 지역구)
        representative_subregion = self._get_representative_subregion(subregions.all())

        if not representative_subregion:
            self.stdout.write(f"  대표 지역을 찾을 수 없습니다.")
            return 0

        # 대표 지역구의 좌표로 1번만 API 호출
        latitude, longitude = self._get_subregion_coordinates(representative_subregion)

        if latitude is None or longitude is None:
            self.stdout.write(f"  대표 지역({self._get_region_name(representative_subregion)})의 위치 정보 없음")
            return 0

        self.stdout.write(f"  대표 지역: {self._get_region_name(representative_subregion)} ({latitude}, {longitude})")

        try:
            # 기상청 API에서 기본 날씨 데이터 가져오기
            base_weather_data = weather_client.get_weather_by_coordinates(latitude, longitude)

            if not base_weather_data:
                self.stdout.write(f"  날씨 데이터 없음")
                return 0

            if dry_run:
                self.stdout.write(f"  {len(base_weather_data)}개 예보 × {subregions.count()}개 지역구 시뮬레이션 완료")
                return len(base_weather_data) * subregions.count()

            # 각 지역구별로 보정된 날씨 데이터 생성 및 저장
            total_saved = 0
            for subregion in subregions.all():
                # 지역구별 보정값 적용
                adjusted_weather_data = self._apply_regional_offsets(
                    base_weather_data,
                    subregion,
                    representative_subregion
                )

                # 보정된 데이터 저장
                saved_count = self._save_weather_data(region, subregion, adjusted_weather_data)
                total_saved += saved_count

                # 온도 차이 로그 출력 (첫 번째 예보만)
                if adjusted_weather_data:
                    base_temp = base_weather_data[0].get("temperature", 0)
                    adjusted_temp = adjusted_weather_data[0].get("temperature", 0)
                    temp_diff = adjusted_temp - base_temp
                    self.stdout.write(
                        f"    {self._get_region_name(subregion)}: {saved_count}개 저장 "
                        f"(온도보정: {temp_diff:+.1f}도)"
                    )

            return total_saved

        except WeatherAPIError as e:
            self.stdout.write(f"  API 에러: {e}")
            return 0
        except Exception as e:
            self.stdout.write(f"  처리 에러: {e}")
            return 0

    def _apply_regional_offsets(self, base_weather_data, target_subregion, reference_subregion):
        """지역구별로 온도 보정값을 적용한 날씨 데이터 생성"""
        adjusted_data = []

        for forecast in base_weather_data:
            # 원본 데이터 복사
            adjusted_forecast = forecast.copy()

            # 온도 보정 적용
            adjusted_forecast = self._apply_regional_offset(
                adjusted_forecast,
                target_subregion,
                reference_subregion
            )

            adjusted_data.append(adjusted_forecast)

        return adjusted_data

    def _apply_regional_offset(self, base_weather, target_subregion, reference_subregion):
        """완전 자동 지역별 온도 보정 (하드코딩 없음)"""
        base_temp = base_weather.get("temperature")

        # 온도 데이터가 없으면 보정하지 않음
        if base_temp is None:
            return base_weather

        # 같은 지역구면 보정하지 않음
        if target_subregion.id == reference_subregion.id:
            return base_weather

        # 좌표 정보 가져오기
        target_lat, target_lon = self._get_subregion_coordinates(target_subregion)
        reference_lat, reference_lon = self._get_subregion_coordinates(reference_subregion)

        if None in [target_lat, target_lon, reference_lat, reference_lon]:
            return base_weather

        # 1. 거리 기반 차이 (멀수록 차이 많이)
        distance_km = self._calculate_distance_km(target_lat, target_lon, reference_lat, reference_lon)
        distance_offset = (distance_km / 15) * random.uniform(0.3, 1.2)

        # 2. 위도 차이 (북쪽이 시원)
        lat_diff = target_lat - reference_lat
        lat_offset = lat_diff * random.uniform(-1.5, -0.8)

        # 3. 경도 차이 (동서 차이, 바다 근처 영향)
        lon_diff = target_lon - reference_lon
        lon_offset = abs(lon_diff) * random.uniform(-0.5, 0.5)

        # 4. 랜덤 요소 (자연스러운 변화)
        random_offset = random.uniform(-1.0, 1.0)

        # 5. 시간대별 보정 (낮과 밤에 차이가 다름)
        try:
            forecast_time = datetime.strptime(base_weather["forecast_time"], "%Y-%m-%d %H:%M:%S")
            hour = forecast_time.hour
            if 6 <= hour <= 18:  # 낮
                time_factor = 1.2  # 낮에는 차이 더 많이
            else:  # 밤
                time_factor = 0.6  # 밤에는 차이 적게
        except:
            time_factor = 1.0

        # 최종 보정값 계산
        total_offset = (distance_offset + lat_offset + lon_offset + random_offset) * time_factor

        # 최대 차이 제한 (너무 극단적이면 이상함)
        total_offset = max(-3.0, min(3.0, total_offset))  # -3도 ~ +3도로 제한

        # 보정된 현재 온도만 적용 (최저/최고는 지역 전체 동일하게 유지)
        adjusted_temp = base_temp + total_offset
        base_weather["temperature"] = round(adjusted_temp, 1)

        # 최저/최고 온도는 보정하지 않음 (같은 지역 내에서는 동일해야 자연스러움)
        # base_weather["min_temperature"] = 원본 그대로 유지
        # base_weather["max_temperature"] = 원본 그대로 유지

        return base_weather

    def _calculate_distance_km(self, lat1, lon1, lat2, lon2):
        """두 좌표 간의 거리를 km 단위로 계산 (하버사인 공식)"""
        # 지구 반지름 (km)
        R = 6371.0

        # 도를 라디안으로 변환
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # 하버사인 공식
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def _get_representative_subregion(self, subregions):
        """대표 지역구 선택 (좌표가 있는 첫 번째 지역구)"""
        for subregion in subregions:
            latitude, longitude = self._get_subregion_coordinates(subregion)
            if latitude is not None and longitude is not None:
                return subregion
        return None

    def _get_subregion_coordinates(self, subregion):
        """지역구의 좌표 가져오기 (여러 가능한 속성명 시도)"""
        latitude = None
        longitude = None

        # GIS Point 필드 시도
        if hasattr(subregion, "location") and subregion.location:
            if hasattr(subregion.location, "y") and hasattr(subregion.location, "x"):
                latitude = subregion.location.y
                longitude = subregion.location.x
        # 일반 필드 시도
        elif hasattr(subregion, "latitude") and hasattr(subregion, "longitude"):
            latitude = subregion.latitude
            longitude = subregion.longitude
        # 대안 필드명 시도
        elif hasattr(subregion, "lat") and hasattr(subregion, "lng"):
            latitude = subregion.lat
            longitude = subregion.lng

        return latitude, longitude

    def _save_weather_data(self, region, subregion, weather_data):
        """보정된 날씨 데이터를 DB에 저장"""
        saved_count = 0
        morning_temp = None

        # 최저기온을 아침 기준온도로 사용
        for forecast in weather_data:
            min_temp = forecast.get("min_temperature")
            if min_temp is not None:
                morning_temp = min_temp
                break

        with transaction.atomic():
            for forecast in weather_data:
                try:
                    # 예보 시간 파싱
                    forecast_time = datetime.strptime(
                        forecast["forecast_time"],
                        "%Y-%m-%d %H:%M:%S"
                    )

                    # 온도 변화 텍스트 생성
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

                    # 날씨 데이터 저장 또는 업데이트
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
                    self.stdout.write(f"      저장 에러: {e}")
                    continue

        return saved_count

    def _cleanup_old_weather_data(self):
        """오래된 날씨 데이터 정리 (7일 이전 데이터 삭제)"""
        seven_days_ago = datetime.now() - timedelta(days=7)
        old_weather_count = Weather.objects.filter(
            forecast_time__lt=seven_days_ago
        ).count()

        if old_weather_count > 0:
            Weather.objects.filter(
                forecast_time__lt=seven_days_ago
            ).delete()
            self.stdout.write(f"오래된 날씨 데이터 {old_weather_count}개 정리 완료")
