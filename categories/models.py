from django.db import models


class Category(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "category"
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리"

    def __str__(self):
        korean_name = self.get_name("ko")
        return korean_name if korean_name else f"Category {self.id}"

    def get_name(self, lang):
        try:
            translation = self.translations.get(lang=lang)
            return translation.name
        except CategoryTranslation.DoesNotExist:
            return None


class SubCategory(models.Model):
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
        korean_name = self.get_name("ko")
        return korean_name if korean_name else f"SubCategory {self.id}"

    def get_name(self, lang):
        try:
            translation = self.translations.get(lang=lang)
            return translation.name
        except SubCategoryTranslation.DoesNotExist:
            return None


class CategoryTranslation(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="카테고리"
    )
    lang = models.CharField(
        max_length=10,
        verbose_name="언어 코드",
        help_text="ko, en, jp, cn"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="번역된 이름"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "category_translation"
        verbose_name = "카테고리 번역"
        verbose_name_plural = "카테고리 번역"
        unique_together = (("category", "lang"),)

    def __str__(self):
        return f"{self.category.id} - {self.lang}: {self.name}"


class SubCategoryTranslation(models.Model):
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="서브카테고리"
    )
    lang = models.CharField(
        max_length=10,
        verbose_name="언어 코드",
        help_text="ko, en, jp, cn"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="번역된 이름"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "subcategory_translation"
        verbose_name = "서브카테고리 번역"
        verbose_name_plural = "서브카테고리 번역"
        unique_together = (("sub_category", "lang"),)

    def __str__(self):
        return f"{self.sub_category.id} - {self.lang}: {self.name}"
