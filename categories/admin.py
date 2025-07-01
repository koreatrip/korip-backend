from django.contrib import admin
from categories.models import (
    Category, CategoryTranslation,
    SubCategory, SubCategoryTranslation
)


# 기존 모델들도 등록
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """카테고리 관리"""
    list_display = ("id", "name_ko", "name_en", "name_jp", "name_cn", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name_ko", "name_en")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    """서브카테고리 관리"""
    list_display = ("id", "name_ko", "name_en", "category", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("name_ko", "name_en")
    readonly_fields = ("created_at", "updated_at")


# 새로운 번역 모델들 등록
@admin.register(CategoryTranslation)
class CategoryTranslationAdmin(admin.ModelAdmin):
    """카테고리 번역 관리"""
    list_display = ("id", "category", "lang", "name", "created_at")
    list_filter = ("lang", "created_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")

    # 카테고리별로 그룹화해서 보기
    ordering = ("category", "lang")


@admin.register(SubCategoryTranslation)
class SubCategoryTranslationAdmin(admin.ModelAdmin):
    """서브카테고리 번역 관리"""
    list_display = ("id", "sub_category", "lang", "name", "created_at")
    list_filter = ("lang", "created_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")

    # 서브카테고리별로 그룹화해서 보기
    ordering = ("sub_category", "lang")


# 인라인으로 번역을 같이 보기 (더 편리함!)
class CategoryTranslationInline(admin.TabularInline):
    """카테고리 상세에서 번역들을 바로 볼 수 있게"""
    model = CategoryTranslation
    extra = 0  # 빈 폼 안 보이게
    readonly_fields = ("created_at", "updated_at")


class SubCategoryTranslationInline(admin.TabularInline):
    """서브카테고리 상세에서 번역들을 바로 볼 수 있게"""
    model = SubCategoryTranslation
    extra = 0
    readonly_fields = ("created_at", "updated_at")


# 기존 Category Admin에 번역 인라인 추가
# (위의 CategoryAdmin을 수정해서 사용)
admin.site.unregister(Category)  # 기존 등록 해제


@admin.register(Category)
class CategoryWithTranslationAdmin(admin.ModelAdmin):
    """카테고리 + 번역 통합 관리"""
    list_display = ("id", "name_ko", "name_en", "get_translation_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name_ko", "name_en")
    readonly_fields = ("created_at", "updated_at")

    # 번역 인라인 추가
    inlines = [CategoryTranslationInline]

    def get_translation_count(self, obj):
        """번역 개수 표시"""
        return obj.translations.count()

    get_translation_count.short_description = "번역 개수"


# 기존 SubCategory Admin에 번역 인라인 추가
admin.site.unregister(SubCategory)  # 기존 등록 해제


@admin.register(SubCategory)
class SubCategoryWithTranslationAdmin(admin.ModelAdmin):
    """서브카테고리 + 번역 통합 관리"""
    list_display = ("id", "name_ko", "name_en", "category", "get_translation_count", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("name_ko", "name_en")
    readonly_fields = ("created_at", "updated_at")

    # 번역 인라인 추가
    inlines = [SubCategoryTranslationInline]

    def get_translation_count(self, obj):
        """번역 개수 표시"""
        return obj.translations.count()

    get_translation_count.short_description = "번역 개수"
