from django.db import transaction
from preferences.models import UserPreference


class PreferenceService:
    """관심사 관련 모든 비즈니스 로직"""
    
    @staticmethod
    @transaction.atomic
    def add_preference(user_id, subcategory_ids):
        deleted_count = UserPreference.objects.filter(user_id=user_id).count()
        UserPreference.objects.filter(user_id=user_id).delete()
        
        # 새로운 관심사들 등록
        new_preferences = []
        for subcategory_id in subcategory_ids:
            preference = UserPreference(
                user_id=user_id,
                subcategory_id=subcategory_id
            )
            new_preferences.append(preference)
        
        # bulk_create로 한번에 등록 (성능 최적화)
        UserPreference.objects.bulk_create(new_preferences)
        
        return {
            'deleted_count': deleted_count,
            'created_count': len(subcategory_ids),
            'preferences': subcategory_ids
        }
