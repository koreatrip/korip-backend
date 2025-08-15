from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.serializers.auth.login import LoginSerializer

class LoginAPIView(APIView):
    """일반 로그인"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="일반 로그인",
        operation_description="이메일과 비밀번호로 로그인하고 JWT 토큰을 발급받습니다.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="로그인 성공",
                examples={
                    "application/json": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
                    }
                }
            ),
            400: openapi.Response(
                description="로그인 실패",
                examples={
                    "application/json": {
                        "error_code": "INVALID_CREDENTIALS",
                        "error_message": "이메일 또는 비밀번호가 올바르지 않습니다."
                    }
                }
            )
        },
        tags=['인증']
    )

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']

            is_first_login = user.last_login is None

            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])
            
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # 토큰에 추가 정보 포함
            access_token['email'] = user.email
            access_token['nickname'] = user.nickname
            access_token['is_social'] = user.is_social
            
            return Response({
                'first_login': is_first_login,
                'access_token': str(access_token),
                'refresh_token': str(refresh)
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
