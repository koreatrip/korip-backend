from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.gis.geos import Point

from places.models import Place, PlaceTranslation
from categories.models import Category, CategoryTranslation, SubCategory, SubCategoryTranslation
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


# === 라우팅 상수 (places/urls.py 기준) ===
BASE = "/api/places/"
PLACES_TOUR = BASE                                 # "" → PlaceTourListAPIView
PLACES_LIST = f"{BASE}test/"                       # "test/" → PlacesListAPIView
PLACES_DETAIL = BASE                               # "<int:place_id>/"
PLACES_BY_SUBREGION_BASE = f"{BASE}regions/"       # "regions/<int:subregion_id>/"
PLACES_BY_CATEGORY_BASE = f"{BASE}category/"       # "category/<int:category_id>/"


class PlacesAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create()
        CategoryTranslation.objects.create(category=self.category, lang="ko", name="문화")
        CategoryTranslation.objects.create(category=self.category, lang="en", name="Culture")

        self.sub_category = SubCategory.objects.create(category=self.category)
        SubCategoryTranslation.objects.create(sub_category=self.sub_category, lang="ko", name="궁궐")

        self.region = Region.objects.create()
        RegionTranslation.objects.create(region=self.region, lang="ko", name="서울")
        RegionTranslation.objects.create(region=self.region, lang="en", name="Seoul")

        self.sub_region = SubRegion.objects.create(
            region=self.region, favorite_count=100, location=Point(126.9770, 37.5796)
        )
        SubRegionTranslation.objects.create(sub_region=self.sub_region, lang="ko", name="종로구")

        self.place1 = Place.objects.create(
            content_id="12345",
            category=self.category,
            sub_category=self.sub_category,
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9770, 37.5796),
            phone_number="02-3700-3900",
            use_time="09:00~18:00",
            favorite_count=50,
        )
        self.place2 = Place.objects.create(
            content_id="67890",
            category=self.category,
            sub_category=self.sub_category,
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9779, 37.5658),
            phone_number="02-765-0195",
            use_time="09:00~17:00",
            favorite_count=30,
        )

        PlaceTranslation.objects.create(
            place=self.place1, lang="ko", name="경복궁", description="조선시대 궁궐", address="서울특별시 종로구 사직로 161"
        )
        PlaceTranslation.objects.create(
            place=self.place1, lang="en", name="Gyeongbokgung Palace",
            description="Joseon Dynasty Palace", address="161 Sajik-ro, Jongno-gu, Seoul"
        )
        PlaceTranslation.objects.create(
            place=self.place2, lang="ko", name="덕수궁", description="대한제국의 궁궐", address="서울특별시 중구 세종대로 99"
        )

    # ── PlacesListAPIView (/api/places/test/) ─────────────────────────────────────
    def test_places_list_api_success(self):
        resp = self.client.get(f"{PLACES_LIST}?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("places", resp.data)

        places = resp.data["places"]
        self.assertEqual(len(places), 2)

        first = places[0]
        self.assertEqual(first["content_id"], "12345")
        self.assertEqual(first["name"], "경복궁")
        self.assertEqual(first["description"], "조선시대 궁궐")
        self.assertIn("category", first)
        self.assertEqual(first["category"]["name"], "문화")
        self.assertIn("region", first)
        self.assertEqual(first["region"]["name"], "서울")

    def test_places_list_api_english(self):
        resp = self.client.get(f"{PLACES_LIST}?lang=en", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        places = resp.data["places"]

        first = places[0]
        self.assertEqual(first["name"], "Gyeongbokgung Palace")
        self.assertEqual(first["description"], "Joseon Dynasty Palace")
        self.assertEqual(first["category"]["name"], "Culture")
        self.assertEqual(first["region"]["name"], "Seoul")

    def test_places_ordering_by_favorite_count(self):
        resp = self.client.get(f"{PLACES_LIST}?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        places = resp.data["places"]
        self.assertGreaterEqual(places[0]["favorite_count"], places[1]["favorite_count"])

    def test_places_filter_by_category(self):
        resp = self.client.get(f"{PLACES_LIST}?category_id={self.category.id}&lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        places = resp.data["places"]
        self.assertEqual(len(places), 2)
        for p in places:
            self.assertEqual(p["category"]["id"], self.category.id)

    def test_places_filter_by_region(self):
        resp = self.client.get(f"{PLACES_LIST}?region_id={self.region.id}&lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        places = resp.data["places"]
        self.assertEqual(len(places), 2)
        for p in places:
            self.assertEqual(p["region"]["id"], self.region.id)

    def test_places_api_default_language(self):
        resp = self.client.get(PLACES_LIST, follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        places = resp.data["places"]
        self.assertEqual(places[0]["name"], "경복궁")

    def test_places_api_missing_translation(self):
        resp = self.client.get(f"{PLACES_LIST}?lang=jp", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        places = resp.data["places"]
        self.assertEqual(places[0]["name"], "")
        self.assertEqual(places[0]["description"], "")

    def test_places_api_pagination_like_bulk(self):
        # 리스트 엔드포인트는 페이지네이션 없음 → 추가 생성 후 총합 그대로 반환
        for i in range(10):
            p = Place.objects.create(
                content_id=f"test_{i}",
                favorite_count=i,
                region=self.region,
                sub_region=self.sub_region,
                location=Point(126.9700 + i * 0.001, 37.5700 + i * 0.001),
            )
            PlaceTranslation.objects.create(place=p, lang="ko", name=f"테스트 관광지 {i}")

        resp = self.client.get(f"{PLACES_LIST}?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["places"]), 12)

    def test_places_api_search_param_ignored_but_ok(self):
        # search 파라미터는 미지원이지만 200 및 내용 반환은 정상이어야 함
        resp = self.client.get(f"{PLACES_LIST}?search=경복궁&lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any("경복궁" in p["name"] for p in resp.data["places"]))

    def test_places_api_multiple_categories(self):
        category2 = Category.objects.create()
        CategoryTranslation.objects.create(category=category2, lang="ko", name="자연")

        nature_place = Place.objects.create(
            content_id="nature_001",
            category=category2,
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9800, 37.5500),
            favorite_count=20,
        )
        PlaceTranslation.objects.create(place=nature_place, lang="ko", name="남산공원", description="서울의 대표 공원")

        # 전체
        resp = self.client.get(f"{PLACES_LIST}?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["places"]), 3)

        # 카테고리 필터
        resp = self.client.get(f"{PLACES_LIST}?category_id={category2.id}&lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        places = resp.data["places"]
        self.assertEqual(len(places), 1)
        self.assertEqual(places[0]["name"], "남산공원")

    def test_places_api_multiple_regions(self):
        region2 = Region.objects.create()
        RegionTranslation.objects.create(region=region2, lang="ko", name="부산")

        sub_region2 = SubRegion.objects.create(region=region2, favorite_count=50, location=Point(129.0756, 35.1796))
        SubRegionTranslation.objects.create(sub_region=sub_region2, lang="ko", name="해운대구")

        busan_place = Place.objects.create(
            content_id="busan_001",
            category=self.category,
            region=region2,
            sub_region=sub_region2,
            location=Point(129.0756, 35.1796),
        )
        PlaceTranslation.objects.create(place=busan_place, lang="ko", name="해운대해수욕장", description="부산의 대표 해수욕장")

        resp = self.client.get(f"{PLACES_LIST}?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["places"]), 3)

        resp = self.client.get(f"{PLACES_LIST}?region_id={region2.id}&lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        places = resp.data["places"]
        self.assertEqual(len(places), 1)
        self.assertEqual(places[0]["name"], "해운대해수욕장")

    def test_places_api_response_structure_minimum(self):
        resp = self.client.get(f"{PLACES_LIST}?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("places", resp.data)
        if resp.data["places"]:
            place = resp.data["places"][0]
            required = [
                "id", "content_id", "name", "description", "address",
                "latitude", "longitude", "phone_number", "use_time",
                "favorite_count", "category", "region",
            ]
            for f in required:
                self.assertIn(f, place, f"필드 '{f}'가 응답에 없습니다")

    def test_places_api_coordinate_precision(self):
        precise = Place.objects.create(
            content_id="precise_coords",
            location=Point(126.87654321, 37.12345678),
            region=self.region,
            sub_region=self.sub_region,
        )
        PlaceTranslation.objects.create(place=precise, lang="ko", name="정밀 좌표 테스트")

        resp = self.client.get(f"{PLACES_LIST}?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        target = next((p for p in resp.data["places"] if p["content_id"] == "precise_coords"), None)
        self.assertIsNotNone(target)
        # 문자열/실수 변환 차이를 피하기 위해 근사 비교
        self.assertAlmostEqual(float(target["latitude"]), 37.12345678, places=8)
        self.assertAlmostEqual(float(target["longitude"]), 126.87654321, places=8)

    def test_places_api_gis_location_field(self):
        test_place = Place.objects.create(
            content_id="gis_test",
            location=Point(127.0, 37.0),
            region=self.region,
            sub_region=self.sub_region,
        )
        PlaceTranslation.objects.create(place=test_place, lang="ko", name="GIS 테스트 장소")

        resp = self.client.get(f"{PLACES_LIST}?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = next((p for p in resp.data["places"] if p["content_id"] == "gis_test"), None)
        self.assertIsNotNone(data)
        self.assertAlmostEqual(float(data["latitude"]), 37.0, places=6)
        self.assertAlmostEqual(float(data["longitude"]), 127.0, places=6)

    def test_places_api_empty_location(self):
        p = Place.objects.create(
            content_id="no_location",
            location=None,
            region=self.region,
            sub_region=self.sub_region,
        )
        PlaceTranslation.objects.create(place=p, lang="ko", name="위치 없는 장소")

        resp = self.client.get(f"{PLACES_LIST}?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = next((x for x in resp.data["places"] if x["content_id"] == "no_location"), None)
        self.assertIsNotNone(data)
        self.assertIsNone(data.get("latitude"))
        self.assertIsNone(data.get("longitude"))

    # ── PlacesBySubRegionAPIView (/api/places/regions/<id>/) ─────────────────────
    def test_places_by_subregion_endpoint_with_pagination_shape(self):
        resp = self.client.get(f"{PLACES_BY_SUBREGION_BASE}{self.sub_region.id}/?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # CustomPagination 형태: count/total_pages/page/page_size/places
        for key in ["count", "total_pages", "page", "page_size", "places"]:
            self.assertIn(key, resp.data)
        self.assertEqual(len(resp.data["places"]), 2)
        for p in resp.data["places"]:
            self.assertEqual(p["sub_region"]["id"], self.sub_region.id)

    # ── PlacesByCategoryIdAPIView (/api/places/category/<id>/) ───────────────────
    def test_places_by_category_endpoint_with_pagination_shape(self):
        url = f"{PLACES_BY_CATEGORY_BASE}{self.category.id}/?lang=ko"
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for key in ["count", "total_pages", "page", "page_size", "places"]:
            self.assertIn(key, resp.data)
        self.assertEqual(len(resp.data["places"]), 2)
        for p in resp.data["places"]:
            self.assertEqual(p["category"]["id"], self.category.id)

    def test_places_by_category_endpoint_empty(self):
        empty_cat = Category.objects.create()
        CategoryTranslation.objects.create(category=empty_cat, lang="ko", name="빈카테고리")

        url = f"{PLACES_BY_CATEGORY_BASE}{empty_cat.id}/?lang=ko"
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)
        self.assertEqual(resp.data["places"], [])

    # ── PlaceTourListAPIView (/api/places/?region_id=...) ────────────────────────
    def test_place_tour_list_api_unauthenticated_shape(self):
        # 기본 region_id=1 과 다를 수 있으므로 생성한 region id 사용
        resp = self.client.get(f"{PLACES_TOUR}?region_id={self.region.id}&lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for key in ["region", "weather", "popular_subregions", "major_places"]:
            self.assertIn(key, resp.data)
        # 비인증이므로 user_recommended_places 키는 없어야 함
        self.assertNotIn("user_recommended_places", resp.data)
        self.assertIsInstance(resp.data["popular_subregions"], list)
        self.assertIsInstance(resp.data["major_places"], list)

    # ── PlaceDetailAPIView (/api/places/<id>/) ───────────────────────────────────
    def test_place_detail_api_success(self):
        resp = self.client.get(f"{PLACES_DETAIL}{self.place1.id}/?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("place", resp.data)

        place_data = resp.data["place"]
        self.assertEqual(place_data["id"], self.place1.id)
        self.assertEqual(place_data["name"], "경복궁")
        self.assertEqual(place_data["phone_number"], "02-3700-3900")
        self.assertEqual(place_data["use_time"], "09:00~18:00")

    def test_place_detail_api_not_found(self):
        resp = self.client.get(f"{PLACES_DETAIL}99999/?lang=ko", follow=True)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
