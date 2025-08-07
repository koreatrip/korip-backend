from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from regions.models import Region, SubRegion
from regions.serializers import RegionSerializer, SubRegionSerializer


class RegionsListAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="지역 목록 조회",
        operation_description="전체 지역 목록을 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'lang',
                openapi.IN_QUERY,
                description="언어 코드 (기본값: ko)",
                type=openapi.TYPE_STRING,
                default='ko',
                enum=['ko', 'en']
            )
        ],
        responses={
            200: openapi.Response(
                description="지역 목록 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'regions': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='지역 ID'),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='지역명'),
                                    'name_en': openapi.Schema(type=openapi.TYPE_STRING, description='지역명 (영문)'),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='생성일'),
                                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='수정일'),
                                }
                            )
                        )
                    }
                )
            )
        },
        tags=['지역']
    )

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
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="지역 상세 정보 조회",
        operation_description="특정 지역의 상세 정보와 하위 지역(서브리전) 목록을 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'lang',
                openapi.IN_QUERY,
                description="언어 코드 (기본값: ko)",
                type=openapi.TYPE_STRING,
                default='ko',
                enum=['ko', 'en']
            ),
            openapi.Parameter(
                'region_id',
                openapi.IN_PATH,
                description="지역 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="지역 상세 정보 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'region': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='지역 ID'),
                                'name': openapi.Schema(type=openapi.TYPE_STRING, description='지역명'),
                                'name_en': openapi.Schema(type=openapi.TYPE_STRING, description='지역명 (영문)'),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='생성일'),
                                'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='수정일'),
                                'subregions': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='서브리전 ID'),
                                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='서브리전명'),
                                            'name_en': openapi.Schema(type=openapi.TYPE_STRING, description='서브리전명 (영문)'),
                                            'favorite_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='즐겨찾기 수'),
                                            'region': openapi.Schema(type=openapi.TYPE_INTEGER, description='상위 지역 ID'),
                                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='생성일'),
                                            'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='수정일'),
                                        }
                                    )
                                )
                            }
                        )
                    }
                )
            ),
            404: openapi.Response(
                description="지역을 찾을 수 없음",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='오류 메시지')
                    }
                )
            )
        },
        tags=['지역']
    )

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