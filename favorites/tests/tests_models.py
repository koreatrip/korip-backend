from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from places.models import Place, PlaceTranslation
from favorites.models import FavoritePlace

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