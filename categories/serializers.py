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
