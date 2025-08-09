from django.contrib import admin
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


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


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = [
        "id",  # 지역 ID
        "get_korean_name",  # 한국어 지역명
        "get_korean_description",  # 한국어 설명
        "get_korean_features",  # 한국어 특징
        "created_at"  # 생성일시
    ]

    list_filter = ["created_at"]
    search_fields = ["translations__name", "translations__description", "translations__features"]
    readonly_fields = ["created_at", "updated_at"]
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