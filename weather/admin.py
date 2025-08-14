from django.contrib import admin
from django.utils.html import format_html
from weather.models import Weather


@admin.register(Weather)
class WeatherAdmin(admin.ModelAdmin):
    list_display = [
        "get_location_name",
        "temperature_display",
        "humidity",
        "weather_condition_display",
        "pm_display",
        "forecast_time",
        "created_at"
    ]

    # 필터 옵션
    list_filter = [
        "region",
        "sub_region",
        "forecast_time",
        "created_at"
    ]

    # 검색 가능한 필드
    search_fields = [
        "region__regiontranslation__name",
        "sub_region__subregiontranslation__name"
    ]

    # 날짜별
    date_hierarchy = "forecast_time"

    # 페이지당 표시 개수
    list_per_page = 50

    # 상세 화면
    fieldsets = (
        ("지역 정보", {
            "fields": ("region", "sub_region")
        }),
        ("기본 날씨 정보", {
            "fields": (
                "temperature",
                "min_temperature",
                "max_temperature",
                "humidity",
                "precipitation"
            )
        }),
        ("날씨 상태", {
            "fields": (
                "sky_code",
                "precipitation_type",
                "wind_speed",
                "wind_direction"
            )
        }),
        ("생활 기상", {
            "fields": (
                "feels_like_temperature",
                "uv_index",
                "sunrise_time",
                "sunset_time"
            )
        }),
        ("대기질", {
            "fields": ("pm25", "pm10")
        }),
        ("시간 정보", {
            "fields": ("forecast_time",)
        })
    )

    # 읽기 전용
    readonly_fields = ["created_at", "updated_at"]

    def get_location_name(self, obj):
        if obj.sub_region:
            return f"{obj.region.get_name('ko')} {obj.sub_region.get_name('ko')}"
        return obj.region.get_name('ko')

    get_location_name.short_description = "지역"
    get_location_name.admin_order_field = "region__regiontranslation__name"

    def temperature_display(self, obj):
        # 기온 (최저/최고 포함)
        temp_html = f"<strong>{obj.temperature}°C</strong>"
        if obj.min_temperature and obj.max_temperature:
            temp_html += f"<br><small>{obj.min_temperature}° / {obj.max_temperature}°</small>"
        return format_html(temp_html)

    temperature_display.short_description = "기온"
    temperature_display.admin_order_field = "temperature"

    def weather_condition_display(self, obj):
        # 날씨 상태 표시(하늘상태 변환)
        sky_map = {"1": "맑음", "3": "구름많음", "4": "흐림"}
        sky_text = sky_map.get(str(obj.sky_code), "알수없음")

        # 강수형태 변환
        precip_map = {
            "0": "", "1": "비", "2": "비/눈", "3": "눈",
            "5": "빗방울", "6": "빗방울눈날림", "7": "눈날림"
        }
        precip_text = precip_map.get(str(obj.precipitation_type), "")

        result = sky_text
        if precip_text:
            result += f"<br>{precip_text}"
        return format_html(result)

    weather_condition_display.short_description = "날씨 상태"

    def pm_display(self, obj):
        # 미세먼지 표시
        if obj.pm25 and obj.pm10:
            # 등급 계산
            pm25_grade = self._get_pm_grade(obj.pm25, "pm25")
            pm10_grade = self._get_pm_grade(obj.pm10, "pm10")

            return format_html(
                "<strong>PM2.5:</strong> {}μg/m³ ({})<br>"
                "<strong>PM10:</strong> {}μg/m³ ({})",
                obj.pm25, pm25_grade, obj.pm10, pm10_grade
            )
        return "데이터 없음"

    pm_display.short_description = "미세먼지"

    def _get_pm_grade(self, value, pm_type):
        # 미세먼지 등급 계산
        try:
            value = float(value)
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
        except:
            return "알수없음"

    # 액션 추가
    actions = ["delete_old_forecasts"]

    def delete_old_forecasts(self, request, queryset):
        # 7일 이상 된 예보 데이터 삭제
        from datetime import timedelta
        from django.utils import timezone

        seven_days_ago = timezone.now() - timedelta(days=7)
        old_count = Weather.objects.filter(forecast_time__lt=seven_days_ago).count()
        Weather.objects.filter(forecast_time__lt=seven_days_ago).delete()

        self.message_user(request, f"{old_count}개의 오래된 예보 데이터를 삭제했습니다.")

    delete_old_forecasts.short_description = "7일 이상 된 예보 데이터 삭제"