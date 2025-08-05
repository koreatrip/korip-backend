from django.contrib import admin

try:
    from django.contrib.gis.admin import GeoModelAdmin as OSMGeoAdmin
except ImportError:
    try:
        from django.contrib.gis.admin import OSMGeoAdmin
    except ImportError:
        OSMGeoAdmin = admin.ModelAdmin

from places.models import Place, PlaceTranslation


class PlaceTranslationInline(admin.TabularInline):
    model = PlaceTranslation
    extra = 1
    fields = ("lang", "name", "description", "address")


@admin.register(Place)
class PlaceAdmin(OSMGeoAdmin):
    list_display = [
        "id",
        "content_id",
        "get_korean_name",
        "category",
        "sub_category",
        "region",
        "sub_region",
        "favorite_count",
        "get_coordinates",
        "created_at"
    ]

    search_fields = ["content_id", "translations__name"]
    list_filter = ["region", "sub_region", "category", "created_at"]
    fieldsets = (
        ("기본 정보", {
            "fields": ("content_id",)
        }),
        ("위치 설정", {
            "fields": ("location", "get_coordinates_display"),
            "description": "지도에서 클릭하거나 드래그하여 위치를 설정할 수 있습니다."
        }),
        ("카테고리", {
            "fields": ("category", "sub_category")
        }),
        ("지역", {
            "fields": ("region", "sub_region")
        }),
        ("연락처/링크", {
            "fields": ("phone_number", "use_time", "link_url")
        }),
        ("통계", {
            "fields": ("favorite_count", "last_synced_at")
        }),
        ("날짜", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )

    readonly_fields = ["created_at", "updated_at", "get_coordinates_display"]
    inlines = [PlaceTranslationInline]

    # GIS 맵 설정 - 한국 전체 지역 표시
    default_lon = 127.5  # 한국 중심 경도
    default_lat = 36.0  # 한국 중심 위도
    default_zoom = 6  # 한국 전체가 확실히 보이는 줌 레벨
    display_wkt = False  # WKT 형식 비활성화
    display_srid = False  # SRID 비활성화
    map_width = 800  # 맵 너비
    map_height = 500  # 맵 높이

    # 맵 타일 설정 - OpenStreetMap 기본 타일 사용 (도로, 건물명 표시)
    map_template = 'gis/admin/openlayers.html'
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'

    # 추가 맵 설정
    scrollable = True  # 스크롤로 줌 활성화 (편의성)
    map_srid = 4326  # 좌표계 명시

    def get_korean_name(self, obj):
        return obj.get_name("ko") or "-"

    get_korean_name.short_description = "한국어명"

    def get_coordinates(self, obj):
        if obj.location:
            return f"{obj.location.y:.6f}, {obj.location.x:.6f}"
        return "-"

    get_coordinates.short_description = "위도, 경도"

    def get_coordinates_display(self, obj):
        """좌표를 읽기 쉽게 표시"""
        if obj.location:
            lat, lon = obj.location.y, obj.location.x
            return f"위도: {lat:.6f}, 경도: {lon:.6f}"
        return "좌표 없음"

    get_coordinates_display.short_description = "현재 좌표"


@admin.register(PlaceTranslation)
class PlaceTranslationAdmin(admin.ModelAdmin):
    list_display = ["place", "lang", "name", "tour_api_content_id", "get_short_description", "created_at"]
    list_filter = ["lang", "created_at"]
    readonly_fields = ["created_at", "updated_at"]

    search_fields = ["name", "description", "place__content_id", "tour_api_content_id"]

    fieldsets = (
        ("기본 정보", {
            "fields": ("place", "lang", "tour_api_content_id")
        }),
        ("번역 내용", {
            "fields": ("name", "description", "address")
        }),
        ("날짜", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )

    def get_short_description(self, obj):
        if obj.description:
            return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
        return "-"

    get_short_description.short_description = "설명 요약"
