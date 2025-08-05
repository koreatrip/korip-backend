from django.db import models
from django.conf import settings
from categories.models import SubCategory


class UserPreference(models.Model):
    """사용자-서브카테고리 관심사 중간테이블"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferences",
        verbose_name="사용자"
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="user_preferences",
        verbose_name="서브카테고리"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일시")
    
    class Meta:
        db_table = "user_preference"
        verbose_name = "사용자 관심사"
        verbose_name_plural = "사용자 관심사"
        unique_together = [['user', 'subcategory']]  # 중복 방지

    def __str__(self):
        return f"{self.user.nickname} - {self.subcategory}"
