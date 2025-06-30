from django.db import models
from categories.models import Category, SubCategory


class PlaceKR(models.Model):
    # 관계
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    # 기본 정보
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    # 위치 정보
    address = models.CharField(max_length=500, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    # 연락처
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    opening_hours = models.CharField(max_length=200, null=True, blank=True)
    # 지역 정보
    region_code = models.CharField(max_length=20, null=True, blank=True)
    region_name = models.CharField(max_length=100, null=True, blank=True)
    # 이미지
    image_url = models.CharField(max_length=500, null=True, blank=True)
    # 조회수
    view_count = models.IntegerField(default=0)
    # 아이돌 성지 관련
    is_idol_spot = models.BooleanField(default=False)
    idol_name = models.CharField(max_length=100, null=True, blank=True)
    idol_group = models.CharField(max_length=100, null=True, blank=True)
    visit_reason = models.CharField(max_length=200, null=True, blank=True)
    # 동기화 정보
    last_synced_at = models.DateTimeField(null=True, blank=True)
    # 생성/수정 시간
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "관광지(한국어)"
        verbose_name_plural = "관광지들(한국어)"


class PlaceEN(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    opening_hours = models.CharField(max_length=200, null=True, blank=True)
    region_code = models.CharField(max_length=20, null=True, blank=True)
    region_name = models.CharField(max_length=100, null=True, blank=True)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    view_count = models.IntegerField(default=0)
    is_idol_spot = models.BooleanField(default=False)
    idol_name = models.CharField(max_length=100, null=True, blank=True)
    idol_group = models.CharField(max_length=100, null=True, blank=True)
    visit_reason = models.CharField(max_length=200, null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "관광지(영어)"
        verbose_name_plural = "관광지들(영어)"


class PlaceJP(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    opening_hours = models.CharField(max_length=200, null=True, blank=True)
    region_code = models.CharField(max_length=20, null=True, blank=True)
    region_name = models.CharField(max_length=100, null=True, blank=True)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    view_count = models.IntegerField(default=0)
    is_idol_spot = models.BooleanField(default=False)
    idol_name = models.CharField(max_length=100, null=True, blank=True)
    idol_group = models.CharField(max_length=100, null=True, blank=True)
    visit_reason = models.CharField(max_length=200, null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "관광지(일본어)"
        verbose_name_plural = "관광지들(일본어)"


class PlaceCN(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    opening_hours = models.CharField(max_length=200, null=True, blank=True)
    region_code = models.CharField(max_length=20, null=True, blank=True)
    region_name = models.CharField(max_length=100, null=True, blank=True)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    view_count = models.IntegerField(default=0)
    is_idol_spot = models.BooleanField(default=False)
    idol_name = models.CharField(max_length=100, null=True, blank=True)
    idol_group = models.CharField(max_length=100, null=True, blank=True)
    visit_reason = models.CharField(max_length=200, null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "관광지(중국어)"
        verbose_name_plural = "관광지들(중국어)"
