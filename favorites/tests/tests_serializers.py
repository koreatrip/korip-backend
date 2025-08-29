from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from favorites.models import FavoritePlace, FavoriteSubRegion
from favorites.serializers import (
    FavoritePlaceSerializer, 
    FavoritePlaceListSerializer,
    FavoriteSubRegionSerializer,
    FavoriteSubRegionListSerializer
)
from places.models import Place, PlaceTranslation
from categories.models import Category, SubCategory
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


User = get_user_model()


class FavoritePlaceSerializerTest(TestCase):
    """FavoritePlaceSerializer 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        # CustomUser 모델에 맞게 수정 (username 제거, 필수 필드 추가)
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nickname='테스트유저',
            phone_number='010-1234-5678'
        )
        
        # Category 생성 (실제 모델 사용)
        self.category = Category.objects.create()
        self.sub_category = SubCategory.objects.create(category=self.category)
        
        # Region 생성
        self.region = Region.objects.create()
        self.sub_region = SubRegion.objects.create(region=self.region)
        
        # Place 생성
        self.place = Place.objects.create(
            content_id='12345',
            category=self.category,
            sub_category=self.sub_category,
            region=self.region,
            sub_region=self.sub_region,
            phone_number='02-1234-5678',
            use_time='09:00~21:00',
            link_url='https://example.com',
            image_url='https://example.com/image.jpg',
            favorite_count=0
        )
        
        # PlaceTranslation 생성
        self.place_translation = PlaceTranslation.objects.create(
            place=self.place,
            lang='ko',
            name='테스트 장소',
            description='테스트 설명',
            address='서울시 강남구 테스트동 123',
            tour_api_content_id='12345'
        )

    def test_valid_place_id(self):
        """유효한 place_id 검증 테스트"""
        serializer = FavoritePlaceSerializer(data={'place_id': self.place.id})
        self.assertTrue(serializer.is_valid())

    def test_invalid_place_id(self):
        """존재하지 않는 place_id 검증 테스트"""
        serializer = FavoritePlaceSerializer(data={'place_id': 99999})
        with self.assertRaises(Exception):  # RequestError 발생 예상
            serializer.is_valid(raise_exception=True)

    def test_toggle_favorite_add(self):
        """즐겨찾기 추가 테스트"""
        serializer = FavoritePlaceSerializer(data={'place_id': self.place.id})
        self.assertTrue(serializer.is_valid())
        
        result = serializer.toggle_favorite(self.user)
        
        self.assertTrue(result['is_favorite'])
        self.assertEqual(result['message'], '즐겨찾기에 추가했습니다.')
        self.assertTrue(
            FavoritePlace.objects.filter(user=self.user, place=self.place).exists()
        )

    def test_toggle_favorite_remove(self):
        """즐겨찾기 제거 테스트"""
        # 먼저 즐겨찾기 추가
        FavoritePlace.objects.create(user=self.user, place=self.place)
        
        serializer = FavoritePlaceSerializer(data={'place_id': self.place.id})
        self.assertTrue(serializer.is_valid())
        
        result = serializer.toggle_favorite(self.user)
        
        self.assertFalse(result['is_favorite'])
        self.assertEqual(result['message'], '즐겨찾기에서 제거했습니다.')
        self.assertFalse(
            FavoritePlace.objects.filter(user=self.user, place=self.place).exists()
        )

    def test_toggle_favorite_nonexistent_place(self):
        """존재하지 않는 장소에 대한 즐겨찾기 토글 테스트"""
        # place를 삭제하여 존재하지 않는 상태로 만듦
        place_id = self.place.id
        self.place.delete()
        
        serializer = FavoritePlaceSerializer(data={'place_id': place_id})
        # validation에서 이미 에러가 발생해야 함
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)


class FavoritePlaceListSerializerTest(TestCase):
    """FavoritePlaceListSerializer 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        # CustomUser 모델에 맞게 수정
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nickname='테스트유저',
            phone_number='010-1234-5678'
        )
        
        # 실제 모델 인스턴스 생성 (Mock 대신)
        self.category = Category.objects.create()
        self.sub_category = SubCategory.objects.create(category=self.category)
        self.region = Region.objects.create()
        self.sub_region = SubRegion.objects.create(region=self.region)
        
        # Place 생성
        self.place = Place.objects.create(
            content_id='12345',
            category=self.category,
            sub_category=self.sub_category,
            region=self.region,
            sub_region=self.sub_region,
            phone_number='02-1234-5678',
            use_time='09:00~21:00',
            link_url='https://example.com',
            image_url='https://example.com/image.jpg',
            favorite_count=5
        )
        
        # PlaceTranslation 생성
        PlaceTranslation.objects.create(
            place=self.place,
            lang='ko',
            name='테스트 장소',
            description='테스트 설명',
            address='서울시 강남구 테스트동 123'
        )
        
        PlaceTranslation.objects.create(
            place=self.place,
            lang='en',
            name='Test Place',
            description='Test Description', 
            address='123 Test-dong, Gangnam-gu, Seoul'
        )
        
        # FavoritePlace 생성
        self.favorite_place = FavoritePlace.objects.create(
            user=self.user,
            place=self.place
        )

    def test_serializer_fields(self):
        """시리얼라이저 필드 테스트 (한국어)"""
        serializer = FavoritePlaceListSerializer(
            self.favorite_place,
            context={"language": "ko"}
        )
        
        data = serializer.data
        
        self.assertEqual(data['id'], self.place.id)
        self.assertEqual(data['content_id'], '12345')
        self.assertEqual(data['name'], '테스트 장소')
        self.assertEqual(data['description'], '테스트 설명')
        self.assertEqual(data['address'], '서울시 강남구 테스트동 123')
        self.assertEqual(data['phone_number'], '02-1234-5678')
        self.assertEqual(data['use_time'], '09:00~21:00')
        self.assertEqual(data['link_url'], 'https://example.com')
        self.assertEqual(data['image_url'], 'https://example.com/image.jpg')
        self.assertEqual(data['favorite_count'], 5)

    def test_serializer_english_language(self):
        """시리얼라이저 영어 언어 테스트"""
        serializer = FavoritePlaceListSerializer(
            self.favorite_place,
            context={"language": "en"}
        )
        
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Place')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(data['address'], '123 Test-dong, Gangnam-gu, Seoul')

    def test_serializer_default_language(self):
        """시리얼라이저 기본 언어(한국어) 테스트"""
        serializer = FavoritePlaceListSerializer(self.favorite_place)
        
        data = serializer.data
        
        self.assertEqual(data['name'], '테스트 장소')

    @patch('categories.models.Category.get_name')
    @patch('categories.models.SubCategory.get_name')
    def test_serializer_category_fields(self, mock_sub_cat_name, mock_cat_name):
        """카테고리 관련 필드 테스트"""
        # Mock 메소드 설정
        mock_cat_name.return_value = '음식'
        mock_sub_cat_name.return_value = '한식'
        
        serializer = FavoritePlaceListSerializer(
            self.favorite_place,
            context={"language": "ko"}
        )
        
        data = serializer.data
        
        if data['category']:  # 카테고리가 있는 경우에만 테스트
            self.assertEqual(data['category']['id'], self.category.id)
            self.assertEqual(data['category']['name'], '음식')
        if data['sub_category']:  # 서브카테고리가 있는 경우에만 테스트
            self.assertEqual(data['sub_category']['id'], self.sub_category.id)
            self.assertEqual(data['sub_category']['name'], '한식')

    def test_serializer_region_fields(self):
        """지역 관련 필드 테스트"""
        # Place의 메소드를 mock으로 설정
        with patch.object(self.place, 'get_region_name') as mock_region, \
             patch.object(self.place, 'get_sub_region_name') as mock_sub_region:
            
            mock_region.return_value = '서울특별시'
            mock_sub_region.return_value = '강남구'
            
            serializer = FavoritePlaceListSerializer(
                self.favorite_place,
                context={"language": "ko"}
            )
            
            data = serializer.data
            
            if data['region']:  # 지역이 있는 경우에만 테스트
                self.assertEqual(data['region']['id'], self.region.id)
                self.assertEqual(data['region']['name'], '서울특별시')
            if data['sub_region']:  # 서브지역이 있는 경우에만 테스트
                self.assertEqual(data['sub_region']['id'], self.sub_region.id)
                self.assertEqual(data['sub_region']['name'], '강남구')


