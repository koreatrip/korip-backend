from django.test import TestCase
from rest_framework import serializers
from users.serializers.auth.social_login import SocialLoginSerializer


class SocialLoginSerializerTest(TestCase):
    """SocialLoginSerializer 테스트"""

    def test_valid_data(self):
        """유효한 데이터로 시리얼라이저 테스트"""
        valid_data = {
            'phone_number': '8201012345678',
            'code': '4/0AeaYSHBqFw8xQwNxYz9h4KqJ5K5K5K5K5K5K5K5K5K5K5K5K5K5'
        }
        
        serializer = SocialLoginSerializer(data=valid_data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['phone_number'], valid_data['phone_number'])
        self.assertEqual(serializer.validated_data['code'], valid_data['code'])

    def test_missing_code(self):
        """code 필드가 없는 경우 테스트"""
        invalid_data = {}
        
        serializer = SocialLoginSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
        self.assertEqual(serializer.errors['code'][0], '이 필드는 필수 항목입니다.')

    def test_empty_code(self):
        """code 필드가 빈 문자열인 경우 테스트"""
        invalid_data = {
            'phone_number': '8201012345678',
            'code': ''
        }
        
        serializer = SocialLoginSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
        self.assertEqual(serializer.errors['code'][0], '이 필드는 blank일 수 없습니다.')

    def test_null_code(self):
        """code 필드가 null인 경우 테스트"""
        invalid_data = {
            'phone_number': '8201012345678',
            'code': None
        }
        
        serializer = SocialLoginSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
        self.assertEqual(serializer.errors['code'][0], '이 필드는 null일 수 없습니다.')

    def test_missing_phone_number(self):
        """phone_number 필드가 없는 경우 테스트"""
        invalid_data = {
            'code': '4/0AeaYSHBqFw8xQwNxYz9h4KqJ5K5K5K5K5'
        }

        serializer = SocialLoginSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)
        self.assertEqual(serializer.errors['phone_number'][0], '이 필드는 필수 항목입니다.')

    def test_empty_phone_number(self):
        """phone_number 필드가 빈 문자열인 경우 테스트"""
        invalid_data = {
            'phone_number': '',
            'code': '4/0AeaYSHBqFw8xQwNxYz9h4KqJ5K5K5K5K5'
        }

        serializer = SocialLoginSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)
        self.assertEqual(serializer.errors['phone_number'][0], '이 필드는 blank일 수 없습니다.')

    def test_null_phone_number(self):
        """phone_number 필드가 null인 경우 테스트"""
        invalid_data = {
            'phone_number': None,
            'code': '4/0AeaYSHBqFw8xQwNxYz9h4KqJ5K5K5K5K5'
        }

        serializer = SocialLoginSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)
        self.assertEqual(serializer.errors['phone_number'][0], '이 필드는 null일 수 없습니다.')
