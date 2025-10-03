# plans/models.py
from django.db import models

# 언어 코드 선택지
LANGUAGE_CHOICES = [
    ("ko", "Korean"),
    ("en", "English"),
    ("jp", "Japanese"),
    ("cn", "Chinese"),
]


class TravelPlan(models.Model):
    """여행 계획 기본 정보"""
    user_id = models.BigIntegerField(verbose_name="사용자 ID")

    subregion_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="서브지역 ID"
    )

    # 어드민용 날짜 필드
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="시작일"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="종료일"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "travel_plan"
        verbose_name = "여행 계획"
        verbose_name_plural = "여행 계획들"
        indexes = [
            models.Index(fields=['user_id'], name='idx_travel_plan_user_id'),
            models.Index(fields=['user_id', 'end_date'], name='idx_travel_plan_user_end'),
        ]

    def __str__(self):
        korean_title = self.get_title("ko")
        return korean_title if korean_title else f"TravelPlan {self.id}"

    def get_title(self, lang="ko"):
        """언어별 제목 조회"""
        try:
            translation = self.translations.get(lang=lang)
            if translation.title.startswith("["):
                ko_translation = self.translations.get(lang="ko")
                return ko_translation.title
            return translation.title
        except TravelPlanTranslation.DoesNotExist:
            # 번역 없으면 한국어로 fallback
            try:
                ko_translation = self.translations.get(lang="ko")
                return ko_translation.title
            except TravelPlanTranslation.DoesNotExist:
                return ""

    def get_description(self, lang="ko"):
        """언어별 설명 조회"""
        try:
            translation = self.translations.get(lang=lang)
            # 임시 데이터면 한국어로 fallback
            if translation.title.startswith("["):
                ko_translation = self.translations.get(lang="ko")
                return ko_translation.description
            return translation.description
        except TravelPlanTranslation.DoesNotExist:
            # 번역 없으면 한국어로 fallback
            try:
                ko_translation = self.translations.get(lang="ko")
                return ko_translation.description
            except TravelPlanTranslation.DoesNotExist:
                return ""


class TravelPlanTranslation(models.Model):
    """여행 계획 다국어 번역"""
    travel_plan = models.ForeignKey(
        TravelPlan,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="여행 계획"
    )
    lang = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        verbose_name="언어 코드"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="제목"
    )
    description = models.TextField(
        blank=True,
        verbose_name="여행 설명"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "travel_plan_translation"
        verbose_name = "여행 계획 번역"
        verbose_name_plural = "여행 계획 번역들"
        unique_together = ["travel_plan", "lang"]

    def __str__(self):
        return f"{self.title} ({self.lang})"


class PlanPlace(models.Model):
    """여행 계획에 포함된 관광지"""
    travel_plan = models.ForeignKey(
        TravelPlan,
        on_delete=models.CASCADE,
        related_name="plan_places",
        verbose_name="여행 계획"
    )
    place_id = models.BigIntegerField(null=True, blank=True, verbose_name="관광지 ID")
    visit_date = models.DateField(null=True, blank=True, verbose_name="방문일")
    visit_time = models.TimeField(null=True, blank=True, verbose_name="방문 시간")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "plan_place"
        verbose_name = "계획 관광지"
        verbose_name_plural = "계획 관광지들"
        indexes = [
            models.Index(fields=['travel_plan'], name='idx_plan_place_travel_plan'),
        ]

    def __str__(self):
        return f"Plan {self.travel_plan_id} - Place {self.place_id}"
