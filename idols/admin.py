from django.contrib import admin
from idols.models import IdolRequest


# 어드민 페이지 커스터마이징
@admin.register(IdolRequest)
class IdolRequestAdmin(admin.ModelAdmin):
    # 목록에서 보여줄 컬럼들
    list_display = [
        "id",
        "idol_name",
        "agency",
        "user",
        "created_at"
    ]

    # 검색 가능한 필드들
    search_fields = [
        "idol_name",
        "agency",
        "user__email"
    ]

    # 필터링 가능한 필드들
    list_filter = [
        "created_at",
    ]

    # 상세 페이지에서 읽기 전용 필드
    readonly_fields = [
        "created_at",
        "updated_at"
    ]

    # 상세 페이지 필드 순서
    fields = [
        "user",
        "idol_name",
        "agency",
        "related_info",
        "additional_notes",
        "admin_memo",
        "created_at",
        "updated_at"
    ]
