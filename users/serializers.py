from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import CustomUser
from helper.email_helper import EmailHelper


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ["email", "nickname", "phone_number", "password"]

    def validate_email(self, value):
        if not EmailHelper.check_verification_email(value):
            raise serializers.ValidationError("인증되지 않은 이메일 입니다.")
        return value
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class SendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")
        return value


class CheckVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")
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
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    '이메일 또는 비밀번호가 올바르지 않습니다.'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    '비활성화된 계정입니다.'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                '이메일과 비밀번호를 모두 입력해주세요.'
            )

