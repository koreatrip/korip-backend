# GIS 기반 관광지 좌표 매칭 유틸리티 (수정 버전)

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from places.models import Place
import logging

logger = logging.getLogger(__name__)


def is_same_location_gis(point1, point2, threshold_meters=100):
    """
    간단한 거리 계산으로 두 좌표가 같은 장소인지 판별 (PostGIS 없이)

    Args:
        point1 (Point): 첫 번째 좌표
        point2 (Point): 두 번째 좌표
        threshold_meters (int): 임계값 (미터 단위, 기본값 100m)

    Returns:
        bool: 같은 장소면 True, 다른 장소면 False
    """
    if not point1 or not point2:
        return False

    try:
        # PostGIS transform 대신 간단한 거리 계산 (한국 기준)
        lat_diff = abs(point1.y - point2.y) * 111000  # 위도 1도 ≈ 111km
        lng_diff = abs(point1.x - point2.x) * 88000  # 경도 1도 ≈ 88km (한국 위도 보정)
        approximate_distance = (lat_diff ** 2 + lng_diff ** 2) ** 0.5

        logger.debug(f"거리 계산: {approximate_distance:.1f}m")
        return approximate_distance <= threshold_meters

    except Exception as e:
        logger.warning(f"거리 계산 실패: {e}")
        return False


def find_closest_place_gis(lat, lng, threshold_meters=100):
    """
    가장 가까운 기존 관광지 찾기 (완전 간단한 방식)

    Args:
        lat (float): 위도
        lng (float): 경도
        threshold_meters (int): 검색 반경 (미터 단위, 기본값 100m)

    Returns:
        Place: 가장 가까운 관광지 객체 (없으면 None)
    """
    if not lat or not lng:
        logger.warning("위도 또는 경도가 없음")
        return None

    logger.debug(f"검색 좌표: lat={lat}, lng={lng}, 반경={threshold_meters}m")

    try:
        # 모든 관광지를 가져와서 Python으로 거리 계산
        places_with_location = Place.objects.filter(location__isnull=False)
        logger.debug(f"전체 관광지 수: {places_with_location.count()}개")

        min_distance_meters = float("inf")
        closest_place = None

        for place in places_with_location:
            try:
                if place.location:
                    # Python으로 거리 계산
                    place_lat = place.location.y
                    place_lng = place.location.x

                    # 위도/경도 차이를 미터로 변환
                    lat_diff_meters = abs(lat - place_lat) * 111000  # 위도 1도 ≈ 111km
                    lng_diff_meters = abs(lng - place_lng) * 88000  # 경도 1도 ≈ 88km (한국)

                    # 직선 거리 계산 (피타고라스)
                    distance_meters = (lat_diff_meters ** 2 + lng_diff_meters ** 2) ** 0.5

                    logger.debug(f"관광지 {place.id}: 거리 {distance_meters:.1f}m")

                    # 임계값 내에서 가장 가까운 곳 찾기
                    if distance_meters <= threshold_meters and distance_meters < min_distance_meters:
                        min_distance_meters = distance_meters
                        closest_place = place
                        logger.debug(f"  → 새로운 최단거리: {distance_meters:.1f}m")

            except Exception as place_error:
                logger.warning(f"관광지 {place.id} 처리 실패: {place_error}")
                continue

        if closest_place:
            logger.info(f"매칭 성공! 관광지 {closest_place.id}, 거리: {min_distance_meters:.1f}m")
            return closest_place
        else:
            logger.info(f"반경 {threshold_meters}m 내 관광지 없음")
            return None

    except Exception as e:
        logger.error(f"전체 검색 실패: {e}")
        return None


def calculate_center_point(coordinates_list):
    """
    여러 좌표의 중심점 계산

    Args:
        coordinates_list (list): [(위도, 경도), ...] 형태의 좌표 리스트

    Returns:
        Point: 중심점 (Django GIS Point 객체), 빈 리스트면 None
    """
    if not coordinates_list:
        return None

    if len(coordinates_list) == 1:
        lat, lng = coordinates_list[0]
        return Point(lng, lat, srid=4326)  # SRID 명시

    total_lat = sum(coord[0] for coord in coordinates_list)
    total_lng = sum(coord[1] for coord in coordinates_list)
    avg_lat = total_lat / len(coordinates_list)
    avg_lng = total_lng / len(coordinates_list)

    return Point(avg_lng, avg_lat, srid=4326)  # SRID 명시


