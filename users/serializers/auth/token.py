from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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