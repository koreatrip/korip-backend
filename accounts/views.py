from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import validate_language, get_supported_languages


class LanguageAPI(APIView):

    def get(self, request):
        lang_param = request.GET.get('lang')
        current_language = validate_language(lang_param)

        return Response({
            'current_language': current_language,
            'supported_languages': get_supported_languages()
        }, status=status.HTTP_200_OK)