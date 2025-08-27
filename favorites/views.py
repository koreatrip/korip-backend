from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import RequestError

from favorites.serializers import FavoritePlaceSerializer, FavoritePlaceListSerializer
from favorites.models import FavoritePlace
from utils.pagination.favorite_pagination import FavoritePagination


class FavoritePlaceAPIView(APIView):

    permission_classes = [IsAuthenticated]
    pagination_class = FavoritePagination
    
    def post(self, request):
        serializer = FavoritePlaceSerializer(data=request.data)
        
        if not serializer.is_valid():
            raise RequestError(ErrorCode.INVALID_DATA)
        
        result = serializer.toggle_favorite(request.user)
        
        return Response(status=status.HTTP_200_OK)
    
    def get(self, request):
        language = request.query_params.get("lang", "ko")

        favorite_relations = FavoritePlace.objects.filter(user=request.user).select_related('place').order_by('-created_at')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(favorite_relations, request)
        
        favorite_place_serializer = FavoritePlaceListSerializer(
            page,
            many=True,
            context={"language": language}
        )

        return paginator.get_paginated_response(favorite_place_serializer.data)