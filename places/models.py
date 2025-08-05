from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

LANGUAGE_CHOICES = [
    ("ko", "한국어"),
    ("en", "English"),
    ("jp", "日本語"),
    ("cn", "中文"),
]


class Place(models.Model):

    content_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="컨텐트 ID"
    )

    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="카테고리"
    )

    sub_category = models.ForeignKey(
        "categories.SubCategory",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="서브 카테고리"
    )

    region = models.ForeignKey(
        "regions.Region",
        on_delete=models.CASCADE,
        related_name="places",
        null=True,
        blank=True,
        verbose_name="지역"
    )

    sub_region = models.ForeignKey(
        "regions.SubRegion",
        on_delete=models.CASCADE,
        related_name="places",
        null=True,
        blank=True,
        verbose_name="지역구"
    )

    location = models.PointField(
        null=True,
        blank=True,
        verbose_name="위치 좌표"
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="전화번호"
    )

    use_time = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="이용시간"
    )

    link_url = models.URLField(
        blank=True,
        verbose_name="공식 사이트 URL"
    )

    favorite_count = models.IntegerField(
        default=0,
        verbose_name="즐겨찾기 수"
    )

    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="마지막 동기화 시간"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시"
    )

    class Meta:
        db_table = "place"
        verbose_name = "관광지"
        verbose_name_plural = "관광지들"
        ordering = ["-created_at"]

    def __str__(self):
        korean_name = self.get_name("ko")
        if korean_name:
            tour_id = self.get_tour_api_content_id("ko")
            if tour_id:
                return f"{korean_name} API:{tour_id}"
            return korean_name
        return self.content_id if self.content_id else f"Place {self.id}"

    @property
    def latitude(self):
        return self.location.y if self.location else None

    @property
    def longitude(self):
        return self.location.x if self.location else None

    def set_coordinates(self, latitude, longitude):
        if latitude and longitude:
            self.location = Point(float(longitude), float(latitude))

    def get_coordinates(self):
        if self.location:
            return (self.location.y, self.location.x)
        return (None, None)

    def get_region_name(self, lang="ko"):
        if self.region:
            return self.region.get_name(lang)
        return ""

    def get_sub_region_name(self, lang="ko"):
        if self.sub_region:
            return self.sub_region.get_name(lang)
        return ""

    def update_favorite_count(self):
        # TODO: UserFavoritePlace 모델 구현 후 활성화
        pass

    def get_name(self, lang="ko"):
        try:
            translation = self.translations.get(lang=lang)
            return translation.name
        except PlaceTranslation.DoesNotExist:
            return ""

    def get_description(self, lang="ko"):
        try:
            translation = self.translations.get(lang=lang)
            return translation.description
        except PlaceTranslation.DoesNotExist:
            return ""

    def get_address(self, lang="ko"):
        try:
            translation = self.translations.get(lang=lang)
            return translation.address
        except PlaceTranslation.DoesNotExist:
            return ""

    def get_tour_api_content_id(self, lang="ko"):
        try:
            translation = self.translations.get(lang=lang)
            return translation.tour_api_content_id or ""
        except PlaceTranslation.DoesNotExist:
            return ""

    def get_available_languages(self):
        available_langs = list(
            self.translations.values_list('lang', flat=True).distinct()
        )
        return sorted(available_langs)

    def has_translation(self, lang="ko"):
        return self.translations.filter(lang=lang).exists()


class PlaceTranslation(models.Model):
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="관광지"
    )

    lang = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        verbose_name="언어 코드"
    )

    name = models.CharField(
        max_length=200,
        verbose_name="관광지명"
    )

    description = models.TextField(
        blank=True,
        verbose_name="설명"
    )

    address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="주소"
    )

    tour_api_content_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="투어API 컨텐츠 ID"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시"
    )

    class Meta:
        db_table = "place_translation"
        verbose_name = "관광지 번역"
        verbose_name_plural = "관광지 번역들"
        unique_together = ["place", "lang"]
        ordering = ["place_id", "lang"]

    def __str__(self):
        if self.tour_api_content_id:
            return f"{self.name} ({self.lang}) API:{self.tour_api_content_id}"
        return f"{self.name} ({self.lang})"