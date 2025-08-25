# weather/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from datetime import datetime, timedelta
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone

from weather.serializers import WeatherResponseSerializer
from weather.models import Weather

logger = logging.getLogger(__name__)


class WeatherBaseView:

    def _get_weather_condition(self, forecast):
        # 날씨 상태 텍스트 변환
        try:
            if hasattr(forecast, 'sky_code'):
                sky_code = forecast.sky_code
                precipitation = forecast.precipitation_type
            else:
                sky_code = forecast.get("sky_condition", 1)
                precipitation = forecast.get("precipitation_type", 0)

            sky_code = int(sky_code) if sky_code is not None else 1
            precipitation = int(precipitation) if precipitation is not None else 0

            if precipitation > 0:
                return "비" if precipitation == 1 else "눈"

            if sky_code == 1:
                return "맑음"
            elif sky_code == 3:
                return "구름많음"
            else:
                return "흐림"
        except Exception as e:
            return "알수없음"

    def _get_pm_grade(self, value, pm_type="pm25"):
        # 미세먼지 등급 계산
        try:
            if value is None or value == "":
                return "데이터없음"

            if isinstance(value, str):
                import re
                numbers = re.findall(r'\d+\.?\d*', value)
                if numbers:
                    value = float(numbers[0])
                else:
                    return "데이터없음"

            value = float(value)

        except (ValueError, TypeError) as e:
            return "데이터없음"

        try:
            if pm_type == "pm25":
                if value <= 15:
                    return "좋음"
                elif value <= 35:
                    return "보통"
                elif value <= 75:
                    return "나쁨"
                else:
                    return "매우나쁨"
            else:  # pm10
                if value <= 30:
                    return "좋음"
                elif value <= 80:
                    return "보통"
                elif value <= 150:
                    return "나쁨"
                else:
                    return "매우나쁨"
        except Exception as e:
            return "데이터없음"

    def _get_travel_tip(self, forecast, location_name=""):
        # 여행 팁 생성
        return "여행 팁 기능은 현재 비활성화 상태입니다."

    def _calculate_temperature_change(self, current_weather):
        # 아침 기온 대비 현재 기온 변화 계산
        try:
            if current_weather.temperature and current_weather.min_temperature:
                temp_diff = float(current_weather.temperature) - float(current_weather.min_temperature)

                if temp_diff > 0:
                    return f"아침보다 {temp_diff:.1f}°↑"
                elif temp_diff < 0:
                    return f"아침보다 {abs(temp_diff):.1f}°↓"
                else:
                    return "아침과 같음"
            else:
                return "+0.0°"
        except Exception as e:
            return "+0.0°"

    def _get_hourly_forecast_from_db(self, region_id, sub_region_id=None, hours=15):
        # DB에서 현재 시간부터 15시간 예보 데이터 조회
        now = timezone.now()
        # 현재 시간이 07:49라면 08:00부터 시작 (다음 정시)
        if now.minute > 0:
            current_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        else:
            current_hour = now.replace(minute=0, second=0, microsecond=0)
        end_time = current_hour + timedelta(hours=hours)

        # Weather 모델에서 해당 시간대 데이터 조회
        weather_query = Weather.objects.filter(
            region_id=region_id,
            forecast_time__gte=current_hour,
            forecast_time__lt=end_time
        ).order_by('forecast_time')

        if sub_region_id:
            weather_query = weather_query.filter(sub_region_id=sub_region_id)

        weather_data = list(weather_query)

        hourly_forecast = []
        for i in range(hours):
            forecast_time = current_hour + timedelta(hours=i)

            # 해당 시간의 데이터 찾기
            matching_data = next(
                (w for w in weather_data
                 if w.forecast_time.replace(tzinfo=None) == forecast_time.replace(tzinfo=None)),
                None
            )

            # 한국 시간으로 변환해서 표시
            korea_time = forecast_time.astimezone()

            if matching_data:
                hourly_forecast.append({
                    "time": f"{korea_time.hour}시",
                    "weather_condition": self._get_weather_condition(matching_data),
                    "temperature": float(matching_data.temperature) if matching_data.temperature else 20.0,
                    "precipitation_probability": int(matching_data.precipitation) if matching_data.precipitation else 0
                })
            else:
                hourly_forecast.append({
                    "time": f"{korea_time.hour}시",
                    "weather_condition": "알수없음",
                    "temperature": 20.0,
                    "precipitation_probability": 0
                })

        return hourly_forecast


