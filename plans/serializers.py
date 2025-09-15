from rest_framework import serializers
from plans.models import TravelPlan, TravelPlanTranslation, PlanPlace
from places.models import Place
from datetime import datetime, timedelta
from places.serializers import PlaceSerializer


class SinglePlaceAddSerializer(serializers.Serializer):
    """관광지 하나만 추가하는 시리얼라이저"""
    place_id = serializers.IntegerField()

    def validate_place_id(self, value):
        """관광지 ID가 실제로 존재하는지 확인"""
        try:
            Place.objects.get(id=value)
            return value
        except Place.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 관광지입니다.")

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


class PlanPlaceDetailSerializer(serializers.ModelSerializer):
    place = serializers.SerializerMethodField()

    class Meta:
        model = PlanPlace
        fields = ["id", "place", "visit_date", "visit_time", "created_at", "updated_at"]

    def get_place(self, obj):
        try:
            place = Place.objects.get(id=obj.place_id)
            serializer = PlaceSerializer(place, context=self.context)
            return serializer.data
        except Place.DoesNotExist:
            return None


def generate_time_slots(start_date, end_date):
    """날짜 범위에 맞는 모든 시간 슬롯 생성"""
    time_slots = ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00", "23:00"]
    slots = []

    current_date = start_date
    while current_date <= end_date:
        for time_slot in time_slots:
            slots.append({
                "place_id": None,
                "visit_date": current_date,
                "visit_time": datetime.strptime(time_slot, "%H:%M").time()
            })
        current_date += timedelta(days=1)

    return slots


class TravelPlanDetailSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    region_id = serializers.SerializerMethodField()
    selected_places = serializers.SerializerMethodField()
    time_slots = serializers.SerializerMethodField()

    class Meta:
        model = TravelPlan
        fields = ["id", "title", "description", "region_id", "subregion_id", "start_date", "end_date",
                  "selected_places", "time_slots", "created_at", "updated_at"]

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

    def get_selected_places(self, obj):
        """담아둔 관광지들만 리스트로 반환"""
        plan_places = obj.plan_places.all()
        places_data = []

        for plan_place in plan_places:
            try:
                place = Place.objects.get(id=plan_place.place_id)
                place_serializer = PlaceSerializer(place, context=self.context)
                places_data.append(place_serializer.data)
            except Place.DoesNotExist:
                continue

        return places_data

    def get_time_slots(self, obj):
        """날짜 범위에 맞는 모든 슬롯 생성 (기존 데이터 포함)"""
        # 날짜 범위 결정
        if obj.start_date and obj.end_date:
            start_date = obj.start_date
            end_date = obj.end_date
        else:
            # 날짜가 없으면 기존 plan_places의 날짜 범위 사용
            plan_places = obj.plan_places.all()
            if plan_places.exists():
                dates = [pp.visit_date for pp in plan_places if pp.visit_date]
                if dates:
                    start_date = min(dates)
                    end_date = max(dates)
                else:
                    # 데이터도 없으면 오늘 하루만
                    start_date = datetime.now().date()
                    end_date = start_date
            else:
                # 완전히 비어있으면 오늘 하루만
                start_date = datetime.now().date()
                end_date = start_date

        # 모든 슬롯 생성 (빈 슬롯들)
        all_slots = generate_time_slots(start_date, end_date)

        existing_places = {
            (pp.visit_date, pp.visit_time): pp
            for pp in obj.plan_places.all()
        }

        # 슬롯에 기존 데이터 적용
        result_slots = []
        for slot in all_slots:
            slot_key = (slot["visit_date"], slot["visit_time"])

            if slot_key in existing_places:
                # 기존 데이터가 있으면 해당 데이터 사용
                existing_place = existing_places[slot_key]
                serializer = PlanPlaceDetailSerializer(
                    existing_place,
                    context=self.context
                )
                result_slots.append(serializer.data)
            else:
                # 빈 슬롯
                result_slots.append({
                    "id": None,
                    "place": None,
                    "visit_date": slot["visit_date"],
                    "visit_time": slot["visit_time"].strftime("%H:%M:%S"),
                    "created_at": None,
                    "updated_at": None
                })

        return result_slots


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
    place_id = serializers.IntegerField(allow_null=True, required=False)
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
        places_data = validated_data.pop("places", None)
        lang = self.context.get("lang", "ko")

        # 기본 정보 업데이트 (start_date, end_date 포함)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 제목/설명 번역 업데이트
        title = validated_data.get("title")
        description = validated_data.get("description")

        if title or description:
            translation, created = TravelPlanTranslation.objects.get_or_create(
                travel_plan=instance,
                lang=lang,
                defaults={"title": title or "", "description": description or ""}
            )
            if not created:
                if title:
                    translation.title = title
                if description:
                    translation.description = description
                translation.save()

        # 관광지 일정 업데이트
        if places_data is not None:
            # 기존 방식 유지 - 프론트에서 전체 슬롯 보내는 경우
            PlanPlace.objects.filter(travel_plan=instance).delete()
            for place_data in places_data:
                # place_id가 None인 빈 슬롯은 저장하지 않음
                if place_data.get("place_id") is not None:
                    PlanPlace.objects.create(
                        travel_plan=instance,
                        **place_data
                    )

        return instance
