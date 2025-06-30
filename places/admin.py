from django.contrib import admin
from places.models import PlaceKR, PlaceEN, PlaceJP, PlaceCN

@admin.register(PlaceKR)
class PlaceKRAdmin(admin.ModelAdmin):
    list_display = ["name", "region_name", "region_code", "view_count", "created_at"]
    list_filter = ["region_code", "is_idol_spot"]
    search_fields = ["name", "address"]

@admin.register(PlaceEN)
class PlaceENAdmin(admin.ModelAdmin):
    list_display = ["name", "region_name", "region_code", "view_count", "created_at"]
    list_filter = ["region_code", "is_idol_spot"]
    search_fields = ["name", "address"]

@admin.register(PlaceJP)
class PlaceJPAdmin(admin.ModelAdmin):
    list_display = ["name", "region_name", "region_code", "view_count", "created_at"]
    list_filter = ["region_code", "is_idol_spot"]
    search_fields = ["name", "address"]

@admin.register(PlaceCN)
class PlaceCNAdmin(admin.ModelAdmin):
    list_display = ["name", "region_name", "region_code", "view_count", "created_at"]
    list_filter = ["region_code", "is_idol_spot"]
    search_fields = ["name", "address"]