from rest_framework import serializers
from .models import Language


class LanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = ['code', 'name']


class LanguageSelectionSerializer(serializers.Serializer):
    language = serializers.CharField(max_length=5, help_text="언어 코드 (ko, en, ja, zh)")

# 언어 코드 유효성 검증
    def validate_language(self, value):
        try:
            language = Language.objects.get(code=value, is_active=True)
            return value
        except Language.DoesNotExist:
            raise serializers.ValidationError("유효하지 않거나 비활성화된 언어 코드입니다.")

    # 언어 선택 처리(실제로는 생성하지 않고 검증만)
    def create(self, validated_data):
        return validated_data
