from django.test import TestCase
from django.contrib.auth import get_user_model
from places.models import PlaceKR, PlaceEN, PlaceJP, PlaceCN
from categories.models import Category, SubCategory
from rest_framework.test import APITestCase
from rest_framework import status
from places.serializers import PlaceKRSerializer, PlaceENSerializer, PlaceJPSerializer, PlaceCNSerializer

User = get_user_model()


class PlaceKRModelTest(TestCase):
    # PlaceKR 모델 생성 테스트
    def test_place_kr_creation(self):
        place = PlaceKR.objects.create(
            name="경복궁",
            address="서울특별시 종로구 사직로 161",
            latitude=37.579617,
            longitude=126.977041,
            region_code="seoul",
            region_name="서울"
        )

        self.assertEqual(place.name, "경복궁")
        self.assertEqual(place.region_code, "seoul")
        self.assertEqual(place.view_count, 0)  # 기본값
        self.assertIsNotNone(place.created_at)

        # 카테고리와 함께 PlaceKR 생성 테스트, 먼저 카테고리 생성
    def test_place_kr_with_category(self):
        category = Category.objects.create(
            name_ko="문화",
            name_en="Culture",
            name_jp="文化",
            name_cn="文化"
        )
        subcategory = SubCategory.objects.create(
            name_ko="궁궐",
            name_en="Palace",
            name_jp="宮殿",
            name_cn="宫殿",
            category=category
        )

        # 카테고리와 함께 관광지 생성
        place = PlaceKR.objects.create(
            name="창덕궁",
            category=category,
            sub_category=subcategory,
            region_code="seoul"
        )

        self.assertEqual(place.category, category)
        self.assertEqual(place.sub_category, subcategory)
        self.assertEqual(place.name, "창덕궁")

# PlaceKR __str__ 메서드 테스트
    def test_place_kr_str_method(self):
        place = PlaceKR.objects.create(name="덕수궁")

        self.assertEqual(str(place), "덕수궁")

# 조회수 증가 테스트,
    def test_place_kr_view_count_increment(self):
        place = PlaceKR.objects.create(name="경희궁")

        # 초기 조회수 확인
        self.assertEqual(place.view_count, 0)

        # 조회수 증가
        place.view_count += 1
        place.save()

        # 조회수 증가 확인
        place.refresh_from_db()
        self.assertEqual(place.view_count, 1)


class PlaceENModelTest(TestCase):
    def test_place_en_creation(self):
        place = PlaceEN.objects.create(
            name="Gyeongbokgung Palace",
            address="161 Sajik-ro, Jongno-gu, Seoul",
            latitude=37.579617,
            longitude=126.977041,
            region_code="seoul",
            region_name="Seoul"
        )

        self.assertEqual(place.name, "Gyeongbokgung Palace")
        self.assertEqual(place.region_code, "seoul")
        self.assertEqual(place.view_count, 0)
        self.assertIsNotNone(place.created_at)

    def test_place_en_with_category(self):
        category = Category.objects.create(
            name_ko="문화",
            name_en="Culture",
            name_jp="文化",
            name_cn="文化"
        )
        subcategory = SubCategory.objects.create(
            name_ko="궁궐",
            name_en="Palace",
            name_jp="宮殿",
            name_cn="宫殿",
            category=category
        )

        place = PlaceEN.objects.create(
            name="Changdeokgung Palace",
            category=category,
            sub_category=subcategory,
            region_code="seoul"
        )

        self.assertEqual(place.category, category)
        self.assertEqual(place.sub_category, subcategory)
        self.assertEqual(place.name, "Changdeokgung Palace")

    def test_place_en_str_method(self):
        place = PlaceEN.objects.create(name="Deoksugung Palace")
        self.assertEqual(str(place), "Deoksugung Palace")


class PlaceJPModelTest(TestCase):
    def test_place_jp_creation(self):
        place = PlaceJP.objects.create(
            name="景福宮",
            address="ソウル特別市鍾路区社稷路161",
            latitude=37.579617,
            longitude=126.977041,
            region_code="seoul",
            region_name="ソウル"
        )

        self.assertEqual(place.name, "景福宮")
        self.assertEqual(place.region_code, "seoul")
        self.assertEqual(place.view_count, 0)
        self.assertIsNotNone(place.created_at)

    def test_place_jp_str_method(self):
        place = PlaceJP.objects.create(name="徳寿宮")
        self.assertEqual(str(place), "徳寿宮")


