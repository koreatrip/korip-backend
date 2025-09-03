from rest_framework import serializers
from plans.models import TravelPlan, TravelPlanTranslation, PlanPlace
from places.models import Place


class TravelPlanListSerializer(serializers.ModelSerializer):
    """여행 계획 목록용 시리얼라이저"""
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    region_id = serializers.SerializerMethodField()

    class Meta:
        model = TravelPlan
        fields = ["id", "region_id", "title", "description", "subregion_id",
                  "created_at", "updated_at"]

    def get_title(self, obj):
        """요청 언어에 맞는 제목 반환"""
        lang = self.context.get("lang", "ko")
        return obj.get_title(lang)

    def get_description(self, obj):
        """요청 언어에 맞는 설명 반환"""
        lang = self.context.get("lang", "ko")
        return obj.get_description(lang)

    def get_region_id(self, obj):
        """첫 번째 관광지의 region_id 반환"""
        first_plan_place = obj.plan_places.first()
        if first_plan_place:
            try:
                place = Place.objects.get(id=first_plan_place.place_id)
                return place.region_id if hasattr(place, "region_id") else place.region.id if hasattr(place,
                                                                                                      "region") else None
            except Place.DoesNotExist:
                pass
        return None


class PlaceDetailSerializer(serializers.Serializer):
    """관광지 상세 정보 시리얼라이저"""
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
        """Place 모델 인스턴스를 API 형태로 변환"""
        if isinstance(instance, Place):
            lang = self.context.get("lang", "ko")
            return {
                "id": instance.id,
                "category_id": getattr(instance, 'category_id', None),
                "subcategory_id": getattr(instance, 'sub_category_id', None),
                "region_id": getattr(instance, 'region_id', None) or (
                    instance.region.id if hasattr(instance, 'region') else None),
                "subregion_id": getattr(instance, 'subregion_id', None) or (
                    instance.subregion.id if hasattr(instance, 'subregion') else None),
                "latitude": getattr(instance, 'latitude', None),
                "longitude": getattr(instance, 'longitude', None),
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


class PlanPlaceDetailSerializer(serializers.ModelSerializer):
    """여행 계획 관광지 상세 시리얼라이저"""
    place = serializers.SerializerMethodField()

    class Meta:
        model = PlanPlace
        fields = ["id", "place", "visit_date", "visit_time", "created_at", "updated_at"]

    def get_place(self, obj):
        """관광지 상세 정보 반환"""
        try:
            place = Place.objects.get(id=obj.place_id)
            serializer = PlaceDetailSerializer(place, context=self.context)
            return serializer.data
        except Place.DoesNotExist:
            return None


class TravelPlanDetailSerializer(serializers.ModelSerializer):
    """여행 계획 상세 시리얼라이저"""
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    region_id = serializers.SerializerMethodField()
    plan_places = PlanPlaceDetailSerializer(many=True, read_only=True)

    class Meta:
        model = TravelPlan
        fields = ["id", "title", "description", "region_id", "subregion_id", "start_date", "end_date",
                  "plan_places", "created_at", "updated_at"]

    def get_title(self, obj):
        """요청 언어에 맞는 제목 반환"""
        lang = self.context.get("lang", "ko")
        return obj.get_title(lang)

    def get_description(self, obj):
        """요청 언어에 맞는 설명 반환"""
        lang = self.context.get("lang", "ko")
        return obj.get_description(lang)

    def get_region_id(self, obj):
        """첫 번째 관광지의 region_id 반환"""
        first_plan_place = obj.plan_places.first()
        if first_plan_place:
            try:
                place = Place.objects.get(id=first_plan_place.place_id)
                return place.region_id if hasattr(place, "region_id") else place.region.id if hasattr(place,
                                                                                                      "region") else None
            except Place.DoesNotExist:
                pass
        return None


class TravelPlanCreateSerializer(serializers.Serializer):
    """여행 계획 생성용 시리얼라이저"""
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(allow_blank=True, required=False)
    subregion_id = serializers.IntegerField()

    def create(self, validated_data):
        """여행 계획 생성"""
        translation_data = {
            'title': validated_data.pop('name'),
            'description': validated_data.pop('description', ''),
        }

        # TravelPlan 생성
        travel_plan = TravelPlan.objects.create(**validated_data)

        # 한국어 번역 생성
        TravelPlanTranslation.objects.create(
            travel_plan=travel_plan,
            lang='ko',
            **translation_data
        )

        return travel_plan


class PlanPlaceCreateSerializer(serializers.Serializer):
    """계획 관광지 생성용 시리얼라이저"""
    place_id = serializers.IntegerField()
    visit_date = serializers.DateField()
    visit_time = serializers.TimeField()


class PlanPlaceListCreateSerializer(serializers.Serializer):
    """계획 관광지 목록 생성용 시리얼라이저"""
    places = PlanPlaceCreateSerializer(many=True)
