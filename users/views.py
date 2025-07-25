from django.shortcuts import render
from django.contrib.auth import authenticate, update_session_auth_hash
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.serializers import (
    SignUpSerializer,
    SendVerificationCodeSerializer,
    CheckVerificationCodeSerializer,
    LoginSerializer
)
from helper.email_helper import EmailHelper
from helper.redis_helper import RedisHelper
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    EmailError,
    CustomTokenError,
    AuthenticationError,
)


class BaseAPIView(APIView):
    redis_helper = RedisHelper()


class SignUpAPIView(BaseAPIView):
    """회원가입"""
    permission_classes = [AllowAny]
    serializer_class = SignUpSerializer

    @swagger_auto_schema(
        operation_summary="회원가입",
        operation_description="새로운 사용자를 등록합니다.",
        request_body=SignUpSerializer,
        responses={
            201: openapi.Response(
                description="회원가입 성공",
                examples={
                    "application/json": {
                        "id": 1,
                        "name": "홍길동",
                        "email": "test@example.com",
                        "phone_number": "01012345678",
                        "created_at": "2024-07-01T12:00:00Z",
                        "updated_at": "2024-07-01T12:00:00Z"
                    }
                }
            ),
            400: openapi.Response(
                description="잘못된 요청",
                examples={
                    "application/json": {
                        "email": ["이 필드는 필수입니다."],
                        "password": ["이 필드는 필수입니다."]
                    }
                }
            )
        },
        tags=['회원가입']
    )

    def post(self, request):     
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():     
            saved_user = serializer.save()
            return Response(data={
                "id": saved_user.id,
                "name": saved_user.nickname,
                "email": saved_user.email,
                "phone_number": saved_user.phone_number,
                "created_at": saved_user.created_at,
                "updated_at": saved_user.updated_at
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationCodeAPIVIew(BaseAPIView):
    """이메일 발송 (인증번호)"""
    permission_classes = [AllowAny]
    serializer_class = SendVerificationCodeSerializer
    
    @swagger_auto_schema(
        operation_summary="이메일 인증번호 발송",
        operation_description="지정된 이메일로 인증번호를 발송합니다. 인증번호는 1분간 유효합니다.",
        request_body=SendVerificationCodeSerializer,
        responses={
            200: openapi.Response(
                description="이메일 발송 성공"
            ),
            400: openapi.Response(
                description="이메일 발송 실패",
                examples={
                    "application/json": {
                        "error_message": "이메일 발송을 실패했습니다."
                    }
                }
            )
        },
        tags=['이메일 인증']
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            verification_code = EmailHelper.send_verification_email(email)

            if verification_code is None:
                raise EmailError(ErrorCode.EMAIL_NOT_CERTIFIED)
            self.redis_helper.set_with_expiry(f"email_verification:{email}", verification_code, 600)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckVerificationCodeAPIView(BaseAPIView):
    """이메일 인증 코드 확인"""
    permission_classes = [AllowAny]
    serializer_class = CheckVerificationCodeSerializer

    @swagger_auto_schema(
        operation_summary="이메일 인증번호 확인",
        operation_description="이메일로 발송된 인증번호를 확인합니다.",
        request_body=CheckVerificationCodeSerializer,
        responses={
            200: openapi.Response(
                description="인증번호 확인 성공"
            ),
            400: openapi.Response(
                description="인증번호 확인 실패",
                examples={
                    "application/json": {
                        "error_message": "이메일 인증번호가 일치하지 않습니다."
                    }
                }
            )
        },
        tags=['이메일 인증']
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            if not EmailHelper.check_verification_code(email, code):
                raise EmailError(ErrorCode.EMAIL_CERTIFICATION_FAIL)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(BaseAPIView):
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
                        "non_field_errors": ["이메일 또는 비밀번호가 올바르지 않습니다."]
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
            
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # 토큰에 추가 정보 포함
            access_token['email'] = user.email
            access_token['nickname'] = user.nickname
            access_token['is_social'] = user.is_social
            
            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh)
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """로그아웃 (토큰 블랙리스트)"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="로그아웃",
        operation_description="사용자의 refresh 토큰을 블랙리스트에 등록하여 로그아웃 처리합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='리프레시 토큰')
            },
            required=['refresh_token']
        ),
        responses={
            200: openapi.Response(description="로그아웃 성공"),
            400: openapi.Response(description="잘못된 요청 또는 토큰 오류")
        },
        tags=['인증']
    )

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response(status=status.HTTP_200_OK)
        
        except TokenError as e:
            raise CustomTokenError(ErrorCode.INVALID_REFRESH_TOKEN)
        except Exception as e:
            raise AuthenticationError(ErrorCode.LOGOUT_FAIL)



class CustomTokenRefreshView(TokenRefreshView):
    """액세스 토큰 갱신"""

    @swagger_auto_schema(
        operation_summary="액세스 토큰 갱신",
        operation_description="리프레시 토큰을 이용하여 새로운 액세스 토큰을 발급합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='리프레시 토큰')
            },
            required=['refresh_token']
        ),
        responses={
            200: openapi.Response(
                description="토큰 갱신 성공",
                examples={
                    "application/json": {
                        "access_token": "new-access-token"
                    }
                }
            ),
            401: openapi.Response(description="유효하지 않은 리프레시 토큰")
        },
        tags=['인증']
    )
    
    def post(self, request, *args, **kwargs):
        try:
            if 'refresh_token' in request.data and 'refresh' not in request.data:
                modified_data = request.data.copy()
                modified_data['refresh'] = modified_data.pop('refresh_token')
                request._full_data = modified_data
            
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                if 'access' in response.data:
                    access_token = response.data.pop('access')
                    response.data['access_token'] = access_token
            return response
            
        except InvalidToken as e:
            raise CustomTokenError(ErrorCode.INVALID_REFRESH_TOKEN)
            return Response({
                'error': '유효하지 않은 리프레시 토큰입니다.'
            }, status=status.HTTP_401_UNAUTHORIZED)