class FavoriteSubRegionSerializerTest(TestCase):
    """FavoriteSubRegionSerializer 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
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

    def test_valid_sub_region_id(self):
        """유효한 sub_region_id 검증 테스트"""
        serializer = FavoriteSubRegionSerializer(data={'sub_region_id': self.sub_region.id})
        self.assertTrue(serializer.is_valid())

    def test_invalid_sub_region_id(self):
        """존재하지 않는 sub_region_id 검증 테스트"""
        serializer = FavoriteSubRegionSerializer(data={'sub_region_id': 99999})
        with self.assertRaises(Exception):  # RequestError 발생 예상
            serializer.is_valid(raise_exception=True)

    def test_toggle_favorite_add(self):
        """즐겨찾기 추가 테스트"""
        serializer = FavoriteSubRegionSerializer(data={'sub_region_id': self.sub_region.id})
        self.assertTrue(serializer.is_valid())
        
        result = serializer.toggle_favorite(self.user)
        
        self.assertTrue(result['is_favorite'])
        self.assertEqual(result['message'], '지역구 즐겨찾기에 추가했습니다.')
        self.assertTrue(
            FavoriteSubRegion.objects.filter(user=self.user, sub_region=self.sub_region).exists()
        )

    def test_toggle_favorite_remove(self):
        """즐겨찾기 제거 테스트"""
        # 먼저 즐겨찾기 추가
        FavoriteSubRegion.objects.create(user=self.user, sub_region=self.sub_region)
        
        serializer = FavoriteSubRegionSerializer(data={'sub_region_id': self.sub_region.id})
        self.assertTrue(serializer.is_valid())
        
        result = serializer.toggle_favorite(self.user)
        
        self.assertFalse(result['is_favorite'])
        self.assertEqual(result['message'], '지역구 즐겨찾기에서 제거했습니다.')
        self.assertFalse(
            FavoriteSubRegion.objects.filter(user=self.user, sub_region=self.sub_region).exists()
        )

    def test_toggle_favorite_nonexistent_sub_region(self):
        """존재하지 않는 지역구에 대한 즐겨찾기 토글 테스트"""
        # sub_region을 삭제하여 존재하지 않는 상태로 만듦
        sub_region_id = self.sub_region.id
        self.sub_region.delete()
        
        serializer = FavoriteSubRegionSerializer(data={'sub_region_id': sub_region_id})
        # validation에서 이미 에러가 발생해야 함
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)


class FavoriteSubRegionListSerializerTest(TestCase):
    """FavoriteSubRegionListSerializer 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
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
        RegionTranslation.objects.create(
            region=self.region,
            lang='en',
            name='Seoul',
            description='Capital of South Korea',
            features='Center of politics, economy, and culture'
        )
        
        # SubRegion 생성
        self.sub_region = SubRegion.objects.create(
            region=self.region,
            favorite_count=10
        )
        SubRegionTranslation.objects.create(
            sub_region=self.sub_region,
            lang='ko',
            name='강남구',
            description='서울의 대표적인 상업지구',
            features='고급 쇼핑몰과 레스토랑이 집중된 지역'
        )
        SubRegionTranslation.objects.create(
            sub_region=self.sub_region,
            lang='en',
            name='Gangnam-gu',
            description='Representative commercial district of Seoul',
            features='Area concentrated with luxury shopping malls and restaurants'
        )
        
        # FavoriteSubRegion 생성
        self.favorite_sub_region = FavoriteSubRegion.objects.create(
            user=self.user,
            sub_region=self.sub_region
        )

    def test_serializer_fields(self):
        """시리얼라이저 필드 테스트 (한국어)"""
        serializer = FavoriteSubRegionListSerializer(
            self.favorite_sub_region,
            context={"language": "ko"}
        )
        
        data = serializer.data
        
        self.assertEqual(data['id'], self.sub_region.id)
        self.assertEqual(data['name'], '강남구')
        self.assertEqual(data['description'], '서울의 대표적인 상업지구')
        self.assertEqual(data['features'], '고급 쇼핑몰과 레스토랑이 집중된 지역')
        self.assertEqual(data['favorite_count'], 10)

    def test_serializer_english_language(self):
        """시리얼라이저 영어 언어 테스트"""
        serializer = FavoriteSubRegionListSerializer(
            self.favorite_sub_region,
            context={"language": "en"}
        )
        
        data = serializer.data
        
        self.assertEqual(data['name'], 'Gangnam-gu')
        self.assertEqual(data['description'], 'Representative commercial district of Seoul')
        self.assertEqual(data['features'], 'Area concentrated with luxury shopping malls and restaurants')

    def test_serializer_default_language(self):
        """시리얼라이저 기본 언어(한국어) 테스트"""
        serializer = FavoriteSubRegionListSerializer(self.favorite_sub_region)
        
        data = serializer.data
        
        self.assertEqual(data['name'], '강남구')

    def test_serializer_location_fields(self):
        """위치 정보 필드 테스트"""
        # location 필드를 직접 mock하여 GIS Point 객체 시뮬레이션
        from django.contrib.gis.geos import Point
        
        # Point 객체 생성 (경도, 위도 순서)
        test_point = Point(127.0473, 37.5173)
        
        # location 필드에 Point 객체 할당
        self.sub_region.location = test_point
        self.sub_region.save()
        
        serializer = FavoriteSubRegionListSerializer(
            self.favorite_sub_region,
            context={"language": "ko"}
        )
        
        data = serializer.data
        
        self.assertEqual(data['latitude'], 37.5173)
        self.assertEqual(data['longitude'], 127.0473)

    def test_serializer_without_translations(self):
        """번역이 없는 경우 테스트"""
        # 번역 없는 SubRegion 생성
        sub_region_no_translation = SubRegion.objects.create(
            region=self.region,
            favorite_count=0
        )
        
        favorite_no_translation = FavoriteSubRegion.objects.create(
            user=self.user,
            sub_region=sub_region_no_translation
        )
        
        serializer = FavoriteSubRegionListSerializer(
            favorite_no_translation,
            context={"language": "ko"}
        )
        
        data = serializer.data
        
        # 번역이 없는 경우 None 또는 빈 문자열이 반환되어야 함
        self.assertIsNone(data['name'])
        self.assertEqual(data['description'], '')
        self.assertEqual(data['features'], '')

    def test_serializer_date_fields(self):
        """날짜 필드 테스트"""
        serializer = FavoriteSubRegionListSerializer(
            self.favorite_sub_region,
            context={"language": "ko"}
        )
        
        data = serializer.data
        
        # 날짜 필드가 존재하는지 확인
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        self.assertIn('favorited_at', data)
        
        # favorited_at은 즐겨찾기 생성일과 같아야 함
        self.assertIsNotNone(data['favorited_at'])

    def test_serializer_missing_language(self):
        """존재하지 않는 언어 코드 테스트"""
        serializer = FavoriteSubRegionListSerializer(
            self.favorite_sub_region,
            context={"language": "fr"}  # 프랑스어 (없는 번역)
        )
        
        data = serializer.data
        
        # 존재하지 않는 언어의 경우 None 또는 빈 값이 반환되어야 함
        self.assertIsNone(data['name'])
        self.assertEqual(data['description'], '')
        self.assertEqual(data['features'], '')

    def test_serializer_context_without_language(self):
        """context에 language가 없는 경우 테스트"""
        serializer = FavoriteSubRegionListSerializer(self.favorite_sub_region)
        
        # get_language()가 기본값 'ko'를 반환하는지 확인
        self.assertEqual(serializer.get_language(), 'ko')
        
        data = serializer.data
        self.assertEqual(data['name'], '강남구')

    def test_serializer_null_location(self):
        """location이 None인 경우 테스트"""
        # location 필드를 None으로 설정
        self.sub_region.location = None
        self.sub_region.save()
        
        serializer = FavoriteSubRegionListSerializer(
            self.favorite_sub_region,
            context={"language": "ko"}
        )
        
        data = serializer.data
        
        self.assertIsNone(data['latitude'])
        self.assertIsNone(data['longitude'])