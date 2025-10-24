from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from idols.models import IdolRequest
from idols.serializers import IdolRequestSerializer


# 아이돌 신청하기 API
class IdolRequestCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="아이돌 신청하기",
        operation_description="새로운 아이돌을 신청합니다. 로그인한 사용자만 신청 가능합니다.",
        request_body=IdolRequestSerializer,
        responses={
            201: openapi.Response(
                description="신청 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="성공 메시지"
                        ),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="생성된 신청 정보"
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="잘못된 요청",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="오류 메시지"
                        ),
                        "details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="상세 오류 정보"
                        )
                    }
                )
            ),
            401: openapi.Response(
                description="인증 필요",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="인증 오류 메시지"
                        )
                    }
                )
            )
        },
        tags=["아이돌 신청"]
    )
    def post(self, request):
        # 요청 데이터를 Serializer로 검증
        serializer = IdolRequestSerializer(data=request.data)

        # 유효성 검사
        if serializer.is_valid():
            # 현재 로그인한 유저로 저장
            serializer.save(user=request.user)

            # 성공 응답
            return Response(
                {
                    "message": "아이돌 신청이 완료되었습니다.",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        # 유효성 검사 실패 시
        return Response(
            {
                "error": "입력 정보를 확인해주세요.",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