class PlaceCNModelTest(TestCase):
    def test_place_cn_creation(self):
        place = PlaceCN.objects.create(
            name="景福宫",
            address="首尔特别市钟路区社稷路161号",
            latitude=37.579617,
            longitude=126.977041,
            region_code="seoul",
            region_name="首尔"
        )

        self.assertEqual(place.name, "景福宫")
        self.assertEqual(place.region_code, "seoul")
        self.assertEqual(place.view_count, 0)
        self.assertIsNotNone(place.created_at)

    def test_place_cn_str_method(self):
        place = PlaceCN.objects.create(name="德寿宫")
        self.assertEqual(str(place), "德寿宫")


class PlaceKRSerializerTest(TestCase):
    # 테스트용 데이터 생성
    def setUp(self):
        self.place_data = {
            'name': '경복궁',
            'address': '서울특별시 종로구 사직로 161',
            'latitude': 37.579617,
            'longitude': 126.977041,
            'region_code': 'seoul',
            'region_name': '서울'
        }
        self.place = PlaceKR.objects.create(**self.place_data)

# PlaceKR Serializer 생성 테스트
    def test_place_kr_serializer_creation(self):
        serializer = PlaceKRSerializer(data=self.place_data)
        self.assertTrue(serializer.is_valid())

# PlaceKR Serializer 데이터 직렬화 테스트
    def test_place_kr_serializer_data(self):
        serializer = PlaceKRSerializer(instance=self.place)
        data = serializer.data

        self.assertEqual(data['name'], '경복궁')
        self.assertEqual(data['region_code'], 'seoul')
        self.assertIn('created_at', data)


class PlaceKRAPITest(APITestCase):
    # 테스트용 관광지 데이터 생성
    def setUp(self):
        self.place1 = PlaceKR.objects.create(
            name='경복궁',
            region_code='seoul',
            region_name='서울'
        )
        self.place2 = PlaceKR.objects.create(
            name='창덕궁',
            region_code='seoul',
            region_name='서울'
        )

# 한국어 관광지 생성 API 테스트
    def test_create_place_kr(self):
        url = "/api/places/kr/"
        data = {
            "name": "덕수궁",
            "address": "서울특별시 중구 세종대로 99",
            "latitude": 37.565944,
            "longitude": 126.975227,
            "region_code": "seoul",
            "region_name": "서울"
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "덕수궁")
        self.assertEqual(PlaceKR.objects.count(), 3)  # 기존 2개 + 새로 생성 1개

# 한국어 관광지 생성 API 잘못된 데이터 테스트
    def test_create_place_kr_invalid_data(self):
        url = "/api/places/kr/"
        data = {
            "address": "서울특별시 중구"
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)  # 필수 필드인 name 이 없어서  필드 에러가 있어야 함

# 한국어 관광지 목록 조회 API 테스트
    def test_get_place_kr_list(self):
        url = '/api/places/kr/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], '경복궁')

# 한국어 관광지 상세 조회 API 테스트
    def test_get_place_kr_detail(self):
        url = f'/api/places/kr/{self.place1.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '경복궁')
        self.assertEqual(response.data['region_code'], 'seoul')

# 한국어 관광지 수정 API 테스트
    def test_update_place_kr(self):
        url = f"/api/places/kr/{self.place1.id}/"
        data = {
            "name": "경복궁 (수정됨)",
            "address": "서울특별시 종로구 사직로 161 (수정됨)",
            "region_code": "seoul",
            "region_name": "서울"
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "경복궁 (수정됨)")

        # DB에서 실제로 수정되었는지 확인
        updated_place = PlaceKR.objects.get(id=self.place1.id)
        self.assertEqual(updated_place.name, "경복궁 (수정됨)")

# 한국어 관광지 부분 수정 API 테스트
    def test_partial_update_place_kr(self):
        url = f"/api/places/kr/{self.place1.id}/"
        data = {
            "name": "경복궁 (부분수정)"
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "경복궁 (부분수정)")
        self.assertEqual(response.data["region_code"], "seoul")  # 기존 데이터 유지

# 한국어 관광지 삭제 API 테스트
    def test_delete_place_kr(self):
        url = f"/api/places/kr/{self.place1.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PlaceKR.objects.count(), 1)  # 기존 2개 - 삭제 1개

        # 삭제된 관광지 조회 시 404 에러
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# 존재하지 않는 관광지 수정 시 404 에러 테스트
    def test_update_nonexistent_place_kr(self):
        url = "/api/places/kr/999/"
        data = {"name": "존재하지 않는 관광지"}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# 카테고리별 관광지 필터링 테스트
    def test_filter_place_kr_by_category(self):
        # 카테고리 생성
        category = Category.objects.create(
            name_ko="문화",
            name_en="Culture",
            name_jp="文化",
            name_cn="文化"
        )

        # 카테고리가 있는 관광지 생성
        place_with_category = PlaceKR.objects.create(
            name="종묘",
            category=category,
            region_code="seoul"
        )

        # 카테고리 필터링 테스트
        url = "/api/places/kr/?category=문화"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "종묘")

