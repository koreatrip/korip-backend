from django.contrib import admin
from regions.models import Region, SubRegion, RegionTranslation, SubRegionTranslation


class RegionTranslationInline(admin.TabularInline):
    model = RegionTranslation
    extra = 4
    max_num = 4
    fields = ["lang", "name", "description"]


class SubRegionTranslationInline(admin.TabularInline):
    model = SubRegionTranslation
    extra = 4
    max_num = 4
    fields = ["lang", "name", "description", "features"]


class SubRegionInline(admin.TabularInline):
    model = SubRegion
    extra = 1
    readonly_fields = ["created_at", "updated_at"]
    fields = ["favorite_count", "latitude", "longitude", "created_at", "updated_at"]

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["id", "get_korean_name", "get_subregion_count", "created_at"]
    search_fields = ["translations__name"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [RegionTranslationInline, SubRegionInline]

    def get_korean_name(self, obj):
        try:
            korean_translation = obj.translations.get(lang="ko")
            return korean_translation.name
        except RegionTranslation.DoesNotExist:
            return f"Region {obj.id}"

    get_korean_name.short_description = "지역명 (한국어)"

    def get_subregion_count(self, obj):
        return obj.subregions.count()

    get_subregion_count.short_description = "지역구 수"


@admin.register(SubRegion)
class SubRegionAdmin(admin.ModelAdmin):
    list_display = [
        "id", "get_korean_name", "get_region_name",
        "favorite_count", "latitude", "longitude", "created_at"
    ]
    search_fields = ["translations__name", "region__translations__name"]
    list_filter = ["region", "created_at"]
    readonly_fields = ["created_at", "updated_at"]
    fields = [
        "region",
        "favorite_count",
        "latitude",
        "longitude",
        "created_at",
        "updated_at"
    ]
    inlines = [SubRegionTranslationInline]

    def get_korean_name(self, obj):
        try:
            korean_translation = obj.translations.get(lang="ko")
            return korean_translation.name
        except SubRegionTranslation.DoesNotExist:
            return f"SubRegion {obj.id}"

    get_korean_name.short_description = "지역구명 (한국어)"

    def get_region_name(self, obj):
        try:
            region_translation = obj.region.translations.get(lang="ko")
            return region_translation.name
        except (RegionTranslation.DoesNotExist, AttributeError):
            return "지역 없음"

    get_region_name.short_description = "소속 지역"

@admin.register(RegionTranslation)
class RegionTranslationAdmin(admin.ModelAdmin):
    list_display = ["id", "region", "lang", "name"]
    list_filter = ["lang"]
    search_fields = ["name"]


@admin.register(SubRegionTranslation)
class SubRegionTranslationAdmin(admin.ModelAdmin):
    list_display = ["id", "sub_region", "lang", "name"]
    list_filter = ["lang"]
    search_fields = ["name"]
