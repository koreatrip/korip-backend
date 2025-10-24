from django.db import models
from django.conf import settings

# 언어 선택지
LANGUAGE_CHOICES = [
    ("ko", "한국어"),
    ("en", "English"),
    ("jp", "日本語"),
    ("cn", "中文"),
]


# 아이돌 신청 정보를 저장하는 테이블
class IdolRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="idol_requests",
        verbose_name="신청자"
    )

    idol_name = models.CharField(
        max_length=100,
        verbose_name="아이돌/그룹 이름"
    )

    agency = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="소속사"
    )

    related_info = models.TextField(
        blank=True,
        null=True,
        verbose_name="관련정보"
    )

    additional_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="비고/하고 싶은 말"
    )

    admin_memo = models.TextField(
        blank=True,
        null=True,
        verbose_name="관리자 메모"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="신청일"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "아이돌 신청"
        verbose_name_plural = "아이돌 신청"

    def __str__(self):
        return f"{self.idol_name} - {self.user.email}"
