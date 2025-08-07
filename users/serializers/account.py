from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from users.models import CustomUser
from categories.models import SubCategory
from preferences.models import UserPreference
from preferences.serializers import PreferenceSerializer
from preferences.services import PreferenceService
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    RequestError,
)


class FindAccountSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class FindPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise RequestError(ErrorCode.INVALID_PASSWORD)
        return value
    
    def validate(self, data):
        user = self.context.get('request').user
        new_password = data.get('new_password')

        if user and user.check_password(new_password):
            raise RequestError(ErrorCode.SAME_CURRENT_PASSWORD)
        return data


class UserInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='nickname')

    preferences = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=SubCategory.objects.all(),
        write_only=True,
        required=False
    )
    preferences_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'name', 'phone_number',
            'login_type', 'is_social', 'is_active', 'created_at', 'updated_at',
            'preferences', 'preferences_display'
        ]
        read_only_fields = [
            'id', 'email', 'login_type', 'is_social',
            'is_active', 'created_at', 'updated_at', 'preferences_display',
        ]

    def update(self, instance, validated_data):
        MAX_PREFERENCES = 9
        
        preferences = validated_data.pop('preferences', None)

        nickname = validated_data.get('nickname')
        phone_number = validated_data.get('phone_number')

        if nickname is not None:
            instance.nickname = nickname
        if phone_number is not None:
            instance.phone_number = phone_number
        instance.save()

        if preferences is not None:
            subcategory_ids = list(set(sub.id for sub in preferences))
            if len(subcategory_ids) > MAX_PREFERENCES:
                raise RequestError(ErrorCode.TOO_MANY_PREFERENCES) 
            
            existing_ids = set(
            SubCategory.objects.filter(id__in=subcategory_ids).values_list('id', flat=True))
        
            invalid_ids = [id for id in subcategory_ids if id not in existing_ids]
            if invalid_ids:
                raise RequestError(
                    ErrorCode.INVALID_SUBCATEGORY_ID,
                    message=ErrorCode.INVALID_SUBCATEGORY_ID.format_message(invalid_ids)
                )

            PreferenceService.add_preference(user_id=instance.id, subcategory_ids=subcategory_ids)

        return instance

    def get_preferences_display(self, obj):
        request = self.context.get('request')
        lang = request.query_params.get('lang', 'ko') if request else 'ko'

        user_preferences = UserPreference.objects.filter(user=obj).select_related('subcategory')
        subcategories = [pref.subcategory for pref in user_preferences]

        return PreferenceSerializer(subcategories, many=True, context={'language': lang}).data
