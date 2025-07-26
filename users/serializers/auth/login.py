from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    AuthenticationError,
    RequestError
)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise RequestError(ErrorCode.MISSING_CREDENTIALS)

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            raise AuthenticationError(ErrorCode.INVALID_USER_INFO)

        attrs['user'] = user
        return attrs