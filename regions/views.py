from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from regions.models import Region, SubRegion
from regions.serializers import RegionSerializer, SubRegionSerializer
from utils.pagination.custom_pagination import CustomPagination


class RegionsListAPI(APIView):
   permission_classes = [AllowAny]

   @swagger_auto_schema(
       operation_summary="지역 목록 조회",
       operation_description="전체 지역 목록을 조회합니다.",
       manual_parameters=[
           openapi.Parameter(
               "lang",
               openapi.IN_QUERY,
               description="언어 코드 (기본값: ko)",
               type=openapi.TYPE_STRING,
               default="ko",
               enum=["ko", "en", "jp", "cn"]
           )
       ],
       responses={
           200: openapi.Response(
               description="지역 목록 조회 성공",
               schema=openapi.Schema(
                   type=openapi.TYPE_OBJECT,
                   properties={
                       "regions": openapi.Schema(
                           type=openapi.TYPE_ARRAY,
                           items=openapi.Schema(
                               type=openapi.TYPE_OBJECT,
                               properties={
                                   "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID"),
                                   "name": openapi.Schema(type=openapi.TYPE_STRING, description="지역명"),
                                   "description": openapi.Schema(type=openapi.TYPE_STRING, description="지역 설명"),
                                   "feature": openapi.Schema(type=openapi.TYPE_STRING, description="지역 특징"),
                                   "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="생성일"),
                                   "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="수정일"),
                               }
                           )
                       )
                   }
               )
           )
       },
       tags=["지역"]
   )

   def get(self, request):
       language = request.query_params.get("lang", "ko")

       regions = Region.objects.all().order_by("id")

       serializer = RegionSerializer(
           regions,
           many=True,
           context={"language": language}
       )

       return Response({
           "regions": serializer.data
       }, status=status.HTTP_200_OK)


class MajorRegionListAPI(APIView):
   permission_classes = [AllowAny]

   @swagger_auto_schema(
       operation_summary="주요 지역 목록 조회",
       operation_description="주요 지역 목록을 조회합니다. (ID: 1, 9, 6, 17)",
       manual_parameters=[
           openapi.Parameter(
               "lang",
               openapi.IN_QUERY,
               description="언어 코드 (기본값: ko)",
               type=openapi.TYPE_STRING,
               default="ko",
               enum=["ko", "en", "jp", "cn"]
           )
       ],
       responses={
           200: openapi.Response(
               description="주요 지역 목록 조회 성공",
               schema=openapi.Schema(
                   type=openapi.TYPE_OBJECT,
                   properties={
                       "regions": openapi.Schema(
                           type=openapi.TYPE_ARRAY,
                           items=openapi.Schema(
                               type=openapi.TYPE_OBJECT,
                               properties={
                                   "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID"),
                                   "name": openapi.Schema(type=openapi.TYPE_STRING, description="지역명"),
                                   "description": openapi.Schema(type=openapi.TYPE_STRING, description="지역 설명"),
                                   "feature": openapi.Schema(type=openapi.TYPE_STRING, description="지역 특징"),
                                   "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="생성일"),
                                   "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="수정일"),
                               }
                           )
                       )
                   }
               )
           )
       },
       tags=["지역"]
   )

   def get(self, request):
       language = request.query_params.get("lang", "ko")

       major_region_ids = [1, 9, 6, 17]
       majorregions = Region.objects.filter(id__in=major_region_ids)

       serializer = RegionSerializer(
           majorregions,
           many=True,
           context={"language": language}
       )

       return Response({
           "regions": serializer.data
       }, status=status.HTTP_200_OK)


class RegionDetailAPI(APIView):
   permission_classes = [AllowAny]
   pagination_class = CustomPagination

   @swagger_auto_schema(
       operation_summary="지역 상세 정보 조회",
       operation_description="특정 지역의 상세 정보와 하위 지역(서브리전) 목록을 조회합니다.",
       manual_parameters=[
           openapi.Parameter(
               "lang",
               openapi.IN_QUERY,
               description="언어 코드 (기본값: ko)",
               type=openapi.TYPE_STRING,
               default="ko",
               enum=["ko", "en", "jp", "cn"]
           ),
           openapi.Parameter(
               "region_id",
               openapi.IN_PATH,
               description="지역 ID",
               type=openapi.TYPE_INTEGER,
               required=True
           ),
           openapi.Parameter(
               "page",
               openapi.IN_QUERY,
               description="페이지 번호 (기본값: 1)",
               type=openapi.TYPE_INTEGER,
               default=1
           ),
           openapi.Parameter(
               "page_size",
               openapi.IN_QUERY,
               description="페이지당 항목 수",
               type=openapi.TYPE_INTEGER,
           )
       ],
       responses={
           200: openapi.Response(
               description="지역 상세 정보 조회 성공",
               schema=openapi.Schema(
                   type=openapi.TYPE_OBJECT,
                   properties={
                       "regions": openapi.Schema(
                           type=openapi.TYPE_OBJECT,
                           properties={
                               "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="지역 ID"),
                               "name": openapi.Schema(type=openapi.TYPE_STRING, description="지역명"),
                               "description": openapi.Schema(type=openapi.TYPE_STRING, description="지역 설명"),
                               "feature": openapi.Schema(type=openapi.TYPE_STRING, description="지역 특징"),
                               "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="생성일"),
                               "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="수정일"),
                               "subregions": openapi.Schema(
                                   type=openapi.TYPE_OBJECT,
                                   properties={
                                       "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="총 서브리전 수"),
                                       "total_pages": openapi.Schema(type=openapi.TYPE_INTEGER, description="총 페이지 수"),
                                       "page": openapi.Schema(type=openapi.TYPE_INTEGER, description="현재 페이지"),
                                       "page_size": openapi.Schema(type=openapi.TYPE_INTEGER, description="페이지 크기"),
                                       "results": openapi.Schema(
                                           type=openapi.TYPE_ARRAY,
                                           items=openapi.Schema(
                                               type=openapi.TYPE_OBJECT,
                                               properties={
                                                   "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="서브리전 ID"),
                                                   "name": openapi.Schema(type=openapi.TYPE_STRING, description="서브리전명"),
                                                   "description": openapi.Schema(type=openapi.TYPE_STRING, description="서브리전 설명"),
                                                   "feature": openapi.Schema(type=openapi.TYPE_STRING, description="서브리전 특징"),
                                                   "favorite_count": openapi.Schema(type=openapi.TYPE_INTEGER, description="즐겨찾기 수"),
                                                   "latitude": openapi.Schema(type=openapi.TYPE_NUMBER, description="위도"),
                                                   "longitude": openapi.Schema(type=openapi.TYPE_NUMBER, description="경도"),
                                               }
                                           )
                                       )
                                   }
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
                       "detail": openapi.Schema(type=openapi.TYPE_STRING, description="오류 메시지")
                   }
               )
           )
       },
       tags=["지역"]
   )

   def get(self, request, region_id):
       language = request.query_params.get("lang", "ko")
       region = get_object_or_404(Region, id=region_id)
       subregions = SubRegion.objects.filter(region=region).order_by("id").prefetch_related("translations")

       paginator = self.pagination_class()
       paginated_subregions = paginator.paginate_queryset(subregions, request)

       subregions_serializer = SubRegionSerializer(
           paginated_subregions,
           many=True,
           context={"language": language}
       )

       region_serializer = RegionSerializer(
           region,
           context={"language": language}
       )

       region_data = region_serializer.data
       region_data["subregions"] = paginator.get_paginated_response(subregions_serializer.data).data

       return Response({
           "regions": region_data
       }, status=status.HTTP_200_OK)
