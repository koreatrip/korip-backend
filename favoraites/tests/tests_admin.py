from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory

from places.models import Place, PlaceTranslation
from favoraites.models import FavoritePlace
from favoraites.admin import FavoritePlaceAdmin

User = get_user_model()


class FavoritePlaceAdminTest(TestCase):
    """FavoritePlaceAdmin 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = FavoritePlaceAdmin(FavoritePlace, self.site)
        
        # 사용자 생성 (CustomUser 모델의 필수 필드들 포함)
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nickname='테스트닉네임',
            phone_number='010-1234-5678'
        )
        
        # 관리자 사용자 생성
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            nickname='관리자',
            phone_number='010-0000-0000'
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
        
        # 즐겨찾기 생성
        self.favorite = FavoritePlace.objects.create(
            user=self.user,
            place=self.place
        )
    
    def test_get_user_nickname(self):
        """get_user_nickname 메소드 테스트"""
        result = self.admin.get_user_nickname(self.favorite)
        expected = self.user.nickname  # nickname 필드는 필수이므로 직접 사용
        self.assertEqual(result, expected)
    
    def test_get_place_name(self):
        """get_place_name 메소드 테스트"""
        result = self.admin.get_place_name(self.favorite)
        expected = self.place.get_name('ko') or self.place.content_id or f"Place {self.place.id}"
        self.assertEqual(result, expected)
    
    def test_get_place_category(self):
        """get_place_category 메소드 테스트"""
        result = self.admin.get_place_category(self.favorite)
        expected = str(self.place.category) if self.place.category else '미분류'
        self.assertEqual(result, expected)
    
    def test_has_add_permission_superuser(self):
        """슈퍼유저의 추가 권한 테스트"""
        request = self.factory.get('/')
        request.user = self.admin_user
        
        self.assertTrue(self.admin.has_add_permission(request))
    
    def test_has_add_permission_regular_user(self):
        """일반 사용자의 추가 권한 테스트"""
        request = self.factory.get('/')
        request.user = self.user
        
        self.assertFalse(self.admin.has_add_permission(request))
    
    def test_has_change_permission_staff(self):
        """스태프의 수정 권한 테스트"""
        self.user.is_staff = True
        self.user.save()
        
        request = self.factory.get('/')
        request.user = self.user
        
        self.assertTrue(self.admin.has_change_permission(request))
    
    def test_has_delete_permission_superuser(self):
        """슈퍼유저의 삭제 권한 테스트"""
        request = self.factory.get('/')
        request.user = self.admin_user
        
        self.assertTrue(self.admin.has_delete_permission(request))
    
    def test_queryset_optimization(self):
        """쿼리셋 최적화 테스트"""
        request = self.factory.get('/')
        request.user = self.admin_user
        
        queryset = self.admin.get_queryset(request)
        
        # select_related가 적용되었는지 확인
        self.assertIn('user', queryset.query.select_related)
        self.assertIn('place', queryset.query.select_related)