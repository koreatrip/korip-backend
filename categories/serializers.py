from rest_framework import serializers
from categories.models import Category, SubCategory, CategoryTranslation, SubCategoryTranslation


class SubCategorySerializer(serializers.Serializer):
    """서브카테고리 시리얼라이저 (새로운 번역 구조)"""
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop("language", "ko")
        super().__init__(*args, **kwargs)

    def get_name(self, instance):
        """헬퍼 메서드 사용해서 언어별 이름 반환"""
        return instance.get_name(self.language)


class CategorySerializer(serializers.Serializer):
    """카테고리 시리얼라이저 (새로운 번역 구조)"""
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop("language", "ko")
        super().__init__(*args, **kwargs)

    def get_name(self, instance):
        """헬퍼 메서드 사용해서 언어별 이름 반환"""
        return instance.get_name(self.language)

    def get_subcategories(self, instance):
        """서브카테고리 목록 반환"""
        subcategories_data = []
        for subcategory in instance.subcategories.all():
            subcategory_serializer = SubCategorySerializer(
                subcategory,
                language=self.language
            )
            subcategories_data.append(subcategory_serializer.data)
        return subcategories_data


class SubCategoryListSerializer(serializers.Serializer):
    """서브카테고리 목록 시리얼라이저"""
    subcategories = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop("language", "ko")
        self.subcategories_queryset = kwargs.pop("subcategories_queryset", None)
        super().__init__(*args, **kwargs)

    def get_subcategories(self, instance):
        """서브카테고리 목록 반환"""
        subcategories_data = []
        if self.subcategories_queryset:
            for subcategory in self.subcategories_queryset:
                subcategory_serializer = SubCategorySerializer(
                    subcategory,
                    language=self.language
                )
                subcategories_data.append(subcategory_serializer.data)
        return subcategories_data


# 번역 생성/수정용 시리얼라이저들
class CategoryTranslationSerializer(serializers.Serializer):
    """카테고리 번역 시리얼라이저"""
    lang = serializers.ChoiceField(choices=["ko", "en", "jp", "cn"])
    name = serializers.CharField(max_length=100, allow_blank=False)

    def validate_name(self, value):
        """이름 검증"""
        if not value or not value.strip():
            raise serializers.ValidationError("이름은 필수입니다.")
        return value.strip()


class CategoryCreateSerializer(serializers.Serializer):
    """카테고리 생성용 시리얼라이저"""
    translations = CategoryTranslationSerializer(many=True)

    def validate_translations(self, value):
        """번역 리스트 검증"""
        if not value:
            raise serializers.ValidationError("최소 하나의 번역이 필요합니다.")

        # 중복 언어 코드 체크
        language_codes = [translation["lang"] for translation in value]
        if len(language_codes) != len(set(language_codes)):
            raise serializers.ValidationError("중복된 언어 코드가 있습니다.")

        return value


class SubCategoryTranslationSerializer(serializers.Serializer):
    """서브카테고리 번역 시리얼라이저"""
    lang = serializers.ChoiceField(choices=["ko", "en", "jp", "cn"])
    name = serializers.CharField(max_length=100, allow_blank=False)

    def validate_name(self, value):
        """이름 검증"""
        if not value or not value.strip():
            raise serializers.ValidationError("이름은 필수입니다.")
        return value.strip()


class SubCategoryCreateSerializer(serializers.Serializer):
    """서브카테고리 생성용 시리얼라이저"""
    category_id = serializers.IntegerField()
    translations = SubCategoryTranslationSerializer(many=True)

    def validate_category_id(self, value):
        """카테고리 ID 검증"""
        if value <= 0:
            raise serializers.ValidationError("유효한 카테고리 ID가 필요합니다.")
        return value

    def validate_translations(self, value):
        """번역 리스트 검증"""
        if not value:
            raise serializers.ValidationError("최소 하나의 번역이 필요합니다.")

        # 중복 언어 코드 체크
        language_codes = [translation["lang"] for translation in value]
        if len(language_codes) != len(set(language_codes)):
            raise serializers.ValidationError("중복된 언어 코드가 있습니다.")

        return value
