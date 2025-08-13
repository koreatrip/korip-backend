from django.db import models


class WeatherData(models.Model):
    # 날씨 데이터 모델

    # 위치 정보
    location_name = models.CharField(
        max_length=100,
        verbose_name="지역명",
        help_text="날씨 조회 지역 이름"
    )

    latitude = models.FloatField(
        verbose_name="위도",
        help_text="위도 좌표"
    )

    longitude = models.FloatField(
        verbose_name="경도",
        help_text="경도 좌표"
    )

    # 현재 날씨 정보
    current_temperature = models.FloatField(
        verbose_name="현재 기온(℃)",
        help_text="현재 시점의 기온"
    )

    humidity = models.IntegerField(
        verbose_name="습도(%)",
        help_text="현재 습도 (0-100%)"
    )

    # 미세먼지 정보
    pm25_value = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="PM2.5(μg/m³)",
        help_text="초미세먼지 농도"
    )

    pm10_value = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="PM10(μg/m³)",
        help_text="미세먼지 농도"
    )

    # 기타 정보
    uv_index = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="자외선 지수",
        help_text="0-11 (0:낮음, 3-5:보통, 6-7:높음, 8-10:매우높음, 11+:위험)"
    )

    # 일출/일몰 시간
    sunrise_time = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="일출 시간",
        help_text="일출 시간 (HH:MM)"
    )

    sunset_time = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="일몰 시간",
        help_text="일몰 시간 (HH:MM)"
    )

    # 자동 생성 필드
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시"
    )

    class Meta:
        db_table = "weather_data"
        verbose_name = "날씨 데이터"
        verbose_name_plural = "날씨 데이터"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.location_name} - {self.current_temperature}℃ ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def get_pm25_grade(self):
        # PM2.5 등급 반환
        if self.pm25_value is None:
            return "정보없음"

        if self.pm25_value <= 15:
            return "좋음"
        elif self.pm25_value <= 35:
            return "보통"
        elif self.pm25_value <= 75:
            return "나쁨"
        else:
            return "매우나쁨"

    def get_pm10_grade(self):
        # PM10 등급 반환
        if self.pm10_value is None:
            return "정보없음"

        if self.pm10_value <= 30:
            return "좋음"
        elif self.pm10_value <= 80:
            return "보통"
        elif self.pm10_value <= 150:
            return "나쁨"
        else:
            return "매우나쁨"

    def get_uv_level(self):
        # 자외선 지수 등급 반환
        if self.uv_index is None:
            return "정보없음"

        if self.uv_index <= 2:
            return "낮음"
        elif self.uv_index <= 5:
            return "보통"
        elif self.uv_index <= 7:
            return "높음"
        else:
            return "매우높음"


class WeatherForecast(models.Model):
    # 날씨 예보 데이터 모델

    # 위치 정보
    location_name = models.CharField(
        max_length=100,
        verbose_name="지역명",
        help_text="예보 지역 이름"
    )

    nx = models.IntegerField(
        verbose_name="격자 X좌표",
        help_text="기상청 격자 X 좌표"
    )

    ny = models.IntegerField(
        verbose_name="격자 Y좌표",
        help_text="기상청 격자 Y 좌표"
    )

    # 예보 시간
    forecast_date = models.CharField(
        max_length=8,
        verbose_name="예보 날짜",
        help_text="예보 날짜 (YYYYMMDD)"
    )

    forecast_time = models.CharField(
        max_length=4,
        verbose_name="예보 시간",
        help_text="예보 시간 (HHMM)"
    )

    # 예보 데이터
    temperature = models.FloatField(
        null=True,
        blank=True,
        verbose_name="기온(℃)",
        help_text="예보 기온"
    )

    humidity = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="습도(%)",
        help_text="예보 습도"
    )

    precipitation_probability = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="강수확률(%)",
        help_text="강수 확률 (0-100%)"
    )

    # 하늘 상태 코드
    sky_condition = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="하늘상태",
        help_text="1:맑음, 3:구름많음, 4:흐림"
    )

    # 강수 형태 코드
    precipitation_type = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="강수형태",
        help_text="0:없음, 1:비, 2:비/눈, 3:눈"
    )

    # 바람 정보
    wind_speed = models.FloatField(
        null=True,
        blank=True,
        verbose_name="풍속(m/s)",
        help_text="바람 속도"
    )

    wind_direction = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="풍향(도)",
        help_text="바람 방향 (0-360도)"
    )

    # 자동 생성 필드
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )

    class Meta:
        db_table = "weather_forecast"
        verbose_name = "날씨 예보"
        verbose_name_plural = "날씨 예보"
        unique_together = ["nx", "ny", "forecast_date", "forecast_time"]
        ordering = ["forecast_date", "forecast_time"]

    def __str__(self):
        return f"{self.location_name} - {self.forecast_date} {self.forecast_time} ({self.temperature}℃)"

    def get_forecast_datetime_display(self):
        try:
            date_str = f"{self.forecast_date[:4]}-{self.forecast_date[4:6]}-{self.forecast_date[6:8]}"
            time_str = f"{self.forecast_time[:2]}:{self.forecast_time[2:]}:00"
            return f"{date_str} {time_str}"
        except:
            return f"{self.forecast_date} {self.forecast_time}"

    def get_sky_condition_text(self):
        sky_map = {
            "1": "맑음",
            "3": "구름많음",
            "4": "흐림"
        }
        return sky_map.get(self.sky_condition, "알수없음")

    def get_precipitation_type_text(self):
        precip_map = {
            "0": "없음",
            "1": "비",
            "2": "비/눈",
            "3": "눈",
            "5": "빗방울",
            "6": "빗방울눈날림",
            "7": "눈날림"
        }
        return precip_map.get(self.precipitation_type, "알수없음")


