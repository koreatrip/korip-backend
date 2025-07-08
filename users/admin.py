from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "nickname", "phone_number")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email", "nickname", "phone_number", "is_social", "is_active", "is_staff", "is_superuser")


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    list_display = (
        "email",
        "nickname", 
        "phone_number",
        "is_social",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "is_social",
        "created_at",
    )
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("개인 정보"), {"fields": ("nickname", "phone_number")}),
        (
            _("권한"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_social",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("중요한 일정"), {"fields": ("last_login", "created_at", "updated_at")}),
    )
    
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nickname", "phone_number", "password1", "password2"),
            },
        ),
    )
    
    search_fields = ("email", "nickname", "phone_number")
    ordering = ("email",)
    readonly_fields = ("created_at", "updated_at", "last_login")
    
    # 사용자 추가 시 필요한 필드들
    filter_horizontal = ("groups", "user_permissions")