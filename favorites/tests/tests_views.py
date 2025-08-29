from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from favorites.models import FavoritePlace, FavoriteSubRegion
from places.models import Place, PlaceTranslation
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


User = get_user_model()


class FavoritePlaceAPIViewTest(APITestCase):
    """FavoritePlaceAPIView 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        # CustomUser 모델에 맞게 수정
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nickname='테스트유저',
            phone_number='010-1234-5678'
        )
        
        # Place 생성
        self.place = Place.objects.create(
            content_id='12345',
            phone_number='02-1234-5678',
            favorite_count=0
        )
        
        PlaceTranslation.objects.create(
            place=self.place,
            lang='ko',
            name='테스트 장소',
            description='테스트 설명',
            address='서울시 강남구 테스트동 123'
        )
        
        self.url = reverse('favorite-places')

    def test_post_without_authentication(self):
        """인증 없이 POST 요청 테스트"""
        data = {'place_id': self.place.id}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_with_authentication(self):
        """인증된 사용자의 POST 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        data = {'place_id': self.place.id}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            FavoritePlace.objects.filter(user=self.user, place=self.place).exists()
        )

    def test_post_invalid_data(self):
        """잘못된 데이터로 POST 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        data = {'place_id': 99999}  # 존재하지 않는 place_id
        response = self.client.post(self.url, data)
        
        # RequestError 발생으로 인한 에러 응답 예상
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_post_missing_data(self):
        """필수 데이터 누락 POST 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        data = {}  # place_id 누락
        response = self.client.post(self.url, data)
        
        # ValidationError 발생으로 인한 에러 응답 예상
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_get_without_authentication(self):
        """인증 없이 GET 요청 테스트"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_empty_favorites(self):
        """즐겨찾기가 없는 사용자의 GET 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 커스텀 페이지네이션 응답 구조 확인 (favorite_places 키 사용)
        self.assertIn('favorite_places', response.data)
        self.assertEqual(len(response.data['favorite_places']), 0)

    def test_get_with_favorites(self):
        """즐겨찾기가 있는 사용자의 GET 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        # 즐겨찾기 추가
        FavoritePlace.objects.create(user=self.user, place=self.place)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('favorite_places', response.data)
        self.assertEqual(len(response.data['favorite_places']), 1)
        
        favorite_data = response.data['favorite_places'][0]
        self.assertEqual(favorite_data['id'], self.place.id)
        self.assertEqual(favorite_data['content_id'], '12345')
        self.assertEqual(favorite_data['name'], '테스트 장소')

    def test_get_with_language_parameter(self):
        """언어 파라미터가 있는 GET 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        # 영어 번역 추가
        PlaceTranslation.objects.create(
            place=self.place,
            lang='en',
            name='Test Place',
            description='Test Description',
            address='123 Test-dong, Seoul'
        )
        
        # 즐겨찾기 추가
        FavoritePlace.objects.create(user=self.user, place=self.place)
        
        response = self.client.get(self.url, {'lang': 'en'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        favorite_data = response.data['favorite_places'][0]
        self.assertEqual(favorite_data['name'], 'Test Place')

    def test_get_pagination(self):
        """페이지네이션 테스트"""
        self.client.force_authenticate(user=self.user)
        
        # 여러 개의 즐겨찾기 장소 생성 (페이지 크기보다 많이)
        places = []
        for i in range(15):  # 페이지 크기가 9라면 2페이지 필요
            place = Place.objects.create(
                content_id=f'place_{i}',
                phone_number=f'02-1234-567{i}'
            )
            PlaceTranslation.objects.create(
                place=place,
                lang='ko',
                name=f'테스트 장소 {i}',
                address=f'주소 {i}'
            )
            FavoritePlace.objects.create(user=self.user, place=place)
            places.append(place)
        
        # 첫 번째 페이지
        response = self.client.get(self.url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('favorite_places', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        
        # 페이지 크기 확인 (최대 9개)
        self.assertLessEqual(len(response.data['favorite_places']), 9)
        self.assertEqual(response.data['count'], 15)
        self.assertIsNotNone(response.data['next'])  # 다음 페이지 존재
        self.assertIsNone(response.data['previous'])  # 이전 페이지 없음

    def test_get_ordering(self):
        """즐겨찾기 목록 정렬 테스트 (최신순)"""
        self.client.force_authenticate(user=self.user)
        
        # 두 개의 장소를 시간차를 두고 즐겨찾기에 추가
        place1 = Place.objects.create(content_id='place1')
        place2 = Place.objects.create(content_id='place2')
        
        PlaceTranslation.objects.create(
            place=place1, lang='ko', name='첫 번째 장소', address='주소1'
        )
        PlaceTranslation.objects.create(
            place=place2, lang='ko', name='두 번째 장소', address='주소2'
        )
        
        favorite1 = FavoritePlace.objects.create(user=self.user, place=place1)
        favorite2 = FavoritePlace.objects.create(user=self.user, place=place2)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['favorite_places']  # 'results' 대신 'favorite_places' 키 사용
        
        # 최신순으로 정렬되어 있는지 확인
        self.assertEqual(len(results), 2)
        # favorite2가 나중에 생성되었으므로 먼저 나와야 함
        self.assertEqual(results[0]['content_id'], 'place2')
        self.assertEqual(results[1]['content_id'], 'place1')


class FavoriteSubRegionAPIViewTest(APITestCase):
    """FavoriteSubRegionAPIView 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        # CustomUser 모델에 맞게 수정
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nickname='테스트유저',
            phone_number='010-1234-5678'
        )
        
        # Region 생성
        self.region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.region,
            lang='ko',
            name='서울특별시',
            description='대한민국의 수도',
            features='정치, 경제, 문화의 중심지'
        )
        
        # SubRegion 생성
        self.sub_region = SubRegion.objects.create(
            region=self.region,
            favorite_count=0
        )
        SubRegionTranslation.objects.create(
            sub_region=self.sub_region,
            lang='ko',
            name='강남구',
            description='서울의 대표적인 상업지구',
            features='고급 쇼핑몰과 레스토랑이 집중된 지역'
        )
        
        # URL 설정 - 실제 URLs 설정에 따라 수정 필요
        # 옵션 1: reverse 사용 (URLConf에 name이 정의된 경우)
        try:
            from django.urls import reverse
            self.url = reverse('favorite-subregions')  # 실제 URL 이름으로 수정
        except:
            # 옵션 2: 직접 URL 경로 지정
            self.url = '/api/favorites/subregions/'

    def test_post_without_authentication(self):
        """인증 없이 POST 요청 테스트"""
        data = {'sub_region_id': self.sub_region.id}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_with_authentication(self):
        """인증된 사용자의 POST 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        data = {'sub_region_id': self.sub_region.id}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            FavoriteSubRegion.objects.filter(user=self.user, sub_region=self.sub_region).exists()
        )

    def test_post_invalid_data(self):
        """잘못된 데이터로 POST 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        data = {'sub_region_id': 99999}  # 존재하지 않는 sub_region_id
        response = self.client.post(self.url, data)
        
        # RequestError 발생으로 인한 에러 응답 예상
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_post_missing_data(self):
        """필수 데이터 누락 POST 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        data = {}  # sub_region_id 누락
        response = self.client.post(self.url, data)
        
        # ValidationError 발생으로 인한 에러 응답 예상
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_get_without_authentication(self):
        """인증 없이 GET 요청 테스트"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_empty_favorites(self):
        """즐겨찾기가 없는 사용자의 GET 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 페이지네이션 응답 구조 확인 (favorite_subregions 키 사용 예상)
        response_data = response.data
        if 'favorite_subregions' in response_data:
            self.assertEqual(len(response_data['favorite_subregions']), 0)
        elif 'results' in response_data:
            self.assertEqual(len(response_data['results']), 0)

    def _get_results_from_response(self, response_data):
        """응답 데이터에서 결과 리스트를 추출하는 헬퍼 메서드"""
        # FavoriteSubRegionAPIView는 "favorite_subregions" 키를 사용
        if 'favorite_subregions' in response_data:
            return response_data['favorite_subregions']
        # 기본적으로는 "results" 키 사용
        return response_data.get('results', [])

    def test_get_with_favorites(self):
        """즐겨찾기가 있는 사용자의 GET 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        # 즐겨찾기 추가
        FavoriteSubRegion.objects.create(user=self.user, sub_region=self.sub_region)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        
        results = self._get_results_from_response(response_data)
        
        # 결과가 없으면 디버깅 정보 출력
        if len(results) == 0:
            print("Empty results. Response keys:", response_data.keys())
            print("Full response:", response_data)
            # 데이터베이스 확인
            favorites_count = FavoriteSubRegion.objects.filter(user=self.user).count()
            print("DB favorites count:", favorites_count)
        
        self.assertEqual(len(results), 1)
        
        favorite_data = results[0]
        self.assertEqual(favorite_data['id'], self.sub_region.id)
        self.assertEqual(favorite_data['name'], '강남구')

    def test_get_with_language_parameter(self):
        """언어 파라미터가 있는 GET 요청 테스트"""
        self.client.force_authenticate(user=self.user)
        
        # 영어 번역 추가
        SubRegionTranslation.objects.create(
            sub_region=self.sub_region,
            lang='en',
            name='Gangnam-gu',
            description='Representative commercial district of Seoul',
            features='Area with luxury shopping malls and restaurants'
        )
        
        # 즐겨찾기 추가
        FavoriteSubRegion.objects.create(user=self.user, sub_region=self.sub_region)
        
        response = self.client.get(self.url, {'lang': 'en'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        results = response_data.get('favorite_subregions') or response_data.get('results', [])
        favorite_data = results[0]
        self.assertEqual(favorite_data['name'], 'Gangnam-gu')

    def test_get_pagination(self):
        """페이지네이션 테스트"""
        self.client.force_authenticate(user=self.user)
        
        # 여러 개의 즐겨찾기 지역구 생성 (페이지 크기보다 많이)
        sub_regions = []
        for i in range(15):  # 페이지 크기가 9라면 2페이지 필요
            sub_region = SubRegion.objects.create(
                region=self.region,
                favorite_count=0
            )
            SubRegionTranslation.objects.create(
                sub_region=sub_region,
                lang='ko',
                name=f'테스트 지역구 {i}',
                description=f'설명 {i}',
                features=f'특징 {i}'
            )
            FavoriteSubRegion.objects.create(user=self.user, sub_region=sub_region)
            sub_regions.append(sub_region)
        
        # 첫 번째 페이지
        response = self.client.get(self.url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.data
        # 페이지네이션 필드 확인
        self.assertIn('count', response_data)
        self.assertIn('next', response_data)
        self.assertIn('previous', response_data)
        
        # 결과 확인
        results = response_data.get('favorite_subregions') or response_data.get('results', [])
        
        # 페이지 크기 확인 (최대 9개)
        self.assertLessEqual(len(results), 9)
        self.assertEqual(response_data['count'], 15)
        self.assertIsNotNone(response_data['next'])  # 다음 페이지 존재
        self.assertIsNone(response_data['previous'])  # 이전 페이지 없음

    def test_get_ordering(self):
        """즐겨찾기 목록 정렬 테스트 (최신순)"""
        self.client.force_authenticate(user=self.user)
        
        # 두 개의 지역구를 시간차를 두고 즐겨찾기에 추가
        sub_region1 = SubRegion.objects.create(region=self.region, favorite_count=0)
        sub_region2 = SubRegion.objects.create(region=self.region, favorite_count=0)
        
        SubRegionTranslation.objects.create(
            sub_region=sub_region1, lang='ko', name='첫 번째 지역구',
            description='설명1', features='특징1'
        )
        SubRegionTranslation.objects.create(
            sub_region=sub_region2, lang='ko', name='두 번째 지역구', 
            description='설명2', features='특징2'
        )
        
        favorite1 = FavoriteSubRegion.objects.create(user=self.user, sub_region=sub_region1)
        favorite2 = FavoriteSubRegion.objects.create(user=self.user, sub_region=sub_region2)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        results = response_data.get('favorite_subregions') or response_data.get('results', [])
        
        # 최신순으로 정렬되어 있는지 확인
        self.assertEqual(len(results), 2)
        # favorite2가 나중에 생성되었으므로 먼저 나와야 함
        self.assertEqual(results[0]['name'], '두 번째 지역구')
        self.assertEqual(results[1]['name'], '첫 번째 지역구')

    def test_toggle_favorite_add_and_remove(self):
        """즐겨찾기 추가 후 제거 테스트"""
        self.client.force_authenticate(user=self.user)
        
        data = {'sub_region_id': self.sub_region.id}
        
        # 첫 번째 POST: 즐겨찾기 추가
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            FavoriteSubRegion.objects.filter(user=self.user, sub_region=self.sub_region).exists()
        )
        
        # 두 번째 POST: 즐겨찾기 제거
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            FavoriteSubRegion.objects.filter(user=self.user, sub_region=self.sub_region).exists()
        )

    def test_get_with_location_data(self):
        """위치 정보가 포함된 즐겨찾기 조회 테스트"""
        self.client.force_authenticate(user=self.user)
        
        # GIS Point 필드 설정
        from django.contrib.gis.geos import Point
        self.sub_region.location = Point(127.0473, 37.5173)  # 경도, 위도
        self.sub_region.save()
        
        # 즐겨찾기 추가
        FavoriteSubRegion.objects.create(user=self.user, sub_region=self.sub_region)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        results = response_data.get('favorite_subregions') or response_data.get('results', [])
        favorite_data = results[0]
        
        self.assertEqual(favorite_data['latitude'], 37.5173)
        self.assertEqual(favorite_data['longitude'], 127.0473)

    def test_get_without_location_data(self):
        """위치 정보가 없는 즐겨찾기 조회 테스트"""
        self.client.force_authenticate(user=self.user)
        
        # location을 None으로 설정
        self.sub_region.location = None
        self.sub_region.save()
        
        # 즐겨찾기 추가
        FavoriteSubRegion.objects.create(user=self.user, sub_region=self.sub_region)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        results = response_data.get('favorite_subregions') or response_data.get('results', [])
        favorite_data = results[0]
        
        self.assertIsNone(favorite_data['latitude'])
        self.assertIsNone(favorite_data['longitude'])

    def test_get_favorite_count_field(self):
        """즐겨찾기 수 필드 테스트"""
        self.client.force_authenticate(user=self.user)
        
        # favorite_count 설정
        self.sub_region.favorite_count = 10
        self.sub_region.save()
        
        # 즐겨찾기 추가
        FavoriteSubRegion.objects.create(user=self.user, sub_region=self.sub_region)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        results = response_data.get('favorite_subregions') or response_data.get('results', [])
        favorite_data = results[0]
        
        # signals로 인해 증가했을 수도 있으므로 최소값만 확인
        self.assertGreaterEqual(favorite_data['favorite_count'], 10)