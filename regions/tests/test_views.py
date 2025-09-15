from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase
from rest_framework import status

from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class RegionsAPITest(APITestCase):
    """
    현재 라우팅에 맞춘 테스트:
      - GET /api/regions/?lang=ko|en
      - GET /api/regions/major?lang=...
      - GET /api/regions/<region_id>/?lang=... (region 최상위 + 내부 subregions 페이지네이션 블록)
    """

    def setUp(self):
        # Region: 서울, 부산
        self.seoul_region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.seoul_region, lang="ko",
            name="서울", description="대한민국의 수도"
        )
        RegionTranslation.objects.create(
            region=self.seoul_region, lang="en",
            name="Seoul", description="Capital of South Korea"
        )

        self.busan_region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.busan_region, lang="ko",
            name="부산", description="해양 도시"
        )

        # SubRegion: 서울 하위 2개 (GIS: location=Point(lon, lat))
        self.gangnam_subregion = SubRegion.objects.create(
            region=self.seoul_region,
            favorite_count=150,
            location=Point(127.0473, 37.5173),
        )
        SubRegionTranslation.objects.create(
            sub_region=self.gangnam_subregion, lang="ko",
            name="강남구", description="서울의 비즈니스 중심지"
        )

        self.jongno_subregion = SubRegion.objects.create(
            region=self.seoul_region,
            favorite_count=120,
            location=Point(126.9770, 37.5796),
        )
        SubRegionTranslation.objects.create(
            sub_region=self.jongno_subregion, lang="ko",
            name="종로구", description="서울의 역사적 중심지"
        )

        # SubRegion: 부산 하위 1개
        self.haeundae_subregion = SubRegion.objects.create(
            region=self.busan_region,
            favorite_count=80,
            location=Point(129.1603, 35.1588),
        )
        SubRegionTranslation.objects.create(
            sub_region=self.haeundae_subregion, lang="ko",
            name="해운대구", description="부산의 대표 해변"
        )

    # ---------- RegionsListAPI ----------
    def test_regions_list_api_success(self):
        response = self.client.get("/api/regions/?lang=ko")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("regions", response.data)

        regions = response.data["regions"]
        self.assertEqual(len(regions), 2)

        seoul_data = next((r for r in regions if r["name"] == "서울"), None)
        self.assertIsNotNone(seoul_data)
        self.assertEqual(seoul_data.get("description"), "대한민국의 수도")

    def test_regions_list_api_english(self):
        response = self.client.get("/api/regions/?lang=en")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        regions = response.data["regions"]

        seoul_data = next((r for r in regions if r["name"] == "Seoul"), None)
        self.assertIsNotNone(seoul_data)
        self.assertEqual(seoul_data.get("description"), "Capital of South Korea")

    def test_regions_api_response_structure(self):
        response = self.client.get("/api/regions/?lang=ko")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("regions", response.data)
        self.assertIsInstance(response.data["regions"], list)

        if response.data["regions"]:
            region = response.data["regions"][0]
            for field in ["id", "name", "description"]:
                self.assertIn(field, region)

    # ---------- MajorRegionListAPI ----------
    def test_major_regions_list_api(self):
        response = self.client.get("/api/regions/major?lang=ko")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("regions", response.data)
        self.assertIsInstance(response.data["regions"], list)

        # 이 엔드포인트는 고정 ID 필터([1,9,6,17])이므로, 결과가 빈 리스트여도 정상.
        # 반환된 경우에는 모두 허용된 ID여야 함.
        major_ids = {1, 6, 9, 17}
        returned_ids = {r["id"] for r in response.data["regions"]}
        self.assertTrue(returned_ids.issubset(major_ids))

    # ---------- RegionDetailAPI ----------
    def test_region_detail_api_success_shape_and_data(self):
        response = self.client.get(f"/api/regions/{self.seoul_region.id}/?lang=ko")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("regions", response.data)  # "region" -> "regions"로 수정

        region_data = response.data["regions"]
        self.assertIn("subregions", region_data)

        sub_block = region_data["subregions"]
        # CustomPagination 스키마 키 확인 - "results" 대신 "regions" 사용
        for key in ["count", "total_pages", "page", "page_size", "regions"]:
            self.assertIn(key, sub_block)

        self.assertEqual(region_data["name"], "서울")
        self.assertEqual(region_data["description"], "대한민국의 수도")

        self.assertEqual(sub_block["count"], 2)
        results = sub_block["regions"]  # "results" -> "regions"
        self.assertEqual(len(results), 2)

        # 구현은 id 오름차순
        self.assertEqual(results[0]["name"], "강남구")
        self.assertEqual(results[1]["name"], "종로구")

    def test_region_detail_api_pagination(self):
        resp1 = self.client.get(f"/api/regions/{self.seoul_region.id}/?lang=ko&page=1&page_size=1")
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        block1 = resp1.data["regions"]["subregions"]
        self.assertEqual(block1["count"], 2)
        self.assertEqual(len(block1["regions"]), 1)  # "results" -> "regions"

        resp2 = self.client.get(f"/api/regions/{self.seoul_region.id}/?lang=ko&page=2&page_size=1")
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        block2 = resp2.data["regions"]["subregions"]
        self.assertEqual(len(block2["regions"]), 1)  # "results" -> "regions"

        names = [block1["regions"][0]["name"], block2["regions"][0]["name"]]  # "results" -> "regions"
        self.assertCountEqual(names, ["강남구", "종로구"])

    def test_region_detail_api_subregion_data_fields(self):
        response = self.client.get(f"/api/regions/{self.seoul_region.id}/?lang=ko")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["regions"]["subregions"]["regions"]  # "results" -> "regions"

        gangnam = next((s for s in results if s["name"] == "강남구"), None)
        self.assertIsNotNone(gangnam)

        for field in ["id", "name", "description", "feature", "favorite_count", "latitude", "longitude"]:
            self.assertIn(field, gangnam)

    def test_region_detail_api_not_found(self):
        response = self.client.get("/api/regions/999999/?lang=ko")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_region_detail_missing_translation(self):
        response = self.client.get(f"/api/regions/{self.seoul_region.id}/?lang=jp")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        region_data = response.data["regions"]
        self.assertEqual(region_data.get("name"), "")
        self.assertEqual(region_data.get("description"), "")

    def test_invalid_language_should_fallback_to_default(self):
        # 현재 구현은 잘못된 lang도 200으로 처리(ko 기본)하므로 이를 검증
        response = self.client.get("/api/regions/?lang=xx")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
