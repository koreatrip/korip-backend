from rest_framework import serializers


class SocialLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()
