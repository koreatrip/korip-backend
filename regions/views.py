from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from regions.models import Region, SubRegion
from regions.serializers import RegionSerializer, SubRegionSerializer


class RegionsListAPI(APIView):
    """전체 지역 목록 조회 API - 서브지역 정보 포함하지 않음"""

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
    """특정 지역 상세 조회 API - 서브지역 목록 포함 (인기순 정렬)"""

    def get(self, request, region_id):
        language = request.query_params.get("lang", "ko")

        # 지역 존재 확인
        region = get_object_or_404(Region, id=region_id)

        # 해당 지역의 서브지역들 조회 (인기순 정렬)
        subregions = SubRegion.objects.filter(region=region).order_by(
            "-favorite_count",  # 즐겨찾기 많은 순
            "id"  # 같으면 ID 순 (나중에 이름순으로 개선 가능)
        )

        # 지역 기본 정보
        region_serializer = RegionSerializer(
            region,
            context={"language": language}
        )

        # 서브지역 정보들
        subregions_serializer = SubRegionSerializer(
            subregions,
            many=True,
            context={"language": language}
        )

        return Response({
            "region": region_serializer.data,
            "subregions": subregions_serializer.data,
            "total_subregions": len(subregions_serializer.data)
        }, status=status.HTTP_200_OK)
