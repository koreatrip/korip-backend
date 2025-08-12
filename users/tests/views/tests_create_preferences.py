from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from categories.models import Category, SubCategory
from exceptions.error_code import ErrorCode
from preferences.services import PreferenceService
from unittest.mock import patch


class CreatePreferenceAPIViewTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            id=1,
            email="test@example.com",
            nickname="testuser",
            password="testpass123"
        )
        self.category = Category.objects.create()
        self.subcategory1 = SubCategory.objects.create(id=1, category=self.category)
        self.subcategory2 = SubCategory.objects.create(id=2, category=self.category)
        self.url = reverse('create-preferences', kwargs={'user_id': self.user.id})
    
    def test_successful_preference_creation(self):
        """정상적인 관심사 등록 테스트"""
        data = {"preferences": [1, 2]}
        
        with patch.object(PreferenceService, 'add_preference') as mock_service:
            mock_service.return_value = True
            response = self.client.post(self.url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            mock_service.assert_called_once_with(self.user.id, [1, 2])
    
    def test_user_not_found(self):
        """존재하지 않는 사용자 테스트"""
        url = reverse('create-preferences', kwargs={'user_id': 999})
        data = {"preferences": [1, 2]}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], ErrorCode.USER_NOT_FOUND.code)
        self.assertEqual(response.data['error_message'], ErrorCode.USER_NOT_FOUND.message)
    
    def test_invalid_data(self):
        """잘못된 데이터 테스트"""
        data = {"preferences": []}  # 빈 리스트
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], ErrorCode.INVALID_DATA.code)
        self.assertEqual(response.data['error_message'], ErrorCode.INVALID_DATA.message)
    
    def test_missing_preferences_field(self):
        """preferences 필드 누락 테스트"""
        data = {}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], ErrorCode.INVALID_DATA.code)
        self.assertEqual(response.data['error_message'], ErrorCode.INVALID_DATA.message)
    
    def test_service_exception_handling(self):
        """서비스 레이어 예외 처리 테스트"""
        data = {"preferences": [1, 2]}
        
        with patch.object(PreferenceService, 'add_preference') as mock_service:
            mock_service.side_effect = Exception("테스트 예외")
            response = self.client.post(self.url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['error_code'], ErrorCode.SERVER_ERROR.code)
            self.assertEqual(response.data['error_message'], ErrorCode.SERVER_ERROR.message)
    
    def test_non_existing_subcategories_in_request(self):
        """존재하지 않는 서브카테고리 ID 요청 테스트"""
        data = {"preferences": [1, 999]}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], ErrorCode.INVALID_SUBCATEGORY_ID.code)

        invalid_ids = [999]  # <- 추가
        expected_message = ErrorCode.INVALID_SUBCATEGORY_ID.format_message(invalid_ids)
        self.assertEqual(response.data['error_message'], expected_message)
    
    def test_max_preferences_limit(self):
        """최대 관심사 개수 제한 테스트"""
        for i in range(3, 13):
            SubCategory.objects.create(id=i, category=self.category)
        
        data = {"preferences": list(range(1, 12))}  # 11개
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], ErrorCode.INVALID_DATA.code)
        self.assertEqual(response.data['error_message'], ErrorCode.INVALID_DATA.message)
