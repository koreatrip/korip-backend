from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    RequestError,
)


class FindAccountSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

class FindPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise RequestError(ErrorCode.INVALID_PASSWORD)
        return value
    
    def validate(self, data):
        user = self.context.get('request').user
        new_password = data.get('new_password')

        if user and user.check_password(new_password):
            raise RequestError(ErrorCode.SAME_CURRENT_PASSWORD)
        return data
