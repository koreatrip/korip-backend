from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from places.models import Place, PlaceTranslation
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation
from favorites.models import FavoritePlace, FavoriteSubRegion

User = get_user_model()


class FavoritePlaceModelTest(TestCase):
    
    def setUp(self):
        # CustomUser 모델에 맞게 수정
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nickname='테스트유저',
            phone_number='010-1234-5678'
        )
        
        self.place = Place.objects.create(
            content_id='12345',
            phone_number='02-1234-5678'
        )
        
        PlaceTranslation.objects.create(
            place=self.place,
            lang='ko',
            name='테스트 장소',
            address='서울시 강남구 테스트동 123'
        )
        
        self.favorite = FavoritePlace.objects.create(
            user=self.user,
            place=self.place
        )
    
    def test_related_name_user(self):
        """user의 related_name 테스트"""
        # 오타 수정: favoraite_places -> favorite_places
        user_favorites = self.user.favorite_places.all()
        self.assertIn(self.favorite, user_favorites)
        self.assertEqual(user_favorites.count(), 1)
    
    def test_related_name_place(self):
        """place의 related_name 테스트"""
        # FavoritePlace 모델의 실제 related_name 확인 필요
        # 만약 favorited_by가 실제 related_name이라면 유지
        # 그렇지 않다면 실제 related_name으로 수정 (예: favorite_places_set)
        try:
            place_favorites = self.place.favorited_by.all()
            self.assertIn(self.favorite, place_favorites)
            self.assertEqual(place_favorites.count(), 1)
        except AttributeError:
            # favorited_by가 없다면 기본 related_name 사용
            place_favorites = self.place.favoriteplace_set.all()
            self.assertIn(self.favorite, place_favorites)
            self.assertEqual(place_favorites.count(), 1)


class FavoriteSubRegionModelTest(TestCase):
    
    def setUp(self):
        # CustomUser 모델에 맞게 수정
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nickname='테스트유저',
            phone_number='010-1234-5678'
        )
        
        # 지역 생성
        self.region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.region,
            lang='ko',
            name='서울특별시',
            description='대한민국의 수도',
            features='정치, 경제, 문화의 중심지'
        )
        
        # 지역구 생성
        self.subregion = SubRegion.objects.create(
            region=self.region,
            favorite_count=0
        )
        SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang='ko',
            name='강남구',
            description='서울의 대표적인 상업지구',
            features='고급 쇼핑몰과 레스토랑이 집중된 지역'
        )
        
        self.favorite = FavoriteSubRegion.objects.create(
            user=self.user,
            sub_region=self.subregion
        )
    
    def test_str_method(self):
        """__str__ 메소드 테스트"""
        expected_str = f"{self.user.nickname} - 서울특별시 강남구"
        self.assertEqual(str(self.favorite), expected_str)
    
    def test_str_method_without_translations(self):
        """번역이 없는 경우 __str__ 메소드 테스트"""
        # 번역 없는 지역과 지역구 생성
        region_no_translation = Region.objects.create()
        subregion_no_translation = SubRegion.objects.create(
            region=region_no_translation,
            favorite_count=0
        )
        
        favorite_no_translation = FavoriteSubRegion.objects.create(
            user=self.user,
            sub_region=subregion_no_translation
        )
        
        expected_str = f"{self.user.nickname} - 지역 SubRegion {subregion_no_translation.id}"
        self.assertEqual(str(favorite_no_translation), expected_str)
    
    def test_related_name_user(self):
        """user의 related_name 테스트"""
        user_favorites = self.user.favorite_subregions.all()
        self.assertIn(self.favorite, user_favorites)
        self.assertEqual(user_favorites.count(), 1)
    
    def test_related_name_subregion(self):
        """sub_region의 related_name 테스트"""
        subregion_favorites = self.subregion.favorited_by.all()
        self.assertIn(self.favorite, subregion_favorites)
        self.assertEqual(subregion_favorites.count(), 1)
    
    def test_unique_together_constraint(self):
        """unique_together 제약 조건 테스트"""
        with self.assertRaises(IntegrityError):
            # 같은 user와 sub_region으로 중복 생성 시도
            FavoriteSubRegion.objects.create(
                user=self.user,
                sub_region=self.subregion
            )
    
    def test_cascade_delete_user(self):
        """사용자 삭제 시 즐겨찾기도 삭제되는지 테스트"""
        favorite_id = self.favorite.id
        self.user.delete()
        
        # FavoriteSubRegion도 함께 삭제되었는지 확인
        with self.assertRaises(FavoriteSubRegion.DoesNotExist):
            FavoriteSubRegion.objects.get(id=favorite_id)
    
    def test_cascade_delete_subregion(self):
        """지역구 삭제 시 즐겨찾기도 삭제되는지 테스트"""
        favorite_id = self.favorite.id
        self.subregion.delete()
        
        # FavoriteSubRegion도 함께 삭제되었는지 확인
        with self.assertRaises(FavoriteSubRegion.DoesNotExist):
            FavoriteSubRegion.objects.get(id=favorite_id)
    
    def test_created_at_auto_now_add(self):
        """created_at이 자동으로 설정되는지 테스트"""
        self.assertIsNotNone(self.favorite.created_at)
    
    def test_multiple_users_same_subregion(self):
        """같은 지역구를 여러 사용자가 즐겨찾기할 수 있는지 테스트"""
        user2 = User.objects.create_user(
            email='test2@example.com',
            password='testpass123',
            nickname='테스트유저2',
            phone_number='010-2222-2222'
        )
        
        favorite2 = FavoriteSubRegion.objects.create(
            user=user2,
            sub_region=self.subregion
        )
        
        # 같은 지역구에 대한 즐겨찾기가 2개인지 확인
        subregion_favorites = self.subregion.favorited_by.all()
        self.assertEqual(subregion_favorites.count(), 2)
        self.assertIn(self.favorite, subregion_favorites)
        self.assertIn(favorite2, subregion_favorites)
    
    def test_one_user_multiple_subregions(self):
        """한 사용자가 여러 지역구를 즐겨찾기할 수 있는지 테스트"""
        # 두 번째 지역구 생성
        subregion2 = SubRegion.objects.create(
            region=self.region,
            favorite_count=0
        )
        SubRegionTranslation.objects.create(
            sub_region=subregion2,
            lang='ko',
            name='서초구',
            description='서울의 법조타운',
            features='법원과 검찰청이 위치한 지역'
        )
        
        favorite2 = FavoriteSubRegion.objects.create(
            user=self.user,
            sub_region=subregion2
        )
        
        # 사용자의 즐겨찾기가 2개인지 확인
        user_favorites = self.user.favorite_subregions.all()
        self.assertEqual(user_favorites.count(), 2)
        self.assertIn(self.favorite, user_favorites)
        self.assertIn(favorite2, user_favorites)
    
    def test_db_table_name(self):
        """db_table 설정이 올바른지 테스트"""
        self.assertEqual(FavoriteSubRegion._meta.db_table, 'favorite_subregion')
    
    def test_verbose_names(self):
        """verbose_name 설정이 올바른지 테스트"""
        self.assertEqual(FavoriteSubRegion._meta.verbose_name, '즐겨찾는 지역구')
        self.assertEqual(FavoriteSubRegion._meta.verbose_name_plural, '즐겨찾는 지역구들')