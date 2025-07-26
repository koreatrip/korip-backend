from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.serializers.serializers import SignUpSerializer

class SignUpAPIView(APIView):
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
