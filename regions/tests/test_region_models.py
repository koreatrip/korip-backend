from django.test import TestCase
from django.db import IntegrityError
from regions.models import Region, RegionTranslation


# 지역 모델 기본 기능 테스트
class RegionModelTest(TestCase):

# 테스트용 데이터
    def setUp(self):
        self.seoul = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.seoul,
            lang="ko",
            name="서울",
            description="전통과 현대가 공존하는 도시"
        )
        RegionTranslation.objects.create(
            region=self.seoul,
            lang="en",
            name="Seoul",
            description="A city where tradition and modernity coexist"
        )

# 지역이 올바르게 생성되는지 테스트
    def test_region_creation(self):
        self.assertTrue(isinstance(self.seoul, Region))
        self.assertIsNotNone(self.seoul.id)
        self.assertIsNotNone(self.seoul.created_at)
        self.assertIsNotNone(self.seoul.updated_at)

# 한국어 이름 가져오기 테스트
    def test_region_get_name_korean(self):
        self.assertEqual(self.seoul.get_name("ko"), "서울")

# 영어 이름 가져오기 테스트
    def test_region_get_name_english(self):
        self.assertEqual(self.seoul.get_name("en"), "Seoul")

# 없는 언어 요청 시 None 반환 테스트
    def test_region_get_name_nonexistent_language(self):
        self.assertIsNone(self.seoul.get_name("jp"))

# 기본 언어(ko) 테스트
    def test_region_get_name_default_language(self):
        self.assertEqual(self.seoul.get_name(), "서울")

# 한국어 설명 가져오기 테스트
    def test_region_get_description_korean(self):
        self.assertEqual(self.seoul.get_description("ko"), "전통과 현대가 공존하는 도시")

# 영어 설명 가져오기 테스트
    def test_region_get_description_english(self):
        self.assertEqual(self.seoul.get_description("en"), "A city where tradition and modernity coexist")

# 없는 언어 설명 요청 시 빈 문자열 반환 테스트
    def test_region_get_description_nonexistent_language(self):
        self.assertEqual(self.seoul.get_description("jp"), "")

# 기본 언어(ko) 설명 테스트
    def test_region_get_description_default_language(self):
        self.assertEqual(self.seoul.get_description(), "전통과 현대가 공존하는 도시")

# Region의 메서드 테스트
    def test_region_str_method(self):
        self.assertEqual(str(self.seoul), "서울")

# 한국어 번역이 없는 경우 메서드 테스트
    def test_region_str_method_without_korean_translation(self):
        busan = Region.objects.create()
        RegionTranslation.objects.create(region=busan, lang="en", name="Busan")

        expected = f"Region {busan.id}"
        self.assertEqual(str(busan), expected)


# 지역 번역 모델 기능 테스트
class RegionTranslationTest(TestCase):

    def setUp(self):
        self.region = Region.objects.create()

# 지역 번역이 모든 필드와 함께 올바르게 생성되는지 테스트
    def test_region_translation_creation_full(self):
        translation = RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="부산",
            description="해양도시 부산"
        )

        self.assertEqual(translation.region, self.region)
        self.assertEqual(translation.lang, "ko")
        self.assertEqual(translation.name, "부산")
        self.assertEqual(translation.description, "해양도시 부산")
        self.assertIsNotNone(translation.created_at)
        self.assertIsNotNone(translation.updated_at)

# 설명 없이 지역 번역 생성 테스트
    def test_region_translation_creation_without_description(self):
        translation = RegionTranslation.objects.create(
            region=self.region,
            lang="en",
            name="Incheon"
            # description 생략
        )

        self.assertEqual(translation.description, "")

# 같은 지역-언어 조합 중복 생성 방지 테스트
    def test_region_translation_unique_constraint(self):
        RegionTranslation.objects.create(region=self.region, lang="ko", name="제주")

        with self.assertRaises(IntegrityError):
            RegionTranslation.objects.create(region=self.region, lang="ko", name="제주도")

