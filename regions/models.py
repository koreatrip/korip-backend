from django.db import models

LANGUAGE_CHOICES = [
    ("ko", "한국어"),
    ("en", "English"),
    ("jp", "日本語"),
    ("cn", "中文"),
]


# 기본 지역 모델
class Region(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "region"
        verbose_name = "지역"
        verbose_name_plural = "지역"

    # 한국어 이름을 기본으로 보여주기
    def __str__(self):
        korean_name = self.get_name("ko")
        return korean_name if korean_name else f"Region {self.id}"

    # 지정한 언어의 지역 이름 가져오기
    def get_name(self, lang="ko"):
        try:
            translation = self.translations.get(lang=lang)
            return translation.name
        except RegionTranslation.DoesNotExist:
            return None

    # 지정한 언어의 지역 설명 가져오기
    def get_description(self, lang="ko"):
        try:
            translation = self.translations.get(lang=lang)
            return translation.description
        except RegionTranslation.DoesNotExist:
            return ""


# 지역 번역 테이블
class RegionTranslation(models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="지역"
    )
    lang = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        verbose_name="언어 코드"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="지역 이름"
    )
    description = models.TextField(
        blank=True,
        verbose_name="지역 설명",
        help_text="이 지역에 대한 간단한 설명 (예: 전통과 현대가 공존하는 도시)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "region_translation"
        verbose_name = "지역 번역"
        verbose_name_plural = "지역 번역"
        unique_together = [("region", "lang")]

    def __str__(self):
        return f"{self.region.id} - {self.lang}: {self.name}"


# 지역구 모델 (즐겨찾기 수, 날씨 연동용 위치 정보 포함)
class SubRegion(models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="subregions",
        verbose_name="부모 지역"
    )

    # 즐겨찾기 수 (인기순 정렬용)
    favorite_count = models.IntegerField(
        default=0,
        verbose_name="즐겨찾기 수",
        help_text="이 지역구가 즐겨찾기된 횟수"
    )

    # 날씨 API 연동용 위도/경도
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="위도",
        help_text="날씨 API 연동용 대표 위도"
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="경도",
        help_text="날씨 API 연동용 대표 경도"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "subregion"
        verbose_name = "지역구"
        verbose_name_plural = "지역구"
        # 즐겨찾기 수 많은 순 → 한국어 이름순으로 자동 정렬
        ordering = ["-favorite_count", "translations__name"]

    def __str__(self):
        korean_name = self.get_name("ko")
        region_name = self.region.get_name("ko") or "지역"
        if korean_name:
            return f"{region_name} {korean_name}"
        return f"SubRegion {self.id}"

    # 지정한 언어의 지역구 이름 가져오기
    def get_name(self, lang="ko"):
        try:
            translation = self.translations.get(lang=lang)
            return translation.name
        except SubRegionTranslation.DoesNotExist:
            return None

    # 지정한 언어의 지역구 설명 가져오기
    def get_description(self, lang="ko"):
        try:
            translation = self.translations.get(lang=lang)
            return translation.description
        except SubRegionTranslation.DoesNotExist:
            return ""

    # 지정한 언어의 지역구 특징 가져오기
    def get_features(self, lang="ko"):
        try:
            translation = self.translations.get(lang=lang)
            return translation.features
        except SubRegionTranslation.DoesNotExist:
            return ""

    # 이 지역구의 즐겨찾기 수 업데이트 (UserFavoriteRegion 모델 연결 후 구현 예정)
    def update_favorite_count(self):
        pass


# 지역구 번역 테이블
class SubRegionTranslation(models.Model):
    sub_region = models.ForeignKey(
        SubRegion,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="지역구"
    )
    lang = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        verbose_name="언어 코드"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="지역구 이름"
    )
    description = models.TextField(
        blank=True,
        verbose_name="지역 설명",
        help_text="이 지역구에 대한 간단한 설명"
    )

    features = models.TextField(
        blank=True,
        verbose_name="특징",
        help_text="이 지역구의 특징 설명 (예: 트레디한 쇼핑몰과 고급 레스토랑)"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "subregion_translation"
        verbose_name = "지역구 번역"
        verbose_name_plural = "서브지역 번역"
        # 같은 지역구에 같은 언어 조합은 한 번만 허용
        unique_together = [("sub_region", "lang")]

    def __str__(self):
        return f"{self.sub_region.id} - {self.lang}: {self.name}"
