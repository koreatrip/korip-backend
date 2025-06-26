from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Language
from .serializers import LanguageSerializer, LanguageSelectionSerializer


# 언어 목록 조회 API
class LanguageListAPI(APIView):

# 활성화된 언어 목록 반환
    def get(self, request):
        languages = Language.objects.filter(is_active=True)
        serializer = LanguageSerializer(languages, many=True)

        return Response({
            'languages': serializer.data
        }, status=status.HTTP_200_OK)

# 언어 선택 API
class LanguageSelectAPI(APIView):

# 언어 선택 처리
    def post(self, request):
        serializer = LanguageSelectionSerializer(data=request.data)

        if serializer.is_valid():
            selected_language = serializer.validated_data['language']

            # 선택된 언어 정보 조회
            language = Language.objects.get(code=selected_language, is_active=True)

            return Response({
                'message': f'Language set to {language.name}',
                'code': selected_language
            }, status=status.HTTP_200_OK)

        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)