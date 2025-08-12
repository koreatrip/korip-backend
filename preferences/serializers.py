from rest_framework import serializers
from categories.models import SubCategory


class PreferenceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ['id', 'name']

    def get_name(self, obj):
        lang = self.context.get('language', 'ko')
        return obj.get_name(lang)