class AirQualityData(models.Model):
    # 대기질 데이터 모델 (환경부 API 결과 저장용)

    # 측정소 정보
    station_name = models.CharField(
        max_length=100,
        verbose_name="측정소명",
        help_text="대기질 측정소 이름"
    )

    # 측정 시간
    measurement_date = models.CharField(
        max_length=20,
        verbose_name="측정 일시",
        help_text="측정 일시 (YYYY-MM-DD HH:MM)"
    )

    # 미세먼지 농도
    pm10_value = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="PM10 농도(μg/m³)",
        help_text="미세먼지 농도"
    )

    pm25_value = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="PM2.5 농도(μg/m³)",
        help_text="초미세먼지 농도"
    )

    # 미세먼지 등급
    pm10_grade = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="PM10 등급",
        help_text="미세먼지 등급 (좋음, 보통, 나쁨, 매우나쁨)"
    )

    pm25_grade = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="PM2.5 등급",
        help_text="초미세먼지 등급 (좋음, 보통, 나쁨, 매우나쁨)"
    )

    # 기타 대기질 정보 (필요시 추가)
    so2_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name="아황산가스(ppm)",
        help_text="SO2 농도"
    )

    co_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name="일산화탄소(ppm)",
        help_text="CO 농도"
    )

    o3_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name="오존(ppm)",
        help_text="O3 농도"
    )

    no2_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name="이산화질소(ppm)",
        help_text="NO2 농도"
    )

    # 자동 생성 필드
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )

    class Meta:
        db_table = "air_quality_data"
        verbose_name = "대기질 데이터"
        verbose_name_plural = "대기질 데이터"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.station_name} - PM2.5:{self.pm25_value}, PM10:{self.pm10_value} ({self.measurement_date})"

    def get_overall_grade(self):
        # 종합 대기질 등급 (더 나쁜 등급 기준)
        grades = ["좋음", "보통", "나쁨", "매우나쁨"]

        pm25_idx = grades.index(self.pm25_grade) if self.pm25_grade in grades else 0
        pm10_idx = grades.index(self.pm10_grade) if self.pm10_grade in grades else 0

        return grades[max(pm25_idx, pm10_idx)]


class Weather(models.Model):

    region = models.ForeignKey(
        "regions.Region",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="지역",
        help_text="날씨 정보를 조회할 지역"
    )

    # 기본 날씨 정보
    temperature = models.FloatField(
        verbose_name="현재 기온(℃)",
        help_text="현재 시점의 기온"
    )

    min_temperature = models.FloatField(
        null=True,
        blank=True,
        verbose_name="최저 기온(℃)",
        help_text="하루 중 최저 기온"
    )

    max_temperature = models.FloatField(
        null=True,
        blank=True,
        verbose_name="최고 기온(℃)",
        help_text="하루 중 최고 기온"
    )

    humidity = models.IntegerField(
        verbose_name="습도(%)",
        help_text="현재 습도 (0-100%)"
    )

    precipitation = models.IntegerField(
        verbose_name="강수확률(%)",
        help_text="강수 확률 (0-100%)"
    )

    # 하늘 상태 (기상청 API 코드)
    sky_code = models.CharField(
        max_length=10,
        verbose_name="하늘상태",
        help_text="1:맑음, 3:구름많음, 4:흐림"
    )

    # 강수 형태 (기상청 API 코드)
    precipitation_type = models.CharField(
        max_length=10,
        verbose_name="강수형태",
        help_text="0:없음, 1:비, 2:비/눈, 3:눈, 5:빗방울, 6:빗방울눈날림, 7:눈날림"
    )

    # 바람 정보
    wind_speed = models.FloatField(
        null=True,
        blank=True,
        verbose_name="풍속(m/s)",
        help_text="바람의 속도"
    )

    wind_direction = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="풍향(도)",
        help_text="바람이 불어오는 방향 (0-360도)"
    )

    # 추가 필드들
    feels_like_temperature = models.FloatField(
        null=True,
        blank=True,
        verbose_name="체감온도(℃)",
        help_text="실제로 느끼는 온도"
    )

    uv_index = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="자외선 지수",
        help_text="0-11 (0:낮음, 3-5:보통, 6-7:높음, 8-10:매우높음, 11+:위험)"
    )

    # 일출/일몰 시간
    sunrise_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="일출 시간",
        help_text="해가 뜨는 시간"
    )

    sunset_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="일몰 시간",
        help_text="해가 지는 시간"
    )

    # 대기질 정보
    pm25 = models.FloatField(
        null=True,
        blank=True,
        verbose_name="미세먼지(μg/m³)",
        help_text="PM2.5 농도"
    )

    pm10 = models.FloatField(
        null=True,
        blank=True,
        verbose_name="초미세먼지(μg/m³)",
        help_text="PM10 농도"
    )

    # 예보 시간
    forecast_time = models.DateTimeField(
        verbose_name="예보 시간",
        help_text="이 날씨 정보가 적용되는 시간"
    )

    # 자동 생성 필드
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시"
    )

    class Meta:
        db_table = "weather"
        verbose_name = "날씨"
        verbose_name_plural = "날씨 정보"
        ordering = ["-forecast_time"]

    def __str__(self):
        region_name = self.region.get_name("ko") if self.region else "지역없음"
        return f"{region_name} - {self.temperature}℃ ({self.forecast_time.strftime('%Y-%m-%d %H:%M')})"
