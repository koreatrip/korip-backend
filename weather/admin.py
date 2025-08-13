from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from weather.models import WeatherData, WeatherForecast, AirQualityData, Weather
from weather.services.weather_api_client import WeatherAPIClient
import json
from datetime import datetime


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):

    list_display = [
        "location_name",
        "current_temperature",
        "humidity",
        "pm25_value",
        "pm10_value",
        "uv_index",
        "created_at"
    ]

    list_filter = ["created_at", "updated_at"]
    search_fields = ["location_name", "latitude", "longitude"]
    ordering = ["-created_at"]
    list_per_page = 20

    # 읽기 전용 필드들 (실시간 API 조회 결과랑 자동 생성 필드만)
    readonly_fields = [
        "created_at",  # 생성일시 (자동)
        "updated_at",  # 수정일시 (자동)
        "get_realtime_basic_weather",  # 실시간 API 조회
        "get_realtime_air_quality",  # 실시간 API 조회
        "get_realtime_detail_info",  # 실시간 API 조회
        "get_hourly_forecast",  # 실시간 API 조회
        "get_travel_tip",  # 실시간 API 조회 결과
        "get_data_comparison",  # 실시간 API 조회 결과
        "get_api_status"  # API 상태 정보
    ]

    fieldsets = (
        ("위치 정보", {
            "fields": ("location_name", "latitude", "longitude")
        }),
        ("저장된 기온 정보", {
            "fields": ("current_temperature", "humidity")
        }),
        ("저장된 대기질 정보", {
            "fields": ("pm25_value", "pm10_value")
        }),
        ("저장된 기타 정보", {
            "fields": ("uv_index", "sunrise_time", "sunset_time")
        }),
        ("실시간 기본 날씨", {
            "fields": ("get_realtime_basic_weather",),
            "description": "WeatherAPIClient로 조회한 실시간 기온, 습도, 풍속 정보"
        }),
        ("실시간 대기질", {
            "fields": ("get_realtime_air_quality",),
            "description": "실시간 미세먼지(PM2.5, PM10) 농도와 등급"
        }),
        ("실시간 상세 정보", {
            "fields": ("get_realtime_detail_info",),
            "description": "실시간 최고/최저기온, 강수확률, 자외선지수, 일출/일몰 시간"
        }),
        ("시간별 예보", {
            "fields": ("get_hourly_forecast",),
            "description": "향후 12시간 시간별 날씨 예보"
        }),
        ("여행 팁", {
            "fields": ("get_travel_tip",),
            "description": "현재 날씨 조건에 따른 여행 팁"
        }),
        ("데이터 비교", {
            "fields": ("get_data_comparison",),
            "description": "저장된 데이터와 실시간 데이터 비교"
        }),
        ("API 상태", {
            "fields": ("get_api_status",),
            "description": "WeatherAPIClient 조회 상태 및 데이터 소스 정보"
        }),
        ("시간 정보", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )

    def _get_current_weather_data(self, obj):
        # 공통으로 사용할 실시간 날씨 데이터 조회
        if not hasattr(self, '_cached_weather_data'):
            if not obj.latitude or not obj.longitude:
                self._cached_weather_data = None
                return None

            try:
                weather_client = WeatherAPIClient()
                weather_data = weather_client.get_weather_by_coordinates(
                    obj.latitude, obj.longitude
                )
                self._cached_weather_data = weather_data[0] if weather_data else None
            except Exception:
                self._cached_weather_data = None

        return self._cached_weather_data

    def get_realtime_basic_weather(self, obj):
        # 실시간 기본 날씨 정보
        current = self._get_current_weather_data(obj)

        if not current:
            return "실시간 데이터를 가져올 수 없습니다."

        info = [
            f"현재 기온: {current.get('temperature', 'N/A')}°C",
            f"체감온도: {current.get('feels_like_temperature', current.get('temperature', 'N/A'))}°C",
            f"습도: {current.get('humidity', 'N/A')}%",
            f"풍속: {current.get('wind_speed', 'N/A')}m/s",
        ]

        return mark_safe("<br>".join(info))

    get_realtime_basic_weather.short_description = "실시간 기본 날씨"

    def get_realtime_air_quality(self, obj):
        # 실시간 대기질 정보
        current = self._get_current_weather_data(obj)

        if not current:
            return "실시간 데이터를 가져올 수 없습니다."

        pm25 = current.get('pm25', 'N/A')
        pm10 = current.get('pm10', 'N/A')

        pm25_grade = self._get_pm_grade(pm25, "pm25") if pm25 != 'N/A' else 'N/A'
        pm10_grade = self._get_pm_grade(pm10, "pm10") if pm10 != 'N/A' else 'N/A'

        info = [
            f"PM2.5: {pm25}μg/m³ ({pm25_grade})",
            f"PM10: {pm10}μg/m³ ({pm10_grade})",
        ]

        return mark_safe("<br>".join(info))

    get_realtime_air_quality.short_description = "실시간 대기질"

    def get_realtime_detail_info(self, obj):
        # 실시간 상세 정보
        current = self._get_current_weather_data(obj)

        if not current:
            return "실시간 데이터를 가져올 수 없습니다."

        info = [
            f"최저기온: {current.get('min_temperature', 'N/A')}°C",
            f"최고기온: {current.get('max_temperature', 'N/A')}°C",
            f"강수확률: {current.get('precipitation', 'N/A')}%",
            f"자외선지수: {current.get('uv_index', 'N/A')}",
            f"일출시간: {current.get('sunrise_time', 'N/A')}",
            f"일몰시간: {current.get('sunset_time', 'N/A')}",
        ]

        return mark_safe("<br>".join(info))

    get_realtime_detail_info.short_description = "실시간 상세 정보"

    def get_hourly_forecast(self, obj):
        # 시간별 예보
        if not obj.latitude or not obj.longitude:
            return "좌표 정보가 없어 시간별 예보를 가져올 수 없습니다."

        try:
            weather_client = WeatherAPIClient()
            all_forecast_data = weather_client.get_weather_by_coordinates(
                obj.latitude, obj.longitude
            )

            if not all_forecast_data or len(all_forecast_data) < 12:
                return "시간별 예보 데이터가 부족합니다."

            hourly_data = all_forecast_data[:12]

            forecast_lines = ["시간  | 날씨 | 기온 | 강수확률"]
            forecast_lines.append("-----|------|------|--------")

            for i, forecast in enumerate(hourly_data):
                time_str = forecast.get('forecast_time', f'{i * 3:02d}:00')[:5]
                weather_icon = self._get_weather_icon(forecast)
                temp = forecast.get('temperature', 'N/A')
                precipitation = forecast.get('precipitation', 'N/A')

                forecast_lines.append(
                    f"{time_str} | {weather_icon}   | {temp}°C | {precipitation}%"
                )

            return mark_safe("<pre>" + "\n".join(forecast_lines) + "</pre>")

        except Exception as e:
            return f"시간별 예보 조회 실패: {str(e)}"

    get_hourly_forecast.short_description = "시간별 예보 (12시간)"

    def get_travel_tip(self, obj):
        # 여행 팁
        current = self._get_current_weather_data(obj)

        if not current:
            return "실시간 데이터를 가져올 수 없어 여행 팁을 제공할 수 없습니다."

        temp = current.get('temperature', 20)
        pm25 = current.get('pm25', 15)
        pm10 = current.get('pm10', 30)
        humidity = current.get('humidity', 50)
        precipitation = current.get('precipitation', 0)
        wind_speed = current.get('wind_speed', 0)
        uv_index = current.get('uv_index', 0)

        # 극한 추위 (영하 5도 이하)
        if temp < -5:
            tip = "매우 추운 혹한기 날씨입니다. 두꺼운 패딩, 목도리, 장갑을 필수로 착용하시고 실내 관광지나 온천, 찜질방 방문을 강력히 추천합니다. 야외활동은 되도록 짧게 하시고 따뜻한 음료를 자주 드세요."

        # 추위 (영하 ~ 5도)
        elif temp <= 5:
            tip = "쌀쌀한 날씨입니다. 따뜻한 코트나 패딩을 착용하시고 목도리와 장갑도 준비하세요. 실내 박물관, 미술관, 대형 쇼핑몰이나 따뜻한 카페에서 시간을 보내시는 것을 추천합니다. 야외 관광 시에는 핫팩을 준비하세요."

        # 폭염 (35도 이상)
        elif temp >= 35:
            tip = "폭염 경보 수준의 매우 더운 날씨입니다. 가급적 오전 일찍이나 저녁 늦게 야외활동을 하시고, 낮에는 에어컨이 잘 되는 백화점, 대형마트, 영화관, 박물관 등 실내 관광지 방문을 권합니다. 충분한 수분 섭취와 자외선 차단제 필수입니다."

        # 매우 더움 (30-34도)
        elif temp >= 30:
            tip = "무더운 여름 날씨입니다. 시원한 실내 관광지나 에어컨이 잘 되는 카페, 쇼핑몰에서 더위를 피하세요. 야외활동 시에는 양산이나 모자, 자외선 차단제를 꼭 준비하시고 시원한 음료를 자주 드시기 바랍니다."

        # 폭우 예상 (강수확률 80% 이상)
        elif precipitation >= 80:
            tip = "폭우가 예상되는 날씨입니다. 우산과 우비를 필수로 준비하시고 가급적 실내 관광지인 박물관, 미술관, 대형 쇼핑몰, 전통시장 실내 구역 방문을 추천합니다. 교통편 지연 가능성도 염두에 두시고 여유 있는 일정을 계획하세요."

        # 비 예상 (강수확률 60-79%)
        elif precipitation >= 60:
            tip = "비가 올 확률이 높은 날씨입니다. 우산을 꼭 휴대하시고 실내 활동 위주로 계획하세요. 카페 투어, 실내 시장 구경, 백화점 쇼핑이나 스파, 찜질방 방문이 좋겠습니다. 우천 시 미끄러운 길 조심하세요."

        # 최악의 대기질 (PM2.5 > 75)
        elif pm25 > 75:
            tip = "미세먼지 농도가 매우 나쁜 상태입니다. KF94 이상 마스크를 반드시 착용하시고 야외활동을 최대한 자제하세요. 실내 관광지인 백화점, 대형마트, 영화관, 박물관 방문을 권하며, 외출 후에는 깨끗이 씻고 충분한 수분을 섭취하세요."

        # 나쁜 대기질 (PM2.5 36-75)
        elif pm25 > 35:
            tip = "미세먼지가 다소 나쁜 상태입니다. 보건용 마스크 착용을 권장하며 장시간 야외활동보다는 실내 관광지나 카페에서 시간을 보내세요. 야외활동 시에는 자주 휴식을 취하고 물을 충분히 드시기 바랍니다."

        # 강풍 주의 (풍속 10m/s 이상)
        elif wind_speed >= 10:
            tip = "바람이 매우 강한 날씨입니다. 모자나 스카프가 날아갈 수 있으니 주의하세요. 높은 곳이나 해안가 관광 시 특히 조심하시고, 가급적 실내 관광지나 바람이 덜한 실내 시장, 지하상가 방문을 추천합니다."

        # 습하고 더움 (습도 80% 이상 + 기온 25도 이상)
        elif humidity >= 80 and temp >= 25:
            tip = "덥고 습한 무더위 날씨입니다. 통풍이 잘 되는 면 소재 옷을 입으시고 땀 흡수가 좋은 옷차림을 권합니다. 에어컨이 잘 되는 실내 관광지에서 휴식을 자주 취하시고 탈수 방지를 위해 물을 자주 드세요."

        # 건조함 주의 (습도 30% 이하)
        elif humidity <= 30:
            tip = "공기가 매우 건조한 날씨입니다. 충분한 수분 섭취와 립밤, 핸드크림 사용을 권장합니다. 정전기 방지를 위해 천연 소재 옷을 입으시고, 가습기가 있는 카페나 실내 관광지에서 휴식을 취하세요."

        # 자외선 매우 강함 (자외선 지수 8 이상)
        elif uv_index >= 8:
            tip = "자외선이 매우 강한 날씨입니다. SPF 50 이상의 자외선 차단제를 2-3시간마다 덧발라 주시고 모자, 선글라스, 긴팔 옷을 착용하세요. 그늘진 곳에서 자주 휴식을 취하시고 10시-16시 사이 야외활동은 피해주세요."

        # 완벽한 날씨 (기온 20-25도, 습도 40-60%, 강수확률 20% 이하)
        elif 20 <= temp <= 25 and 40 <= humidity <= 60 and precipitation <= 20:
            tip = "관광하기에 완벽한 날씨입니다! 야외 관광지 투어, 공원 산책, 한강이나 바다 구경, 고궁 탐방 등 어떤 활동이든 즐겁게 하실 수 있어요. 가벼운 외투 하나 정도만 준비하시면 완벽한 하루가 될 것 같습니다!"

        # 쾌적한 봄/가을 날씨 (기온 15-20도)
        elif 15 <= temp <= 20:
            tip = "쾌적한 봄/가을 날씨입니다. 가벼운 외투나 카디건을 준비하시고 야외 관광지나 공원 산책, 고궁 투어를 즐겨보세요. 일교차가 있을 수 있으니 얇은 겉옷을 하나 더 준비하시면 좋겠습니다."

        # 쌀쌀한 날씨 (기온 10-15도)
        elif 10 <= temp <= 15:
            tip = "쌀쌀하지만 나쁘지 않은 날씨입니다. 따뜻한 옷차림으로 야외 관광도 충분히 즐기실 수 있어요. 실내외를 오가며 관광하기 좋은 날씨이니 박물관과 궁궐 투어를 병행해보세요. 따뜻한 음료 한 잔의 여유도 즐겨보세요."

        # 서늘한 날씨 (기온 5-10도)
        elif 5 <= temp <= 10:
            tip = "서늘한 날씨입니다. 따뜻한 코트나 점퍼를 착용하시고 목도리를 준비하세요. 실내 관광지와 따뜻한 카페를 위주로 일정을 계획하시되, 짧은 야외 산책도 나쁘지 않습니다. 온천이나 찜질방도 추천해요."

        # 소나기 가능성 (강수확률 30-59%)
        elif 30 <= precipitation <= 59:
            tip = "소나기가 올 수 있는 날씨입니다. 접이식 우산을 꼭 가지고 다니시고 실내외 관광을 적절히 섞어서 계획하세요. 갑작스러운 비에 대비해 지하상가나 백화점 위치를 미리 파악해두시면 좋겠습니다."

        # 대기질 좋음 + 좋은 날씨 (PM2.5 ≤ 15, 기온 적당)
        elif pm25 <= 15 and 18 <= temp <= 28:
            tip = "대기가 매우 깨끗하고 기온도 적당한 최고의 관광 날씨입니다! 야외 활동을 마음껏 즐기세요. 한강공원, 남산, 해안가 산책이나 등산, 자전거 투어 등 어떤 야외활동이든 추천합니다. 깊게 숨쉬며 한국의 아름다운 자연을 만끽하세요!"

        # 미지근한 날씨 (기온 26-29도, 적당한 습도)
        elif 26 <= temp <= 29 and humidity <= 70:
            tip = "따뜻하고 쾌적한 여름 날씨입니다. 반팔과 얇은 겉옷을 준비하시고 야외 관광지나 공원에서 시간을 보내기 좋습니다. 시원한 음료수나 아이스크림을 즐기며 여유로운 관광을 즐겨보세요. 저녁에는 야외 테라스가 있는 카페도 좋겠어요."

        # 기본 좋은 날씨 (나머지 모든 경우)
        else:
            tip = "관광하기 좋은 날씨입니다! 편안한 옷차림으로 원하시는 관광지를 자유롭게 둘러보세요. 실내외 관광지를 적절히 섞어서 알찬 하루를 보내시기 바랍니다. 즐거운 한국 여행 되세요!"

        return mark_safe(tip)

    get_travel_tip.short_description = "여행 팁"

    def get_data_comparison(self, obj):
        # 데이터 비교
        current = self._get_current_weather_data(obj)

        if not current:
            return "실시간 데이터를 가져올 수 없어 비교할 수 없습니다."

        temp_diff = self._get_temp_diff(current.get('temperature'), obj.current_temperature)
        pm25_diff = self._get_pm_diff(current.get('pm25'), obj.pm25_value)

        info = [
            f"기온 차이: {temp_diff}",
            f"PM2.5 차이: {pm25_diff}",
        ]

        return mark_safe("<br>".join(info))

    get_data_comparison.short_description = "데이터 비교"

    def get_api_status(self, obj):
        # API 상태 정보
        current = self._get_current_weather_data(obj)

        status_info = [
            f"조회 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"조회 좌표: ({obj.latitude}, {obj.longitude})" if obj.latitude and obj.longitude else "좌표 없음",
            f"API 상태: {'정상' if current else '실패'}",
            "데이터 소스: 기상청 단기예보 + 환경부 미세먼지 + 생활기상지수 API"
        ]

        return mark_safe("<br>".join(status_info))

    get_api_status.short_description = "API 상태 정보"

    def _get_pm_grade(self, value, pm_type="pm25"):
        # 대기질 등급 계산
        if not value or value == 'N/A':
            return "정보없음"

        try:
            value = float(value)
        except (ValueError, TypeError):
            return "정보없음"

        if pm_type == "pm25":
            if value <= 15:
                return "좋음"
            elif value <= 35:
                return "보통"
            elif value <= 75:
                return "나쁨"
            else:
                return "매우나쁨"
        else:
            if value <= 30:
                return "좋음"
            elif value <= 80:
                return "보통"
            elif value <= 150:
                return "나쁨"
            else:
                return "매우나쁨"

    def _get_temp_diff(self, current_temp, saved_temp):
        # 기온 차이 계산
        if current_temp is None or saved_temp is None:
            return "비교불가"

        try:
            diff = float(current_temp) - float(saved_temp)
            if abs(diff) < 0.1:
                return "동일"
            elif diff > 0:
                return f"+{diff:.1f}°C (상승)"
            else:
                return f"{diff:.1f}°C (하강)"
        except (ValueError, TypeError):
            return "비교불가"

    def _get_pm_diff(self, current_pm25, saved_pm25):
        # PM2.5 차이 계산
        if current_pm25 is None or saved_pm25 is None:
            return "비교불가"

        try:
            diff = float(current_pm25) - float(saved_pm25)
            if abs(diff) < 1:
                return "동일"
            elif diff > 0:
                return f"+{diff:.0f}μg/m³ (악화)"
            else:
                return f"{diff:.0f}μg/m³ (개선)"
        except (ValueError, TypeError):
            return "비교불가"


def refresh_weather_data(modeladmin, request, queryset):
    # 선택된 날씨 데이터를 실시간으로 새로고침
    updated_count = 0
    failed_count = 0
    weather_client = WeatherAPIClient()

    for weather_data in queryset:
        if weather_data.latitude and weather_data.longitude:
            try:
                live_data = weather_client.get_weather_by_coordinates(
                    weather_data.latitude, weather_data.longitude
                )

                if live_data:
                    current = live_data[0]
                    weather_data.current_temperature = current.get('temperature')
                    weather_data.humidity = current.get('humidity')
                    weather_data.pm25_value = current.get('pm25')
                    weather_data.pm10_value = current.get('pm10')
                    weather_data.uv_index = current.get('uv_index')
                    weather_data.sunrise_time = current.get('sunrise_time')
                    weather_data.sunset_time = current.get('sunset_time')
                    weather_data.save()
                    updated_count += 1
                else:
                    failed_count += 1
            except Exception:
                failed_count += 1
        else:
            failed_count += 1

    if updated_count > 0:
        modeladmin.message_user(
            request,
            f"{updated_count}개 지역의 날씨 데이터가 성공적으로 업데이트되었습니다."
        )

    if failed_count > 0:
        modeladmin.message_user(
            request,
            f"{failed_count}개 지역의 데이터 업데이트에 실패했습니다.",
            level='WARNING'
        )


refresh_weather_data.short_description = "선택된 지역의 날씨 데이터 수동 새로고침"
WeatherDataAdmin.actions = [refresh_weather_data]

try:
    admin.site.unregister(WeatherForecast)
    admin.site.unregister(AirQualityData)
    admin.site.unregister(Weather)
except admin.sites.NotRegistered:
    pass
