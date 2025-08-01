from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.serializers.account import (
    ChangePasswordSerializer,
    FindAccountSerializer,
    FindPasswordSerializer
)
from users.models import CustomUser
from helper.email_helper import EmailHelper
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    AuthenticationError,
    RequestError,
    UserError,
    EmailError
)


class FindAccountAPIView(APIView):
    """가입한 계정 찾기"""
    permission_classes = [AllowAny]
    serializer_class = FindAccountSerializer

    @swagger_auto_schema(
        operation_summary="가입한 계정 찾기",
        operation_description="전화번호로 가입된 계정들을 찾습니다. 이메일은 보안을 위해 마스킹되어 반환됩니다.",
        request_body=FindAccountSerializer,
        responses={
            200: openapi.Response(
                description="계정 찾기 성공",
                examples={
                    "application/json": {
                        "accounts": [
                            {
                                "id": 1,
                                "email": "jo**@example.com",
                                "login_type": "email"
                            },
                            {
                                "id": 2,
                                "email": "jo**@gmail.com", 
                                "login_type": "google"
                            }
                        ]
                    }
                }
            ),
            400: openapi.Response(
                description="유효성 검사 실패",
                examples={
                    "application/json": {
                        "phone_number": ["전화번호는 필수 항목입니다."]
                    }
                }
            ),
            404: openapi.Response(
                description="계정을 찾을 수 없음",
                examples={
                    "application/json": {
                        "error_code": "ACCOUNT_NOT_FOUND",
                        "message": "해당 전화번호로 가입된 계정이 없습니다."
                    }
                }
            )
        },
        tags=["사용자 계정"]
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        rq_phone_number = serializer.validated_data['phone_number']
        
        users = CustomUser.objects.filter(phone_number=rq_phone_number)

        if not users.exists():
            raise RequestError(ErrorCode.ACCOUNT_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)

        response_data = {
            "accounts": [
                {
                    "id": user.id,
                    "email": self._mask_email(user.email),
                    "login_type": user.login_type
                }
                for user in users
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
    def _mask_email(self, email):
        if '@' not in email:
            return email
        local, domain = email.split("@")
        if len(local) <= 1:
            return email
        elif len(local) == 2:
            return local[0] + "*" + "@" + domain
        elif len(local) == 3:
            return local[:2] + "*" + "@" + domain
        else:
            mask_length = min(8, len(local) - 2)
            return local[:2] + "*" * mask_length + "@" + domain


class FindPasswordAPIView(APIView):
    """비밀번호 찾기"""
    permission_classes = [AllowAny]
    serializer_class = FindPasswordSerializer


    @swagger_auto_schema(
        operation_summary="비밀번호 찾기",
        operation_description="등록된 이메일을 통해 임시 비밀번호를 발송합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description='등록된 이메일 주소',
                    example='user@example.com'
                )
            },
            required=['email']
        ),
        responses={
            200: openapi.Response(
                description="임시 비밀번호 발송 성공",
                examples={}
            ),
            404: openapi.Response(
                description="존재하지 않는 사용자",
                examples={
                    "application/json": {
                        "error_code": "USER_NOT_FOUND",
                        "error_message": "해당 이메일로 등록된 사용자가 없습니다."
                    }
                }
            ),
            400: openapi.Response(
                description="유효하지 않은 요청",
                examples={
                    "application/json": {
                        "email": ["유효한 이메일 주소를 입력해주세요."]
                    }
                }
            )
        },
        tags=['사용자 계정']
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get('email')
        user = CustomUser.objects.filter(email=email).first()
        
        if not user:
            raise UserError(ErrorCode.USER_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)

        temporary_password = EmailHelper.send_temporary_password(email)

        if not temporary_password:
            raise EmailError(ErrorCode.EMAIL_SEND_FAILED)

        user.set_password(temporary_password)
        user.save()
        
        return Response(status=status.HTTP_200_OK)


class ChangePasswordAPIView(APIView):
    """비밀번호 변경"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @swagger_auto_schema(
        operation_summary="비밀번호 변경",
        operation_description="현재 비밀번호를 확인한 후 새 비밀번호로 변경합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'current_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='현재 비밀번호',
                    example='old_password123'
                ),
                'new_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='새 비밀번호',
                    example='new_password456'
                )
            },
            required=['current_password', 'new_password']
        ),
        responses={
            200: openapi.Response(
                description="변경 성공",
                examples={
                    "application/json": {
                        "message": "비밀번호가 성공적으로 변경되었습니다."
                    }
                }
            ),
            400: openapi.Response(
                description="입력 오류 또는 인증 실패",
                examples={
                    "application/json": {
                        "error_code": "MISSMATCHED_PASSWORD",
                        "error_message": "현재 비밀번호가 올바르지 않습니다."
                    }
                }
            )
        },
        tags=['비밀번호']
    )

    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        current_password = serializer.validated_data.get('current_password')
        new_password = serializer.validated_data.get('new_password')
        
        user = request.user
        if not user.check_password(current_password):
            raise AuthenticationError(ErrorCode.MISSMATCHED_PASSWORD)
        
        user.set_password(new_password)
        user.save()
        
        return Response(status=status.HTTP_200_OK)
