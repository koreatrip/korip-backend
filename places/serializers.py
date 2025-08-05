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
