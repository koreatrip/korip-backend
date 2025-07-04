# Place 모델 기본 테스트
from django.test import TestCase
from django.db import IntegrityError
from places.models import Place


# Place 모델 기본 기능 테스트
class PlaceModelBasicTest(TestCase):

# 테스트에서 사용할 기본 Place 데이터 생성
    def setUp(self):
        self.place = Place.objects.create(
            content_id="test_place_001",
            category_id=1,
            sub_category_id=10,
            latitude=37.5665,
            longitude=126.9780,
            phone_number="02-1234-5678",
            opening_hours="09:00-18:00",
            region_id=1,
            view_count=100
        )

# Place 모델이 올바르게 생성되는지 확인
    def test_place_creation(self):
        self.assertEqual(self.place.content_id, "test_place_001")
        self.assertEqual(self.place.category_id, 1)
        self.assertEqual(self.place.sub_category_id, 10)
        self.assertEqual(self.place.latitude, 37.5665)
        self.assertEqual(self.place.longitude, 126.9780)
        self.assertEqual(self.place.phone_number, "02-1234-5678")
        self.assertEqual(self.place.region_id, 1)
        self.assertEqual(self.place.view_count, 100)

# Place 모델의 __str__ 메서드가 올바르게 작동하는지 확인
    def test_place_str_method(self):
        expected = f"Place {self.place.id} ({self.place.content_id})"
        self.assertEqual(str(self.place), expected)

# content_id가 유니크 제약조건을 올바르게 가지는지 확인
    def test_place_content_id_unique(self):
        with self.assertRaises(IntegrityError):
            Place.objects.create(
                content_id="test_place_001",  # 중복된 content_id
                latitude=37.5665,
                longitude=126.9780
            )

# 기본값들이 올바르게 설정되는지 확인
    def test_place_default_values(self):
        place = Place.objects.create(content_id="test_default")
        self.assertEqual(place.view_count, 0)
        self.assertIsNone(place.category_id)
        self.assertIsNone(place.sub_category_id)
        self.assertIsNone(place.region_id)
        self.assertIsNone(place.last_synced_at)

# 선택적 필드들이 비어있어도 저장되는지 확인
    def test_place_optional_fields(self):
        place = Place.objects.create(
            content_id="minimal_place",
        )

        self.assertEqual(place.content_id, "minimal_place")
        self.assertIsNone(place.latitude)
        self.assertIsNone(place.longitude)
        self.assertEqual(place.phone_number, "")
        self.assertIsNone(place.category_id)
        self.assertIsNone(place.region_id)
        self.assertIsNone(place.last_synced_at)

# 조회수 기능이 올바르게 작동하는지 확인
    def test_place_view_count_functionality(self):
        place = Place.objects.create(content_id="view_test")

        # 기본값 확인
        self.assertEqual(place.view_count, 0)

        # 조회수 증가
        place.view_count += 1
        place.save()

        # 다시 불러와서 확인
        place.refresh_from_db()
        self.assertEqual(place.view_count, 1)

# Foreign Key 역할을 하는 ID 필드들이 올바르게 작동하는지 확인
    def test_place_foreign_key_fields(self):
        place = Place.objects.create(
            content_id="fk_test",
            category_id=5,
            sub_category_id=25,
            region_id=3
        )

        self.assertEqual(place.category_id, 5)
        self.assertEqual(place.sub_category_id, 25)
        self.assertEqual(place.region_id, 3)

        # None 값도 허용하는지 확인
        place_no_fk = Place.objects.create(content_id="no_fk_test")
        self.assertIsNone(place_no_fk.category_id)
        self.assertIsNone(place_no_fk.sub_category_id)
        self.assertIsNone(place_no_fk.region_id)

# Place 모델의 기본 정렬이 올바른지 확인
    def test_place_ordering(self):
        place1 = Place.objects.create(content_id="place1")
        place2 = Place.objects.create(content_id="place2")
        place3 = Place.objects.create(content_id="place3")

        places = Place.objects.all()
        self.assertEqual(places[0], place3)
        self.assertEqual(places[1], place2)
        self.assertEqual(places[2], place1)
        self.assertEqual(places[3], self.place)

# 위도, 경도의 소수점 정밀도가 올바른지 확인
    def test_place_decimal_fields_precision(self):
        place = Place.objects.create(
            content_id="precision_test",
            latitude=37.12345678,  # 8자리 소수점
            longitude=126.12345678  # 8자리 소수점
        )

        self.assertEqual(place.latitude, 37.12345678)
        self.assertEqual(place.longitude, 126.12345678)
