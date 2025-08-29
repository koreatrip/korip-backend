from django.db import models
from django.conf import settings
from places.models import Place
from regions.models import SubRegion 


class FavoritePlace(models.Model):
    """사용자 즐겨찾는 장소 중간테이블"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_places",  # 수정: 더 명확한 이름
        verbose_name="사용자"
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="favorited_by",  # 수정: 더 명확한 이름
        verbose_name="즐겨찾는 장소"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일시")
    
    class Meta:
        db_table = "favorite_place"  # 수정: 올바른 철자
        verbose_name = "즐겨찾는 장소"
        verbose_name_plural = "즐겨찾는 장소들"
        unique_together = [['user', 'place']]  # 중복 방지
        
        # 추가: 인덱스 설정 (성능 향상)
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['place']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        place_name = self.place.get_name('ko') or self.place.content_id or f"Place {self.place.id}"
        return f"{self.user.nickname} - {place_name}"


class FavoriteSubRegion(models.Model):
    """사용자 즐겨찾는 지역구 중간테이블"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_subregions",
        verbose_name="사용자"
    )
    sub_region = models.ForeignKey(
        SubRegion,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="즐겨찾는 지역구"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일시")
    
    class Meta:
        db_table = "favorite_subregion"
        verbose_name = "즐겨찾는 지역구"
        verbose_name_plural = "즐겨찾는 지역구들"
        unique_together = [['user', 'sub_region']]  # 중복 방지
        
        # 인덱스 설정 (성능 향상)
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['sub_region']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        subregion_name = self.sub_region.get_name('ko') or f"SubRegion {self.sub_region.id}"
        region_name = self.sub_region.region.get_name('ko') or "지역"
        return f"{self.user.nickname} - {region_name} {subregion_name}"