# 같은 지역에 다른 언어 번역은 생성 가능한지 테스트
    def test_region_translation_different_languages_allowed(self):
        korean = RegionTranslation.objects.create(region=self.region, lang="ko", name="대구")
        english = RegionTranslation.objects.create(region=self.region, lang="en", name="Daegu")

        self.assertEqual(korean.region, self.region)
        self.assertEqual(english.region, self.region)
        self.assertNotEqual(korean.lang, english.lang)

    def test_region_translation_str_method(self):
        translation = RegionTranslation.objects.create(
            region=self.region, lang="ko", name="광주"
        )
        expected = f"{self.region.id} - ko: 광주"
        self.assertEqual(str(translation), expected)


class RegionRelationshipTest(TestCase):

    def setUp(self):
        self.region = Region.objects.create()
        self.ko_translation = RegionTranslation.objects.create(
            region=self.region, lang="ko", name="울산", description="산업도시 울산"
        )
        self.en_translation = RegionTranslation.objects.create(
            region=self.region, lang="en", name="Ulsan", description="Industrial city of Ulsan"
        )

    def test_region_has_multiple_translations(self):
        translations = self.region.translations.all()
        self.assertEqual(translations.count(), 2)

        korean_translation = translations.filter(lang="ko").first()
        english_translation = translations.filter(lang="en").first()

        self.assertEqual(korean_translation.name, "울산")
        self.assertEqual(korean_translation.description, "산업도시 울산")
        self.assertEqual(english_translation.name, "Ulsan")
        self.assertEqual(english_translation.description, "Industrial city of Ulsan")

# 지역 삭제 시 관련 번역들도 삭제되는지 테스트
    def test_region_translation_cascade_delete(self):
        region_id = self.region.id

        self.region.delete()

        remaining_translations = RegionTranslation.objects.filter(region_id=region_id)
        self.assertEqual(remaining_translations.count(), 0)

    def test_region_translations_access_via_related_name(self):
        korean_name = self.region.translations.get(lang="ko").name
        english_name = self.region.translations.get(lang="en").name

        self.assertEqual(korean_name, "울산")
        self.assertEqual(english_name, "Ulsan")


class KoripServiceRegionTest(TestCase):

    def setUp(self):
        self.seoul = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.seoul,
            lang="ko",
            name="서울",
            description="전통과 현대가 공존하는 도시"
        )
        RegionTranslation.objects.create(
            region=self.seoul,
            lang="en",
            name="Seoul",
            description="A city where tradition and modernity coexist"
        )

        self.busan = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.busan,
            lang="ko",
            name="부산",
            description="해양도시 부산"
        )

        self.jeju = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.jeju,
            lang="ko",
            name="제주",
            description="아름다운 섬"
        )

    def test_main_service_regions_exist(self):
        main_regions = ["서울", "부산", "제주"]

        for region_name in main_regions:
            region_exists = Region.objects.filter(
                translations__lang="ko",
                translations__name=region_name
            ).exists()
            self.assertTrue(region_exists, f"{region_name} 지역이 존재하지 않습니다")

    def test_region_descriptions_for_frontend(self):
        self.assertEqual(self.seoul.get_description("ko"), "전통과 현대가 공존하는 도시")
        self.assertEqual(self.busan.get_description("ko"), "해양도시 부산")
        self.assertEqual(self.jeju.get_description("ko"), "아름다운 섬")

    def test_multilingual_support_for_tourists(self):
        self.assertEqual(self.seoul.get_name("ko"), "서울")

        self.assertEqual(self.seoul.get_name("en"), "Seoul")

        self.assertIsNone(self.seoul.get_name("jp"))
        self.assertIsNone(self.seoul.get_name("cn"))

    def test_korean_translation_required_for_service(self):
        region = Region.objects.create()

        self.assertIsNone(region.get_name("ko"))
        self.assertEqual(str(region), f"Region {region.id}")

        RegionTranslation.objects.create(region=region, lang="ko", name="대구")
        self.assertEqual(region.get_name("ko"), "대구")
        self.assertEqual(str(region), "대구")
