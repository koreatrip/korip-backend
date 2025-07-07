# places/admin.py
from django.contrib import admin
from places.models import Place, PlaceTranslation


# Place Admin에서 번역을 인라인으로 관리
class PlaceTranslationInline(admin.TabularInline):
    model = PlaceTranslation
    extra = 4  # 4개 언어 지원하니까 4개 빈 폼 표시
    fields = ["lang", "name", "description", "address"]


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "content_id",
        "get_korean_name",
        "category_id",
        "sub_category_id",
        "region_id",
        "favorite_count",
        "region_code",
        "created_at"
    ]

    list_filter = [
        "category_id",
        "sub_category_id",
        "region_id",
        "region_code",
        "created_at"
    ]

    search_fields = [
        "content_id",
        "region_code",
        "translations__name",
    ]

    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "last_synced_at"
    ]

# PlaceTranslation을 인라인으로 추가
    inlines = [PlaceTranslationInline]

    fieldsets = [
        ("기본 정보", {
            "fields": [
                "content_id",
                "latitude",
                "longitude",
                "phone_number",
                "use_time",
                "link_url"
            ]
        }),
        ("카테고리 및 지역", {
            "fields": [
                "category_id",
                "sub_category_id",
                "region_id",
                "region_code"
            ]
        }),
        ("통계", {
            "fields": [
                "favorite_count"
            ]
        }),
        ("시스템", {
            "fields": [
                "created_at",
                "updated_at",
                "last_synced_at"
            ]
        })
    ]

# 리스트에서 한국어 이름 표시
    def get_korean_name(self, obj):
        name = obj.get_name("ko")
        return name if name else "(번역 없음)"

    get_korean_name.short_description = "한국어명"


# 관광지 번역 관리 Admin
@admin.register(PlaceTranslation)
class PlaceTranslationAdmin(admin.ModelAdmin):
    list_display = ["place", "lang", "name", "get_short_description", "created_at"]
    list_filter = ["lang", "created_at"]
    search_fields = ["name", "description", "place__content_id"]

    fieldsets = (
        ("기본 정보", {
            "fields": ("place", "lang")
        }),
        ("번역 내용", {
            "fields": ("name", "description", "address")
        }),
        ("시스템", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    readonly_fields = ["created_at", "updated_at"]

# 설명을 50자로 제한해서 표시
    def get_short_description(self, obj):
        if obj.description:
            return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
        return "-"

    get_short_description.short_description = "설명"