# 지역별 관광지 필터링 테스트
    def test_filter_place_kr_by_region(self):
        # 부산 관광지 추가
        PlaceKR.objects.create(
            name="해운대해수욕장",
            region_code="busan",
            region_name="부산"
        )

        # 서울 지역만 필터링
        url = "/api/places/kr/?region=seoul"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # setUp에서 만든 서울 관광지 2개만 나와야 함
        seoul_places = [place for place in response.data if place["region_code"] == "seoul"]
        self.assertEqual(len(seoul_places), 2)

# 이름으로 관광지 검색 테스트
    def test_search_place_kr_by_name(self):
        url = "/api/places/kr/?search=경복"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "경복궁")

class PlaceENAPITest(APITestCase):
    def setUp(self):
        self.place1 = PlaceEN.objects.create(
            name="Gyeongbokgung Palace",
            region_code="seoul",
            region_name="Seoul"
        )
        self.place2 = PlaceEN.objects.create(
            name="Changdeokgung Palace",
            region_code="seoul",
            region_name="Seoul"
        )

    def test_get_place_en_list(self):
        url = "/api/places/en/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Gyeongbokgung Palace")

    def test_get_place_en_detail(self):
        url = f"/api/places/en/{self.place1.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Gyeongbokgung Palace")
        self.assertEqual(response.data["region_code"], "seoul")

    def test_create_place_en(self):
        url = "/api/places/en/"
        data = {
            "name": "Deoksugung Palace",
            "address": "99 Sejong-daero, Jung-gu, Seoul",
            "latitude": 37.565944,
            "longitude": 126.975227,
            "region_code": "seoul",
            "region_name": "Seoul"
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Deoksugung Palace")
        self.assertEqual(PlaceEN.objects.count(), 3)

    def test_update_place_en(self):
        url = f"/api/places/en/{self.place1.id}/"
        data = {
            "name": "Gyeongbokgung Palace (Updated)",
            "region_code": "seoul",
            "region_name": "Seoul"
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Gyeongbokgung Palace (Updated)")

    def test_delete_place_en(self):
        url = f"/api/places/en/{self.place1.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PlaceEN.objects.count(), 1)

    def test_search_place_en_by_name(self):
        url = "/api/places/en/?search=Gyeongbok"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Gyeongbokgung Palace")


class PlaceJPAPITest(APITestCase):
    def setUp(self):
        self.place1 = PlaceJP.objects.create(
            name="景福宮",
            region_code="seoul",
            region_name="ソウル"
        )
        self.place2 = PlaceJP.objects.create(
            name="昌徳宮",
            region_code="seoul",
            region_name="ソウル"
        )

    def test_get_place_jp_list(self):
        url = "/api/places/jp/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "景福宮")

    def test_create_place_jp(self):
        url = "/api/places/jp/"
        data = {
            "name": "徳寿宮",
            "region_code": "seoul",
            "region_name": "ソウル"
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "徳寿宮")

    def test_search_place_jp_by_name(self):
        url = "/api/places/jp/?search=景福"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "景福宮")

    def test_filter_place_jp_by_region(self):
        PlaceJP.objects.create(
            name="海雲台海水浴場",
            region_code="busan",
            region_name="釜山"
        )

        url = "/api/places/jp/?region=seoul"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        seoul_places = [place for place in response.data if place["region_code"] == "seoul"]
        self.assertEqual(len(seoul_places), 2)


class PlaceCNAPITest(APITestCase):
    def setUp(self):
        self.place1 = PlaceCN.objects.create(
            name="景福宫",
            region_code="seoul",
            region_name="首尔"
        )
        self.place2 = PlaceCN.objects.create(
            name="昌德宫",
            region_code="seoul",
            region_name="首尔"
        )

    def test_get_place_cn_list(self):
        url = "/api/places/cn/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "景福宫")

    def test_create_place_cn(self):
        url = "/api/places/cn/"
        data = {
            "name": "德寿宫",
            "region_code": "seoul",
            "region_name": "首尔"
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "德寿宫")

    def test_search_place_cn_by_name(self):
        url = "/api/places/cn/?search=景福"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "景福宫")

    def test_filter_place_cn_by_region(self):
        PlaceCN.objects.create(
            name="海云台海水浴场",
            region_code="busan",
            region_name="釜山"
        )

        url = "/api/places/cn/?region=seoul"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        seoul_places = [place for place in response.data if place["region_code"] == "seoul"]
        self.assertEqual(len(seoul_places), 2)
