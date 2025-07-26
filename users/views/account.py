from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.serializers.serializers import ChangePasswordSerializer
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import AuthenticationError


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