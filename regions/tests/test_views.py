from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class RegionsAPITest(APITestCase):

    def setUp(self):
        self.seoul_region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.seoul_region,
            lang="ko",
            name="서울",
            description="대한민국의 수도"
        )
        RegionTranslation.objects.create(
            region=self.seoul_region,
            lang="en",
            name="Seoul",
            description="Capital of South Korea"
        )

        self.busan_region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.busan_region,
            lang="ko",
            name="부산",
            description="해양 도시"
        )

        self.gangnam_subregion = SubRegion.objects.create(
            region=self.seoul_region,
            favorite_count=150,
            latitude=37.5173,
            longitude=127.0473
        )
        SubRegionTranslation.objects.create(
            sub_region=self.gangnam_subregion,
            lang="ko",
            name="강남구",
            description="서울의 비즈니스 중심지",
            feature="쇼핑, 업무지구"
        )

        self.jongno_subregion = SubRegion.objects.create(
            region=self.seoul_region,
            favorite_count=120,
            latitude=37.5796,
            longitude=126.9770
        )
        SubRegionTranslation.objects.create(
            sub_region=self.jongno_subregion,
            lang="ko",
            name="종로구",
            description="서울의 역사적 중심지",
            feature="궁궐, 전통문화"
        )

        self.haeundae_subregion = SubRegion.objects.create(
            region=self.busan_region,
            favorite_count=80,
            latitude=35.1588,
            longitude=129.1603
        )
        SubRegionTranslation.objects.create(
            sub_region=self.haeundae_subregion,
            lang="ko",
            name="해운대구",
            description="부산의 대표 해변",
            feature="해변, 관광"
        )

    def test_regions_list_api_success(self):
        response = self.client.get("/api/regions/?lang=ko")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("regions", response.data)

        regions = response.data["regions"]
        self.assertEqual(len(regions), 2)

        seoul_data = next((r for r in regions if r["name"] == "서울"), None)
        self.assertIsNotNone(seoul_data)
        self.assertEqual(seoul_data["description"], "대한민국의 수도")

    def test_regions_list_api_english(self):
        response = self.client.get("/api/regions/?lang=en")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        regions = response.data["regions"]

        seoul_data = next((r for r in regions if r["name"] == "Seoul"), None)
        self.assertIsNotNone(seoul_data)
        self.assertEqual(seoul_data["description"], "Capital of South Korea")

    def test_region_detail_api_success(self):
        response = self.client.get(f"/api/regions/{self.seoul_region.id}/?lang=ko")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("region", response.data)
        self.assertIn("subregions", response.data)
        self.assertIn("total_subregions", response.data)

        region_data = response.data["region"]
        self.assertEqual(region_data["name"], "서울")
        self.assertEqual(region_data["description"], "대한민국의 수도")

        subregions = response.data["subregions"]
        self.assertEqual(len(subregions), 2)
        self.assertEqual(response.data["total_subregions"], 2)

        self.assertEqual(subregions[0]["name"], "강남구")
        self.assertEqual(subregions[1]["name"], "종로구")

    def test_region_detail_api_subregion_data(self):
        response = self.client.get(f"/api/regions/{self.seoul_region.id}/?lang=ko")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subregions = response.data["subregions"]

        gangnam_data = subregions[0]
        required_fields = [
            "id", "name", "description", "feature",
            "favorite_count", "latitude", "longitude"
        ]

        for field in required_fields:
            self.assertIn(field, gangnam_data)

        self.assertEqual(gangnam_data["name"], "강남구")
        self.assertEqual(gangnam_data["favorite_count"], 150)
        self.assertEqual(float(gangnam_data["latitude"]), 37.5173)
        self.assertEqual(float(gangnam_data["longitude"]), 127.0473)

    def test_region_detail_api_not_found(self):
        response = self.client.get("/api/regions/99999/?lang=ko")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_region_detail_api_no_subregions(self):
        empty_region = Region.objects.create()
        RegionTranslation.objects.create(
            region=empty_region,
            lang="ko",
            name="제주",
            description="아름다운 섬"
        )

        response = self.client.get(f"/api/regions/{empty_region.id}/?lang=ko")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["subregions"]), 0)
        self.assertEqual(response.data["total_subregions"], 0)

    def test_region_detail_api_favorite_count_sorting(self):
        high_favorite_subregion = SubRegion.objects.create(
            region=self.seoul_region,
            favorite_count=200,
            latitude=37.5000,
            longitude=127.0000
        )
        SubRegionTranslation.objects.create(
            sub_region=high_favorite_subregion,
            lang="ko",
            name="새로운구",
            description="가장 인기 많은 구"
        )

        response = self.client.get(f"/api/regions/{self.seoul_region.id}/?lang=ko")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subregions = response.data["subregions"]

        self.assertEqual(subregions[0]["name"], "새로운구")
        self.assertEqual(subregions[1]["name"], "강남구")
        self.assertEqual(subregions[2]["name"], "종로구")

    def test_regions_api_response_structure(self):
        response = self.client.get("/api/regions/?lang=ko")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("regions", response.data)
        self.assertIsInstance(response.data["regions"], list)

        if len(response.data["regions"]) > 0:
            region = response.data["regions"][0]
            required_fields = ["id", "name", "description"]
            for field in required_fields:
                self.assertIn(field, region)

    def test_region_detail_missing_translation(self):
        response = self.client.get(f"/api/regions/{self.seoul_region.id}/?lang=jp")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        region_data = response.data["region"]
        self.assertEqual(region_data["name"], "")
        self.assertEqual(region_data["description"], "")