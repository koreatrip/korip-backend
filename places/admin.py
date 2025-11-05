from django import forms
from django.contrib import admin
from django.contrib.gis.geos import Point
from categories.models import SubCategory
from regions.models import SubRegion

try:
    from django.contrib.gis.admin import GeoModelAdmin as OSMGeoAdmin
except ImportError:
    try:
        from django.contrib.gis.admin import OSMGeoAdmin
    except ImportError:
        OSMGeoAdmin = admin.ModelAdmin

from places.models import Place, PlaceTranslation, IdolVisit, IdolVisitTranslation


class PlaceAdminForm(forms.ModelForm):
    latitude = forms.FloatField(
        required=False,
        label="위도",
        help_text="예: 37.5665 (서울 시청 위도)"
    )
    longitude = forms.FloatField(
        required=False,
        label="경도",
        help_text="예: 126.9780 (서울 시청 경도)"
    )

    class Meta:
        model = Place
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 기존 데이터가 있으면 위도/경도 값 채워넣기
        if self.instance and self.instance.location:
            self.fields["latitude"].initial = self.instance.location.y
            self.fields["longitude"].initial = self.instance.location.x

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        # 위도/경도 둘 다 입력되었으면 Point 객체 생성
        if latitude is not None and longitude is not None:
            cleaned_data["location"] = Point(longitude, latitude)

        return cleaned_data


class PlaceTranslationInline(admin.TabularInline):
    model = PlaceTranslation
    extra = 1
    fields = ("lang", "name", "description", "address")


# IdolVisitTranslation Inline (아이돌 방문 기록의 번역)
class IdolVisitTranslationInline(admin.TabularInline):
    model = IdolVisitTranslation
    extra = 1
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
        "place__translations__name",
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
    autocomplete_fields = ["place"]

    def get_place_name(self, obj):
        return obj.place.get_name("ko") or "-"

    get_place_name.short_description = "방문 장소"

    def get_description_preview(self, obj):
        desc = obj.get_description("ko")
        if desc:
            return desc[:50] + "..." if len(desc) > 50 else desc
        return "-"

    get_description_preview.short_description = "설명 미리보기"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            self.message_user(
                request,
                f"'{obj.place.get_name('ko')}'이(가) 자동으로 K-POP 명소로 표시되었습니다.",
                level="SUCCESS"
            )


# IdolVisitTranslation Admin
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
        if obj.idol_visit.idol_group:
            return f"{obj.idol_visit.idol_group} {obj.idol_visit.idol_name}"
        return obj.idol_visit.idol_name

    get_idol_info.short_description = "아이돌"

    def get_description_preview(self, obj):
        if obj.description:
            return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
        return "-"

    get_description_preview.short_description = "설명 미리보기"


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    form = PlaceAdminForm

    autocomplete_fields = ["category", "sub_category", "region", "sub_region"]

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
        "created_at"
    ]

    search_fields = ["content_id", "translations__name"]

    list_filter = [
        "category",
        "sub_category",
        "region",
        "sub_region",
        "is_kpop_spot",
        "created_at"
    ]

    fieldsets = (
        ("기본 정보", {
            "fields": ("content_id", "is_kpop_spot"),
            "description": "content_id는 투어 API 데이터만 입력됩니다. 수동 추가 시 비워두세요."
        }),
        ("위치 설정 (좌표)", {
            "fields": ["latitude", "longitude", "get_coordinates_display"],
            "description": "위도/경도를 직접 입력하세요. 예: 서울시청 (37.5665, 126.9780)"
        }),
        ("카테고리", {
            "fields": ("category", "sub_category"),
            "description": "카테고리를 먼저 선택하면 서브카테고리가 필터링됩니다."
        }),
        ("지역", {
            "fields": ("region", "sub_region"),
            "description": "지역을 먼저 선택하면 지역구가 필터링됩니다."
        }),
        ("연락처/링크", {
            "fields": ("phone_number", "use_time", "link_url", "image_url")
        }),
        ("통계", {
            "fields": ("favorite_count", "last_synced_at"),
            "classes": ("collapse",)
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

    def get_korean_name(self, obj):
        return obj.get_name("ko") or "-"

    get_korean_name.short_description = "한국어명"

    def get_coordinates(self, obj):
        if obj.location:
            return f"{obj.location.y:.6f}, {obj.location.x:.6f}"
        return "-"

    get_coordinates.short_description = "위도, 경도"

    def get_coordinates_display(self, obj):
        if obj.location:
            lat, lon = obj.location.y, obj.location.x
            return f"위도: {lat:.6f}, 경도: {lon:.6f}"
        return "좌표 없음"

    get_coordinates_display.short_description = "현재 좌표"

    # 카테고리/지역 동적 필터링
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # 서브카테고리 필터링
        if db_field.name == "sub_category":
            category_id = request.GET.get("category")
            if category_id:
                # 카테고리 선택되어 있으면 필터링
                kwargs["queryset"] = SubCategory.objects.filter(parent_id=category_id)
            # 선택 안 되어 있으면 전체 목록 보여주기

        # 지역구 필터링
        if db_field.name == "sub_region":
            region_id = request.GET.get("region")
            if region_id:
                # 지역 선택되어 있으면 필터링
                kwargs["queryset"] = SubRegion.objects.filter(region_id=region_id)
            # 선택 안 되어 있으면 전체 목록 보여주기

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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

