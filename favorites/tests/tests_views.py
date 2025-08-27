from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch, MagicMock
import json

from favorites.models import FavoritePlace
from favorites.serializers import FavoritePlaceSerializer, FavoritePlaceListSerializer
from places.models import Place, PlaceTranslation
from categories.models import Category, SubCategory
from regions.models import Region, SubRegion


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
        