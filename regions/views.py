from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from regions.models import Region, SubRegion
from regions.serializers import (
    RegionSerializer,
    RegionDetailSerializer,
    SubRegionSerializer,
    SubRegionListSerializer
)


class RegionsAPI(APIView):
    def get(self, request):
        lang = request.query_params.get("lang", "ko")

        supported_languages = ["ko", "en", "jp", "cn"]
        if lang not in supported_languages:
            return Response(
                {"error": f"지원하지 않는 언어입니다. 지원 언어: {', '.join(supported_languages)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            regions = Region.objects.all().order_by("id")
            serializer = RegionSerializer(
                regions,
                many=True,
                context={"lang": lang}
            )

            return Response(
                {"regions": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": "지역 목록 조회 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegionDetailAPI(APIView):
    def get(self, request, region_id):
        lang = request.query_params.get("lang", "ko")
        supported_languages = ["ko", "en", "jp", "cn"]
        if lang not in supported_languages:
            return Response(
                {"error": f"지원하지 않는 언어입니다. 지원 언어: {', '.join(supported_languages)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            region = get_object_or_404(Region, id=region_id)
            serializer = RegionDetailSerializer(
                region,
                context={"lang": lang}
            )

            return Response(
                {"region": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": "지역 상세 정보 조회 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegionSubRegionsAPI(APIView):
    def get(self, request, region_id):
        lang = request.query_params.get("lang", "ko")

        supported_languages = ["ko", "en", "jp", "cn"]
        if lang not in supported_languages:
            return Response(
                {"error": f"지원하지 않는 언어입니다. 지원 언어: {', '.join(supported_languages)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            region = get_object_or_404(Region, id=region_id)
            subregions = region.subregions.select_related().prefetch_related(
                'translations'
            ).all()
            def sort_key(subregion):
                korean_name = subregion.get_name("ko") or f"SubRegion {subregion.id}"
                return (-subregion.favorite_count, korean_name)

            sorted_subregions = sorted(subregions, key=sort_key)
            serializer = SubRegionListSerializer(
                sorted_subregions,
                many=True,
                context={"lang": lang}
            )

            return Response(
                {"subregions": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": "서브지역 목록 조회 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubRegionDetailAPI(APIView):
    def get(self, request, subregion_id):
        lang = request.query_params.get("lang", "ko")
        supported_languages = ["ko", "en", "jp", "cn"]
        if lang not in supported_languages:
            return Response(
                {"error": f"지원하지 않는 언어입니다. 지원 언어: {', '.join(supported_languages)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subregion = get_object_or_404(SubRegion, id=subregion_id)
            serializer = SubRegionSerializer(
                subregion,
                context={"lang": lang}
            )

            return Response(
                {"subregion": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": "서브지역 상세 정보 조회 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DefaultRegionAPI(APIView):
    def get(self, request):
        lang = request.query_params.get("lang", "ko")
        supported_languages = ["ko", "en", "jp", "cn"]
        if lang not in supported_languages:
            return Response(
                {"error": f"지원하지 않는 언어입니다. 지원 언어: {', '.join(supported_languages)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            seoul_region = None
            regions = Region.objects.all()

            for region in regions:
                if region.get_name("ko") == "서울":
                    seoul_region = region
                    break

            if not seoul_region:
                return Response(
                    {"error": "기본 지역(서울)을 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = RegionDetailSerializer(
                seoul_region,
                context={"lang": lang}
            )

            return Response(
                {"region": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": "기본 지역 조회 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AllSubRegionsAPI(APIView):
    def get(self, request):
        lang = request.query_params.get("lang", "ko")
        region_id = request.query_params.get("region_id")
        supported_languages = ["ko", "en", "jp", "cn"]
        if lang not in supported_languages:
            return Response(
                {"error": f"지원하지 않는 언어입니다. 지원 언어: {', '.join(supported_languages)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subregions_queryset = SubRegion.objects.select_related().prefetch_related(
                'translations'
            ).all()

            if region_id:
                region = get_object_or_404(Region, id=region_id)
                subregions_queryset = subregions_queryset.filter(region=region)
            def sort_key(subregion):
                korean_name = subregion.get_name("ko") or f"SubRegion {subregion.id}"
                return (-subregion.favorite_count, korean_name)

            sorted_subregions = sorted(subregions_queryset, key=sort_key)

            serializer = SubRegionListSerializer(
                sorted_subregions,
                many=True,
                context={"lang": lang}
            )

            return Response(
                {"subregions": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": "서브지역 목록 조회 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
