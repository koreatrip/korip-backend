from django.conf import settings
from rest_framework import serializers
from places.models import Place
from utils.helper.lang_helper import SUPPORTED_LANGS


class PlaceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    sub_region = serializers.SerializerMethodField()
    # GIS 호환성 프로퍼티
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    # 즐겨찾기 여부
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = [
            "id",
            "content_id",
            "name",
            "description",
            "address",
            "latitude",
            "longitude",
            "phone_number",
            "use_time",
            "link_url",
            "image_url",
            "category",
            "sub_category",
            "region",
            "sub_region",
            "favorite_count",
            "is_favorite",
            "created_at",
            "updated_at"
        ]

    def get_language(self):
        raw = self.context.get("lang") or self.context.get("language")
        if raw and raw.lower() in SUPPORTED_LANGS:
            return raw.lower()
        return settings.DEFAULT_LANG

    def get_latitude(self, obj):
        return obj.latitude

    def get_longitude(self, obj):
        return obj.longitude

    def get_name(self, obj):
        return obj.get_name(self.get_language())

    def get_description(self, obj):
        return obj.get_description(self.get_language())

    def get_address(self, obj):
        return obj.get_address(self.get_language())

    def get_category(self, obj):
        if not obj.category:
            return None

        try:
            category = obj.category
            return {
                "id": category.id,
                "name": category.get_name(self.get_language())
            }
        except AttributeError:
            return None

    def get_sub_category(self, obj):
        if not obj.sub_category:
            return None

        try:
            sub_category = obj.sub_category
            return {
                "id": sub_category.id,
                "name": sub_category.get_name(self.get_language())
            }
        except AttributeError:
            return None

    def get_region(self, obj):
        if not obj.region:
            return None

        return {
            "id": obj.region.id,
            "name": obj.get_region_name(self.get_language())
        }

    def get_sub_region(self, obj):
        if not obj.sub_region:
            return None

        return {
            "id": obj.sub_region.id,
            "name": obj.get_sub_region_name(self.get_language())
        }

    def get_is_favorite(self, obj):
        """
        현재 로그인한 유저가 해당 장소를 즐겨찾기했는지 확인
        성능 최적화: context에서 미리 조회된 즐겨찾기 ID 목록 활용
        """

        user_favorite_place_ids = self.context.get('user_favorite_place_ids')
        if user_favorite_place_ids is not None:
            return obj.id in user_favorite_place_ids
        
        return False
