from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.utils import validate_language, get_supported_languages, get_language_name


# 언어 유틸리티 함수 테스트
class LanguageUtilsTest(TestCase):

    # 유효한 언어 코드 검증 테스트
    def test_validate_language_with_valid_code(self):
        self.assertEqual(validate_language('ko'), 'ko')
        self.assertEqual(validate_language('en'), 'en')
        self.assertEqual(validate_language('jp'), 'jp')
        self.assertEqual(validate_language('cn'), 'cn')

    # 유효하지 않은 언어 코드는 기본값 반환
    def test_validate_language_with_invalid_code(self):
        self.assertEqual(validate_language('fr'), 'ko')
        self.assertEqual(validate_language(''), 'ko')
        self.assertEqual(validate_language(None), 'ko')
        self.assertEqual(validate_language('invalid'), 'ko')

    # 지원 언어 목록 반환 테스트
    def test_get_supported_languages(self):
        languages = get_supported_languages()
        self.assertIn('ko', languages)
        self.assertIn('en', languages)
        self.assertIn('jp', languages)
        self.assertIn('cn', languages)
        self.assertEqual(languages['ko'], '한국어')

    # 언어 이름 반환 테스트
    def test_get_language_name(self):
        self.assertEqual(get_language_name('ko'), '한국어')
        self.assertEqual(get_language_name('en'), 'English')
        self.assertEqual(get_language_name('invalid'), '한국어')


# 언어 설정 API 테스트
class LanguageAPITest(APITestCase):

    # 지원 언어 목록 조회 API 테스트
    def test_language_list_api(self):
        response = self.client.get('/api/languages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('supported_languages', response.data)
        self.assertIn('ko', response.data['supported_languages'])

    # 유효한 언어 파라미터로 API 호출
    def test_language_api_with_valid_parameter(self):
        response = self.client.get('/api/languages/?lang=en')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_language'], 'en')

    # 유효하지 않은 언어 파라미터는 기본값 사용
    def test_language_api_with_invalid_parameter(self):
        response = self.client.get('/api/languages/?lang=invalid')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_language'], 'ko')