from rest_framework import serializers
from categories.models import SubCategory


class CreatePreferenceSerializer(serializers.Serializer):
    preferences = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1,
        max_length=9,
        help_text="서브카테고리 ID 리스트 (최대 9개)"
    )
    
    def validate_preferences(self, value):
        """preferences 필드 유효성 검증"""
        # 중복 제거
        unique_preferences = list(set(value))
        
        # 중복 제거 후 최대 개수 재확인
        if len(unique_preferences) > 9:
            raise serializers.ValidationError("최대 9개까지만 선택 가능합니다.")
        
        # 실제 존재하는 서브카테고리인지 확인
        existing_ids = set(
            SubCategory.objects.filter(id__in=unique_preferences)
            .values_list('id', flat=True)
        )
        
        invalid_ids = [id for id in unique_preferences if id not in existing_ids]
        if invalid_ids:
            raise serializers.ValidationError(
                f"존재하지 않는 서브카테고리 ID: {invalid_ids}"
            )
        
        return unique_preferences
