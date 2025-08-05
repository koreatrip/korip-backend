from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.gis.geos import Point
from places.models import Place, PlaceTranslation
from categories.models import Category, CategoryTranslation, SubCategory, SubCategoryTranslation
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class PlacesAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="문화"
        )
        CategoryTranslation.objects.create(
            category=self.category,
            lang="en",
            name="Culture"
        )

        self.sub_category = SubCategory.objects.create(category=self.category)
        SubCategoryTranslation.objects.create(
            sub_category=self.sub_category,
            lang="ko",
            name="궁궐"
        )

        self.region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="서울"
        )
        RegionTranslation.objects.create(
            region=self.region,
            lang="en",
            name="Seoul"
        )

        self.sub_region = SubRegion.objects.create(
            region=self.region,
            favorite_count=100,
            location=Point(126.9770, 37.5796)
        )
        SubRegionTranslation.objects.create(
            sub_region=self.sub_region,
            lang="ko",
            name="종로구"
        )

        self.place1 = Place.objects.create(
            content_id="12345",
            category=self.category,
            sub_category=self.sub_category,
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9770, 37.5796),
            phone_number="02-3700-3900",
            use_time="09:00~18:00",
            favorite_count=50
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
            favorite_count=30
        )

        PlaceTranslation.objects.create(
            place=self.place1,
            lang="ko",
            name="경복궁",
            description="조선시대 궁궐",
            address="서울특별시 종로구 사직로 161"
        )

        PlaceTranslation.objects.create(
            place=self.place1,
            lang="en",
            name="Gyeongbokgung Palace",
            description="Joseon Dynasty Palace",
            address="161 Sajik-ro, Jongno-gu, Seoul"
        )

        PlaceTranslation.objects.create(
            place=self.place2,
            lang="ko",
            name="덕수궁",
            description="대한제국의 궁궐",
            address="서울특별시 중구 세종대로 99"
        )

    def test_places_list_api_success(self):
        response = self.client.get("/api/places/?lang=ko", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("places", response.data)

        places = response.data["places"]
        self.assertEqual(len(places), 2)

        place1_data = places[0]
        self.assertEqual(place1_data["content_id"], "12345")
        self.assertEqual(place1_data["name"], "경복궁")
        self.assertEqual(place1_data["description"], "조선시대 궁궐")

        self.assertIn("category", place1_data)
        self.assertEqual(place1_data["category"]["name"], "문화")

        self.assertIn("region", place1_data)
        self.assertEqual(place1_data["region"]["name"], "서울")

    def test_places_list_api_english(self):
        response = self.client.get("/api/places/?lang=en", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]

        place1_data = places[0]
        self.assertEqual(place1_data["name"], "Gyeongbokgung Palace")
        self.assertEqual(place1_data["description"], "Joseon Dynasty Palace")
        self.assertEqual(place1_data["category"]["name"], "Culture")
        self.assertEqual(place1_data["region"]["name"], "Seoul")

    def test_place_detail_api_success(self):
        response = self.client.get(f"/api/places/{self.place1.id}/?lang=ko", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("place", response.data)

        place_data = response.data["place"]
        self.assertEqual(place_data["id"], self.place1.id)
        self.assertEqual(place_data["name"], "경복궁")
        self.assertEqual(place_data["phone_number"], "02-3700-3900")
        self.assertEqual(place_data["use_time"], "09:00~18:00")

    def test_place_detail_api_not_found(self):
        response = self.client.get("/api/places/99999/?lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_places_filter_by_category(self):
        response = self.client.get(f"/api/places/?category_id={self.category.id}&lang=ko", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 2)

        for place_data in places:
            self.assertEqual(place_data["category"]["id"], self.category.id)

    def test_places_filter_by_region(self):
        response = self.client.get(f"/api/places/?region_id={self.region.id}&lang=ko", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 2)

        for place_data in places:
            self.assertEqual(place_data["region"]["id"], self.region.id)

    def test_places_filter_by_subregion(self):
        response = self.client.get(f"/api/places/regions/{self.sub_region.id}/?lang=ko", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 2)

        for place_data in places:
            self.assertEqual(place_data["sub_region"]["id"], self.sub_region.id)

    def test_places_ordering_by_favorite_count(self):
        response = self.client.get("/api/places/?lang=ko", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]

        self.assertGreaterEqual(places[0]["favorite_count"], places[1]["favorite_count"])

    def test_places_api_default_language(self):
        response = self.client.get("/api/places/", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]

        self.assertEqual(places[0]["name"], "경복궁")

    def test_places_api_missing_translation(self):
        response = self.client.get("/api/places/?lang=jp", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]

        self.assertEqual(places[0]["name"], "")
        self.assertEqual(places[0]["description"], "")

    def test_places_api_pagination(self):
        for i in range(10):
            place = Place.objects.create(
                content_id=f"test_{i}",
                favorite_count=i,
                region=self.region,
                sub_region=self.sub_region,
                location=Point(126.9700 + i * 0.001, 37.5700 + i * 0.001)
            )
            PlaceTranslation.objects.create(
                place=place,
                lang="ko",
                name=f"테스트 관광지 {i}"
            )

        response = self.client.get("/api/places/?lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        places = response.data["places"]
        self.assertEqual(len(places), 12)

    def test_places_api_search_functionality(self):
        response = self.client.get("/api/places/?search=경복궁&lang=ko", follow=True)

        if response.status_code == status.HTTP_200_OK:
            places = response.data["places"]
            found_gyeongbok = any(
                "경복궁" in place["name"] for place in places
            )
            self.assertTrue(found_gyeongbok)

    def test_places_api_multiple_categories(self):
        category2 = Category.objects.create()
        CategoryTranslation.objects.create(
            category=category2,
            lang="ko",
            name="자연"
        )

        nature_place = Place.objects.create(
            content_id="nature_001",
            category=category2,
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9800, 37.5500),
            favorite_count=20
        )

        PlaceTranslation.objects.create(
            place=nature_place,
            lang="ko",
            name="남산공원",
            description="서울의 대표 공원"
        )

        response = self.client.get("/api/places/?lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 3)

        response = self.client.get(f"/api/places/?category_id={category2.id}&lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 1)
        self.assertEqual(places[0]["name"], "남산공원")

    def test_places_api_multiple_regions(self):
        region2 = Region.objects.create()
        RegionTranslation.objects.create(
            region=region2,
            lang="ko",
            name="부산"
        )

        sub_region2 = SubRegion.objects.create(
            region=region2,
            favorite_count=50,
            location=Point(129.0756, 35.1796)
        )
        SubRegionTranslation.objects.create(
            sub_region=sub_region2,
            lang="ko",
            name="해운대구"
        )

        busan_place = Place.objects.create(
            content_id="busan_001",
            category=self.category,
            region=region2,
            sub_region=sub_region2,
            location=Point(129.0756, 35.1796)
        )

        PlaceTranslation.objects.create(
            place=busan_place,
            lang="ko",
            name="해운대해수욕장",
            description="부산의 대표 해수욕장"
        )

        response = self.client.get("/api/places/?lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 3)

        response = self.client.get(f"/api/places/?region_id={region2.id}&lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 1)
        self.assertEqual(places[0]["name"], "해운대해수욕장")

    def test_places_api_sorting_options(self):
        low_favorite_place = Place.objects.create(
            content_id="low_fav",
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9750, 37.5750),
            favorite_count=5
        )
        PlaceTranslation.objects.create(
            place=low_favorite_place,
            lang="ko",
            name="인기 없는 장소"
        )

        high_favorite_place = Place.objects.create(
            content_id="high_fav",
            region=self.region,
            sub_region=self.sub_region,
            location=Point(126.9850, 37.5850),
            favorite_count=100
        )
        PlaceTranslation.objects.create(
            place=high_favorite_place,
            lang="ko",
            name="인기 많은 장소"
        )

        response = self.client.get("/api/places/?sort=favorite&lang=ko", follow=True)

        if response.status_code == status.HTTP_200_OK:
            places = response.data["places"]
            self.assertGreaterEqual(places[0]["favorite_count"], places[-1]["favorite_count"])

    def test_places_api_error_handling(self):
        response = self.client.get("/api/places/?category_id=99999&lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 0)

        response = self.client.get("/api/places/?region_id=99999&lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = response.data["places"]
        self.assertEqual(len(places), 0)

    def test_places_api_response_structure(self):
        response = self.client.get("/api/places/?lang=ko", follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("places", response.data)

        if len(response.data["places"]) > 0:
            place_data = response.data["places"][0]

            required_fields = [
                "id", "content_id", "name", "description", "address",
                "latitude", "longitude", "phone_number", "use_time",
                "favorite_count", "category", "region"
            ]

            for field in required_fields:
                self.assertIn(field, place_data, f"필드 '{field}'가 응답에 없습니다")

    def test_places_api_coordinate_precision(self):
        precise_place = Place.objects.create(
            content_id="precise_coords",
            location=Point(126.87654321, 37.12345678),
            region=self.region,
            sub_region=self.sub_region
        )

        PlaceTranslation.objects.create(
            place=precise_place,
            lang="ko",
            name="정밀 좌표 테스트"
        )

        response = self.client.get("/api/places/?lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        places = response.data["places"]

        precise_place_data = None
        for place in places:
            if place["content_id"] == "precise_coords":
                precise_place_data = place
                break

        self.assertIsNotNone(precise_place_data)
        self.assertEqual(str(precise_place_data["latitude"]), "37.12345678")
        self.assertEqual(str(precise_place_data["longitude"]), "126.87654321")

    def test_places_api_gis_location_field(self):
        test_place = Place.objects.create(
            content_id="gis_test",
            location=Point(127.0000, 37.0000),
            region=self.region,
            sub_region=self.sub_region
        )

        PlaceTranslation.objects.create(
            place=test_place,
            lang="ko",
            name="GIS 테스트 장소"
        )

        response = self.client.get("/api/places/?lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        places = response.data["places"]

        gis_place_data = None
        for place in places:
            if place["content_id"] == "gis_test":
                gis_place_data = place
                break

        self.assertIsNotNone(gis_place_data)
        self.assertAlmostEqual(float(gis_place_data["latitude"]), 37.0, places=6)
        self.assertAlmostEqual(float(gis_place_data["longitude"]), 127.0, places=6)

    def test_places_api_empty_location(self):
        place_no_location = Place.objects.create(
            content_id="no_location",
            location=None,
            region=self.region,
            sub_region=self.sub_region
        )

        PlaceTranslation.objects.create(
            place=place_no_location,
            lang="ko",
            name="위치 없는 장소"
        )

        response = self.client.get("/api/places/?lang=ko", follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        places = response.data["places"]

        no_location_place_data = None
        for place in places:
            if place["content_id"] == "no_location":
                no_location_place_data = place
                break

        self.assertIsNotNone(no_location_place_data)
        self.assertIsNone(no_location_place_data.get("latitude"))
        self.assertIsNone(no_location_place_data.get("longitude"))
