from rest_framework import serializers
from regions.models import Region, SubRegion


class RegionSerializer(serializers.ModelSerializer):

   name = serializers.SerializerMethodField()
   description = serializers.SerializerMethodField()
   feature = serializers.SerializerMethodField()

   class Meta:
       model = Region
       fields = ["id", "name", "description", "feature", "image"]

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
           return translation.features if translation else ""
       except:
           return ""


class SubRegionSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    feature = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()  # 즐겨찾기 여부 추가
    place_count = serializers.SerializerMethodField()  # 명소 개수

    class Meta:
        model = SubRegion
        fields = [
            "id", "name", "description", "feature", "place_count",
            "favorite_count", "is_favorite", "latitude", "longitude"
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
            return translation.features if translation else ""
        except:
            return ""

    def get_is_favorite(self, obj):
        """
        현재 로그인한 유저가 해당 서브지역을 즐겨찾기했는지 확인
        성능 최적화: context에서 미리 조회된 즐겨찾기 ID 목록 활용
        """
        user_favorite_subregion_ids = self.context.get('user_favorite_subregion_ids')
        if user_favorite_subregion_ids is not None:
            return obj.id in user_favorite_subregion_ids
        
        return False
    
    def get_place_count(self, obj):
        """
        해당 서브지역(지역구)에 속한 관광지 개수 반환
        annotate로 미리 계산된 값 사용
        """
        return getattr(obj, 'place_count', 0)
