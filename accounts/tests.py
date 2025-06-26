from django.test import TestCase
from django.db import IntegrityError
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import Language


class LanguageModelTest(TestCase):
    """Language 모델 테스트"""

# 테스트용 데이터 준비
    def setUp(self):
        self.language_data = {
            'code': 'ko',
            'name': '한국어'
        }

    # Language 모델이 정상적으로 생성되는지 테스트
    def test_language_creation(self):
        language = Language.objects.create(**self.language_data)

        self.assertEqual(language.code, 'ko')
        self.assertEqual(language.name, '한국어')
        self.assertTrue(language.is_active)  # 기본값이 True인지
        self.assertIsNotNone(language.created_at)
        self.assertIsNotNone(language.updated_at)

# __str__ 메서드가 올바르게 동작하는지 테스트
    def test_language_str_method(self):
        language = Language.objects.create(**self.language_data)
        expected_str = "한국어 (ko)"

        self.assertEqual(str(language), expected_str)

#  언어 코드가 유니크한지 테스트, 첫 번째 언어 생성
    def test_language_code_unique(self):
        Language.objects.create(**self.language_data)

        # 같은 code로 두 번째 언어 생성 시도 -> 에러가 나야 함
        with self.assertRaises(IntegrityError):
            Language.objects.create(**self.language_data)

# 언어가 code 순으로 정렬되는지 테스트, 여러 언어 생성
    def test_language_ordering(self):
        Language.objects.create(code='zh', name='中文')
        Language.objects.create(code='en', name='English')
        Language.objects.create(code='ko', name='한국어')
        Language.objects.create(code='ja', name='日本語')

        # code 순으로 정렬되어 조회되는지 확인
        languages = Language.objects.all()
        codes = [lang.code for lang in languages]

        self.assertEqual(codes, ['en', 'ja', 'ko', 'zh'])

# is_active 필드의 기본값이 True인지 테스트
    def test_language_is_active_default(self):
        language = Language.objects.create(**self.language_data)
        self.assertTrue(language.is_active)


class LanguageAPITest(APITestCase):
    """Language API 테스트"""

# 테스트용 언어 데이터 생성
    def setUp(self):
        self.languages = [
            Language.objects.create(code='ko', name='한국어'),
            Language.objects.create(code='en', name='English'),
            Language.objects.create(code='ja', name='日本語'),
            Language.objects.create(code='zh', name='中文'),
        ]
        # 비활성화된 언어 (결과에 포함되면 안 됨)
        Language.objects.create(code='fr', name='Français', is_active=False)

# 언어 목록 조회 API 테스트
    def test_get_languages_list(self):
        url = reverse('language-list')  # URL name은 나중에 정의
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('languages', response.data)

        # 활성화된 언어만 4개 반환되는지 확인
        languages = response.data['languages']
        self.assertEqual(len(languages), 4)

        # 언어 코드 순으로 정렬되어 있는지 확인
        codes = [lang['code'] for lang in languages]
        self.assertEqual(codes, ['en', 'ja', 'ko', 'zh'])

        # 각 언어 객체가 올바른 필드를 가지고 있는지 확인
        first_language = languages[0]
        self.assertIn('code', first_language)
        self.assertIn('name', first_language)

# 유효한 언어 선택 API 테스트
    def test_post_language_selection_valid(self):
        url = reverse('language-select')  # URL name은 나중에 정의
        data = {'language': 'en'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('code', response.data)
        self.assertEqual(response.data['code'], 'en')

# 유효하지 않은 언어 선택 API 테스트
    def test_post_language_selection_invalid(self):
        url = reverse('language-select')
        data = {'language': 'invalid'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

# 비활성화된 언어 선택 시 에러 테스트
    def test_post_language_selection_inactive(self):
        url = reverse('language-select')
        data = {'language': 'fr'}  # 비활성화된 언어

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

# language 파라미터 없이 요청 시 에러 테스트
    def test_post_language_selection_missing_parameter(self):
        url = reverse('language-select')
        data = {}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)