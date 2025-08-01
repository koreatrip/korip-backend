from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    CustomTokenError,
    AuthenticationError,
)


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
            400: openapi.Response(
                description="잘못된 요청 또는 토큰 오류",
                examples={
                    "application/json": {
                        "error_code": "INVALID_REFRESH_TOKEN",
                        "error_message": "유효하지 않은 리프레시 토큰입니다."
                    }
                }
            ),
            500: openapi.Response(
                description="서버 오류",
                examples={
                    "application/json": {
                        "error_code": "LOGOUT_FAIL",
                        "error_message": "로그아웃 처리 중 오류가 발생했습니다."
                    }
                }
            )
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