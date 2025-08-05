from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from places.models import Place


def is_same_location_gis(point1, point2, threshold_meters=100):
    """
    GIS로 두 좌표가 같은 장소인지 판별

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
        # EPSG:5179 (Korea 2000 / Unified CS) - 한국 전용 미터 좌표계
        point1_meter = point1.transform(5179, clone=True)
        point2_meter = point2.transform(5179, clone=True)
        distance_meters = point1_meter.distance(point2_meter)
        return distance_meters <= threshold_meters

    except Exception:
        # 좌표계 변환 실패 시 근사 계산
        lat_diff = abs(point1.y - point2.y) * 111000
        lng_diff = abs(point1.x - point2.x) * 111000 * 0.88
        approximate_distance = (lat_diff ** 2 + lng_diff ** 2) ** 0.5
        return approximate_distance <= threshold_meters


def find_closest_place_gis(lat, lng, threshold_meters=100):
    """
    가장 가까운 기존 관광지 찾기

    Args:
        lat (float): 위도
        lng (float): 경도
        threshold_meters (int): 검색 반경 (미터 단위, 기본값 100m)

    Returns:
        Place: 가장 가까운 관광지 객체 (없으면 None)
    """
    if not lat or not lng:
        return None

    try:
        search_point = Point(lng, lat)
        nearby_places = Place.objects.filter(
            location__dwithin=(search_point, D(m=threshold_meters))
        ).order_by(search_point.distance("location"))

        return nearby_places.first() if nearby_places.exists() else None

    except Exception:
        # GIS 검색 실패 시 전체 관광지와 거리 비교
        search_point = Point(lng, lat)
        min_distance = float("inf")
        closest_place = None

        for place in Place.objects.filter(location__isnull=False):
            if place.location and is_same_location_gis(search_point, place.location, threshold_meters):
                distance = abs(search_point.y - place.location.y) + abs(search_point.x - place.location.x)
                if distance < min_distance:
                    min_distance = distance
                    closest_place = place

        return closest_place


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
        return Point(lng, lat)

    total_lat = sum(coord[0] for coord in coordinates_list)
    total_lng = sum(coord[1] for coord in coordinates_list)
    avg_lat = total_lat / len(coordinates_list)
    avg_lng = total_lng / len(coordinates_list)

    return Point(avg_lng, avg_lat)


def get_coordinates_from_place(place):
    """
    Place 객체에서 위도/경도 추출

    Args:
        place (Place): 관광지 객체

    Returns:
        tuple: (위도, 경도) 또는 (None, None)
    """
    if place and place.location:
        return place.location.y, place.location.x
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
    if lat and lng:
        return Point(lng, lat)
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
    return find_closest_place_gis(lat, lng, threshold_meters)


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
        if translation.place and translation.place.location:
            lat, lng = get_coordinates_from_place(translation.place)
            if lat and lng:
                coordinates.append((lat, lng))

    return calculate_center_point(coordinates)
