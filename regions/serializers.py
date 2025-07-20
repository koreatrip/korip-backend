from rest_framework import serializers
from regions.models import Region, SubRegion


class SubRegionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    place_count = serializers.SerializerMethodField()

    class Meta:
        model = SubRegion
        fields = [
            "id",
            "name",
            "description",
            "features",
            "favorite_count",
            "place_count",
            "latitude",
            "longitude"
        ]

    def get_name(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_name(lang) or f"SubRegion {obj.id}"

    def get_description(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_description(lang)

    def get_features(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_features(lang)

    def get_place_count(self, obj):
        # Place 모델 연결 후 실제 카운트 구현
        return 0


class SubRegionListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    place_count = serializers.SerializerMethodField()

    class Meta:
        model = SubRegion
        fields = [
            "id",
            "name",
            "features",
            "favorite_count",
            "place_count"
        ]

    def get_name(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_name(lang) or f"SubRegion {obj.id}"

    def get_features(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_features(lang)

    def get_place_count(self, obj):
        return 0


class RegionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    subregion_count = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = [
            "id",
            "name",
            "description",
            "subregion_count"
        ]

    def get_name(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_name(lang) or f"Region {obj.id}"

    def get_description(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_description(lang)

    def get_subregion_count(self, obj):
        return obj.subregions.count()


class RegionDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    subregions = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = [
            "id",
            "name",
            "description",
            "subregions"
        ]

    def get_name(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_name(lang) or f"Region {obj.id}"

    def get_description(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_description(lang)

    def get_subregions(self, obj):
        subregions = obj.subregions.select_related().prefetch_related(
            'translations'
        ).all()

        def sort_key(subregion):
            korean_name = subregion.get_name("ko") or f"SubRegion {subregion.id}"
            return (-subregion.favorite_count, korean_name)

        sorted_subregions = sorted(subregions, key=sort_key)

        lang = self.context.get("lang", "ko")
        serializer = SubRegionListSerializer(
            sorted_subregions,
            many=True,
            context={"lang": lang}
        )
        return serializer.data
