from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from favorites.models import FavoritePlace, FavoriteSubRegion


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


@receiver(post_save, sender=FavoriteSubRegion)
def increment_favorite_count(sender, instance, created, **kwargs):
    """즐겨찾기 추가 시 favorite_count 증가"""
    if created:  # 새로 생성된 경우에만
        with transaction.atomic():
            sub_region = instance.sub_region
            # select_for_update로 동시성 문제 방지
            sub_region = type(sub_region).objects.select_for_update().get(id=sub_region.id)
            sub_region.favorite_count += 1
            sub_region.save(update_fields=['favorite_count'])


@receiver(post_delete, sender=FavoriteSubRegion)
def decrement_favorite_count(sender, instance, **kwargs):
    """즐겨찾기 삭제 시 favorite_count 감소"""
    with transaction.atomic():
        sub_region = instance.sub_region
        # select_for_update로 동시성 문제 방지
        sub_region = type(sub_region).objects.select_for_update().get(id=sub_region.id)
        sub_region.favorite_count = max(0, sub_region.favorite_count - 1)
        sub_region.save(update_fields=['favorite_count'])