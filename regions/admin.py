from django.contrib import admin
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation
from django.utils.html import format_html
from django import forms
from storages.backends.s3boto3 import S3Boto3Storage


class RegionTranslationInline(admin.TabularInline):
    model = RegionTranslation
    extra = 1
    max_num = 4
    fields = ["lang", "name", "description", "features"]


class SubRegionTranslationInline(admin.TabularInline):
    model = SubRegionTranslation
    extra = 1
    max_num = 4
    fields = ["lang", "name", "description", "features"]


class SubRegionInline(admin.TabularInline):
    model = SubRegion
    extra = 1
    readonly_fields = ["get_coordinate_display", "created_at"]
    fields = ["favorite_count", "get_coordinate_display", "created_at"]

    def get_coordinate_display(self, obj):
        if obj and obj.latitude and obj.longitude:
            return f"({obj.latitude:.4f}, {obj.longitude:.4f})"
        return "-"

    get_coordinate_display.short_description = "좌표 (위도, 경도)"


class RegionAdminForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = "__all__"

    def save(self, commit=True):
        instance = super().save(commit=False)

        # 이미지 파일이 있으면 강제로 S3에 저장
        if self.cleaned_data.get("image"):
            image_file = self.cleaned_data["image"]
            s3_storage = S3Boto3Storage()

            # S3에 저장
            file_path = f"regions/{image_file.name}"
            saved_name = s3_storage.save(file_path, image_file)

            # DB에는 중복 경로 제거해서 저장
            clean_path = saved_name.replace("regions/regions/", "regions/")
            instance.image.name = clean_path

        if commit:
            instance.save()
        return instance


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    form = RegionAdminForm
    list_display = [
        "id",  # 지역 ID
        "get_korean_name",  # 한국어 지역명
        "get_image_preview",
        "get_korean_description",  # 한국어 설명
        "get_korean_features",  # 한국어 특징
        "created_at"  # 생성일시
    ]

    list_filter = ["created_at"]
    search_fields = ["translations__name", "translations__description", "translations__features"]
    readonly_fields = ["created_at", "updated_at"]

    fields = [
        "image",  # 이미지 필드
        "created_at",
        "updated_at"
    ]

    inlines = [RegionTranslationInline, SubRegionInline]

    def get_korean_name(self, obj):
        korean_name = obj.get_name("ko")
        return korean_name if korean_name else f"Region {obj.id}"

    get_korean_name.short_description = "지역명 (한국어)"

    def get_korean_description(self, obj):
        korean_desc = obj.get_description("ko")
        if korean_desc:
            return korean_desc[:40] + ("..." if len(korean_desc) > 40 else "")
        return "-"

    get_korean_description.short_description = "설명"

    def get_korean_features(self, obj):
        korean_features = obj.get_features("ko")
        if korean_features:
            return korean_features[:40] + ("..." if len(korean_features) > 40 else "")
        return "-"

    get_korean_features.short_description = "특징"

    def get_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "-"

    get_image_preview.short_description = "이미지"


@admin.register(SubRegion)
class SubRegionAdmin(admin.ModelAdmin):
    list_display = [
        "id",  # 지역구 ID
        "get_korean_name",  # 한국어 지역구명
        "get_region_name",  # 지역명
        "favorite_count",  # 즐겨찾기 수
        "get_korean_description",  # 한국어 설명
        "get_korean_features",  # 한국어 특징
        "get_latitude",
        "get_longitude",
        "created_at"  # 생성일시
    ]

    list_filter = ["region", "created_at"]
    search_fields = [
        "translations__name",
        "translations__description",
        "translations__features",
        "region__translations__name"
    ]
    readonly_fields = ["created_at", "updated_at"]
    fields = [
        "region",  # 지역 선택
        "favorite_count",  # 즐겨찾기 수
        "location",
        "created_at",  # 생성일
        "updated_at"  # 수정일
    ]

    inlines = [SubRegionTranslationInline]

    def get_korean_name(self, obj):
        korean_name = obj.get_name("ko")
        return korean_name if korean_name else f"SubRegion {obj.id}"

    get_korean_name.short_description = "지역구명 (한국어)"

    def get_region_name(self, obj):
        if obj.region:
            return obj.region.get_name("ko")
        return "-"

    get_region_name.short_description = "지역"

    def get_korean_description(self, obj):
        korean_desc = obj.get_description("ko")
        if korean_desc:
            return korean_desc[:30] + ("..." if len(korean_desc) > 30 else "")
        return "-"

    get_korean_description.short_description = "설명"

    def get_korean_features(self, obj):
        korean_features = obj.get_features("ko")
        if korean_features:
            return korean_features[:30] + ("..." if len(korean_features) > 30 else "")
        return "-"

    get_korean_features.short_description = "특징"

    def get_latitude(self, obj):
        return obj.latitude if obj.latitude else "-"

    get_latitude.short_description = "위도"

    def get_longitude(self, obj):
        return obj.longitude if obj.longitude else "-"

    get_longitude.short_description = "경도"


@admin.register(RegionTranslation)
class RegionTranslationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "region",
        "lang",
        "name",
        "get_short_description",
        "get_short_features"
    ]
    list_filter = ["lang", "region"]
    search_fields = ["name", "description", "features"]

    def get_short_description(self, obj):
        if obj.description:
            return obj.description[:30] + ("..." if len(obj.description) > 30 else "")
        return "-"

    get_short_description.short_description = "설명"

    def get_short_features(self, obj):
        if obj.features:
            return obj.features[:30] + ("..." if len(obj.features) > 30 else "")
        return "-"

    get_short_features.short_description = "특징"


@admin.register(SubRegionTranslation)
class SubRegionTranslationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "sub_region",
        "lang",
        "name",
        "get_short_description",
        "get_short_features"
    ]
    list_filter = ["lang", "sub_region__region"]
    search_fields = ["name", "description", "features", "sub_region__translations__name"]

    def get_short_description(self, obj):
        if obj.description:
            return obj.description[:30] + ("..." if len(obj.description) > 30 else "")
        return "-"

    get_short_description.short_description = "설명"

    def get_short_features(self, obj):
        if obj.features:
            return obj.features[:30] + ("..." if len(obj.features) > 30 else "")
        return "-"

    get_short_features.short_description = "특징"
