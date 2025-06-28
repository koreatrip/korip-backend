from rest_framework import serializers
from categories.models import Category, SubCategory


class SubCategorySerializer(serializers.Serializer):

   id = serializers.IntegerField()
   name = serializers.SerializerMethodField()

   def __init__(self, *args, **kwargs):
       self.language = kwargs.pop("language", "ko")
       super().__init__(*args, **kwargs)

   def get_name(self, instance):
       language_field_map = {
           "ko": "name_ko",
           "en": "name_en",
           "jp": "name_jp",
           "cn": "name_cn"
       }

       field_name = language_field_map.get(self.language, "name_ko")
       return getattr(instance, field_name)


class CategorySerializer(serializers.Serializer):

   id = serializers.IntegerField()
   name = serializers.SerializerMethodField()
   subcategories = serializers.SerializerMethodField()

   def __init__(self, *args, **kwargs):
       self.language = kwargs.pop("language", "ko")
       super().__init__(*args, **kwargs)

   def get_name(self, instance):
       language_field_map = {
           "ko": "name_ko",
           "en": "name_en",
           "jp": "name_jp",
           "cn": "name_cn"
       }

       field_name = language_field_map.get(self.language, "name_ko")
       return getattr(instance, field_name)

   def get_subcategories(self, instance):
       subcategories_data = []
       for subcategory in instance.subcategories.all():
           subcategory_serializer = SubCategorySerializer(subcategory, language=self.language)
           subcategories_data.append(subcategory_serializer.data)

       return subcategories_data