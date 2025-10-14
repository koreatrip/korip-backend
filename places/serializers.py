from django.conf import settings
from rest_framework import serializers
from places.models import Place, IdolVisit, IdolVisitTranslation
from utils.helper.lang_helper import SUPPORTED_LANGS


class IdolVisitTranslationSerializer(serializers.ModelSerializer):
    """
    아이돌 방문 기록의 언어별 번역 데이터
    """

    class Meta:
        model = IdolVisitTranslation
        fields = ["lang", "description"]


class IdolVisitSerializer(serializers.ModelSerializer):
    """
    아이돌 방문 기록 (언어에 맞는 설명 포함)
    """
    description = serializers.SerializerMethodField()

    class Meta:
        model = IdolVisit
        fields = [
            "id",
            "idol_name",
            "idol_group",
            "description",
            "visit_date",
            "source_url"
        ]

    def get_language(self):
        # PlaceSerializer랑 똑같은 로직
        raw = self.context.get("lang") or self.context.get("language")
        if raw and raw.lower() in SUPPORTED_LANGS:
            return raw.lower()
        return settings.DEFAULT_LANG

    def get_description(self, obj):
        # 모델의 get_description 메서드 활용
        return obj.get_description(self.get_language())

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
    # k-pop 관련
    idol_names = serializers.SerializerMethodField()  # 목록용: 간단하게 이름만
    idol_visits = serializers.SerializerMethodField()  # 상세용: 전체 정보

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
            "idol_names",
            "idol_visits",
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

    def get_idol_names(self, obj):
        """
        목록 화면에서 간단하게 표시할 아이돌 이름들
        예: ["BTS 정국", "블랙핑크 로제"]

        context에 'include_idol_info'가 True일 때만 포함
        (K-POP 관심사 있는 사용자만)
        """
        # K-POP 관심사 없으면 None 반환 (필드 자체가 안 나감)
        if not self.context.get("include_idol_info", False):
            return None

        # K-POP 명소가 아니면 빈 리스트
        if not obj.is_kpop_spot:
            return []

        # 아이돌 이름 목록 만들기
        idol_names = []
        for visit in obj.idol_visits.all():
            if visit.idol_group:
                idol_names.append(f"{visit.idol_group} {visit.idol_name}")
            else:
                idol_names.append(visit.idol_name)

        return idol_names

    # 아이돌 방문 상세 정보 (상세 API용 - 전체 정보)
    def get_idol_visits(self, obj):
        """
        상세 화면에서 보여줄 아이돌 방문 전체 정보

        context에 'include_idol_details'가 True일 때만 포함
        (상세 페이지 + K-POP 관심사 있는 사용자)
        """
        # K-POP 상세 정보 필요 없으면 None 반환
        if not self.context.get("include_idol_details", False):
            return None

        # K-POP 명소가 아니면 빈 리스트
        if not obj.is_kpop_spot:
            return []

        # IdolVisitSerializer로 변환해서 반환
        visits = obj.idol_visits.all()
        return IdolVisitSerializer(
            visits,
            many=True,
            context=self.context  # 언어 정보 전달
        ).data