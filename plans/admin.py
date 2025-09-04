# plans/admin.py
from django.contrib import admin
from plans.models import TravelPlan, TravelPlanTranslation, PlanPlace


class TravelPlanTranslationInline(admin.TabularInline):
    """여행 계획 번역 인라인"""
    model = TravelPlanTranslation
    extra = 1
    fields = ["lang", "title", "description"]


class PlanPlaceInline(admin.TabularInline):
    """계획 관광지 인라인"""
    model = PlanPlace
    extra = 0
    fields = ["place_id", "visit_date", "visit_time"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(TravelPlan)
class TravelPlanAdmin(admin.ModelAdmin):
    """여행 계획 관리"""
    list_display = ["id", "get_title", "user_id", "subregion_id", "start_date", "end_date",
                    "created_at"]  # get_destination 제거
    list_filter = ["start_date", "end_date", "created_at"]
    search_fields = ["translations__title", "user_id"]  # translations__destination 제거
    readonly_fields = ["created_at", "updated_at"]

    inlines = [TravelPlanTranslationInline, PlanPlaceInline]

    fieldsets = [
        ("기본 정보", {
            "fields": ["user_id", "subregion_id"]
        }),
        ("날짜 정보", {
            "fields": ["start_date", "end_date"]
        }),
        ("시간 정보", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"]
        }),
    ]

    def get_title(self, obj):
        """한국어 제목 표시"""
        return obj.get_title("ko")

    get_title.short_description = "제목"


@admin.register(TravelPlanTranslation)
class TravelPlanTranslationAdmin(admin.ModelAdmin):
    """여행 계획 번역 관리"""
    list_display = ["id", "travel_plan", "lang", "title", "created_at"]  # destination 제거
    list_filter = ["lang", "created_at"]
    search_fields = ["title", "description", "travel_plan__id"]  # destination 제거
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = [
        ("번역 정보", {
            "fields": ["travel_plan", "lang", "title", "description"]  # destination 제거
        }),
        ("시간 정보", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"]
        }),
    ]


@admin.register(PlanPlace)
class PlanPlaceAdmin(admin.ModelAdmin):
    """계획 관광지 관리"""
    list_display = ["id", "travel_plan", "place_id", "visit_date", "visit_time", "created_at"]
    list_filter = ["visit_date", "visit_time", "created_at"]
    search_fields = ["travel_plan__translations__title", "place_id"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = [
        ("계획 정보", {
            "fields": ["travel_plan", "place_id"]
        }),
        ("방문 정보", {
            "fields": ["visit_date", "visit_time"]
        }),
        ("시간 정보", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"]
        }),
    ]
