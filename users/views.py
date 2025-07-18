from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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

    def post(self, request):     
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():     
            serializer.save()
            return Response(data={"message": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationCodeAPIVIew(BaseAPIView):
    """이메일 발송 (인증번호)"""
    serializer_class = SendVerificationCodeSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            verification_code = EmailHelper.send_verification_email(email)

            if verification_code is None:
                return Response(data={"error_message": "이메일 발송을 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
            self.redis_helper.set_with_expiry(f"email_verification:{email}", verification_code, 600)
            return Response(data={"message": "이메일 발송이 완료되었습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckVerificationCodeAPIView(BaseAPIView):
    """이메일 인증 코드 확인"""
    serializers_class = CheckVerificationCodeSerializer

    def post(self, request):
        serializer = self.serializers_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            if not EmailHelper.check_verification_code(email, code):
                return Response(data={"error_message": "이메일 인증번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data={"message": "이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
