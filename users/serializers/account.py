from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from users.models import CustomUser
from categories.models import SubCategory
from preferences.models import UserPreference
from preferences.serializers import PreferenceSerializer
from preferences.services import PreferenceService
from plans.models import TravelPlan
from favorites.models import FavoritePlace, FavoriteSubRegion
from plans.models import TravelPlan, PlanPlace
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
    preferences_display = serializers.SerializerMethodField()
    my_total_plans = serializers.SerializerMethodField()
    my_total_favorites = serializers.SerializerMethodField()
    visited_places = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'name', 'phone_number',
            'login_type', 'is_social', 'is_active', 'created_at', 'updated_at',
            'preferences', 'preferences_display', 'my_total_plans',
            'my_total_favorites', 'visited_places'
        ]
        read_only_fields = [
            'id', 'email', 'login_type', 'is_social',
            'is_active', 'created_at', 'updated_at', 'preferences_display',
            'my_total_plans', 'my_total_favorites', 'visited_places'
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

    def get_my_total_plans(self, obj):
        """사용자가 생성한 모든 여행 계획의 총 개수를 반환"""
        return TravelPlan.objects.filter(user_id=obj.id).count()

    def get_my_total_favorites(self, obj):
        """사용자가 즐겨찾기한 장소 및 지역의 총 개수를 반환"""        
        favorite_places_count = FavoritePlace.objects.filter(user=obj).count()
        favorite_subregions_count = FavoriteSubRegion.objects.filter(user=obj).count()
        
        return favorite_places_count + favorite_subregions_count

    def get_visited_places(self, obj):
        """현재 시간 기준 이전 여행 일정에 포함된 장소들의 총 개수를 반환"""
        current_date = timezone.now().date()
        
        # 사용자의 과거 여행 계획들을 조회 (종료일이 현재 날짜보다 이전인 계획들)
        past_travel_plans = TravelPlan.objects.filter(
            user_id=obj.id,
            end_date__lt=current_date
        )
        
        # 과거 여행 계획들에 포함된 장소들의 총 개수
        visited_places_count = PlanPlace.objects.filter(
            travel_plan__in=past_travel_plans
        ).count()
        
        return visited_places_count

    def to_representation(self, instance):
        """GET 요청일 때만 통계 포함"""
        representation = super().to_representation(instance)
        
        # context에서 request 확인
        request = self.context.get('request')
        
        # PATCH/PUT 요청이면 통계 필드 제거
        if request and request.method in ['PATCH', 'PUT']:
            representation.pop('my_total_plans', None)
            representation.pop('my_total_favorites', None)
            representation.pop('visited_places', None)
        
        return representation