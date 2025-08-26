
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from places.models import Place, PlaceTranslation
from favoraites.models import FavoritePlace


User = get_user_model()


class FavoritePlaceModelTest(TestCase):
    """FavoritePlace 모델 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        # CustomUser 필수 필드들 포함
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nickname='테스트닉네임',
            phone_number='010-1234-5678'
        )
            
        # Place 생성 (모든 필드가 nullable이므로 최소한으로 생성)
        self.place = Place.objects.create(
            content_id='test_place_001'
        )
        
        # PlaceTranslation 생성 (Place 이름을 표시하기 위해)
        self.place_translation = PlaceTranslation.objects.create(
            place=self.place,
            lang='ko',
            name='테스트 관광지',
            address='서울시 강남구 테스트로 123',
            description='테스트용 관광지입니다'
        )
    
    def test_favorite_place_creation(self):
        """즐겨찾기 생성 테스트"""
        favorite = FavoritePlace.objects.create(
            user=self.user,
            place=self.place
        )
        
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.place, self.place)
        self.assertIsNotNone(favorite.created_at)
    
    def test_favorite_place_str_method(self):
        """__str__ 메소드 테스트"""
        favorite = FavoritePlace.objects.create(
            user=self.user,
            place=self.place
        )
        
        # CustomUser는 nickname 필드를 가지고 있음
        expected_str = f"{self.user.nickname} - {self.place}"
        self.assertEqual(str(favorite), expected_str)
    
    def test_unique_together_constraint(self):
        """중복 방지 제약조건 테스트"""
        # 첫 번째 즐겨찾기 생성
        FavoritePlace.objects.create(
            user=self.user,
            place=self.place
        )
        
        # 같은 사용자, 같은 장소로 두 번째 즐겨찾기 생성 시도
        with self.assertRaises(IntegrityError):
            FavoritePlace.objects.create(
                user=self.user,
                place=self.place
            )
    
    def test_related_name_user(self):
        """user의 related_name 테스트"""
        favorite = FavoritePlace.objects.create(
            user=self.user,
            place=self.place
        )
        
        # 사용자의 즐겨찾기 목록 조회
        user_favorites = self.user.favorite_places.all()
        self.assertIn(favorite, user_favorites)
    
    def test_related_name_place(self):
        """place의 related_name 테스트"""
        favorite = FavoritePlace.objects.create(
            user=self.user,
            place=self.place
        )
        
        # 장소를 즐겨찾기한 사용자 목록 조회
        place_favorited_by = self.place.favorited_by.all()
        self.assertIn(favorite, place_favorited_by)
    
    def test_cascade_delete_user(self):
        """사용자 삭제 시 즐겨찾기도 함께 삭제되는지 테스트"""
        favorite = FavoritePlace.objects.create(
            user=self.user,
            place=self.place
        )
        favorite_id = favorite.id
        
        # 사용자 삭제
        self.user.delete()
        
        # 즐겨찾기도 함께 삭제되었는지 확인
        with self.assertRaises(FavoritePlace.DoesNotExist):
            FavoritePlace.objects.get(id=favorite_id)
    
    def test_cascade_delete_place(self):
        """장소 삭제 시 즐겨찾기도 함께 삭제되는지 테스트"""
        favorite = FavoritePlace.objects.create(
            user=self.user,
            place=self.place
        )
        favorite_id = favorite.id
        
        # 장소 삭제
        self.place.delete()
        
        # 즐겨찾기도 함께 삭제되었는지 확인
        with self.assertRaises(FavoritePlace.DoesNotExist):
            FavoritePlace.objects.get(id=favorite_id)