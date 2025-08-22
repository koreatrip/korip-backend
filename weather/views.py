from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from datetime import datetime, timedelta
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from weather.serializers import WeatherResponseSerializer
from weather.models import Weather

logger = logging.getLogger(__name__)


class WeatherBaseView:

    def _get_weather_condition(self, forecast):
        # 날씨 상태 텍스트 변환
        try:
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
        # 여행 팁 생성 - 임시 주석 처리
        return "여행 팁 기능은 현재 비활성화 상태입니다."

        # try:
        #     def safe_float(value, default=0.0):
        #         try:
        #             if value is None or value == "":
        #                 return default
        #             return float(str(value))
        #         except:
        #             return default

        #     def safe_int(value, default=0):
        #         try:
        #             if value is None or value == "":
        #                 return default
        #             return int(float(str(value)))
        #         except:
        #             return default

        #     temp = safe_float(forecast.get("temperature"), 20.0)
        #     pm25 = safe_float(forecast.get("pm25"), 15.0)
        #     pm10 = safe_float(forecast.get("pm10"), 30.0)
        #     humidity = safe_int(forecast.get("humidity"), 50)
        #     precipitation = safe_int(forecast.get("precipitation"), 0)
        #     wind_speed = safe_float(forecast.get("wind_speed"), 0.0)
        #     uv_index = safe_int(forecast.get("uv_index"), 0)

        #     # 극한 추위
        #     if temp < -5:
        #         return f"{location_name}은 매우 추운 혹한기 날씨입니다. 두꺼운 패딩, 목도리, 장갑을 필수로 착용하시고 실내 관광지나 온천, 찜질방 방문을 강력히 추천합니다. 야외활동은 되도록 짧게 하시고 따뜻한 음료를 자주 드세요."

        #     # 추위
        #     elif temp <= 5:
        #         return f"{location_name}은 쌀쌀한 날씨입니다. 따뜻한 코트나 패딩을 착용하시고 목도리와 장갑도 준비하세요. 실내 박물관, 미술관, 대형 쇼핑몰이나 따뜻한 카페에서 시간을 보내시는 것을 추천합니다. 야외 관광 시에는 핫팩을 준비하세요."

        #     # 폭염
        #     elif temp >= 35:
        #         return f"{location_name}은 폭염 경보 수준의 매우 더운 날씨입니다. 가급적 오전 일찍이나 저녁 늦게 야외활동을 하시고, 낮에는 에어컨이 잘 되는 백화점, 대형마트, 영화관, 박물관 등 실내 관광지 방문을 권합니다. 충분한 수분 섭취와 자외선 차단제 필수입니다."

        #     # 매우 더움
        #     elif temp >= 30:
        #         return f"{location_name}은 무더운 여름 날씨입니다. 시원한 실내 관광지나 에어컨이 잘 되는 카페, 쇼핑몰에서 더위를 피하세요. 야외활동 시에는 양산이나 모자, 자외선 차단제를 꼭 준비하시고 시원한 음료를 자주 드시기 바랍니다."

        #     # 폭우 예상
        #     elif precipitation >= 80:
        #         return f"{location_name}은 폭우가 예상되는 날씨입니다. 우산과 우비를 필수로 준비하시고 가급적 실내 관광지인 박물관, 미술관, 대형 쇼핑몰, 전통시장 실내 구역 방문을 추천합니다. 교통편 지연 가능성도 염두에 두시고 여유 있는 일정을 계획하세요."

        #     # 비 예상
        #     elif precipitation >= 60:
        #         return f"{location_name}은 비가 올 확률이 높은 날씨입니다. 우산을 꼭 휴대하시고 실내 활동 위주로 계획하세요. 카페 투어, 실내 시장 구경, 백화점 쇼핑이나 스파, 찜질방 방문이 좋겠습니다. 우천 시 미끄러운 길 조심하세요."

        #     # 최악의 대기질
        #     elif pm25 > 75:
        #         return f"{location_name}은 미세먼지 농도가 매우 나쁜 상태입니다. KF94 이상 마스크를 반드시 착용하시고 야외활동을 최대한 자제하세요. 실내 관광지인 백화점, 대형마트, 영화관, 박물관 방문을 권하며, 외출 후에는 깨끗이 씻고 충분한 수분을 섭취하세요."

        #     # 나쁜 대기질
        #     elif pm25 > 35:
        #         return f"{location_name}은 미세먼지가 다소 나쁜 상태입니다. 보건용 마스크 착용을 권장하며 장시간 야외활동보다는 실내 관광지나 카페에서 시간을 보내세요. 야외활동 시에는 자주 휴식을 취하고 물을 충분히 드시기 바랍니다."

        #     # 강풍 주의
        #     elif wind_speed >= 10:
        #         return f"{location_name}은 바람이 매우 강한 날씨입니다. 모자나 스카프가 날아갈 수 있으니 주의하세요. 높은 곳이나 해안가 관광 시 특히 조심하시고, 가급적 실내 관광지나 바람이 덜한 실내 시장, 지하상가 방문을 추천합니다."

        #     # 습하고 더움
        #     elif humidity >= 80 and temp >= 25:
        #         return f"{location_name}은 덥고 습한 무더위 날씨입니다. 통풍이 잘 되는 면 소재 옷을 입으시고 땀 흡수가 좋은 옷차림을 권합니다. 에어컨이 잘 되는 실내 관광지에서 휴식을 자주 취하시고 탈수 방지를 위해 물을 자주 드세요."

        #     # 건조함 주의
        #     elif humidity <= 30:
        #         return f"{location_name}은 공기가 매우 건조한 날씨입니다. 충분한 수분 섭취와 립밤, 핸드크림 사용을 권장합니다. 정전기 방지를 위해 천연 소재 옷을 입으시고, 가습기가 있는 카페나 실내 관광지에서 휴식을 취하세요."

        #     # 자외선 매우 강함
        #     elif uv_index >= 8:
        #         return f"{location_name}은 자외선이 매우 강한 날씨입니다. SPF 50 이상의 자외선 차단제를 2-3시간마다 덧발라 주시고 모자, 선글라스, 긴팔 옷을 착용하세요. 그늘진 곳에서 자주 휴식을 취하시고 10시-16시 사이 야외활동은 피해주세요."

        #     # 완벽한 날씨
        #     elif 20 <= temp <= 25 and 40 <= humidity <= 60 and precipitation <= 20:
        #         return f"{location_name}은 관광하기에 완벽한 날씨입니다! 야외 관광지 투어, 공원 산책, 한강이나 바다 구경, 고궁 탐방 등 어떤 활동이든 즐겁게 하실 수 있어요. 가벼운 외투 하나 정도만 준비하시면 완벽한 하루가 될 것 같습니다!"

        #     # 쾌적한 봄/가을 날씨
        #     elif 15 <= temp <= 20:
        #         return f"{location_name}은 쾌적한 봄/가을 날씨입니다. 가벼운 외투나 카디건을 준비하시고 야외 관광지나 공원 산책, 고궁 투어를 즐겨보세요. 일교차가 있을 수 있으니 얇은 겉옷을 하나 더 준비하시면 좋겠습니다."

        #     # 쌀쌀한 날씨
        #     elif 10 <= temp <= 15:
        #         return f"{location_name}은 쌀쌀하지만 나쁘지 않은 날씨입니다. 따뜻한 옷차림으로 야외 관광도 충분히 즐기실 수 있어요. 실내외를 오가며 관광하기 좋은 날씨이니 박물관과 궁궐 투어를 병행해보세요. 따뜻한 음료 한 잔의 여유도 즐겨보세요."

        #     # 서늘한 날씨
        #     elif 5 <= temp <= 10:
        #         return f"{location_name}은 서늘한 날씨입니다. 따뜻한 코트나 점퍼를 착용하시고 목도리를 준비하세요. 실내 관광지와 따뜻한 카페를 위주로 일정을 계획하시되, 짧은 야외 산책도 나쁘지 않습니다. 온천이나 찜질방도 추천해요."

        #     # 소나기 가능성
        #     elif 30 <= precipitation <= 59:
        #         return f"{location_name}은 소나기가 올 수 있는 날씨입니다. 접이식 우산을 꼭 가지고 다니시고 실내외 관광을 적절히 섞어서 계획하세요. 갑작스러운 비에 대비해 지하상가나 백화점 위치를 미리 파악해두시면 좋겠습니다."

        #     # 대기질 좋음 + 좋은 날씨
        #     elif pm25 <= 15 and 18 <= temp <= 28:
        #         return f"{location_name}은 대기가 매우 깨끗하고 기온도 적당한 최고의 관광 날씨입니다! 야외 활동을 마음껏 즐기세요. 한강공원, 남산, 해안가 산책이나 등산, 자전거 투어 등 어떤 야외활동이든 추천합니다. 깊게 숨쉬며 한국의 아름다운 자연을 만끽하세요!"

        #     # 미지근한 날씨
        #     elif 26 <= temp <= 29 and humidity <= 70:
        #         return f"{location_name}은 따뜻하고 쾌적한 여름 날씨입니다. 반팔과 얇은 겉옷을 준비하시고 야외 관광지나 공원에서 시간을 보내기 좋습니다. 시원한 음료수나 아이스크림을 즐기며 여유로운 관광을 즐겨보세요. 저녁에는 야외 테라스가 있는 카페도 좋겠어요."

        #     # 기본 좋은 날씨
        #     else:
        #         return f"{location_name}은 관광하기 좋은 날씨입니다! 편안한 옷차림으로 원하시는 관광지를 자유롭게 둘러보세요. 실내외 관광지를 적절히 섞어서 알찬 하루를 보내시기 바랍니다. 즐거운 한국 여행 되세요!"

        # except Exception as e:
        #     return f"{location_name} 날씨 정보를 처리할 수 없습니다."


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
            # 지역구별 날씨 조회
            return self._get_subregion_weather(request, region_id, subregion_id)
        else:
            # 지역별 날씨 조회
            return self._get_region_weather(request, region_id)

    def _get_region_weather(self, request, region_id):
        try:
            from regions.models import Region

            region = Region.objects.get(id=region_id)
            region_name = region.get_name("ko")

            # DB에서 날씨 데이터 조회
            weather_queryset = Weather.objects.filter(
                region_id=region_id,
                created_at__date__gte=datetime.now().date()
            ).order_by("created_at")

            if not weather_queryset.exists():
                return Response({
                    "error": f"'{region_name}' 지역의 날씨 데이터가 없습니다. 날씨 동기화를 먼저 실행해주세요.",
                    "hint": f"python manage.py sync_weather --region_id={region_id} 명령어를 실행하세요."
                }, status=status.HTTP_404_NOT_FOUND)

            # 첫 번째 날씨 데이터 가져오기
            current_weather = weather_queryset.first()

            # Weather 모델을 API 응답 형태로 변환
            weather_data = [{
                "temperature": current_weather.temperature,
                "humidity": current_weather.humidity,
                "precipitation": current_weather.precipitation,
                "sky_condition": current_weather.sky_code,
                "precipitation_type": current_weather.precipitation_type,
                "wind_speed": current_weather.wind_speed,
                "wind_direction": current_weather.wind_direction,
                "feels_like_temperature": current_weather.feels_like_temperature,
                "uv_index": current_weather.uv_index,
                "pm25": current_weather.pm25,
                "pm10": current_weather.pm10,
                "sunrise_time": current_weather.sunrise_time.strftime(
                    "%H:%M") if current_weather.sunrise_time else "06:00",
                "sunset_time": current_weather.sunset_time.strftime(
                    "%H:%M") if current_weather.sunset_time else "18:00",
                "min_temperature": current_weather.min_temperature,
                "max_temperature": current_weather.max_temperature,
                "forecast_time": current_weather.forecast_time.strftime("%Y-%m-%d %H:%M"),
                "created_date": current_weather.created_at.strftime("%Y-%m-%d")
            }]

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
            response_data = self._transform_to_ui_format(weather_data, region_id, region_name)
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

            # DB에서 해당 지역구의 날씨 데이터 조회
            weather_queryset = Weather.objects.filter(
                sub_region_id=subregion_id,
                created_at__date__gte=datetime.now().date()
            ).order_by("created_at")

            if not weather_queryset.exists():
                return Response({
                    "error": f"'{region_name} {subregion_name}' 지역의 날씨 데이터가 없습니다. 날씨 동기화를 먼저 실행해주세요.",
                    "hint": f"python manage.py sync_weather --region_id={region_id} 명령어를 실행하세요."
                }, status=status.HTTP_404_NOT_FOUND)

            # 첫 번째 날씨 데이터 가져오기
            current_weather = weather_queryset.first()

            # Weather 모델을 API 응답 형태로 변환
            weather_data = [{
                "temperature": current_weather.temperature,
                "humidity": current_weather.humidity,
                "precipitation": current_weather.precipitation,
                "sky_condition": current_weather.sky_code,
                "precipitation_type": current_weather.precipitation_type,
                "wind_speed": current_weather.wind_speed,
                "wind_direction": current_weather.wind_direction,
                "feels_like_temperature": current_weather.feels_like_temperature,
                "uv_index": current_weather.uv_index,
                "pm25": current_weather.pm25,
                "pm10": current_weather.pm10,
                "sunrise_time": current_weather.sunrise_time.strftime(
                    "%H:%M") if current_weather.sunrise_time else "06:00",
                "sunset_time": current_weather.sunset_time.strftime(
                    "%H:%M") if current_weather.sunset_time else "18:00",
                "min_temperature": current_weather.min_temperature,
                "max_temperature": current_weather.max_temperature,
                "forecast_time": current_weather.forecast_time.strftime("%Y-%m-%d %H:%M"),
                "created_date": current_weather.created_at.strftime("%Y-%m-%d")
            }]

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
                weather_data, region_id, region_name, subregion_id, subregion_name
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

    def _transform_to_ui_format(self, raw_data, region_id, region_name):
        try:
            if not raw_data:
                raise ValueError("날씨 데이터가 없습니다")

            current = raw_data[0]

            weather_condition = self._get_weather_condition(current)
            pm25_grade = self._get_pm_grade(current.get("pm25", 15))
            pm10_grade = self._get_pm_grade(current.get("pm10", 30), pm_type="pm10")
            travel_tip = self._get_travel_tip(current, region_name)

            # 날짜 계산
            now = datetime.now()
            tomorrow = now + timedelta(days=1)

            # 안전한 값 추출
            def safe_get(key, default=0):
                value = current.get(key, default)
                if value is None:
                    return default
                try:
                    return float(value) if isinstance(default, float) else int(value)
                except:
                    return default

            return {
                "current_weather": {
                    "current_date": now.strftime("%m.%d"),
                    "temperature": safe_get("temperature", 20.0),
                    "weather_condition": weather_condition,
                    "temperature_change": "+0.0°",
                    "min_temperature": safe_get("min_temperature", 15.0),
                    "max_temperature": safe_get("max_temperature", 25.0),
                },

                "tomorrow_weather": {
                    "tomorrow_date": tomorrow.strftime("%m.%d"),
                    "min_temperature": safe_get("min_temperature", 15.0),
                    "max_temperature": safe_get("max_temperature", 25.0),
                    "morning_condition": weather_condition,
                    "morning_precipitation": safe_get("precipitation", 0),
                    "afternoon_condition": weather_condition,
                    "afternoon_precipitation": safe_get("precipitation", 0),
                },

                "detail_info": {
                    "feels_like": safe_get("feels_like_temperature", safe_get("temperature", 20.0)),
                    "humidity": safe_get("humidity", 50),
                    "uv_index": safe_get("uv_index", 0),
                    "uv_level": "보통",
                    "wind_speed": safe_get("wind_speed", 0.0),
                    "sunrise": current.get("sunrise_time", "06:00"),
                    "sunset": current.get("sunset_time", "18:00"),
                    "air_quality_status": "보통",
                },

                "hourly_forecast": [
                    {
                        "time": f"{i + 1}시",
                        "weather_condition": weather_condition,
                        "temperature": safe_get("temperature", 20.0),
                        "precipitation_probability": safe_get("precipitation", 0)
                    }
                    for i in range(12)
                ],

                "air_quality": {
                    "pm25_value": int(safe_get("pm25", 15)),
                    "pm25_grade": pm25_grade,
                    "pm10_value": int(safe_get("pm10", 30)),
                    "pm10_grade": pm10_grade,
                },

                "travel_tip": {
                    "tip_message": travel_tip
                },

                "location_name": region_name,
                "latitude": 37.5665,
                "longitude": 126.9780,
                "last_updated": now.isoformat(),
            }

        except Exception as e:
            raise

    def _transform_to_ui_format_subregion(self, raw_data, region_id, region_name, subregion_id, subregion_name):
        try:
            if not raw_data:
                raise ValueError("날씨 데이터가 없습니다")

            current = raw_data[0]
            weather_condition = self._get_weather_condition(current)
            pm25_grade = self._get_pm_grade(current.get("pm25", 15))
            pm10_grade = self._get_pm_grade(current.get("pm10", 30), pm_type="pm10")
            travel_tip = self._get_travel_tip(current, f"{region_name} {subregion_name}")

            # 날짜 계산
            now = datetime.now()
            tomorrow = now + timedelta(days=1)

            # 안전한 값 추출
            def safe_get(key, default=0):
                value = current.get(key, default)
                if value is None:
                    return default
                try:
                    return float(value) if isinstance(default, float) else int(value)
                except:
                    return default

            return {
                "current_weather": {
                    "current_date": now.strftime("%m.%d"),
                    "temperature": safe_get("temperature", 20.0),
                    "weather_condition": weather_condition,
                    "temperature_change": "+0.0°",
                    "min_temperature": safe_get("min_temperature", 15.0),
                    "max_temperature": safe_get("max_temperature", 25.0),
                },
                "tomorrow_weather": {
                    "tomorrow_date": tomorrow.strftime("%m.%d"),
                    "min_temperature": safe_get("min_temperature", 15.0),
                    "max_temperature": safe_get("max_temperature", 25.0),
                    "morning_condition": weather_condition,
                    "morning_precipitation": safe_get("precipitation", 0),
                    "afternoon_condition": weather_condition,
                    "afternoon_precipitation": safe_get("precipitation", 0),
                },
                "detail_info": {
                    "feels_like": safe_get("feels_like_temperature", safe_get("temperature", 20.0)),
                    "humidity": safe_get("humidity", 50),
                    "uv_index": safe_get("uv_index", 0),
                    "uv_level": "보통",
                    "wind_speed": safe_get("wind_speed", 0.0),
                    "sunrise": current.get("sunrise_time", "06:00"),
                    "sunset": current.get("sunset_time", "18:00"),
                    "air_quality_status": "보통",
                },
                "hourly_forecast": [
                    {
                        "time": f"{i + 1}시",
                        "weather_condition": weather_condition,
                        "temperature": safe_get("temperature", 20.0),
                        "precipitation_probability": safe_get("precipitation", 0)
                    }
                    for i in range(12)
                ],
                "air_quality": {
                    "pm25_value": int(safe_get("pm25", 15)),
                    "pm25_grade": pm25_grade,
                    "pm10_value": int(safe_get("pm10", 30)),
                    "pm10_grade": pm10_grade,
                },
                "travel_tip": {
                    "tip_message": travel_tip
                },
                "location_name": f"{region_name} {subregion_name}",
                "latitude": 37.5735,
                "longitude": 126.9788,
                "last_updated": now.isoformat(),
            }
        except Exception as e:
            raise