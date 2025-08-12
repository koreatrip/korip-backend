from rest_framework import serializers
from categories.models import Category, SubCategory, CategoryTranslation, SubCategoryTranslation


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = self.context.get("language", "ko")

    def get_name(self, instance):
        return instance.get_name(self.language)


class SubCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = self.context.get("language", "ko")

    def get_name(self, instance):
        return instance.get_name(self.language)


class SubCategoryListSerializer(serializers.Serializer):
    subcategories = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = self.context.get("language", "ko")
        self.subcategories_queryset = self.context.get("subcategories_queryset", None)

    def get_subcategories(self, instance):
        subcategories_data = []
        if self.subcategories_queryset:
            for subcategory in self.subcategories_queryset:
                subcategory_serializer = SubCategorySerializer(
                    subcategory,
                    context={"language": self.language}
                )
                subcategories_data.append(subcategory_serializer.data)
        return subcategories_data
