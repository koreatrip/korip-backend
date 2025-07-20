from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class RegionsAPITDDTest(APITestCase):
    #테스트용 데이터 생성
    def setUp(self):
        self.seoul = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.seoul,
            lang="ko",
            name="서울",
            description="전통과 현대가 공존하는 도시"
        )
        RegionTranslation.objects.create(
            region=self.seoul,
            lang="en",
            name="Seoul",
            description="A city where tradition and modernity coexist"
        )

        self.busan = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.busan,
            lang="ko",
            name="부산",
            description="바다와 산이 어우러진 항구도시"
        )

        self.gangnam = SubRegion.objects.create(
            region=self.seoul,
            favorite_count=150,
            latitude=37.5665,
            longitude=126.9780
        )
        SubRegionTranslation.objects.create(
            sub_region=self.gangnam,
            lang="ko",
            name="강남구",
            description="한국의 경제 중심지",
            features="트렌디한 쇼핑몰과 고급 레스토랑"
        )

        self.gangbuk = SubRegion.objects.create(
            region=self.seoul,
            favorite_count=0,
            latitude=37.6396,
            longitude=127.0253
        )
        SubRegionTranslation.objects.create(
            sub_region=self.gangbuk,
            lang="ko",
            name="강북구",
            description="조용한 주거지역",
            features="전통시장과 주택가"
        )

        self.mapo = SubRegion.objects.create(
            region=self.seoul,
            favorite_count=80,
            latitude=37.5663,
            longitude=126.9019
        )
        SubRegionTranslation.objects.create(
            sub_region=self.mapo,
            lang="ko",
            name="마포구",
            description="젊음과 문화의 중심",
            features="홍대, 상암동 디지털미디어시티"
        )

    def test_regions_list_api_should_exist(self):
        response = self.client.get("/api/regions/?lang=ko", follow=True)

        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("regions", response.data)
        self.assertIsInstance(response.data["regions"], list)
        self.assertEqual(len(response.data["regions"]), 2)

    def test_region_detail_api_should_exist(self):
        response = self.client.get(f"/api/regions/{self.seoul.id}?lang=ko", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("region", response.data)
        region_data = response.data["region"]
        self.assertEqual(region_data["name"], "서울")
        self.assertEqual(region_data["description"], "전통과 현대가 공존하는 도시")
        self.assertIn("subregions", region_data)
        self.assertEqual(len(region_data["subregions"]), 3)

    def test_subregions_should_be_sorted_by_popularity_then_korean_name(self):
        response = self.client.get(f"/api/regions/{self.seoul.id}/?lang=ko", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subregions = response.data["region"]["subregions"]
        self.assertEqual(subregions[0]["name"], "강남구")
        self.assertEqual(subregions[0]["favorite_count"], 150)

        self.assertEqual(subregions[1]["name"], "마포구")
        self.assertEqual(subregions[1]["favorite_count"], 80)

        self.assertEqual(subregions[2]["name"], "강북구")
        self.assertEqual(subregions[2]["favorite_count"], 0)

    def test_default_region_api_should_return_seoul(self):
        response = self.client.get("/api/regions/default?lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("region", response.data)

        region_data = response.data["region"]
        self.assertEqual(region_data["name"], "서울")

        self.assertIn("subregions", region_data)
        self.assertEqual(len(region_data["subregions"]), 3)

    def test_all_subregions_api_should_exist(self):

        response = self.client.get("/api/regions/subregions/?lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("subregions", response.data)
        self.assertEqual(len(response.data["subregions"]), 3)

        subregions = response.data["subregions"]
        self.assertEqual(subregions[0]["name"], "강남구")
        self.assertEqual(subregions[1]["name"], "마포구")
        self.assertEqual(subregions[2]["name"], "강북구")

    def test_subregion_detail_api_should_exist(self):

        response = self.client.get(f"/api/regions/subregions/{self.gangnam.id}/?lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("subregion", response.data)

        subregion_data = response.data["subregion"]
        self.assertEqual(subregion_data["name"], "강남구")
        self.assertEqual(subregion_data["favorite_count"], 150)
        self.assertEqual(subregion_data["features"], "트렌디한 쇼핑몰과 고급 레스토랑")

    def test_language_parameter_should_work(self):
        response = self.client.get("/api/regions/?lang=en", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        regions = response.data["regions"]
        seoul_data = None
        for region in regions:
            if region["name"] == "Seoul":
                seoul_data = region
                break

        self.assertIsNotNone(seoul_data)
        self.assertEqual(seoul_data["name"], "Seoul")
        self.assertEqual(seoul_data["description"], "A city where tradition and modernity coexist")

    def test_invalid_language_should_return_error(self):
        response = self.client.get("/api/regions/?lang=invalid", follow=True)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
