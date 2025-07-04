from django.test import TestCase
from django.db import IntegrityError
from places.models import Place, PlaceTranslation


# PlaceTranslation 모델 기본 기능 테스트
class PlaceTranslationModelTest(TestCase):

# 테스트에서 사용할 기본 Place 데이터 생성
    def setUp(self):
        self.place = Place.objects.create(
            content_id="test_place_translation",
            category_id=1,
            sub_category_id=10,
            latitude=37.5665,
            longitude=126.9780,
            phone_number="02-1234-5678",
            opening_hours="09:00-18:00",
            region_id=1
        )

    # PlaceTranslation 모델이 올바르게 생성되는지 확인
    def test_place_translation_creation(self):
        translation = PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁",
            description="조선 왕조의 법궁",
            address="서울특별시 종로구 사직로 161"
        )

        self.assertEqual(translation.place, self.place)
        self.assertEqual(translation.lang, "ko")
        self.assertEqual(translation.name, "경복궁")
        self.assertEqual(translation.description, "조선 왕조의 법궁")
        self.assertEqual(translation.address, "서울특별시 종로구 사직로 161")

    # PlaceTranslation의 __str__ 메서드가 올바르게 작동하는지 확인
    def test_place_translation_str_method(self):
        translation = PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁"
        )

        expected = "경복궁 (ko)"
        self.assertEqual(str(translation), expected)

    # 같은 Place에 여러 언어 번역이 가능한지 확인
    def test_multiple_language_translations(self):
        translations_data = [
            {"lang": "ko", "name": "경복궁", "description": "조선 왕조의 법궁"},
            {"lang": "en", "name": "Gyeongbokgung Palace", "description": "Royal palace of Joseon Dynasty"},
            {"lang": "ja", "name": "景福宮", "description": "朝鮮王朝の法宮"},
            {"lang": "zh", "name": "景福宫", "description": "朝鲜王朝的法宫"},
        ]

        for data in translations_data:
            PlaceTranslation.objects.create(
                place=self.place,
                **data
            )

        # 모든 번역이 생성되었는지 확인
        self.assertEqual(self.place.translations.count(), 4)

        # 각 언어별로 제대로 저장되었는지 확인
        ko_translation = self.place.translations.get(lang="ko")
        en_translation = self.place.translations.get(lang="en")
        ja_translation = self.place.translations.get(lang="ja")
        zh_translation = self.place.translations.get(lang="zh")

        self.assertEqual(ko_translation.name, "경복궁")
        self.assertEqual(en_translation.name, "Gyeongbokgung Palace")
        self.assertEqual(ja_translation.name, "景福宮")
        self.assertEqual(zh_translation.name, "景福宫")

# unique_together 제약조건이 올바르게 작동하는지 확인
    def test_place_translation_unique_constraint(self):
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁",
            description="조선 왕조의 법궁"
        )

        # 같은 Place에 같은 언어로 다시 생성하면 에러 발생
        with self.assertRaises(IntegrityError):
            PlaceTranslation.objects.create(
                place=self.place,
                lang="ko",
                name="다른 이름",
                description="다른 설명"
            )

    # 선택적 필드들이 비어있어도 저장되는지 확인
    def test_place_translation_optional_fields(self):
        translation = PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Test Place"  # description과 address는 비워둠
        )

        self.assertEqual(translation.name, "Test Place")
        self.assertEqual(translation.description, "")
        self.assertEqual(translation.address, "")

    # 언어 선택지가 올바르게 제한되는지 확인
    def test_place_translation_language_choices(self):
        valid_languages = ["ko", "en", "ja", "zh"]

        for lang in valid_languages:
            translation = PlaceTranslation.objects.create(
                place=self.place,
                lang=lang,
                name=f"Test Name {lang}"
            )
            self.assertEqual(translation.lang, lang)

    # Place가 삭제되면 관련 번역도 삭제되는지 확인
    def test_place_translation_cascade_delete(self):
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁"
        )
        PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Gyeongbokgung Palace"
        )

        # 번역이 2개 생성되었는지 확인
        self.assertEqual(PlaceTranslation.objects.filter(place=self.place).count(), 2)

        place_id = self.place.id
        self.place.delete()

        # 관련 번역들도 모두 삭제되었는지 확인
        self.assertEqual(PlaceTranslation.objects.filter(place_id=place_id).count(), 0)


# Place 모델의 다국어 메서드 테스트
class PlaceModelTranslationMethodTest(TestCase):

    # 테스트에서 사용할 기본 Place와 다국어 번역 생성
    def setUp(self):
        self.place = Place.objects.create(
            content_id="test_translation_methods",
            latitude=37.5665,
            longitude=126.9780
        )

        # 한국어와 영어 번역 생성
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁",
            description="조선 왕조의 법궁",
            address="서울특별시 종로구 사직로 161"
        )

        PlaceTranslation.objects.create(
            place=self.place,
            lang="en",
            name="Gyeongbokgung Palace",
            description="Royal palace of Joseon Dynasty",
            address="161 Sajik-ro, Jongno-gu, Seoul"
        )

    def test_get_name_method(self):
        ko_name = self.place.get_name("ko")
        self.assertEqual(ko_name, "경복궁")

        en_name = self.place.get_name("en")
        self.assertEqual(en_name, "Gyeongbokgung Palace")

        default_name = self.place.get_name()
        self.assertEqual(default_name, "경복궁")

        missing_name = self.place.get_name("fr")
        self.assertEqual(missing_name, "")

    def test_get_description_method(self):
        ko_desc = self.place.get_description("ko")
        self.assertEqual(ko_desc, "조선 왕조의 법궁")

        en_desc = self.place.get_description("en")
        self.assertEqual(en_desc, "Royal palace of Joseon Dynasty")

        default_desc = self.place.get_description()
        self.assertEqual(default_desc, "조선 왕조의 법궁")

        missing_desc = self.place.get_description("ja")
        self.assertEqual(missing_desc, "")

    def test_get_address_method(self):
        ko_addr = self.place.get_address("ko")
        self.assertEqual(ko_addr, "서울특별시 종로구 사직로 161")

        en_addr = self.place.get_address("en")
        self.assertEqual(en_addr, "161 Sajik-ro, Jongno-gu, Seoul")

        default_addr = self.place.get_address()
        self.assertEqual(default_addr, "서울특별시 종로구 사직로 161")

        missing_addr = self.place.get_address("zh")
        self.assertEqual(missing_addr, "")

    def test_place_str_method_with_translation(self):
        expected = "경복궁"
        self.assertEqual(str(self.place), expected)

        place_no_translation = Place.objects.create(content_id="no_translation_place")
        expected_no_trans = f"Place {place_no_translation.id} (no_translation_place)"
        self.assertEqual(str(place_no_translation), expected_no_trans)

    def test_translation_methods_with_no_translations(self):
        place_empty = Place.objects.create(content_id="empty_place")

        self.assertEqual(place_empty.get_name("ko"), "")
        self.assertEqual(place_empty.get_description("en"), "")
        self.assertEqual(place_empty.get_address("ja"), "")

        self.assertEqual(place_empty.get_name(), "")
        self.assertEqual(place_empty.get_description(), "")
        self.assertEqual(place_empty.get_address(), "")
