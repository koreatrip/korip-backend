from django.contrib import admin
from categories.models import Category, SubCategory, CategoryTranslation, SubCategoryTranslation


class CategoryTranslationInline(admin.TabularInline):
    model = CategoryTranslation
    extra = 1
    max_num = 4


class SubCategoryTranslationInline(admin.TabularInline):
    model = SubCategoryTranslation
    extra = 1
    max_num = 4


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "get_korean_name", "get_english_name", "created_at"]
    list_display_links = ["id", "get_korean_name"]
    search_fields = ["translations__name"]
    ordering = ["id"]
    inlines = [CategoryTranslationInline]

    def get_korean_name(self, obj):
        return obj.get_name("ko") or "-"

    get_korean_name.short_description = "한국어 이름"

    def get_english_name(self, obj):
        return obj.get_name("en") or "-"

    get_english_name.short_description = "영어 이름"


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "get_korean_name", "get_english_name", "category", "created_at"]
    list_display_links = ["id", "get_korean_name"]
    list_filter = ["category"]
    search_fields = ["translations__name"]
    ordering = ["category", "id"]
    inlines = [SubCategoryTranslationInline]

    def get_korean_name(self, obj):
        return obj.get_name("ko") or "-"

    get_korean_name.short_description = "한국어 이름"

    def get_english_name(self, obj):
        return obj.get_name("en") or "-"

    get_english_name.short_description = "영어 이름"


@admin.register(CategoryTranslation)
class CategoryTranslationAdmin(admin.ModelAdmin):
    list_display = ["id", "category", "lang", "name", "created_at"]
    list_filter = ["lang"]
    search_fields = ["name"]
    ordering = ["category", "lang"]


@admin.register(SubCategoryTranslation)
class SubCategoryTranslationAdmin(admin.ModelAdmin):
    list_display = ["id", "sub_category", "lang", "name", "created_at"]
    list_filter = ["lang"]
    search_fields = ["name"]
    ordering = ["sub_category", "lang"]