from django.contrib import admin
from places.models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "content_id",
        "category_id",
        "sub_category_id",
        "region_id",
        "view_count",
        "created_at"
    ]

    list_filter = [
        "category_id",
        "sub_category_id",
        "region_id",
        "created_at"
    ]

    search_fields = [
        "content_id",
    ]

    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "last_synced_at"
    ]

    fieldsets = [
        ("기본 정보", {
            "fields": [
                "content_id",
                "latitude",
                "longitude",
                "phone_number",
                "opening_hours"
            ]
        }),
        ("카테고리 및 지역", {
            "fields": [
                "category_id",
                "sub_category_id",
                "region_id"
            ]
        }),
        ("통계", {
            "fields": [
                "view_count"
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
