from django.db import models


class Weather(models.Model):
    # 메인 날씨 정보 모델

    # 지역 연결
    region = models.ForeignKey(
        "regions.Region",
        on_delete=models.CASCADE,
        verbose_name="지역"
    )

    sub_region = models.ForeignKey(
        "regions.SubRegion",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="지역구"
    )

    # 기본 날씨 정보 (기상청 단기예보 API)
    temperature = models.FloatField(verbose_name="현재 기온(℃)")
    min_temperature = models.FloatField(null=True, blank=True, verbose_name="최저 기온(℃)")
    max_temperature = models.FloatField(null=True, blank=True, verbose_name="최고 기온(℃)")
    humidity = models.IntegerField(verbose_name="습도(%)")
    precipitation = models.IntegerField(verbose_name="강수확률(%)")

    # 하늘 상태 (기상청 API 코드)
    sky_code = models.CharField(max_length=10, verbose_name="하늘상태")
    precipitation_type = models.CharField(max_length=10, verbose_name="강수형태")

    # 바람 정보 (기상청 지상시간자료 API)
    wind_speed = models.FloatField(null=True, blank=True, verbose_name="풍속(m/s)")
    wind_direction = models.IntegerField(null=True, blank=True, verbose_name="풍향(도)")

    # 체감온도 및 자외선 (기상청 생활기상지수 API)
    feels_like_temperature = models.FloatField(null=True, blank=True, verbose_name="체감온도(℃)")
    uv_index = models.IntegerField(null=True, blank=True, verbose_name="자외선 지수")

    # 일출/일몰 시간 (계산)
    sunrise_time = models.TimeField(null=True, blank=True, verbose_name="일출 시간")
    sunset_time = models.TimeField(null=True, blank=True, verbose_name="일몰 시간")

    # 대기질 정보 (환경부 미세먼지 API)
    pm25 = models.FloatField(null=True, blank=True, verbose_name="PM2.5(μg/m³)")
    pm10 = models.FloatField(null=True, blank=True, verbose_name="PM10(μg/m³)")

    # 예보 시간
    forecast_time = models.DateTimeField(verbose_name="예보 시간")

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "weather"
        verbose_name = "날씨"
        verbose_name_plural = "날씨 정보"
        ordering = ["-forecast_time"]

    def __str__(self):
        if self.sub_region:
            return f"{self.region.get_name('ko')} {self.sub_region.get_name('ko')} - {self.temperature}℃"
        else:
            return f"{self.region.get_name('ko')} - {self.temperature}℃"


class WeatherForecast(models.Model):
    # 시간별 날씨 예보 모델 (78개 시간별 예보 저장)

    # 지역 연결 (region은 필수, sub_region은 선택)
    region = models.ForeignKey(
        "regions.Region",
        on_delete=models.CASCADE,
        verbose_name="지역"
    )

    sub_region = models.ForeignKey(
        "regions.SubRegion",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="지역구"
    )

    # 격자 좌표 (기상청 API 필요)
    nx = models.IntegerField(verbose_name="격자 X좌표")
    ny = models.IntegerField(verbose_name="격자 Y좌표")

    # 예보 시간
    forecast_date = models.CharField(max_length=8, verbose_name="예보 날짜")
    forecast_time = models.CharField(max_length=4, verbose_name="예보 시간")

    # 예보 데이터
    temperature = models.FloatField(null=True, blank=True, verbose_name="기온(℃)")
    humidity = models.IntegerField(null=True, blank=True, verbose_name="습도(%)")
    precipitation_probability = models.IntegerField(null=True, blank=True, verbose_name="강수확률(%)")
    sky_condition = models.CharField(max_length=10, null=True, blank=True, verbose_name="하늘상태")
    precipitation_type = models.CharField(max_length=10, null=True, blank=True, verbose_name="강수형태")
    wind_speed = models.FloatField(null=True, blank=True, verbose_name="풍속(m/s)")
    wind_direction = models.IntegerField(null=True, blank=True, verbose_name="풍향(도)")

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")

    class Meta:
        db_table = "weather_forecast"
        verbose_name = "날씨 예보"
        verbose_name_plural = "날씨 예보"
        unique_together = ["nx", "ny", "forecast_date", "forecast_time"]
        ordering = ["forecast_date", "forecast_time"]

    def __str__(self):
        if self.sub_region:
            region_name = f"{self.region.get_name('ko')} {self.sub_region.get_name('ko')}"
        else:
            region_name = self.region.get_name("ko")
        return f"{region_name} - {self.forecast_date} {self.forecast_time}"

    def get_sky_condition_text(self):
        # 하늘상태 코드를 텍스트로 변환
        sky_map = {"1": "맑음", "3": "구름많음", "4": "흐림"}
        return sky_map.get(self.sky_condition, "알수없음")

    def get_precipitation_type_text(self):
        # 강수형태 코드를 텍스트로 변환
        precip_map = {
            "0": "없음", "1": "비", "2": "비/눈", "3": "눈",
            "5": "빗방울", "6": "빗방울눈날림", "7": "눈날림"
        }
        return precip_map.get(self.precipitation_type, "알수없음")


class AirQualityData(models.Model):
    # 대기질 상세 데이터 모델 (환경부 API 결과 저장)

    # 지역 연결 (region은 필수, sub_region은 선택)
    region = models.ForeignKey(
        "regions.Region",
        on_delete=models.CASCADE,
        verbose_name="지역"
    )

    sub_region = models.ForeignKey(
        "regions.SubRegion",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="지역구"
    )

    # 측정소 정보
    station_name = models.CharField(max_length=100, verbose_name="측정소명")
    measurement_date = models.CharField(max_length=20, verbose_name="측정 일시")

    # 미세먼지 농도
    pm10_value = models.IntegerField(null=True, blank=True, verbose_name="PM10 농도(μg/m³)")
    pm25_value = models.IntegerField(null=True, blank=True, verbose_name="PM2.5 농도(μg/m³)")

    # 미세먼지 등급
    pm10_grade = models.CharField(max_length=10, null=True, blank=True, verbose_name="PM10 등급")
    pm25_grade = models.CharField(max_length=10, null=True, blank=True, verbose_name="PM2.5 등급")

    # 기타 대기질 정보
    so2_value = models.FloatField(null=True, blank=True, verbose_name="아황산가스(ppm)")
    co_value = models.FloatField(null=True, blank=True, verbose_name="일산화탄소(ppm)")
    o3_value = models.FloatField(null=True, blank=True, verbose_name="오존(ppm)")
    no2_value = models.FloatField(null=True, blank=True, verbose_name="이산화질소(ppm)")

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")

    class Meta:
        db_table = "air_quality_data"
        verbose_name = "대기질 데이터"
        verbose_name_plural = "대기질 데이터"
        ordering = ["-created_at"]

    def __str__(self):
        if self.sub_region:
            region_name = f"{self.region.get_name('ko')} {self.sub_region.get_name('ko')}"
        else:
            region_name = self.region.get_name("ko")
        return f"{region_name} {self.station_name} - PM2.5:{self.pm25_value}"

    def get_overall_grade(self):
        # 종합 대기질 등급 (더 나쁜 등급 기준)
        grades = ["좋음", "보통", "나쁨", "매우나쁨"]
        pm25_idx = grades.index(self.pm25_grade) if self.pm25_grade in grades else 0
        pm10_idx = grades.index(self.pm10_grade) if self.pm10_grade in grades else 0
        return grades[max(pm25_idx, pm10_idx)]
