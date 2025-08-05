# places/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from places.models import Place
from places.serializers import PlaceSerializer


class PlacesListAPI(APIView):
    """관광지 목록 조회 API - 지역구까지만 검색 지원"""

    def get(self, request):
        # 언어 설정 (기본값: 한국어)
        language = request.query_params.get("lang", "ko")

        # 기본 쿼리셋
        queryset = Place.objects.all()

        # 🔍 검색 기능 - 지역/지역구만 검색 (주소 기반)
        search = request.query_params.get("search")
        if search:
            # 주소에서만 검색 (지역명, 지역구명 포함)
            # 관광지 이름이나 설명은 검색하지 않음 (나중에 Elasticsearch로 구현 예정)
            queryset = queryset.filter(
                Q(translations__address__icontains=search)  # 주소에서만 검색
            ).distinct()  # 중복 제거

        # 카테고리 필터링
        category_id = request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category=category_id)

        # 지역 필터링
        region_id = request.query_params.get("region_id")
        if region_id:
            queryset = queryset.filter(region=region_id)

        # 지역구 필터링 (가장 효율적인 검색)
        subregion_id = request.query_params.get("subregion_id")
        if subregion_id:
            queryset = queryset.filter(sub_region=subregion_id)

        # 정렬 옵션 처리
        sort_type = request.query_params.get("sort_type", "favorite")

        if sort_type == "name":
            # 이름순 정렬: 한국어 번역 기준
            # 현재는 단순하게 ID 순으로 정렬 (나중에 개선 가능)
            queryset = queryset.order_by("id")
        else:
            # 기본 정렬: 즐겨찾기 수 높은 순 → 생성일 최신순
            queryset = queryset.order_by("-favorite_count", "-created_at")

        # 🚀 성능 최적화: 페이지네이션 추가 (선택사항)
        # 한 번에 너무 많은 데이터를 조회하지 않도록
        limit = request.query_params.get("limit")
        if limit:
            try:
                limit = int(limit)
                offset = int(request.query_params.get("offset", 0))

                total_count = queryset.count()
                queryset = queryset[offset:offset + limit]

                # 페이지네이션 정보 포함한 응답
                serializer = PlaceSerializer(
                    queryset,
                    many=True,
                    context={"language": language}
                )

                return Response({
                    "places": serializer.data,
                    "total_count": total_count,
                    "has_more": offset + limit < total_count,
                    "offset": offset,
                    "limit": limit
                }, status=status.HTTP_200_OK)

            except (ValueError, TypeError):
                # limit이나 offset이 잘못된 경우 무시하고 전체 조회
                pass

        # 기본 응답 (페이지네이션 없음)
        serializer = PlaceSerializer(
            queryset,
            many=True,
            context={"language": language}
        )

        return Response({
            "places": serializer.data
        }, status=status.HTTP_200_OK)


class UserFavoritePlacesAPI(APIView):
    """사용자별 즐겨찾기 관광지 목록 조회 API"""

    def get(self, request, user_id):
        language = request.query_params.get("lang", "ko")

        # UserFavoritePlace 모델을 통해 사용자가 즐겨찾기한 관광지들만 조회
        try:
            from accounts.models import UserFavoritePlace

            # 사용자가 즐겨찾기한 관광지 ID들 가져오기
            favorite_place_ids = UserFavoritePlace.objects.filter(
                user_id=user_id
            ).values_list('place_id', flat=True)

            # 해당 관광지들 조회
            queryset = Place.objects.filter(id__in=favorite_place_ids)

            # 정렬: 즐겨찾기 추가한 순서 (최신순)
            queryset = queryset.order_by("-created_at")

            serializer = PlaceSerializer(
                queryset,
                many=True,
                context={"language": language}
            )

            return Response({
                "places": serializer.data,
                "user_id": user_id,
                "total_count": len(serializer.data)
            }, status=status.HTTP_200_OK)

        except ImportError:
            # UserFavoritePlace 모델이 없는 경우
            return Response({
                "error": "UserFavoritePlace 모델이 구현되지 않았습니다.",
                "places": []
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"즐겨찾기 조회 중 오류가 발생했습니다: {str(e)}",
                "places": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlaceDetailAPI(APIView):
    """관광지 상세 조회 API"""

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
    """지역구별 관광지 목록 조회 API - 가장 효율적인 조회 방식"""

    def get(self, request, subregion_id):
        language = request.query_params.get("lang", "ko")

        # 정렬 방식 파라미터 (기본값: favorite)
        sort_type = request.query_params.get("sort_type", "favorite")

        # 지역구별 관광지 필터링 (인덱스 활용 가능)
        queryset = Place.objects.filter(sub_region=subregion_id)

        # 정렬 처리
        if sort_type == "name":
            # 이름순 정렬은 한국어 번역 기준 (복잡하므로 기본 정렬 사용)
            queryset = queryset.order_by("id")
        else:
            # 즐겨찾기 수 높은 순 → 생성일 최신순
            queryset = queryset.order_by("-favorite_count", "-created_at")

        serializer = PlaceSerializer(
            queryset,
            many=True,
            context={"language": language}
        )

        return Response({
            "places": serializer.data
        }, status=status.HTTP_200_OK)
    