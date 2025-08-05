from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.contrib import admin
from unittest.mock import Mock, patch
from users.models import CustomUser
from categories.models import Category, SubCategory
from preferences.models import UserPreference
from preferences.admin import UserPreferenceAdmin


class UserPreferenceAdminTest(TestCase):
    """UserPreferenceAdmin 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.site = AdminSite()
        self.admin = UserPreferenceAdmin(UserPreference, self.site)
        
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            nickname='testuser',
            password='testpass123'
        )
        
        self.superuser = CustomUser.objects.create_superuser(
            email='admin@example.com',
            nickname='admin',
            password='adminpass123'
        )
        
        # Mock SubCategory
        test_category = Category.objects.create()
        self.subcategory = SubCategory.objects.create(category=test_category)
    
    def test_list_display(self):
        """list_display 설정 테스트"""
        expected_display = ('id', 'user', 'subcategory', 'created_at')
        self.assertEqual(self.admin.list_display, expected_display)
    
    def test_list_filter(self):
        """list_filter 설정 테스트"""
        expected_filters = ('created_at', 'subcategory')
        self.assertEqual(self.admin.list_filter, expected_filters)
    
    def test_search_fields(self):
        """search_fields 설정 테스트"""
        expected_fields = ('user__email', 'user__nickname', 'subcategory__name')
        self.assertEqual(self.admin.search_fields, expected_fields)
    
    def test_autocomplete_fields(self):
        """autocomplete_fields 설정 테스트"""
        expected_fields = ('user', 'subcategory')
        self.assertEqual(self.admin.autocomplete_fields, expected_fields)
    
    def test_ordering(self):
        """ordering 설정 테스트"""
        expected_ordering = ('-created_at',)
        self.assertEqual(self.admin.ordering, expected_ordering)
    
    def test_readonly_fields(self):
        """readonly_fields 설정 테스트"""
        expected_fields = ('created_at',)
        self.assertEqual(self.admin.readonly_fields, expected_fields)
    
    def test_fieldsets(self):
        """fieldsets 설정 테스트"""
        expected_fieldsets = (
            (None, {
                'fields': ('user', 'subcategory', 'created_at')
            }),
        )
        self.assertEqual(self.admin.fieldsets, expected_fieldsets)
    
    def test_admin_registration(self):
        """Admin 등록 테스트"""
        self.assertIn(UserPreference, admin.site._registry)
        self.assertIsInstance(admin.site._registry[UserPreference], UserPreferenceAdmin)
    
    def test_admin_permissions(self):
        """Admin 권한 테스트"""
        request = HttpRequest()
        request.user = self.superuser
        
        # 기본 권한 메서드들이 제대로 동작하는지 확인
        self.assertTrue(self.admin.has_view_permission(request))
        self.assertTrue(self.admin.has_add_permission(request))
        self.assertTrue(self.admin.has_change_permission(request))
        self.assertTrue(self.admin.has_delete_permission(request))
    
    def test_admin_queryset(self):
        """Admin queryset 테스트"""
        with patch('categories.models.SubCategory.objects') as mock_subcategory:
            mock_subcategory.get.return_value = self.subcategory
            
            # 테스트 데이터 생성
            preference = UserPreference.objects.create(
                user=self.user,
                subcategory=self.subcategory
            )
            
            request = HttpRequest()
            request.user = self.superuser
            
            # queryset이 제대로 반환되는지 확인
            queryset = self.admin.get_queryset(request)
            self.assertIn(preference, queryset)
