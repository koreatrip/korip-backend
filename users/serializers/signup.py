from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from users.models import CustomUser
from helper.email_helper import EmailHelper
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    EmailError,
    RequestError
)


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ["email", "nickname", "phone_number", "password"]

    def validate_email(self, value):
        if not EmailHelper.check_verification_email(value):
            raise EmailError(ErrorCode.EMAIL_NOT_CERTIFIED)
        return value
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise RequestError(ErrorCode.INVALID_PASSWORD)
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user