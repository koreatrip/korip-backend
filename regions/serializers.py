from rest_framework import serializers
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class RegionSerializer(serializers.ModelSerializer):
    """지역 기본 정보 직렬화"""

    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ["id", "name", "description"]

    def get_name(self, obj):
        """언어별 지역 이름 반환"""
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.name if translation else ""
        except:
            return ""

    def get_description(self, obj):
        """언어별 지역 설명 반환"""
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.description if translation else ""
        except:
            return ""


class SubRegionSerializer(serializers.ModelSerializer):
    """서브지역 정보 직렬화"""

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
        """언어별 서브지역 이름 반환"""
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.name if translation else ""
        except:
            return ""

    def get_description(self, obj):
        """언어별 서브지역 설명 반환"""
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.description if translation else ""
        except:
            return ""

    def get_feature(self, obj):
        """언어별 서브지역 특징 반환"""
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.feature if translation else ""
        except:
            return ""


class RegionDetailSerializer(serializers.ModelSerializer):
    """지역 상세 정보 직렬화 (서브지역 포함)"""

    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    subregions = SubRegionSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        fields = ["id", "name", "description", "subregions"]

    def get_name(self, obj):
        """언어별 지역 이름 반환"""
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.name if translation else ""
        except:
            return ""

    def get_description(self, obj):
        """언어별 지역 설명 반환"""
        language = self.context.get("language", "ko")

        try:
            translation = obj.translations.filter(lang=language).first()
            return translation.description if translation else ""
        except:
            return ""
