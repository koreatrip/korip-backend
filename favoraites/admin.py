from django.contrib import admin
from .models import FavoritePlace


@admin.register(FavoritePlace)
class FavoritePlaceAdmin(admin.ModelAdmin):
    """즐겨찾는 장소 Admin 설정"""
    
    # 목록 페이지에 표시할 필드들
    list_display = (
        'id',
        'get_user_nickname',
        'get_place_name', 
        'get_place_category',
        'created_at',
    )
    
    # 필터링 옵션들
    list_filter = (
        'created_at',
        'place__category',
        'place__region',
    )
    
    # 검색 가능한 필드들
    search_fields = (
        'user__nickname',
        'user__email',
        'user__phone_number',
        'place__content_id',
        'place__translations__name',
        'place__translations__address',
    )
    
    # 상세 페이지 필드 순서
    fields = ('user', 'place', 'created_at')
    
    # 읽기 전용 필드
    readonly_fields = ('created_at',)
    
    # 페이지당 표시할 항목 수
    list_per_page = 25
    
    # 날짜별 계층구조 네비게이션
    date_hierarchy = 'created_at'
    
    # 기본 정렬 순서
    ordering = ('-created_at',)
    
    # 관련 객체를 미리 가져와서 쿼리 최적화
    list_select_related = ('user', 'place')
    
    # 인라인에서 수정 가능한 필드들
    autocomplete_fields = ['user', 'place']  # 검색 가능한 드롭다운
    
    def get_user_nickname(self, obj):
        """사용자 닉네임 표시"""
        return obj.user.nickname
    get_user_nickname.short_description = '사용자'
    get_user_nickname.admin_order_field = 'user__nickname'
    
    def get_place_name(self, obj):
        """장소명 표시"""
        return obj.place.get_name('ko') or obj.place.content_id or f"Place {obj.place.id}"
    get_place_name.short_description = '장소명'
    get_place_name.admin_order_field = 'place__content_id'
    
    def get_place_category(self, obj):
        """장소 카테고리 표시"""
        if obj.place.category:
            return str(obj.place.category)
        return '미분류'
    get_place_category.short_description = '카테고리'
    get_place_category.admin_order_field = 'place__category'
    
    # 액션들
    actions = ['delete_selected']
    
    def get_queryset(self, request):
        """쿼리셋 최적화"""
        return super().get_queryset(request).select_related(
            'user', 'place'
        ).prefetch_related(
            'place__category',  # 필요시 추가
        )
    
    # 권한 관련 메소드들 (필요시 사용)
    def has_add_permission(self, request):
        """추가 권한"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """수정 권한"""
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        """삭제 권한"""
        return request.user.is_superuser