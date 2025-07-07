from django.db import models

# 언어 선택지 정의
LANGUAGE_CHOICES = [
    ("ko", "한국어"),
    ("en", "English"),
    ("ja", "日本語"),
    ("zh", "中文"),
]


class Place(models.Model):
    content_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="컨텐트 ID"
    )

    category_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="카테고리 ID"
    )
    sub_category_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="서브 카테고리 ID"
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="위도"
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="경도"
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

    region_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="지역 ID"
    )

    region_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="지역 코드"
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
        # 한국어 이름이 있으면 한국어, 없으면 기존 방식
        korean_name = self.get_name("ko")
        if korean_name:
            return korean_name
        return f"Place {self.id} ({self.content_id})"

# 즐겨찾기 수를 실제 UserFavoritePlace 개수로 업데이트
    def update_favorite_count(self):
        # self.favorite_count = self.userfavoriteplace_set.count()
        # self.save(update_fields=["favorite_count"])
        pass  # 일단 pass로 두고 나중에 UserFavoritePlace 만들면 구현


    # 다국어 지원 메서드들 추가
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
        # 같은 Place에 같은 언어의 번역이 중복되지 않게
        unique_together = ["place", "lang"]
        ordering = ["place_id", "lang"]

    def __str__(self):
        return f"{self.name} ({self.lang})"
