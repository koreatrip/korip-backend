from rest_framework import serializers
from places.models import Place


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
            "created_at",
            "updated_at"
        ]

    def get_language(self):
        return self.context.get("language", "ko")

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

class PlaceDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    subcategory_id = serializers.IntegerField()
    region_id = serializers.IntegerField()
    subregion_id = serializers.IntegerField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    phone_number = serializers.CharField()
    use_time = serializers.CharField()
    image_url = serializers.URLField()
    address = serializers.CharField()
    description = serializers.CharField()
    favorite_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def to_representation(self, instance):
        if isinstance(instance, Place):
            lang = self.context.get("lang", "ko")

            # GIS PointField에서 위도/경도 추출
            latitude = instance.latitude
            longitude = instance.longitude

            return {
                "id": instance.id,
                "category_id": getattr(instance, 'category_id', None),
                "subcategory_id": getattr(instance, 'sub_category_id', None),
                "region_id": self._get_region_id(instance),
                "subregion_id": self._get_subregion_id(instance),
                "latitude": latitude,
                "longitude": longitude,
                "phone_number": getattr(instance, 'phone_number', ""),
                "use_time": getattr(instance, 'use_time', ""),
                "image_url": getattr(instance, 'image_url', ""),
                "address": instance.get_address(lang) if hasattr(instance, 'get_address') else "",
                "description": instance.get_description(lang) if hasattr(instance, 'get_description') else "",
                "favorite_count": getattr(instance, 'favorite_count', 0),
                "created_at": instance.created_at,
                "updated_at": instance.updated_at,
            }
        return super().to_representation(instance)

    def _get_region_id(self, instance):
        if hasattr(instance, 'region') and instance.region:
            return instance.region.id
        if hasattr(instance, 'region_id') and instance.region_id:
            return instance.region_id
        return None

    def _get_subregion_id(self, instance):
        if hasattr(instance, 'sub_region') and instance.sub_region:
            return instance.sub_region.id
        if hasattr(instance, 'sub_region_id') and instance.sub_region_id:
            return instance.sub_region_id
        return None