from django.db import models


class Category(models.Model):
    """기존 카테고리 모델 (당분간 유지)"""
    name_ko = models.CharField(max_length=50, null=False, blank=False, verbose_name="한국어 이름")
    name_en = models.CharField(max_length=50, null=False, blank=False, verbose_name="영어 이름")
    name_jp = models.CharField(max_length=50, null=False, blank=False, verbose_name="일본어 이름")
    name_cn = models.CharField(max_length=50, null=False, blank=False, verbose_name="중국어 이름")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "category"
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리"

    def __str__(self):
        return self.name_ko

    def get_name(self, lang):
        """언어별 카테고리 이름 조회 헬퍼 메서드"""
        try:
            translation = self.translations.get(lang=lang)
            return translation.name
        except CategoryTranslation.DoesNotExist:
            return None


class SubCategory(models.Model):
    """기존 서브카테고리 모델 (당분간 유지)"""
    name_ko = models.CharField(max_length=50, null=False, blank=False, verbose_name="한국어 이름")
    name_en = models.CharField(max_length=50, null=False, blank=False, verbose_name="영어 이름")
    name_jp = models.CharField(max_length=50, null=False, blank=False, verbose_name="일본어 이름")
    name_cn = models.CharField(max_length=50, null=False, blank=False, verbose_name="중국어 이름")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name="부모 카테고리"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "subcategory"
        verbose_name = "서브 카테고리"
        verbose_name_plural = "서브 카테고리"

    def __str__(self):
        return self.name_ko

    def get_name(self, lang):
        """언어별 서브카테고리 이름 조회 헬퍼 메서드"""
        try:
            translation = self.translations.get(lang=lang)
            return translation.name
        except SubCategoryTranslation.DoesNotExist:
            return None


# 새로운 번역 방식 모델들
class CategoryTranslation(models.Model):
    """카테고리 번역 테이블"""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="카테고리"
    )
    lang = models.CharField(
        max_length=10,
        verbose_name="언어 코드"
    )
    name = models.CharField(
        max_length=50,
        verbose_name="번역된 이름"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "category_translation"
        verbose_name = "카테고리 번역"
        verbose_name_plural = "카테고리 번역"
        # 카테고리 + 언어 조합은 유일해야 함
        unique_together = (("category", "lang"),)

    def __str__(self):
        return f"{self.category.id} - {self.lang}: {self.name}"


class SubCategoryTranslation(models.Model):
    """서브카테고리 번역 테이블"""
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="서브카테고리"
    )
    lang = models.CharField(
        max_length=10,
        verbose_name="언어 코드"
    )
    name = models.CharField(
        max_length=50,
        verbose_name="번역된 이름"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "subcategory_translation"
        verbose_name = "서브카테고리 번역"
        verbose_name_plural = "서브카테고리 번역"
        # 서브카테고리 + 언어 조합은 유일해야 함
        unique_together = (("sub_category", "lang"),)

    def __str__(self):
        return f"{self.sub_category.id} - {self.lang}: {self.name}"