def get_coordinates_from_place(place):
    """
    Place 객체에서 위도/경도 추출

    Args:
        place (Place): 관광지 객체

    Returns:
        tuple: (위도, 경도) 또는 (None, None)
    """
    try:
        if place and place.location:
            return place.location.y, place.location.x
        return None, None
    except Exception as e:
        logger.warning(f"좌표 추출 실패: {e}")
        return None, None


def create_point_from_coordinates(lat, lng):
    """
    위도/경도에서 Django GIS Point 객체 생성

    Args:
        lat (float): 위도
        lng (float): 경도

    Returns:
        Point: Django GIS Point 객체
    """
    try:
        if lat and lng:
            return Point(lng, lat, srid=4326)  # SRID 명시
        return None
    except Exception as e:
        logger.warning(f"Point 생성 실패: {e}")
        return None


def find_matching_place_by_gis(lat, lng, threshold_meters=100):
    """
    다국어 동기화에서 사용할 GIS 기반 기존 관광지 찾기

    Args:
        lat (float): 위도
        lng (float): 경도
        threshold_meters (int): 검색 반경 (미터)

    Returns:
        Place: 매칭되는 기존 관광지 (없으면 None)
    """
    logger.info(f"GIS 매칭 시작: lat={lat}, lng={lng}, 반경={threshold_meters}m")
    result = find_closest_place_gis(lat, lng, threshold_meters)

    if result:
        logger.info(f"매칭 성공: Place ID {result.id}")
    else:
        logger.info("매칭 실패: 새로운 관광지로 생성 필요")

    return result


def calculate_optimal_location(place_translations):
    """
    다국어 관광지들의 최적 위치 계산

    Args:
        place_translations (list): PlaceTranslation 객체들의 리스트

    Returns:
        Point: 최적 위치 (중심점)
    """
    coordinates = []

    for translation in place_translations:
        try:
            if translation.place and translation.place.location:
                lat, lng = get_coordinates_from_place(translation.place)
                if lat and lng:
                    coordinates.append((lat, lng))
        except Exception as e:
            logger.warning(f"번역 {translation.id} 좌표 추출 실패: {e}")
            continue

    if coordinates:
        logger.info(f"{len(coordinates)}개 좌표로 중심점 계산")
        return calculate_center_point(coordinates)
    else:
        logger.warning("유효한 좌표가 없어 중심점 계산 불가")
        return None


# 디버깅용 함수 추가
def debug_gis_search(lat, lng, threshold_meters=100):
    """
    간단한 거리 계산 디버깅용 함수

    Args:
        lat (float): 위도
        lng (float): 경도
        threshold_meters (int): 검색 반경

    Returns:
        dict: 디버깅 정보
    """
    logger.info("=== 간단한 거리 계산 디버깅 시작 ===")

    try:
        # 전체 관광지 수 확인
        total_places = Place.objects.filter(location__isnull=False).count()
        logger.info(f"전체 관광지 수: {total_places}개")
        logger.info(f"검색 좌표: lat={lat}, lng={lng}")
        logger.info(f"검색 반경: {threshold_meters}m")

        # 모든 관광지와의 거리 계산
        nearby_places = []
        all_places = Place.objects.filter(location__isnull=False)

        for place in all_places:
            if place.location:
                place_lat = place.location.y
                place_lng = place.location.x

                # 거리 계산
                lat_diff_meters = abs(lat - place_lat) * 111000  # 위도 1도 ≈ 111km
                lng_diff_meters = abs(lng - place_lng) * 88000  # 경도 1도 ≈ 88km (한국)
                distance_meters = (lat_diff_meters ** 2 + lng_diff_meters ** 2) ** 0.5

                # 반경 내 관광지만 수집
                if distance_meters <= threshold_meters:
                    nearby_places.append({
                        "id": place.id,
                        "distance_meters": round(distance_meters, 1),
                        "lat": place_lat,
                        "lng": place_lng
                    })

        # 거리순 정렬
        nearby_places.sort(key=lambda x: x["distance_meters"])

        logger.info(f"반경 {threshold_meters}m 내 관광지: {len(nearby_places)}개")

        # 가장 가까운 3개 출력
        for i, place_info in enumerate(nearby_places[:3]):
            logger.info(
                f"#{i + 1} 관광지 {place_info['id']}: {place_info['distance_meters']}m, 좌표({place_info['lat']:.6f}, {place_info['lng']:.6f})")

        return {
            "total_places": total_places,
            "nearby_count": len(nearby_places),
            "closest_places": nearby_places[:5]  # 상위 5개만 반환
        }

    except Exception as e:
        logger.error(f"디버깅 실패: {e}")
        return {"error": str(e)}
