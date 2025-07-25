from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.serializers import (
    SignUpSerializer,
    SendVerificationCodeSerializer,
    CheckVerificationCodeSerializer
)
from helper.email_helper import EmailHelper
from helper.redis_helper import RedisHelper

class BaseAPIView(APIView):
    redis_helper = RedisHelper()


class SignUpAPIView(BaseAPIView):
    """회원가입"""
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
                return Response(data={"error_message": "이메일 발송을 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
            self.redis_helper.set_with_expiry(f"email_verification:{email}", verification_code, 600)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckVerificationCodeAPIView(BaseAPIView):
    """이메일 인증 코드 확인"""
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
                return Response(data={"error_message": "이메일 인증번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
