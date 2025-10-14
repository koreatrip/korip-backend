from django.contrib import admin

try:
    from django.contrib.gis.admin import GeoModelAdmin as OSMGeoAdmin
except ImportError:
    try:
        from django.contrib.gis.admin import OSMGeoAdmin
    except ImportError:
        OSMGeoAdmin = admin.ModelAdmin

from places.models import Place, PlaceTranslation, IdolVisit, IdolVisitTranslation


class PlaceTranslationInline(admin.TabularInline):
    model = PlaceTranslation
    extra = 1
    fields = ("lang", "name", "description", "address")


# IdolVisitTranslation Inline (아이돌 방문 기록의 번역)
class IdolVisitTranslationInline(admin.TabularInline):
    model = IdolVisitTranslation
    extra = 1  # 기본으로 1개 빈 폼 표시
    fields = ("lang", "description")
    verbose_name = "아이돌 방문 설명 (언어별)"
    verbose_name_plural = "아이돌 방문 설명 (언어별)"


# IdolVisit Admin
@admin.register(IdolVisit)
class IdolVisitAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "get_place_name",
        "idol_name",
        "idol_group",
        "visit_date",
        "get_description_preview",
        "created_at"
    ]

    list_filter = ["idol_group", "visit_date", "created_at"]
    search_fields = [
        "idol_name",
        "idol_group",
        "place__translations__name",  # 장소명으로 검색
    ]

    fieldsets = (
        ("기본 정보", {
            "fields": ("place", "idol_name", "idol_group"),
            "description": "어떤 장소에 어떤 아이돌이 방문했는지 입력하세요."
        }),
        ("방문 상세", {
            "fields": ("visit_date", "source_url"),
            "description": "방문 날짜와 출처 링크를 입력하세요. (선택사항)"
        }),
        ("날짜", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )

    readonly_fields = ["created_at", "updated_at"]
    inlines = [IdolVisitTranslationInline]

    # 자동완성
    autocomplete_fields = ["place"]

    def get_place_name(self, obj):
        """장소 한국어명 표시"""
        return obj.place.get_name("ko") or "-"

    get_place_name.short_description = "방문 장소"

    def get_description_preview(self, obj):
        """한국어 설명 미리보기"""
        desc = obj.get_description("ko")
        if desc:
            return desc[:50] + "..." if len(desc) > 50 else desc
        return "-"

    get_description_preview.short_description = "설명 미리보기"

    # 저장 후 메시지
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # 새로 생성된 경우
            self.message_user(
                request,
                f"'{obj.place.get_name('ko')}'이(가) 자동으로 K-POP 명소로 표시되었습니다.",
                level="SUCCESS"
            )


# IdolVisitTranslation Admin (필요시 직접 수정용)
@admin.register(IdolVisitTranslation)
class IdolVisitTranslationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "get_idol_info",
        "lang",
        "get_description_preview",
        "created_at"
    ]

    list_filter = ["lang", "created_at"]
    search_fields = [
        "idol_visit__idol_name",
        "idol_visit__idol_group",
        "description"
    ]

    fieldsets = (
        ("기본 정보", {
            "fields": ("idol_visit", "lang")
        }),
        ("번역 내용", {
            "fields": ("description",)
        }),
        ("날짜", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )

    readonly_fields = ["created_at", "updated_at"]

    def get_idol_info(self, obj):
        """아이돌 정보 표시"""
        if obj.idol_visit.idol_group:
            return f"{obj.idol_visit.idol_group} {obj.idol_visit.idol_name}"
        return obj.idol_visit.idol_name

    get_idol_info.short_description = "아이돌"

    def get_description_preview(self, obj):
        """설명 미리보기"""
        if obj.description:
            return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
        return "-"

    get_description_preview.short_description = "설명 미리보기"

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "content_id",
        "get_korean_name",
        "category",
        "sub_category",
        "region",
        "sub_region",
        "is_kpop_spot",
        "favorite_count",
        "get_coordinates",
        "image_url",
        "created_at"
    ]

    search_fields = ["content_id", "translations__name"]
    list_filter = [
        "region",
        "sub_region",
        "category",
        "is_kpop_spot",
        "created_at"
    ]
    fieldsets = (
        ("기본 정보", {
            "fields": ("content_id", "is_kpop_spot"),
            "description": "is_kpop_spot은 자동으로 설정됩니다. (IdolVisit 추가 시)"
        }),
        ("위치 설정", {
            "fields": ["get_coordinates_display"],
        }),
        ("카테고리", {
            "fields": ("category", "sub_category")
        }),
        ("지역", {
            "fields": ("region", "sub_region")
        }),
        ("연락처/링크", {
            "fields": ("phone_number", "use_time", "link_url", "image_url")
        }),
        ("통계", {
            "fields": ("favorite_count", "last_synced_at")
        }),
        ("날짜", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )

    readonly_fields = [
        "created_at",
        "updated_at",
        "get_coordinates_display",
        "is_kpop_spot"
    ]
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

    def image_preview(self, obj):
        if obj.image_url:
            return f'<img src="{obj.image_url}" width="100" height="60" />'
        return "이미지 없음"
    image_preview.allow_tags = True
    image_preview.short_description = "이미지 미리보기"


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
