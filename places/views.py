from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from places.models import Place
from places.serializers import PlaceSerializer


class PlacesListAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        language = request.query_params.get("lang", "ko")
        queryset = Place.objects.all()
        category_id = request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category=category_id)
        region_id = request.query_params.get("region_id")
        if region_id:
            queryset = queryset.filter(region=region_id)

        # TODO: 한국어 번역 기준 정렬 구현 예정, 현재는 created_at 순으로 임시 처리
        queryset = queryset.order_by("-favorite_count", "-created_at")

        serializer = PlaceSerializer(
            queryset,
            many=True,
            context={"language": language}
        )

        return Response({
            "places": serializer.data
        }, status=status.HTTP_200_OK)


class PlaceDetailAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, place_id):
        language = request.query_params.get("lang", "ko")
        place = get_object_or_404(Place, id=place_id)

        serializer = PlaceSerializer(
            place,
            context={"language": language}
        )

        return Response({
            "place": serializer.data
        }, status=status.HTTP_200_OK)


class PlacesBySubRegionAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, subregion_id):
        language = request.query_params.get("lang", "ko")
        sort_type = request.query_params.get("sort_type", "favorite")
        queryset = Place.objects.filter(sub_region=subregion_id)
        if sort_type == "name":
            queryset = queryset.order_by("id")
        else:
            queryset = queryset.order_by("-favorite_count", "-created_at")

        serializer = PlaceSerializer(
            queryset,
            many=True,
            context={"language": language}
        )

        return Response({
            "places": serializer.data
        }, status=status.HTTP_200_OK)