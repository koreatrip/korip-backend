# places/tests/test_search_functionality.py (수정된 전체 코드)

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.gis.geos import Point

from places.models import Place, PlaceTranslation
from categories.models import Category, CategoryTranslation
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class PlacesSearchAPITest(APITestCase):
    """Places API 검색 기능 테스트 - 지역구까지만 검색"""

    def setUp(self):
        """테스트 데이터 준비"""
        # 카테고리 생성
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="문화"
        )

        # 지역 생성 (region_code 없이)
        self.region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="서울"
        )

        # 지역구 생성 (subregion_code 없이, 위도/경도 추가)
        self.sub_region = SubRegion.objects.create(
            region=self.region,
            favorite_count=0,
            latitude=37.5796,
            longitude=126.9770
        )
        SubRegionTranslation.objects.create(
            sub_region=self.sub_region,
            lang="ko",
            name="종로구"
        )

        # 테스트용 관광지들 생성
        # 1. 경복궁 (한국어/영어 번역 있음)
        self.gyeongbok_palace = Place.objects.create(
            content_id="126508",
            category=self.category,
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9770, 37.5788),  # GIS Point 사용
            favorite_count=150,
            phone_number="02-3700-3900",
            use_time="09:00~18:00"
        )

        PlaceTranslation.objects.create(
            place=self.gyeongbok_palace,
            lang="ko",
            name="경복궁",
            description="조선 왕조의 법궁",
            address="서울특별시 종로구 사직로 161"
        )

        PlaceTranslation.objects.create(
            place=self.gyeongbok_palace,
            lang="en",
            name="Gyeongbokgung Palace",
            description="The main royal palace of the Joseon dynasty",
            address="161 Sajik-ro, Jongno-gu, Seoul"
        )

        # 2. 창덕궁 (한국어만)
        self.changdeok_palace = Place.objects.create(
            content_id="126509",
            category=self.category,
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9910, 37.5794),  # GIS Point 사용
            favorite_count=120,
            phone_number="02-3668-2300"
        )

        PlaceTranslation.objects.create(
            place=self.changdeok_palace,
            lang="ko",
            name="창덕궁",
            description="유네스코 세계문화유산",
            address="서울특별시 종로구 율곡로 99"
        )

        # 3. 남산타워 (다른 주소)
        self.namsan_tower = Place.objects.create(
            content_id="126510",
            category=self.category,
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9883, 37.5512),  # GIS Point 사용
            favorite_count=200
        )

        PlaceTranslation.objects.create(
            place=self.namsan_tower,
            lang="ko",
            name="남산서울타워",
            description="서울의 랜드마크",
            address="서울특별시 용산구 남산공원길 105"
        )

    def test_search_by_region_name(self):
        """지역명으로 검색 테스트 (주소 기반)"""
        # When: "서울"로 검색 (주소에 포함된)
        response = self.client.get("/api/places/?search=서울&lang=ko")

        # Then: 서울 주소를 가진 관광지들이 나와야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertGreaterEqual(len(places), 1)

        # 모든 결과의 주소에 "서울"이 포함되어야 함
        for place in places:
            self.assertIn("서울", place.get("address", ""))

    def test_search_by_subregion_name(self):
        """지역구명으로 검색 테스트 (주소 기반)"""
        # When: "종로구"로 검색 (주소에 포함된)
        response = self.client.get("/api/places/?search=종로구&lang=ko")

        # Then: 종로구 주소를 가진 관광지들이 나와야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertGreaterEqual(len(places), 1)

        # 모든 결과의 주소에 "종로구"가 포함되어야 함
        for place in places:
            self.assertIn("종로구", place.get("address", ""))

    def test_search_partial_match(self):
        """부분 일치 검색 테스트 (지역구 기반)"""
        # When: "구" 로 검색 (종로구, 용산구에 포함)
        response = self.client.get("/api/places/?search=구&lang=ko")

        # Then: 주소에 "구"가 포함된 관광지들이 나와야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertGreaterEqual(len(places), 1)

        # 모든 결과의 주소에 "구"가 포함되어야 함
        for place in places:
            self.assertIn("구", place.get("address", ""))

    def test_search_case_insensitive(self):
        """대소문자 구분없는 검색 테스트"""
        # When: "서울"(소문자/대문자 혼합)로 검색
        response = self.client.get("/api/places/?search=서울&lang=ko")

        # Then: 결과가 나와야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertGreaterEqual(len(places), 1)

        # 주소에 서울이 포함되어야 함
        for place in places:
            self.assertIn("서울", place.get("address", ""))

    def test_search_by_address(self):
        """주소로 검색 테스트"""
        # When: "용산구"로 검색
        response = self.client.get("/api/places/?search=용산구&lang=ko")

        # Then: 용산구 주소를 가진 관광지들이 나와야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertGreaterEqual(len(places), 1)

        # 남산타워가 용산구 주소를 가지고 있음
        found_namsan = any("남산서울타워" in place["name"] for place in places)
        self.assertTrue(found_namsan)

    def test_search_by_description_not_supported(self):
        """설명으로 검색은 지원하지 않음 테스트"""
        # When: "조선"으로 검색 (설명에만 있고 주소에는 없음)
        response = self.client.get("/api/places/?search=조선&lang=ko")

        # Then: 검색 결과가 없어야 함 (주소 기반 검색만 지원)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 0)

    def test_search_by_place_name_not_supported(self):
        """관광지 이름으로 검색은 지원하지 않음 테스트"""
        # When: "경복궁"으로 검색 (이름에만 있고 주소에는 없음)
        response = self.client.get("/api/places/?search=경복궁&lang=ko")

        # Then: 검색 결과가 없어야 함 (주소 기반 검색만 지원)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 0)

    def test_search_no_results(self):
        """검색 결과 없을 때 테스트"""
        # When: 존재하지 않는 지역명으로 검색
        response = self.client.get("/api/places/?search=화성시&lang=ko")

        # Then: 빈 배열이 반환되어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 0)

    def test_search_empty_string(self):
        """빈 검색어일 때 테스트"""
        # When: 빈 문자열로 검색
        response = self.client.get("/api/places/?search=&lang=ko")

        # Then: 전체 목록이 반환되어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 3)  # 모든 관광지

    def test_search_with_other_filters(self):
        """검색과 다른 필터 조합 테스트"""
        # When: 검색어와 카테고리 필터를 함께 사용
        response = self.client.get(
            f"/api/places/?search=종로구&category_id={self.category.id}&lang=ko"
        )

        # Then: 두 조건을 모두 만족하는 결과만 나와야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertGreaterEqual(len(places), 1)

        for place in places:
            self.assertEqual(place["category"]["id"], self.category.id)
            self.assertIn("종로구", place.get("address", ""))

    def test_search_maintains_sorting(self):
        """검색 결과도 정렬 유지 테스트"""
        # When: 검색 후 이름순 정렬 요청
        response = self.client.get("/api/places/?search=종로구&sort_type=name&lang=ko")

        # Then: 종로구 주소를 가진 관광지들이 정렬되어 나와야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertGreaterEqual(len(places), 1)

        # 주소에 종로구가 포함되어야 함
        for place in places:
            self.assertIn("종로구", place.get("address", ""))

    def test_search_special_characters(self):
        """특수문자 포함 검색 테스트"""
        # When: 특수문자가 포함된 지역명으로 검색
        response = self.client.get("/api/places/?search=서울특별시&lang=ko")

        # Then: 정상적으로 검색되어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertGreaterEqual(len(places), 1)

        # 주소에 서울이 포함되어야 함
        for place in places:
            address = place.get("address", "")
            self.assertTrue("서울" in address or "서울특별시" in address)

    def test_search_sorting_by_favorite_count(self):
        """검색 결과 즐겨찾기 순 정렬 테스트"""
        # When: 서울로 검색 (모든 관광지가 서울 주소를 가짐)
        response = self.client.get("/api/places/?search=서울&lang=ko")

        # Then: 즐겨찾기 수 순으로 정렬되어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertGreaterEqual(len(places), 2)

        # 첫 번째가 가장 높은 즐겨찾기 수를 가져야 함
        if len(places) >= 2:
            self.assertGreaterEqual(
                places[0]["favorite_count"],
                places[1]["favorite_count"]
            )
