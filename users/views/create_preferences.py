from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.models import CustomUser
from users.serializers.create_preferences import CreatePreferenceSerializer
from preferences.services import PreferenceService
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    RequestError,
    ServerError
)
import logging
logger = logging.getLogger(__name__)


class CreatePreferenceAPIView(APIView):
    """사용자 관심사 입력"""
    permission_classes = [AllowAny]
    serializer_class = CreatePreferenceSerializer

    @swagger_auto_schema(
        operation_summary="사용자 관심사 등록",
        operation_description="사용자의 관심사(서브카테고리)를 등록합니다. 기존 관심사는 삭제되고 새로운 관심사로 대체됩니다.",
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_PATH,
                description="사용자 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=CreatePreferenceSerializer,
        responses={
            201: openapi.Response(
                description="관심사 등록 성공",
                examples={}
            ),
            400: openapi.Response(
                description="잘못된 요청 데이터",
                examples={
                    "application/json": {
                        "error_code": "INVALID_DATA",
                        "error_message": "데이터가 올바르지 않습니다."
                    }
                }
            ),
            404: openapi.Response(
                description="사용자를 찾을 수 없음",
                examples={
                    "application/json": {
                        "error_code": "USER_NOT_FOUND",
                        "error_message": "사용자를 찾을 수 없습니다."
                    }
                }
            ),
            500: openapi.Response(
                description="서버 내부 오류",
                examples={
                    "application/json": {
                        "error_code": "SERVER_ERROR",
                        "error_message": "서버 내부 오류가 발생했습니다."
                    }
                }
            )
        },
        tags=['관심사 선택']
    )

    def post(self, request, user_id):

        user = CustomUser.objects.filter(id=user_id).first()
        if user is None:
            raise RequestError(ErrorCode.USER_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            raise RequestError(ErrorCode.INVALID_DATA)
        
        subcategories_ids = serializer.validated_data['preferences']
        
        try:
            result = PreferenceService.add_preference(user_id, subcategories_ids)
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"관심사 등록 중 오류 발생: {str(e)}")
            raise ServerError(ErrorCode.SERVER_ERROR)
