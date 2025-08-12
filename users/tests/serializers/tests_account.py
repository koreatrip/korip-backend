from django.test import TestCase
from unittest.mock import Mock, patch
from users.serializers.account import (
    FindAccountSerializer,
    FindPasswordSerializer,
    ChangePasswordSerializer,
    UserInfoSerializer
)
from users.models import CustomUser
from categories.models import SubCategory, Category, SubCategoryTranslation, CategoryTranslation
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import RequestError


class FindAccountSerializerTest(TestCase):

    def test_valid_phone_number(self):
        data = {'phone_number': '01012345678'}
        serializer = FindAccountSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['phone_number'], '01012345678')

    def test_blank_phone_number(self):
        data = {'phone_number': ''}
        serializer = FindAccountSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)

    def test_missing_phone_number(self):
        data = {}
        serializer = FindAccountSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)


class FindPasswordSerializerTest(TestCase):
    
    def test_valid_email(self):
        data = {'email': 'test@example.com'}
        serializer = FindPasswordSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], data['email'])

    def test_invalid_email_format(self):
        data = {'email': 'invalid-email'}
        serializer = FindPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_missing_email(self):
        data = {}
        serializer = FindPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_blank_email(self):
        data = {'email': ''}
        serializer = FindPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class ChangePasswordSerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="changepw@example.com",
            password="OldPass123!",
            nickname="pw_user"
        )

    def _mock_request(self):
        class DummyRequest:
            user = self.user
        return DummyRequest()

    def test_change_password_success(self):
        """비밀번호 변경 성공"""
        data = {
            "current_password": "OldPass123!",
            "new_password": "NewSecure123!"
        }
        serializer = ChangePasswordSerializer(data=data, context={"request": self._mock_request()})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_change_password_same_as_current(self):
        """비밀번호 변경 실패 (현재 비밀번호와 동일)"""
        data = {
            "current_password": "OldPass123!",
            "new_password": "OldPass123!"
        }
        serializer = ChangePasswordSerializer(data=data, context={"request": self._mock_request()})
        with self.assertRaises(RequestError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(context.exception.detail["error_code"], ErrorCode.SAME_CURRENT_PASSWORD.code)

    def test_change_password_weak(self):
        """비밀번호 변경 실패 (너무 약한 새 비밀번호)"""
        data = {
            "current_password": "OldPass123!",
            "new_password": "123"
        }
        serializer = ChangePasswordSerializer(data=data, context={"request": self._mock_request()})
        with self.assertRaises(RequestError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(context.exception.detail["error_code"], ErrorCode.INVALID_PASSWORD.code)


class UserInfoSerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="userinfo@example.com",
            password="TestPass123!",
            nickname="test_user",
            phone_number="01012345678"
        )
        
        # Create test category first
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="테스트 카테고리"
        )
        CategoryTranslation.objects.create(
            category=self.category,
            lang="en",
            name="Test Category"
        )
        
        # Create test subcategories
        self.subcategory1 = SubCategory.objects.create(category=self.category)
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory1,
            lang="ko",
            name="서브카테고리1"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory1,
            lang="en", 
            name="SubCategory1"
        )
        
        self.subcategory2 = SubCategory.objects.create(category=self.category)
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory2,
            lang="ko",
            name="서브카테고리2"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory2,
            lang="en",
            name="SubCategory2"
        )
        
        self.subcategory3 = SubCategory.objects.create(category=self.category)
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory3,
            lang="ko",
            name="서브카테고리3"
        )
        SubCategoryTranslation.objects.create(
            sub_category=self.subcategory3,
            lang="en",
            name="SubCategory3"
        )

    def _mock_request(self, lang='ko'):
        """Mock request with query parameters"""
        request = Mock()
        request.query_params = {'lang': lang}
        return request

    def test_serializer_fields(self):
        """시리얼라이저 필드 확인"""
        serializer = UserInfoSerializer(instance=self.user)
        data = serializer.data
        
        expected_fields = [
            'id', 'email', 'name', 'phone_number',
            'login_type', 'is_social', 'is_active', 'created_at', 'updated_at',
            'preferences_display'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
        
        # name field는 nickname을 source로 사용
        self.assertEqual(data['name'], self.user.nickname)

    def test_read_only_fields(self):
        """읽기 전용 필드 확인"""
        data = {
            'id': 999,
            'email': 'newemail@example.com',
            'login_type': 'email',
            'is_social': True,
            'is_active': False,
            'name': 'updated_name',
            'phone_number': '01087654321'
        }
        
        serializer = UserInfoSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        
        # 읽기 전용 필드들은 변경되지 않음
        self.assertNotEqual(updated_user.id, 999)
        self.assertNotEqual(updated_user.email, 'newemail@example.com')
        
        # 쓰기 가능한 필드들은 변경됨
        self.assertEqual(updated_user.nickname, 'updated_name')
        self.assertEqual(updated_user.phone_number, '01087654321')

    def test_update_nickname_and_phone(self):
        """닉네임과 전화번호 업데이트 테스트"""
        data = {
            'name': 'updated_nickname',
            'phone_number': '01099999999'
        }
        
        serializer = UserInfoSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        self.assertEqual(updated_user.nickname, 'updated_nickname')
        self.assertEqual(updated_user.phone_number, '01099999999')

    @patch('preferences.services.PreferenceService.add_preference')
    def test_update_preferences_success(self, mock_add_preference):
        """선호도 업데이트 성공 테스트"""
        data = {
            'preferences': [self.subcategory1.id, self.subcategory2.id]
        }
        
        serializer = UserInfoSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        
        # PreferenceService.add_preference가 올바른 파라미터로 호출되었는지 확인
        # 순서는 상관없으므로 set으로 비교
        mock_add_preference.assert_called_once()
        call_args = mock_add_preference.call_args
        called_user_id = call_args[1]['user_id']
        called_subcategory_ids = set(call_args[1]['subcategory_ids'])
        expected_subcategory_ids = {self.subcategory1.id, self.subcategory2.id}
        
        self.assertEqual(called_user_id, self.user.id)
        self.assertEqual(called_subcategory_ids, expected_subcategory_ids)

    def test_update_preferences_too_many(self):
        """선호도 개수 초과 테스트 (최대 9개)"""
        # 10개의 서브카테고리 생성
        subcategories = []
        for i in range(10):
            subcategory = SubCategory.objects.create(category=self.category)
            SubCategoryTranslation.objects.create(
                sub_category=subcategory,
                lang="ko",
                name=f"서브카테고리{i+4}"
            )
            SubCategoryTranslation.objects.create(
                sub_category=subcategory,
                lang="en",
                name=f"SubCategory{i+4}"
            )
            subcategories.append(subcategory.id)
        
        data = {
            'preferences': subcategories
        }
        
        serializer = UserInfoSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        with self.assertRaises(RequestError) as context:
            serializer.save()
        
        self.assertEqual(context.exception.detail["error_code"], ErrorCode.TOO_MANY_PREFERENCES.code)

    def test_update_preferences_invalid_subcategory_id(self):
        """존재하지 않는 서브카테고리 ID 테스트"""
        invalid_id = 99999
        data = {
            'preferences': [self.subcategory1.id, invalid_id]
        }
        
        serializer = UserInfoSerializer(instance=self.user, data=data, partial=True)
        # 시리얼라이저 validation 단계에서는 통과함 (PrimaryKeyRelatedField는 존재하지 않는 ID도 허용)
        # 실제 save() 할 때 검증됨
        self.assertFalse(serializer.is_valid())  # PrimaryKeyRelatedField 때문에 validation 실패할 수 있음

    def test_update_preferences_duplicate_ids(self):
        """중복된 서브카테고리 ID 처리 테스트"""
        data = {
            'preferences': [self.subcategory1.id, self.subcategory1.id, self.subcategory2.id]
        }
        
        with patch('preferences.services.PreferenceService.add_preference') as mock_add_preference:
            serializer = UserInfoSerializer(instance=self.user, data=data, partial=True)
            self.assertTrue(serializer.is_valid())
            
            serializer.save()
            
            # 중복 제거된 ID 리스트가 전달되는지 확인
            called_args = mock_add_preference.call_args[1]
            subcategory_ids = called_args['subcategory_ids']
            self.assertEqual(len(subcategory_ids), 2)  # 중복 제거로 2개만 남아야 함
            self.assertIn(self.subcategory1.id, subcategory_ids)
            self.assertIn(self.subcategory2.id, subcategory_ids)

    @patch('users.serializers.account.PreferenceSerializer')  # 실제 import 경로로 수정
    @patch('preferences.models.UserPreference.objects.filter')
    def test_get_preferences_display_korean(self, mock_filter, mock_preference_serializer):
        """선호도 표시 (한국어) 테스트"""
        # Mock UserPreference queryset
        mock_pref1 = Mock()
        mock_pref1.subcategory = self.subcategory1
        mock_pref2 = Mock()  
        mock_pref2.subcategory = self.subcategory2
        
        mock_queryset = Mock()
        mock_queryset.select_related.return_value = [mock_pref1, mock_pref2]
        mock_filter.return_value = mock_queryset
        
        # Mock PreferenceSerializer instance
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = [
            {'name': '서브카테고리1'},
            {'name': '서브카테고리2'}
        ]
        mock_preference_serializer.return_value = mock_serializer_instance
        
        request = self._mock_request(lang='ko')
        serializer = UserInfoSerializer(instance=self.user, context={'request': request})
        
        preferences_display = serializer.get_preferences_display(self.user)
        
        # PreferenceSerializer가 올바른 context로 호출되었는지 확인
        mock_preference_serializer.assert_called_once()
        call_args = mock_preference_serializer.call_args
        self.assertEqual(call_args[1]['context']['language'], 'ko')

    @patch('users.serializers.account.PreferenceSerializer')  # 실제 import 경로로 수정
    @patch('preferences.models.UserPreference.objects.filter')
    def test_get_preferences_display_english(self, mock_filter, mock_preference_serializer):
        """선호도 표시 (영어) 테스트"""
        mock_pref1 = Mock()
        mock_pref1.subcategory = self.subcategory1
        
        mock_queryset = Mock()
        mock_queryset.select_related.return_value = [mock_pref1]
        mock_filter.return_value = mock_queryset
        
        # Mock PreferenceSerializer instance
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = [{'name': 'SubCategory1'}]
        mock_preference_serializer.return_value = mock_serializer_instance
        
        request = self._mock_request(lang='en')
        serializer = UserInfoSerializer(instance=self.user, context={'request': request})
        
        preferences_display = serializer.get_preferences_display(self.user)
        
        # PreferenceSerializer가 영어 context로 호출되었는지 확인
        mock_preference_serializer.assert_called_once()
        call_args = mock_preference_serializer.call_args
        self.assertEqual(call_args[1]['context']['language'], 'en')

    @patch('users.serializers.account.PreferenceSerializer')  # 실제 import 경로로 수정
    @patch('preferences.models.UserPreference.objects.filter')
    def test_get_preferences_display_default_language_with_data(self, mock_filter, mock_preference_serializer):
        """기본 언어(한국어) 테스트 - request가 없을 때 (데이터 있음)"""
        # UserPreference가 하나 이상 있어야 PreferenceSerializer가 호출됨
        mock_pref1 = Mock()
        mock_pref1.subcategory = self.subcategory1
        
        mock_queryset = Mock()
        mock_queryset.select_related.return_value = [mock_pref1]
        mock_filter.return_value = mock_queryset
        
        # Mock PreferenceSerializer instance
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = [{'name': '서브카테고리1'}]
        mock_preference_serializer.return_value = mock_serializer_instance
        
        # context에 request가 없는 경우
        serializer = UserInfoSerializer(instance=self.user)
        preferences_display = serializer.get_preferences_display(self.user)
        
        # PreferenceSerializer가 호출되었는지 확인
        mock_preference_serializer.assert_called_once()
        call_args = mock_preference_serializer.call_args
        # 기본값인 'ko'로 호출되었는지 확인
        self.assertEqual(call_args[1]['context']['language'], 'ko')

    def test_preferences_field_not_required(self):
        """preferences 필드가 필수가 아님을 확인"""
        data = {
            'name': 'test_user_updated'
        }
        
        serializer = UserInfoSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        # preferences 없이도 정상 업데이트
        updated_user = serializer.save()
        self.assertEqual(updated_user.nickname, 'test_user_updated')

    def test_partial_update_with_none_values(self):
        """None 값으로 부분 업데이트 테스트"""
        original_nickname = self.user.nickname
        original_phone = self.user.phone_number
        
        # nickname만 업데이트, phone_number는 None으로 전달하지 않음
        data = {
            'name': 'only_nickname_updated'
        }
        
        serializer = UserInfoSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        self.assertEqual(updated_user.nickname, 'only_nickname_updated')
        self.assertEqual(updated_user.phone_number, original_phone)  # 기존 값 유지
