from django.db import models


class Category(models.Model):

    name_ko = models.CharField(max_length=50, null=False, blank=False, verbose_name="한국어 이름")
    name_en = models.CharField(max_length=50, null=False, blank=False, verbose_name="영어 이름")
    name_jp = models.CharField(max_length=50, null=False, blank=False, verbose_name="일본어 이름")
    name_cn = models.CharField(max_length=50, null=False, blank=False, verbose_name="중국어 이름")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = 'category'
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리들'

    def __str__(self):
        return self.name_ko


class SubCategory(models.Model):

    name_ko = models.CharField(max_length=50, null=False, blank=False, verbose_name="한국어 이름")
    name_en = models.CharField(max_length=50, null=False, blank=False, verbose_name="영어 이름")
    name_jp = models.CharField(max_length=50, null=False, blank=False, verbose_name="일본어 이름")
    name_cn = models.CharField(max_length=50, null=False, blank=False, verbose_name="중국어 이름")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name="부모 카테고리"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = 'subcategory'
        verbose_name = '서브 카테고리'
        verbose_name_plural = '서브 카테고리들'

    def __str__(self):
        return self.name_ko