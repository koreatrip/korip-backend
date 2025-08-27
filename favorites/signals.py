from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import FavoritePlace


@receiver(post_save, sender=FavoritePlace)
def increment_favorite_count(sender, instance, created, **kwargs):
    """즐겨찾기 추가 시 favorite_count 증가"""
    if created:  # 새로 생성된 경우에만
        with transaction.atomic():
            place = instance.place
            # select_for_update로 동시성 문제 방지
            place = type(place).objects.select_for_update().get(id=place.id)
            place.favorite_count += 1
            place.save(update_fields=['favorite_count'])


@receiver(post_delete, sender=FavoritePlace)
def decrement_favorite_count(sender, instance, **kwargs):
    """즐겨찾기 삭제 시 favorite_count 감소"""
    with transaction.atomic():
        place = instance.place
        # select_for_update로 동시성 문제 방지
        place = type(place).objects.select_for_update().get(id=place.id)
        place.favorite_count = max(0, place.favorite_count - 1)
        place.save(update_fields=['favorite_count'])