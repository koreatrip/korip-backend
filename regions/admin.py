# regions/admin.py
# GIS 기능 완전 지원 + 테스트 완전 호환 최종 버전

from django.contrib import admin
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class RegionTranslationInline(admin.TabularInline):
    """Region 번역 인라인 - Region 수정할 때 번역도 같이 수정 가능"""
    model = RegionTranslation
    extra = 1  # 새로 추가할 수 있는 폼 1개 (테스트 호환)
    max_num = 4  # 최대 4개 언어 (ko, en, jp, cn)


class SubRegionTranslationInline(admin.TabularInline):
    """SubRegion 번역 인라인 - SubRegion 수정할 때 번역도 같이 수정 가능"""
    model = SubRegionTranslation
    extra = 1  # 새로 추가할 수 있는 폼 1개
    max_num = 4  # 최대 4개 언어


class SubRegionInline(admin.TabularInline):
    """Region 수정할 때 SubRegion들도 같이 보여주는 인라인"""
    model = SubRegion
    extra = 1  # 테스트에서 subregions-0-favorite_count를 기대하므로 1로 설정
    readonly_fields = ["get_coordinate_display", "created_at"]
    fields = ["favorite_count", "get_coordinate_display", "created_at"]

    def get_coordinate_display(self, obj):
        """SubRegion의 GIS location 필드에서 좌표를 예쁘게 표시

        왜 이렇게 하는지:
        1. location은 PostGIS Point 객체라서 복잡해
        2. 사용자가 한눈에 보기 쉽게 (위도, 경도) 형태로 표시
        3. SubRegion 모델의 latitude, longitude 프로퍼티 활용
        """
        if obj and obj.latitude and obj.longitude:
            return f"({obj.latitude:.4f}, {obj.longitude:.4f})"
        return "-"

    get_coordinate_display.short_description = "좌표 (위도, 경도)"


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    """지역(Region) 관리 페이지 설정

    주요 기능:
    1. 지역 목록에서 한국어 이름과 생성일 표시
    2. 지역명으로 검색 가능
    3. 지역 수정할 때 번역과 하위 지역구들도 같이 관리
    """

    # 🔥 지역 목록 페이지에서 보여줄 컬럼들
    list_display = [
        "id",  # 지역 ID
        "get_korean_name",  # 한국어 지역명
        "created_at"  # 생성일시
    ]

    # 🔥 필터링 옵션 (생성일로 필터 가능)
    list_filter = ["created_at"]

    # 🔥 검색 기능 (지역 번역 이름으로 검색)
    search_fields = ["translations__name"]

    # 🔥 수정 불가능한 필드들
    readonly_fields = ["created_at", "updated_at"]

    # 🔥 Region 수정할 때 같이 보여줄 인라인들
    inlines = [RegionTranslationInline, SubRegionInline]

    def get_korean_name(self, obj):
        """지역의 한국어 이름을 가져와서 표시하는 메서드

        왜 이 메서드가 필요한지:
        Region 모델 자체에는 이름이 없고, RegionTranslation에 저장되어 있어
        그래서 한국어(ko) 번역을 찾아서 이름을 가져와야 해
        """
        korean_name = obj.get_name("ko")
        return korean_name if korean_name else f"Region {obj.id}"

    get_korean_name.short_description = "지역명 (한국어)"


@admin.register(SubRegion)
class SubRegionAdmin(admin.ModelAdmin):
    """지역구(SubRegion) 관리 페이지 설정

    주요 기능:
    1. 지역구 목록에서 이름, 부모지역, 좌표, 즐겨찾기수 표시
    2. GIS location 필드에서 위도/경도 자동 추출해서 표시
    3. 부모 지역별로 필터링 가능
    """

    # 🔥 지역구 목록 페이지에서 보여줄 컬럼들 (GIS 호환)
    list_display = [
        "id",  # 지역구 ID
        "get_korean_name",  # 한국어 지역구명
        "get_region_name",  # 부모 지역명
        "favorite_count",  # 즐겨찾기 수
        "get_latitude",  # GIS에서 추출한 위도
        "get_longitude",  # GIS에서 추출한 경도
        "created_at"  # 생성일시
    ]

    # 🔥 필터링 옵션
    list_filter = ["region", "created_at"]

    # 🔥 검색 기능
    search_fields = ["translations__name", "region__translations__name"]

    # 🔥 수정 불가능한 필드들
    readonly_fields = ["created_at", "updated_at"]

    # 🔥 SubRegion 수정할 때 보여줄 필드들 (GIS location 포함)
    fields = [
        "region",  # 부모 지역 선택
        "favorite_count",  # 즐겨찾기 수
        "location",  # GIS Point 필드 (지도 위젯으로 표시됨)
        "created_at",  # 생성일 (읽기 전용)
        "updated_at"  # 수정일 (읽기 전용)
    ]

    # 🔥 SubRegion 번역 인라인
    inlines = [SubRegionTranslationInline]

    def get_korean_name(self, obj):
        """지역구의 한국어 이름을 가져와서 표시"""
        korean_name = obj.get_name("ko")
        return korean_name if korean_name else f"SubRegion {obj.id}"

    get_korean_name.short_description = "지역구명 (한국어)"

    def get_region_name(self, obj):
        """부모 지역의 한국어 이름을 가져와서 표시"""
        if obj.region:
            return obj.region.get_name("ko")
        return "-"

    get_region_name.short_description = "부모 지역"

    def get_latitude(self, obj):
        """GIS location PointField에서 위도를 추출해서 표시

        왜 이렇게 하는지:
        1. location은 PostGIS Point 객체
        2. SubRegion 모델에 @property latitude가 정의되어 있어서
        3. obj.latitude로 접근하면 내부적으로 location.y 값을 반환해
        """
        return obj.latitude if obj.latitude else "-"

    get_latitude.short_description = "위도"

    def get_longitude(self, obj):
        """GIS location PointField에서 경도를 추출해서 표시"""
        return obj.longitude if obj.longitude else "-"

    get_longitude.short_description = "경도"


@admin.register(RegionTranslation)
class RegionTranslationAdmin(admin.ModelAdmin):
    """지역 번역 관리 페이지"""
    list_display = ["id", "region", "lang", "name"]
    list_filter = ["lang", "region"]
    search_fields = ["name"]


@admin.register(SubRegionTranslation)
class SubRegionTranslationAdmin(admin.ModelAdmin):
    """지역구 번역 관리 페이지"""
    list_display = ["id", "sub_region", "lang", "name"]
    list_filter = ["lang", "sub_region__region"]
    search_fields = ["name", "sub_region__translations__name"]
