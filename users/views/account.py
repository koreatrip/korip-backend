from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.serializers.account import (
    ChangePasswordSerializer,
    FindAccountSerializer,
    FindPasswordSerializer,
    UserInfoSerializer
)
from users.models import CustomUser
from utils.helper.email_helper import EmailHelper
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import (
    AuthenticationError,
    RequestError,
    UserError,
    EmailError,
)


authorization_header = openapi.Parameter(
    'Authorization', 
    openapi.IN_HEADER,
    description="JWT Token을 'Bearer <token>' 형식으로 추가하세요.",
    type=openapi.TYPE_STRING,
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
                        "error_message": "해당 전화번호로 가입된 계정이 없습니다."
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
                examples={}
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


class UserInfoAPIView(APIView):
    """유저정보 조회, 수정, 삭제"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserInfoSerializer

    @swagger_auto_schema(
        operation_summary="사용자 정보 조회",
        operation_description="현재 인증된 사용자의 정보를 조회합니다. 이메일과 전화번호 등의 중요한 정보는 마스킹되어 반환됩니다.",
        manual_parameters=[
            openapi.Parameter(
                'lang',
                openapi.IN_QUERY,
                description="언어 설정 (ko: 한국어, en: 영어)",
                type=openapi.TYPE_STRING,
                enum=['ko', 'en', 'jp', 'cn'],
                default='ko',
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="사용자 정보 조회 성공",
                examples={
                    "application/json": {
                        "id": 3,
                        "email": "test@test.com",
                        "name": "testuser",
                        "phone_number": "8201012345678",
                        "login_type": "email",
                        "is_social": False,
                        "is_active": True,
                        "created_at": "2025-07-31T16:15:58.044344+09:00",
                        "updated_at": "2025-08-08T00:20:03.148108+09:00",
                        "preferences_display": [
                            {"id": 1, "name": "역사"},
                            {"id": 2, "name": "박물관"},
                            {"id": 3, "name": "미술관"},
                            {"id": 7, "name": "산"},
                            {"id": 8, "name": "바다"},
                            {"id": 9, "name": "강"}
                        ],
                        "my_total_plans": 5,
                        "my_total_favorites": 12,
                        "visited_places": 23
                    }
                }
            ),
            401: openapi.Response(
                description="인증 실패",
                examples={
                    "application/json": {
                        "error_code": "AUTHENTICATION_FAILED",
                        "error_message": "인증이 실패했습니다. 로그인 후 다시 시도해 주세요."
                    }
                }
            )
        },
        tags=["사용자 계정"]
    )

    def get(self, request):
        serializer = self.serializer_class(instance=request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="사용자 정보 수정",
        operation_description="현재 인증된 사용자의 정보를 수정합니다. 이름, 전화번호, 관심사 등을 부분적으로 업데이트할 수 있습니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='사용자 이름',
                    example='홍길동'
                ),
                'phone_number': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='전화번호 (국가코드 포함)',
                    example='8201012345678'
                ),
                'preferences': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='관심사 ID 배열',
                    example=[1, 2, 3, 7, 8, 9]
                ),
            },
            required=[],  # 모든 필드가 선택적이므로 빈 배열
        ),
        responses={
            200: openapi.Response(
                description="사용자 정보 수정 성공",
                examples={
                    "application/json": {
                        "id": 3,
                        "email": "test@test.com",
                        "name": "홍길동",  # 수정된 이름
                        "phone_number": "8201012345678",
                        "login_type": "email",
                        "is_social": False,
                        "is_active": True,
                        "created_at": "2025-07-31T16:15:58.044344+09:00",
                        "updated_at": "2025-08-08T00:20:03.148108+09:00",
                        "preferences_display": [
                            {"id": 1, "name": "역사"},
                            {"id": 2, "name": "박물관"},
                            {"id": 3, "name": "미술관"},
                            {"id": 7, "name": "산"},
                            {"id": 8, "name": "바다"},
                            {"id": 9, "name": "강"}
                        ]
                    }
                }
            ),
            400: openapi.Response(
                description="잘못된 요청",
                examples={
                    "application/json": {
                        "error_code": "VALIDATION_ERROR",
                        "error_message": "입력값이 올바르지 않습니다.",
                        "details": {
                            "phone_number": ["올바른 전화번호 형식이 아닙니다."]
                        }
                    }
                }
            ),
            401: openapi.Response(
                description="인증 실패",
                examples={
                    "application/json": {
                        "error_code": "AUTHENTICATION_FAILED",
                        "error_message": "인증이 실패했습니다. 로그인 후 다시 시도해 주세요."
                    }
                }
            )
        },
        tags=["사용자 계정"]
    )

    def patch(self, request):
        serializer = self.serializer_class(
            instance=request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="사용자 삭제",
        operation_description="현재 인증된 사용자의 계정을 삭제합니다. 비밀번호 확인 후 계정이 삭제되며, 삭제 후에는 복구할 수 없습니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['password'],
            properties={
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='계정 삭제를 위한 현재 비밀번호',
                    example='current_password123'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="사용자 삭제 성공",
                examples={
                    "application/json": {}
                }
            ),
            400: openapi.Response(
                description="잘못된 요청 데이터 또는 비밀번호 불일치",
                examples={
                    "application/json": {
                        "error_code": "INVALID_DATA",
                        "error_message": "비밀번호를 입력해주세요."
                    }
                }
            ),
            401: openapi.Response(
                description="비밀번호 불일치",
                examples={
                    "application/json": {
                        "error_code": "MISSMATCHED_PASSWORD", 
                        "error_message": "비밀번호가 일치하지 않습니다."
                    }
                }
            )
        },
        tags=["사용자 계정"]
    )
    
    def delete(self, request):
        user = request.user
        password = request.data.get('password')

        if not password:
            raise RequestError(ErrorCode.INVALID_DATA)

        if not user.check_password(password):
            raise RequestError(ErrorCode.MISSMATCHED_PASSWORD)

        user.delete()
        return Response(status=status.HTTP_200_OK)