class WeatherAPI(APIView, WeatherBaseView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="get_weather",
        operation_summary="날씨 정보 조회",
        operation_description="""
        지역별 또는 지역구별 현재 날씨 및 예보 정보를 조회합니다.

        **기능:**
        - 지역별 날씨 조회 (subregion_id 미제공시)
        - 지역구별 상세 날씨 조회 (subregion_id 제공시)
        - 현재 날씨, 내일 예보, 시간별 예보, 대기질 정보 포함

        **사용 예시:**
        - 서울 전체 날씨: `/api/weather/1/`
        - 강남구 날씨: `/api/weather/1/?subregion_id=5`
        """,
        manual_parameters=[
            openapi.Parameter(
                "region_id",
                openapi.IN_PATH,
                description="지역 ID (필수)",
                type=openapi.TYPE_INTEGER,
                required=True,
                example=1
            ),
            openapi.Parameter(
                "subregion_id",
                openapi.IN_QUERY,
                description="지역구 ID (선택사항). 제공되면 해당 지역구의 상세 날씨 조회",
                type=openapi.TYPE_INTEGER,
                required=False,
                example=5
            )
        ],
        responses={
            200: openapi.Response(
                description="날씨 정보 조회 성공",
                schema=WeatherResponseSerializer,
                examples={
                    "application/json": {
                        "current_weather": {
                            "current_date": "08.22",
                            "temperature": 25.5,
                            "weather_condition": "맑음",
                            "temperature_change": "+2.1°",
                            "min_temperature": 18.0,
                            "max_temperature": 28.0
                        },
                        "tomorrow_weather": {
                            "tomorrow_date": "08.23",
                            "min_temperature": 19.0,
                            "max_temperature": 29.0,
                            "morning_condition": "흐림",
                            "morning_precipitation": 10,
                            "afternoon_condition": "맑음",
                            "afternoon_precipitation": 0
                        },
                        "detail_info": {
                            "feels_like": 27.0,
                            "humidity": 65,
                            "uv_index": 7,
                            "uv_level": "높음",
                            "wind_speed": 3.2,
                            "sunrise": "06:05",
                            "sunset": "19:25",
                            "air_quality_status": "좋음"
                        },
                        "hourly_forecast": [
                            {
                                "time": "1시",
                                "weather_condition": "맑음",
                                "temperature": 25.5,
                                "precipitation_probability": 0
                            }
                        ],
                        "air_quality": {
                            "pm25_value": 12,
                            "pm25_grade": "좋음",
                            "pm10_value": 25,
                            "pm10_grade": "좋음"
                        },
                        "travel_tip": {
                            "tip_message": "야외 활동하기 좋은 날씨입니다."
                        },
                        "location_name": "서울특별시",
                        "latitude": 37.5665,
                        "longitude": 126.9780,
                        "last_updated": "2025-08-22T14:30:00"
                    }
                }
            ),
            400: openapi.Response(
                description="잘못된 요청 파라미터",
                examples={
                    "application/json": {
                        "error": "잘못된 지역 ID입니다.",
                        "details": "region_id는 양의 정수여야 합니다."
                    }
                }
            ),
            404: openapi.Response(
                description="지역 또는 날씨 데이터를 찾을 수 없음",
                examples={
                    "application/json": {
                        "error": "'서울특별시' 지역의 날씨 데이터가 없습니다. 날씨 동기화를 먼저 실행해주세요.",
                        "hint": "python manage.py sync_weather --region_id=1 명령어를 실행하세요."
                    }
                }
            ),
            500: openapi.Response(
                description="서버 내부 오류",
                examples={
                    "application/json": {
                        "error": "날씨 조회 중 오류가 발생했습니다.",
                        "details": "Database connection timeout"
                    }
                }
            )
        },
        tags=["날씨"]
    )
    def get(self, request, region_id):
        # subregion_id 쿼리 파라미터 확인
        subregion_id = request.GET.get("subregion_id")

        if subregion_id:
            return self._get_subregion_weather(request, region_id, subregion_id)
        else:
            return self._get_region_weather(request, region_id)

    def _get_region_weather(self, request, region_id):
        try:
            from regions.models import Region

            region = Region.objects.get(id=region_id)
            region_name = region.get_name("ko")

            # 현재 시간 기준으로 가장 가까운 예보 시간의 날씨 데이터 조회
            now = timezone.now()
            current_weather = Weather.objects.filter(
                region_id=region_id,
                forecast_time__gte=now
            ).order_by("forecast_time").first()

            if not current_weather:
                return Response({
                    "error": f"'{region_name}' 지역의 날씨 데이터가 없습니다. 날씨 동기화를 먼저 실행해주세요.",
                    "hint": f"python manage.py sync_weather --region_id={region_id} 명령어를 실행하세요."
                }, status=status.HTTP_404_NOT_FOUND)

            # 시간별 예보 데이터 조회 (현재 시간부터 15시간)
            hourly_forecast = self._get_hourly_forecast_from_db(region_id, hours=15)

        except Region.DoesNotExist:
            return Response({
                "error": "존재하지 않는 지역입니다."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"지역 날씨 조회 오류: {str(e)}")
            return Response({
                "error": f"지역 정보 조회 중 오류가 발생했습니다: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            response_data = self._transform_to_ui_format(
                current_weather, region_name, hourly_forecast
            )
            serializer = WeatherResponseSerializer(data=response_data)

            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "데이터 형식 오류",
                    "details": serializer.errors
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"날씨 데이터 변환 오류: {str(e)}")
            return Response({
                "error": "날씨 조회 중 오류가 발생했습니다.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_subregion_weather(self, request, region_id, subregion_id):
        try:
            from regions.models import Region, SubRegion

            region = Region.objects.get(id=region_id)
            region_name = region.get_name("ko")

            subregion = SubRegion.objects.get(id=subregion_id, region=region)
            subregion_name = subregion.get_name("ko")

            # 현재 시간 기준으로 가장 가까운 예보 시간의 날씨 데이터 조회
            now = timezone.now()
            current_weather = Weather.objects.filter(
                sub_region_id=subregion_id,
                forecast_time__gte=now
            ).order_by("forecast_time").first()

            if not current_weather:
                return Response({
                    "error": f"'{region_name} {subregion_name}' 지역의 날씨 데이터가 없습니다. 날씨 동기화를 먼저 실행해주세요.",
                    "hint": f"python manage.py sync_weather --region_id={region_id} 명령어를 실행하세요."
                }, status=status.HTTP_404_NOT_FOUND)

            # 시간별 예보 데이터 조회 (현재 시간부터 15시간)
            hourly_forecast = self._get_hourly_forecast_from_db(region_id, subregion_id, hours=15)

        except Region.DoesNotExist:
            return Response({
                "error": "존재하지 않는 지역입니다."
            }, status=status.HTTP_404_NOT_FOUND)
        except SubRegion.DoesNotExist:
            return Response({
                "error": "존재하지 않는 지역구이거나 해당 지역에 속하지 않습니다."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"지역구 날씨 조회 오류: {str(e)}")
            return Response({
                "error": f"지역구 정보 조회 중 오류가 발생했습니다: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            response_data = self._transform_to_ui_format_subregion(
                current_weather, region_name, subregion_name, hourly_forecast
            )

            serializer = WeatherResponseSerializer(data=response_data)
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "데이터 형식 오류",
                    "details": serializer.errors
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"지역구 날씨 데이터 변환 오류: {str(e)}")
            return Response({
                "error": "날씨 조회 중 오류가 발생했습니다.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _transform_to_ui_format(self, current_weather, region_name, hourly_forecast):
        # Weather 모델을 UI 형식으로 변환
        try:
            now = timezone.now()
            tomorrow = now + timedelta(days=1)

            # 내일 날씨 데이터 조회
            tomorrow_weather = Weather.objects.filter(
                region=current_weather.region,
                forecast_time__date=tomorrow.date()
            ).order_by('forecast_time').first()

            def safe_get(obj, field, default=0):
                value = getattr(obj, field, default)
                if value is None:
                    return default
                try:
                    return float(value) if isinstance(default, float) else int(value)
                except:
                    return default

            weather_condition = self._get_weather_condition(current_weather)
            pm25_grade = self._get_pm_grade(current_weather.pm25)
            pm10_grade = self._get_pm_grade(current_weather.pm10, pm_type="pm10")
            travel_tip = self._get_travel_tip(current_weather, region_name)

            # 아침 기온 대비 계산
            temperature_change = self._calculate_temperature_change(current_weather)

            return {
                "current_weather": {
                    "current_date": now.strftime("%m.%d"),
                    "temperature": safe_get(current_weather, "temperature", 20.0),
                    "weather_condition": weather_condition,
                    "temperature_change": temperature_change,
                    "min_temperature": safe_get(current_weather, "min_temperature", 15.0),
                    "max_temperature": safe_get(current_weather, "max_temperature", 25.0),
                },
                "tomorrow_weather": {
                    "tomorrow_date": tomorrow.strftime("%m.%d"),
                    "min_temperature": safe_get(tomorrow_weather, "min_temperature",
                                                15.0) if tomorrow_weather else 15.0,
                    "max_temperature": safe_get(tomorrow_weather, "max_temperature",
                                                25.0) if tomorrow_weather else 25.0,
                    "morning_condition": self._get_weather_condition(
                        tomorrow_weather) if tomorrow_weather else weather_condition,
                    "morning_precipitation": safe_get(tomorrow_weather, "precipitation", 0) if tomorrow_weather else 0,
                    "afternoon_condition": self._get_weather_condition(
                        tomorrow_weather) if tomorrow_weather else weather_condition,
                    "afternoon_precipitation": safe_get(tomorrow_weather, "precipitation",
                                                        0) if tomorrow_weather else 0,
                },
                "detail_info": {
                    "feels_like": safe_get(current_weather, "feels_like_temperature",
                                           safe_get(current_weather, "temperature", 20.0)),
                    "humidity": safe_get(current_weather, "humidity", 50),
                    "uv_index": safe_get(current_weather, "uv_index", 0),
                    "uv_level": "보통",
                    "wind_speed": safe_get(current_weather, "wind_speed", 0.0),
                    "sunrise": current_weather.sunrise_time.strftime(
                        "%H:%M") if current_weather.sunrise_time else "06:00",
                    "sunset": current_weather.sunset_time.strftime("%H:%M") if current_weather.sunset_time else "18:00",
                    "air_quality_status": "보통",
                },
                "hourly_forecast": hourly_forecast,
                "air_quality": {
                    "pm25_value": int(safe_get(current_weather, "pm25", 15)),
                    "pm25_grade": pm25_grade,
                    "pm10_value": int(safe_get(current_weather, "pm10", 30)),
                    "pm10_grade": pm10_grade,
                },
                "travel_tip": {
                    "tip_message": travel_tip
                },
                "location_name": region_name,
                "latitude": 37.5665,
                "longitude": 126.9780,
                "last_updated": current_weather.updated_at.isoformat(),
            }

        except Exception as e:
            raise ValueError(f"데이터 변환 중 오류: {str(e)}")

    def _transform_to_ui_format_subregion(self, current_weather, region_name, subregion_name, hourly_forecast):
        # Weather 모델을 지역구 UI 형식으로 변환
        try:
            now = timezone.now()
            tomorrow = now + timedelta(days=1)

            # 내일 날씨 데이터 조회
            tomorrow_weather = Weather.objects.filter(
                sub_region=current_weather.sub_region,
                forecast_time__date=tomorrow.date()
            ).order_by('forecast_time').first()

            def safe_get(obj, field, default=0):
                value = getattr(obj, field, default)
                if value is None:
                    return default
                try:
                    return float(value) if isinstance(default, float) else int(value)
                except:
                    return default

            weather_condition = self._get_weather_condition(current_weather)
            pm25_grade = self._get_pm_grade(current_weather.pm25)
            pm10_grade = self._get_pm_grade(current_weather.pm10, pm_type="pm10")
            travel_tip = self._get_travel_tip(current_weather, f"{region_name} {subregion_name}")

            # 아침 기온 대비 계산
            temperature_change = self._calculate_temperature_change(current_weather)

            return {
                "current_weather": {
                    "current_date": now.strftime("%m.%d"),
                    "temperature": safe_get(current_weather, "temperature", 20.0),
                    "weather_condition": weather_condition,
                    "temperature_change": temperature_change,
                    "min_temperature": safe_get(current_weather, "min_temperature", 15.0),
                    "max_temperature": safe_get(current_weather, "max_temperature", 25.0),
                },
                "tomorrow_weather": {
                    "tomorrow_date": tomorrow.strftime("%m.%d"),
                    "min_temperature": safe_get(tomorrow_weather, "min_temperature",
                                                15.0) if tomorrow_weather else 15.0,
                    "max_temperature": safe_get(tomorrow_weather, "max_temperature",
                                                25.0) if tomorrow_weather else 25.0,
                    "morning_condition": self._get_weather_condition(
                        tomorrow_weather) if tomorrow_weather else weather_condition,
                    "morning_precipitation": safe_get(tomorrow_weather, "precipitation", 0) if tomorrow_weather else 0,
                    "afternoon_condition": self._get_weather_condition(
                        tomorrow_weather) if tomorrow_weather else weather_condition,
                    "afternoon_precipitation": safe_get(tomorrow_weather, "precipitation",
                                                        0) if tomorrow_weather else 0,
                },
                "detail_info": {
                    "feels_like": safe_get(current_weather, "feels_like_temperature",
                                           safe_get(current_weather, "temperature", 20.0)),
                    "humidity": safe_get(current_weather, "humidity", 50),
                    "uv_index": safe_get(current_weather, "uv_index", 0),
                    "uv_level": "보통",
                    "wind_speed": safe_get(current_weather, "wind_speed", 0.0),
                    "sunrise": current_weather.sunrise_time.strftime(
                        "%H:%M") if current_weather.sunrise_time else "06:00",
                    "sunset": current_weather.sunset_time.strftime("%H:%M") if current_weather.sunset_time else "18:00",
                    "air_quality_status": "보통",
                },
                "hourly_forecast": hourly_forecast,
                "air_quality": {
                    "pm25_value": int(safe_get(current_weather, "pm25", 15)),
                    "pm25_grade": pm25_grade,
                    "pm10_value": int(safe_get(current_weather, "pm10", 30)),
                    "pm10_grade": pm10_grade,
                },
                "travel_tip": {
                    "tip_message": travel_tip
                },
                "location_name": f"{region_name} {subregion_name}",
                "latitude": 37.5735,
                "longitude": 126.9788,
                "last_updated": current_weather.updated_at.isoformat(),
            }
        except Exception as e:
            raise ValueError(f"데이터 변환 중 오류: {str(e)}")
