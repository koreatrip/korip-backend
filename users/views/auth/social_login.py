from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.oauth.factory import get_provider
from users.models import CustomUser
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers.auth.social_login import SocialLoginSerializer
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import RequestError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class SocialLoginAPIView(APIView):
    """소셜 로그인 (프론트에서 인가코드 받아서 백엔드에 전달)"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="social_login",
        operation_summary="소셜 로그인",
        operation_description="""
        Google OAuth 인가 코드를 사용하여 소셜 로그인을 수행합니다.
        
        **프로세스:**
        1. 프론트엔드에서 Google OAuth 인가 코드를 받습니다
        2. 백엔드에서 인가 코드를 사용해 액세스 토큰을 받습니다
        3. 액세스 토큰으로 사용자 정보를 가져옵니다
        4. 사용자가 존재하지 않으면 새로 생성합니다
        5. JWT 토큰을 발급하여 반환합니다
        """,
        tags=["인증"],
        manual_parameters=[
            openapi.Parameter(
                name="provider",
                in_=openapi.IN_QUERY,
                description="OAuth 제공자 (현재 'google'만 지원)",
                type=openapi.TYPE_STRING,
                required=True,
                enum=["google"],
                example="google"
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["code", "phone_number"],
            properties={
                "code": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Google OAuth 인가 코드",
                    example="4/0AeaYSHBqFw8xQwN..."
                ),
                "phone_number": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="사용자 전화번호",
                    example="010-1234-5678"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="로그인 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "first_login": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            description="첫 로그인 여부",
                            example=True
                        ),
                        "access_token": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="JWT 액세스 토큰 (사용자 정보 포함)",
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        ),
                        "refresh_token": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="JWT 리프레시 토큰",
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "first_login": True,
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQwOTk5OTk5LCJpYXQiOjE2NDA5OTk5OTksImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJuaWNrbmFtZSI6IuyCrOyaqeyekCIsImlzX3NvY2lhbCI6dHJ1ZX0...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY0MDk5OTk5OSwiaWF0IjoxNjQwOTk5OTk5LCJqdGkiOiIxMjM0NTY3ODkwIiwidXNlcl9pZCI6MX0..."
                    }
                }
            ),
            400: openapi.Response(
                description="잘못된 요청",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error_code": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="에러 코드",
                            example="UNSUPPORTED_PROVIDER"
                        ),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="에러 메시지",
                            example="지원하지 않는 OAuth 제공자입니다"
                        ),
                        "detail": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="상세 에러 정보 (선택사항)"
                        )
                    }
                ),
                examples={
                    "unsupported_provider": {
                        "error_code": "UNSUPPORTED_PROVIDER",
                        "message": "지원하지 않는 OAuth 제공자입니다"
                    },
                    "invalid_code": {
                        "error_code": "INVALID_AUTH_CODE",
                        "message": "유효하지 않은 인가 코드입니다"
                    },
                    "validation_error": {
                        "code": ["이 필드는 필수입니다."],
                        "phone_number": ["이 필드는 필수입니다."]
                    }
                }
            ),
            401: openapi.Response(
                description="인증 실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error_code": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="에러 코드"
                        ),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="에러 메시지"
                        )
                    }
                )
            ),
            500: openapi.Response(
                description="서버 내부 오류",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error_code": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="에러 코드"
                        ),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="에러 메시지"
                        )
                    }
                )
            )
        }
    )

    def post(self, request):
        provider_name = request.query_params.get("provider")
        if provider_name != "google":
            raise RequestError(ErrorCode.UNSUPPORTED_PROVIDER)

        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]
        phone_number = serializer.validated_data["phone_number"]

        provider = get_provider(provider_name)
        access_token = provider.get_token(code)
        user_info = provider.get_user_info(access_token)

        email = user_info.get("email")
        name = user_info.get("name")
        login_type = user_info.get("login_type")
        nickname = (
            name
            or user_info.get("nickname")
            or f"소셜유저{user_info.get('sub')}"
        )

        user, created = CustomUser.objects.get_or_create(
            email=email,
            phone_number=phone_number,
            defaults={
                "nickname": nickname,
                "is_social": True,
                "login_type": login_type
            }
        )

        if created:
            user.set_unusable_password()
            user.save()

        is_first_login = user.last_login is None

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        access["email"] = user.email
        access["nickname"] = user.nickname
        access["is_social"] = user.is_social

        return Response({
            "first_login": is_first_login,
            "access_token": str(access),
            "refresh_token": str(refresh)
        }, status=status.HTTP_200_OK)
