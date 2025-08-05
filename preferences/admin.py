from django.contrib import admin
from .models import UserPreference

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subcategory', 'created_at')
    list_filter = ('created_at', 'subcategory')
    search_fields = ('user__email', 'user__nickname', 'subcategory__name')
    autocomplete_fields = ('user', 'subcategory')
    ordering = ('-created_at',)

    # 읽기 전용 필드 설정 (선택사항)
    readonly_fields = ('created_at',)

    # 필드 정리 (선택사항)
    fieldsets = (
        (None, {
            'fields': ('user', 'subcategory', 'created_at')
        }),
    )
