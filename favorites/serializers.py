from rest_framework import serializers
from django.db import transaction, IntegrityError
from places.models import Place
from .models import FavoritePlace
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import RequestError, ServerError


class FavoritePlaceSerializer(serializers.Serializer):
    """즐겨찾기 토글 시리얼라이저 (시그널 버전)"""
    place_id = serializers.IntegerField()
    is_favorite = serializers.BooleanField(read_only=True)
    message = serializers.CharField(read_only=True)
    
    def validate_place_id(self, value):
        """장소 존재 여부 확인"""
        try:
            Place.objects.get(id=value)
        except Place.DoesNotExist:
            raise RequestError(ErrorCode.INVALID_DATA, message="존재하지 않는 장소입니다.")
        return value
    
    @transaction.atomic
    def toggle_favorite(self, user):
        """즐겨찾기 토글 DB 로직 (시그널이 자동으로 favorite_count 업데이트)"""
        try:
            place_id = self.validated_data['place_id']
            place = Place.objects.get(id=place_id)
            
            favorite = FavoritePlace.objects.filter(
                user=user,
                place=place
            ).first()
            
            if favorite:
                # 즐겨찾기 삭제 (post_delete 시그널이 자동으로 favorite_count 감소)
                favorite.delete()
                return {
                    'is_favorite': False,
                    'message': '즐겨찾기에서 제거했습니다.'
                }
            else:
                # 즐겨찾기 추가 (post_save 시그널이 자동으로 favorite_count 증가)
                try:
                    FavoritePlace.objects.create(user=user, place=place)
                    return {
                        'is_favorite': True,
                        'message': '즐겨찾기에 추가했습니다.'
                    }
                except IntegrityError:
                    # unique_together 제약 위반 (동시 요청 등)
                    raise RequestError(ErrorCode.INVALID_DATA, message="이미 즐겨찾기에 추가된 장소입니다.")
                    
        except Place.DoesNotExist:
            raise RequestError(ErrorCode.INVALID_DATA, message="존재하지 않는 장소입니다.")
        except Exception as e:
            # 예상치 못한 에러
            raise ServerError(ErrorCode.SERVER_ERROR)


class FavoritePlaceListSerializer(serializers.ModelSerializer):
    """FavoritePlace 관계를 시리얼라이즈하는 방법"""

    id = serializers.IntegerField(source='place.id')
    content_id = serializers.CharField(source='place.content_id')
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    latitude = serializers.DecimalField(source='place.latitude', max_digits=15, decimal_places=10)
    longitude = serializers.DecimalField(source='place.longitude', max_digits=15, decimal_places=10)
    phone_number = serializers.CharField(source='place.phone_number')
    use_time = serializers.CharField(source='place.use_time')
    link_url = serializers.URLField(source='place.link_url')
    image_url = serializers.URLField(source='place.image_url')
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    sub_region = serializers.SerializerMethodField()
    favorite_count = serializers.IntegerField(source='place.favorite_count')
    created_at = serializers.DateTimeField(source='place.created_at')  # Place 생성일
    updated_at = serializers.DateTimeField(source='place.updated_at')  # Place 수정일
    favorited_at = serializers.DateTimeField(source='created_at')  # 즐겨찾기 등록일

    class Meta:
        model = FavoritePlace
        fields = [
            'id', 'content_id', 'name', 'description', 'address',
            'latitude', 'longitude', 'phone_number', 'use_time',
            'link_url', 'image_url', 'category', 'sub_category',
            'region', 'sub_region', 'favorite_count', 'created_at',
            'updated_at', 'favorited_at'
        ]

    def get_language(self):
        return self.context.get("language", "ko")

    def get_name(self, obj):
        return obj.place.get_name(self.get_language())

    def get_description(self, obj):
        return obj.place.get_description(self.get_language())

    def get_address(self, obj):
        return obj.place.get_address(self.get_language())

    def get_category(self, obj):
        if not obj.place.category:
            return None
        try:
            category = obj.place.category
            return {
                "id": category.id,
                "name": category.get_name(self.get_language())
            }
        except AttributeError:
            return None

    def get_sub_category(self, obj):
        if not obj.place.sub_category:
            return None
        try:
            sub_category = obj.place.sub_category
            return {
                "id": sub_category.id,
                "name": sub_category.get_name(self.get_language())
            }
        except AttributeError:
            return None

    def get_region(self, obj):
        if not obj.place.region:
            return None
        return {
            "id": obj.place.region.id,
            "name": obj.place.get_region_name(self.get_language())
        }

    def get_sub_region(self, obj):
        if not obj.place.sub_region:
            return None
        return {
            "id": obj.place.sub_region.id,
            "name": obj.place.get_sub_region_name(self.get_language())
        }
