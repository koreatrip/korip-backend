from rest_framework import serializers
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class RegionSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ["id", "name", "description"]

    def get_name(self, obj):
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.name if translation else ""
        except:
            return ""

    def get_description(self, obj):
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.description if translation else ""
        except:
            return ""


class SubRegionSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    feature = serializers.SerializerMethodField()

    class Meta:
        model = SubRegion
        fields = [
            "id", "name", "description", "feature",
            "favorite_count", "latitude", "longitude"
        ]

    def get_name(self, obj):
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.name if translation else ""
        except:
            return ""

    def get_description(self, obj):
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.description if translation else ""
        except:
            return ""

    def get_feature(self, obj):
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.feature if translation else ""
        except:
            return ""


class RegionDetailSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    subregions = SubRegionSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        fields = ["id", "name", "description", "subregions"]

    def get_name(self, obj):
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.name if translation else ""
        except:
            return ""

    def get_description(self, obj):
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.description if translation else ""
        except:
            return ""
