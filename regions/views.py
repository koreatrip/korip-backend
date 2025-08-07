from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from regions.models import Region, SubRegion
from regions.serializers import RegionSerializer, SubRegionSerializer


class RegionsListAPI(APIView):

    def get(self, request):
        language = request.query_params.get("lang", "ko")

        # 전체 지역 목록 조회
        regions = Region.objects.all().order_by("id")

        serializer = RegionSerializer(
            regions,
            many=True,
            context={"language": language}
        )

        return Response({
            "regions": serializer.data
        }, status=status.HTTP_200_OK)


class RegionDetailAPI(APIView):

    def get(self, request, region_id):
        language = request.query_params.get("lang", "ko")
        region = get_object_or_404(Region, id=region_id)
        subregions = SubRegion.objects.filter(region=region).order_by(
            "-favorite_count",
            "id" # TODO : 가나다순 구현해야 됨
        )

        subregions_serializer = SubRegionSerializer(
            subregions,
            many=True,
            context={"language": language}
        )

        region_serializer = RegionSerializer(
            region,
            context={"language": language}
        )

        region_data = region_serializer.data
        region_data["subregions"] = subregions_serializer.data

        return Response({
            "region": region_data
        }, status=status.HTTP_200_OK)