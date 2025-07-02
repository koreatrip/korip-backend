from rest_framework import serializers
from categories.models import Category, SubCategory, CategoryTranslation, SubCategoryTranslation


class SubCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop("language", "ko")
        super().__init__(*args, **kwargs)

    def get_name(self, instance):
        return instance.get_name(self.language)


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop("language", "ko")
        super().__init__(*args, **kwargs)

    def get_name(self, instance):
        return instance.get_name(self.language)

    def get_subcategories(self, instance):
        subcategories_data = []
        for subcategory in instance.subcategories.all():
            subcategory_serializer = SubCategorySerializer(
                subcategory,
                language=self.language
            )
            subcategories_data.append(subcategory_serializer.data)
        return subcategories_data


class SubCategoryListSerializer(serializers.Serializer):
    subcategories = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop("language", "ko")
        self.subcategories_queryset = kwargs.pop("subcategories_queryset", None)
        super().__init__(*args, **kwargs)

    def get_subcategories(self, instance):
        subcategories_data = []
        if self.subcategories_queryset:
            for subcategory in self.subcategories_queryset:
                subcategory_serializer = SubCategorySerializer(
                    subcategory,
                    language=self.language
                )
                subcategories_data.append(subcategory_serializer.data)
        return subcategories_data


class CategoryTranslationSerializer(serializers.Serializer):
    lang = serializers.ChoiceField(choices=["ko", "en", "jp", "cn"])
    name = serializers.CharField(max_length=100, allow_blank=False)

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("이름은 필수입니다.")
        return value.strip()


class CategoryCreateSerializer(serializers.Serializer):
    translations = CategoryTranslationSerializer(many=True)

    def validate_translations(self, value):
        if not value:
            raise serializers.ValidationError("최소 하나의 번역이 필요합니다.")

        language_codes = [translation["lang"] for translation in value]
        if len(language_codes) != len(set(language_codes)):
            raise serializers.ValidationError("중복된 언어 코드가 있습니다.")

        return value


class SubCategoryTranslationSerializer(serializers.Serializer):
    lang = serializers.ChoiceField(choices=["ko", "en", "jp", "cn"])
    name = serializers.CharField(max_length=100, allow_blank=False)

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("이름은 필수입니다.")
        return value.strip()


class SubCategoryCreateSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    translations = SubCategoryTranslationSerializer(many=True)

    def validate_category_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("유효한 카테고리 ID가 필요합니다.")
        return value

    def validate_translations(self, value):
        if not value:
            raise serializers.ValidationError("최소 하나의 번역이 필요합니다.")

        language_codes = [translation["lang"] for translation in value]
        if len(language_codes) != len(set(language_codes)):
            raise serializers.ValidationError("중복된 언어 코드가 있습니다.")

        return value
