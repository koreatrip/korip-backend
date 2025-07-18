from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from django.contrib import admin
from users.admin import CustomUserAdmin, CustomUserCreationForm, CustomUserChangeForm
from users.models import CustomUser

User = get_user_model()


class CustomUserAdminTest(TestCase):
    """CustomUserAdmin 테스트"""
    
    def setUp(self):
        self.site = AdminSite()
        self.admin = CustomUserAdmin(CustomUser, self.site)
        
    def test_admin_registered(self):
        """Admin에 CustomUser가 등록되었는지 확인"""
        self.assertIn(CustomUser, admin.site._registry)
        
    def test_list_display(self):
        """list_display 설정 확인"""
        expected = (
            "email", "nickname", "phone_number", "is_social", 
            "is_active", "is_staff", "is_superuser", "created_at"
        )
        self.assertEqual(self.admin.list_display, expected)
        
    def test_search_fields(self):
        """search_fields 설정 확인"""
        expected = ("email", "nickname", "phone_number")
        self.assertEqual(self.admin.search_fields, expected)
        
    def test_list_filter(self):
        """list_filter 설정 확인"""
        expected = ("is_active", "is_staff", "is_superuser", "is_social", "created_at")
        self.assertEqual(self.admin.list_filter, expected)
        
    def test_readonly_fields(self):
        """readonly_fields 설정 확인"""
        expected = ("created_at", "updated_at", "last_login")
        self.assertEqual(self.admin.readonly_fields, expected)


class CustomUserCreationFormTest(TestCase):
    """CustomUserCreationForm 테스트"""
    
    def test_form_fields(self):
        """폼 필드 설정 확인"""
        form = CustomUserCreationForm()
        self.assertEqual(form.Meta.model, CustomUser)
        self.assertEqual(form.Meta.fields, ("email", "nickname", "phone_number"))
        
    def test_form_valid_data(self):
        """유효한 데이터로 폼 생성"""
        form_data = {
            'email': 'test@example.com',
            'nickname': 'testuser',
            'phone_number': '010-1234-5678',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_form_save(self):
        """폼 저장 확인"""
        form_data = {
            'email': 'test@example.com',
            'nickname': 'testuser',
            'phone_number': '010-1234-5678',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
        form = CustomUserCreationForm(data=form_data)
        if form.is_valid():
            user = form.save()
            self.assertEqual(user.email, 'test@example.com')
            self.assertEqual(user.nickname, 'testuser')


class CustomUserChangeFormTest(TestCase):
    """CustomUserChangeForm 테스트"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nickname='testuser',
            phone_number='010-1234-5678'
        )
        
    def test_form_fields(self):
        """폼 필드 설정 확인"""
        form = CustomUserChangeForm(instance=self.user)
        self.assertEqual(form.Meta.model, CustomUser)
        expected_fields = (
            "email", "nickname", "phone_number", "is_social", 
            "is_active", "is_staff", "is_superuser"
        )
        self.assertEqual(form.Meta.fields, expected_fields)
        
    def test_form_initial_data(self):
        """폼 초기 데이터 확인"""
        form = CustomUserChangeForm(instance=self.user)
        self.assertEqual(form.initial['email'], 'test@example.com')
        self.assertEqual(form.initial['nickname'], 'testuser')


class CustomUserAdminViewTest(TestCase):
    """Admin 뷰 접근 테스트"""
    
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass123',
            nickname='admin',
            phone_number='010-0000-0000'
        )
        self.client = Client()
        self.client.login(email='admin@test.com', password='adminpass123')
        
    def test_admin_access(self):
        """Admin 페이지 접근 확인"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
