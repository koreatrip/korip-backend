from django.contrib.auth.models import AbstractUser
from django.db import models


class Language(models.Model):
    code = models.CharField(max_length=5, unique=True, help_text="언어 코드 (ko, en, ja, zh)")
    name = models.CharField(max_length=50, help_text="언어 이름")
    is_active = models.BooleanField(default=True, help_text="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.name} ({self.code})"

# 곽승환이 교체 예정. 임시 설정
class User(AbstractUser):
    pass
