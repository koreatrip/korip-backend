from rest_framework import serializers
from plans.models import TravelPlan, TravelPlanTranslation, PlanPlace
from places.models import Place


class TravelPlanListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    region_id = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()

    class Meta:
        model = TravelPlan
        fields = ["id", "region_id", "title", "description", "subregion_id",
                  "start_date", "end_date", "created_at", "updated_at"]

    def get_title(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_title(lang)

    def get_description(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_description(lang)

    def get_region_id(self, obj):
        if obj.subregion_id:
            try:
                from regions.models import SubRegion
                subregion = SubRegion.objects.select_related("region").get(id=obj.subregion_id)
                return subregion.region.id
            except SubRegion.DoesNotExist:
                pass
        return None

    def get_start_date(self, obj):
        # DB 필드에 값이 있으면 우선 사용
        if obj.start_date:
            return obj.start_date

        # 관광지 방문일 기준으로 계산
        plan_places = obj.plan_places.all()
        if not plan_places.exists():
            return None

        dates = [pp.visit_date for pp in plan_places if pp.visit_date]
        if not dates:
            return None

        return min(dates)

    def get_end_date(self, obj):
        # DB 필드에 값이 있으면 우선 사용
        if obj.end_date:
            return obj.end_date

        # 관광지 방문일 기준으로 계산
        plan_places = obj.plan_places.all()
        if not plan_places.exists():
            return None

        dates = [pp.visit_date for pp in plan_places if pp.visit_date]
        if not dates:
            return None

        return max(dates)


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


class PlanPlaceDetailSerializer(serializers.ModelSerializer):
    place = serializers.SerializerMethodField()

    class Meta:
        model = PlanPlace
        fields = ["id", "place", "visit_date", "visit_time", "created_at", "updated_at"]

    def get_place(self, obj):
        try:
            place = Place.objects.get(id=obj.place_id)
            serializer = PlaceDetailSerializer(place, context=self.context)
            return serializer.data
        except Place.DoesNotExist:
            return None


class TravelPlanDetailSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    region_id = serializers.SerializerMethodField()
    plan_places = PlanPlaceDetailSerializer(many=True, read_only=True)
    schedule_by_date = serializers.SerializerMethodField()

    class Meta:
        model = TravelPlan
        fields = ["id", "title", "description", "region_id", "subregion_id", "start_date", "end_date",
                  "plan_places", "schedule_by_date", "created_at", "updated_at"]

    def get_title(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_title(lang)

    def get_description(self, obj):
        lang = self.context.get("lang", "ko")
        return obj.get_description(lang)

    def get_region_id(self, obj):
        if obj.subregion_id:
            try:
                from regions.models import SubRegion
                subregion = SubRegion.objects.select_related("region").get(id=obj.subregion_id)
                return subregion.region.id
            except SubRegion.DoesNotExist:
                pass

        # fallback: 첫 번째 관광지의 region_id
        first_plan_place = obj.plan_places.first()
        if first_plan_place:
            try:
                place = Place.objects.get(id=first_plan_place.place_id)
                return place.region_id if hasattr(place, "region_id") else place.region.id if hasattr(place,
                                                                                                      "region") else None
            except Place.DoesNotExist:
                pass
        return None

    def get_schedule_by_date(self, obj):
        from datetime import datetime, timedelta

        time_slots = ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00", "23:00"]
        schedule_by_date = {}

        if obj.start_date and obj.end_date:
            # 날짜가 설정된 경우: 설정된 기간의 모든 날짜
            current_date = obj.start_date
            while current_date <= obj.end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                schedule_by_date[date_str] = {slot: None for slot in time_slots}
                current_date += timedelta(days=1)
        else:
            # 날짜가 설정 안 된 경우: 오늘 날짜 하루만 기본 표시
            today = datetime.now().date()
            date_str = today.strftime("%Y-%m-%d")
            schedule_by_date[date_str] = {slot: None for slot in time_slots}

        # 실제 관광지 데이터가 있는 경우 처리
        plan_places = obj.plan_places.all()
        for plan_place in plan_places:
            date_str = plan_place.visit_date.strftime("%Y-%m-%d")

            # 날짜가 처음 나오면 빈 슬롯 구조 생성 (예외 케이스)
            if date_str not in schedule_by_date:
                schedule_by_date[date_str] = {slot: None for slot in time_slots}

            time_str = plan_place.visit_time.strftime("%H:%M") if plan_place.visit_time else None

            # 고정 슬롯에 맞는 시간이면 데이터 추가
            if time_str in time_slots:
                try:
                    place = Place.objects.get(id=plan_place.place_id)
                    place_serializer = PlaceDetailSerializer(place, context=self.context)
                    place_data = place_serializer.data
                except Place.DoesNotExist:
                    place_data = None

                schedule_by_date[date_str][time_str] = {
                    "id": plan_place.id,
                    "place": place_data
                }

        return schedule_by_date


class TravelPlanCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(allow_blank=True, required=False)
    subregion_id = serializers.IntegerField()

    def create(self, validated_data):
        # lang 파라미터 분리 (사용자가 입력한 언어)
        input_lang = validated_data.pop("lang", "ko")

        translation_data = {
            "title": validated_data.pop("name"),
            "description": validated_data.pop("description", ""),
        }

        # TravelPlan 생성
        travel_plan = TravelPlan.objects.create(**validated_data)

        # 지원하는 모든 언어로 번역 생성
        supported_languages = ["ko", "en", "jp", "cn"]

        for lang in supported_languages:
            if lang == input_lang:
                # 사용자가 입력한 언어는 실제 데이터 사용
                TravelPlanTranslation.objects.create(
                    travel_plan=travel_plan,
                    lang=lang,
                    **translation_data
                )
            else:
                # 다른 언어는 빈 값으로 생성 (나중에 번역 추가 예정)
                TravelPlanTranslation.objects.create(
                    travel_plan=travel_plan,
                    lang=lang,
                    title=f"[{lang.upper()}] {translation_data['title']}",  # 임시 표시
                    description=""
                )

        return travel_plan


class PlanPlaceCreateSerializer(serializers.Serializer):
    place_id = serializers.IntegerField()
    visit_date = serializers.DateField()
    visit_time = serializers.TimeField()

    def validate_visit_time(self, value):
        allowed_times = ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00", "23:00"]
        time_str = value.strftime("%H:%M")

        if time_str not in allowed_times:
            raise serializers.ValidationError(
                f"시간은 다음 중 하나여야 합니다: {', '.join(allowed_times)}"
            )
        return value


class PlanPlaceListCreateSerializer(serializers.Serializer):
    places = PlanPlaceCreateSerializer(many=True)


class TravelPlanUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    places = PlanPlaceCreateSerializer(many=True, required=False)

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("시작일은 종료일보다 이전이어야 합니다")

        return data

    def update(self, instance, validated_data):
        places_data = validated_data.pop('places', None)
        lang = self.context.get('lang', 'ko')

        # 기본 정보 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 제목/설명 번역 업데이트
        title = validated_data.get('title')
        description = validated_data.get('description')

        if title or description:
            translation, created = TravelPlanTranslation.objects.get_or_create(
                travel_plan=instance,
                lang=lang,
                defaults={'title': title or '', 'description': description or ''}
            )
            if not created:
                if title:
                    translation.title = title
                if description:
                    translation.description = description
                translation.save()

        # 관광지 일정 업데이트
        if places_data is not None:
            PlanPlace.objects.filter(travel_plan=instance).delete()
            for place_data in places_data:
                PlanPlace.objects.create(
                    travel_plan=instance,
                    **place_data
                )

        return instance
