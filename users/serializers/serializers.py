from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import CustomUser
from helper.email_helper import EmailHelper
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    EmailError,
    AuthenticationError,
    RequestError,
    UserError,
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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # 토큰에 추가 정보 포함
        token['email'] = user.email
        token['nickname'] = user.nickname
        token['is_social'] = user.is_social
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # 응답에 사용자 정보 추가
        data.update({
            'user': {
                'id': self.user.id,
                'email': self.user.email,
                'name': self.user.nickname,
                'phone_number': self.user.phone_number,
                'is_social': self.user.is_social,
            }
        })
        
        return data


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
