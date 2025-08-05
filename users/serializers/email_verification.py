from rest_framework import serializers
from users.models import CustomUser
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import EmailError


class SendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise EmailError(ErrorCode.EMAIL_ALREADY_REGISTERED)
        return value


class CheckVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise EmailError(ErrorCode.EMAIL_ALREADY_REGISTERED)
        return value