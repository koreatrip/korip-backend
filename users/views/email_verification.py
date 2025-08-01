from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from helper.email_helper import EmailHelper
from helper.redis_helper import RedisHelper
from users.serializers.email_verification import (
    SendVerificationCodeSerializer,
    CheckVerificationCodeSerializer
)
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import EmailError


class BaseAPIView(APIView):
    redis_helper = RedisHelper()


class SendVerificationCodeAPIVIew(BaseAPIView):
    """이메일 발송 (인증번호)"""
    permission_classes = [AllowAny]
    serializer_class = SendVerificationCodeSerializer
    
    @swagger_auto_schema(
        operation_summary="이메일 인증번호 발송",
        operation_description="지정된 이메일로 인증번호를 발송합니다. 인증번호는 1분간 유효합니다.",
        request_body=SendVerificationCodeSerializer,
        responses={
            200: openapi.Response(description="이메일 발송 성공"),
            400: openapi.Response(
                description="이메일 발송 실패",
                examples={
                    "application/json": {
                        "error_code": "EMAIL_NOT_CERTIFIED",
                        "error_message": "이메일 인증번호 발송에 실패했습니다."
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
            200: openapi.Response(description="인증번호 확인 성공"),
            400: openapi.Response(
                description="인증번호 확인 실패",
                examples={
                    "application/json": {
                        "error_code": "EMAIL_CERTIFICATION_FAIL",
                        "error_message": "이메일 인증번호가 일치하지 않거나 만료되었습니다."
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
