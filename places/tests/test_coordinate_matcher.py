# places/tests/test_coordinate_matcher.py

from django.test import TestCase
from django.contrib.gis.geos import Point
from places.utils.coordinate_matcher import (
    is_same_location_gis,
    find_closest_place_gis,
    calculate_center_point
)
from places.models import Place


class CoordinateMatcherTest(TestCase):
    def setUp(self):
        self.gyeongbok_palace = Place.objects.create(
            content_id="test_gyeongbok",
            location=Point(126.9770, 37.5796),
            phone_number="02-3700-3900"
        )

        self.changdeok_palace = Place.objects.create(
            content_id="test_changdeok",
            location=Point(126.9910, 37.5794),
            phone_number="02-3668-2300"
        )

    def test_is_same_location_gis_within_100m(self):
        """100m 이내 좌표는 같은 장소로 판별해야 함"""
        point1 = Point(126.9770, 37.5796)
        point2 = Point(126.9775, 37.5797)

        result = is_same_location_gis(point1, point2, threshold_meters=100)
        self.assertTrue(result, "100m 이내 좌표는 같은 장소로 판별되어야 함")

    def test_is_same_location_gis_beyond_100m(self):
        """100m 초과 좌표는 다른 장소로 판별해야 함"""
        point1 = Point(126.9770, 37.5796)
        point2 = Point(126.9910, 37.5794)

        result = is_same_location_gis(point1, point2, threshold_meters=100)
        self.assertFalse(result, "100m 초과 좌표는 다른 장소로 판별되어야 함")

    def test_find_closest_place_gis_exists(self):
        """가까운 기존 관광지를 찾아야 함"""
        lat, lng = 37.5797, 126.9771

        closest_place = find_closest_place_gis(lat, lng)

        self.assertIsNotNone(closest_place, "가까운 관광지를 찾아야 함")
        self.assertEqual(closest_place.content_id, "test_gyeongbok")

    def test_find_closest_place_gis_not_exists(self):
        """100m 이내에 기존 관광지가 없으면 None 반환"""
        lat, lng = 37.5145, 127.0559

        closest_place = find_closest_place_gis(lat, lng)

        self.assertIsNone(closest_place, "100m 이내에 관광지가 없으면 None을 반환해야 함")

    def test_calculate_center_point(self):
        """여러 좌표의 중심점을 계산해야 함"""
        coordinates_list = [
            (37.5796, 126.9770),
            (37.5795, 126.9769),
            (37.5797, 126.9771),
            (37.5794, 126.9768),
        ]

        center_point = calculate_center_point(coordinates_list)

        self.assertIsInstance(center_point, Point)
        self.assertAlmostEqual(center_point.y, 37.5795, places=3)
        self.assertAlmostEqual(center_point.x, 126.9770, places=3)

    def test_calculate_center_point_empty_list(self):
        """빈 좌표 리스트면 None 반환"""
        coordinates_list = []

        center_point = calculate_center_point(coordinates_list)

        self.assertIsNone(center_point, "빈 리스트면 None을 반환해야 함")

    def test_calculate_center_point_single_coordinate(self):
        """좌표가 하나만 있으면 그 좌표를 반환"""
        coordinates_list = [(37.5796, 126.9770)]

        center_point = calculate_center_point(coordinates_list)

        self.assertEqual(center_point.y, 37.5796)
        self.assertEqual(center_point.x, 126.9770)

    def test_edge_case_none_coordinates(self):
        """None이나 빈 좌표 처리 테스트"""
        result = is_same_location_gis(None, Point(126.9770, 37.5796))
        self.assertFalse(result, "None 좌표는 False를 반환해야 함")

        closest_place = find_closest_place_gis(None, None)
        self.assertIsNone(closest_place, "None 좌표 검색은 None을 반환해야 함")

    def test_same_coordinates(self):
        """동일한 좌표는 같은 장소로 판별"""
        point1 = Point(126.9770, 37.5796)
        point2 = Point(126.9770, 37.5796)

        result = is_same_location_gis(point1, point2)
        self.assertTrue(result, "동일한 좌표는 같은 장소로 판별되어야 함")

    def test_multilang_scenario(self):
        """다국어 시나리오 통합 테스트"""
        korean_coords = (37.5796, 126.9770)
        english_coords = (37.5795, 126.9769)
        japanese_coords = (37.5797, 126.9771)
        chinese_coords = (37.5794, 126.9768)

        closest = find_closest_place_gis(*english_coords)
        self.assertEqual(closest.content_id, "test_gyeongbok")

        all_coords = [korean_coords, english_coords, japanese_coords, chinese_coords]
        center = calculate_center_point(all_coords)

        for coords in all_coords:
            coord_point = Point(coords[1], coords[0])
            self.assertTrue(
                is_same_location_gis(center, coord_point, threshold_meters=100),
                f"중심점이 좌표 {coords}와 100m 이내에 있어야 함"
            )
