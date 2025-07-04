from django.db import models


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
    opening_hours = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="운영시간"
    )

    region_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="지역 ID"
    )

    view_count = models.IntegerField(
        default=0,
        verbose_name="조회수"
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
        return f"Place {self.id} ({self.content_id})"
