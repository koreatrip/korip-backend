from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import CustomTokenError

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
            401: openapi.Response(
                description="유효하지 않은 리프레시 토큰",
                examples={
                    "application/json": {
                        "error_code": "INVALID_REFRESH_TOKEN",
                        "error_message": "유효하지 않은 리프레시 토큰입니다."
                    }
                }
            )
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