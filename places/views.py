from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, SubCategory
from .serializers import CategorySerializer


class ThemesAPIView(APIView):

    def get(self, request):
        language = request.query_params.get('lang', 'ko')

        supported_languages = ['ko', 'en', 'jp', 'cn']
        if language not in supported_languages:
            language = 'ko'

        categories = Category.objects.prefetch_related('subcategories').all()

        serializer = CategorySerializer(categories, many=True, language=language)

        return Response({
            'themes': serializer.data
        }, status=status.HTTP_200_OK)
