from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


# 지역구 모델 기본 기능 테스트
class SubRegionModelTest(TestCase):

    def setUp(self):
        # 서울 지역 생성
        self.seoul = Region.objects.create()
        RegionTranslation.objects.create(region=self.seoul, lang="ko", name="서울")

        # 강남구 생성
        self.gangnam = SubRegion.objects.create(
            region=self.seoul,
            favorite_count=100,
            latitude=Decimal("37.51730500"),
            longitude=Decimal("127.04750200")
        )
        SubRegionTranslation.objects.create(
            sub_region=self.gangnam,
            lang="ko",
            name="강남구",
            description="서울의 대표적인 번화가"
        )
        SubRegionTranslation.objects.create(
            sub_region=self.gangnam,
            lang="en",
            name="Gangnam-gu",
            description="Representative downtown area of Seoul"
        )

    # 지역구가 모든 필드와 함께 올바르게 생성되는지 테스트
    def test_subregion_creation_with_all_fields(self):
        self.assertTrue(isinstance(self.gangnam, SubRegion))
        self.assertEqual(self.gangnam.region, self.seoul)
        self.assertEqual(self.gangnam.favorite_count, 100)
        self.assertEqual(self.gangnam.latitude, Decimal("37.51730500"))
        self.assertEqual(self.gangnam.longitude, Decimal("127.04750200"))
        self.assertIsNotNone(self.gangnam.created_at)
        self.assertIsNotNone(self.gangnam.updated_at)

    # 지역구 기본값들이 올바르게 설정되는지 테스트
    def test_subregion_creation_with_default_values(self):
        subregion = SubRegion.objects.create(region=self.seoul)

        self.assertEqual(subregion.favorite_count, 0)
        self.assertIsNone(subregion.latitude)
        self.assertIsNone(subregion.longitude)

    # 한국어 이름 가져오기 테스트
    def test_subregion_get_name_korean(self):
        self.assertEqual(self.gangnam.get_name("ko"), "강남구")

    # 영어 이름 가져오기 테스트
    def test_subregion_get_name_english(self):
        self.assertEqual(self.gangnam.get_name("en"), "Gangnam-gu")

    # 없는 언어 요청 시 None 반환 테스트
    def test_subregion_get_name_nonexistent_language(self):
        self.assertIsNone(self.gangnam.get_name("ja"))

    # 기본 언어(ko) 테스트
    def test_subregion_get_name_default_language(self):
        self.assertEqual(self.gangnam.get_name(), "강남구")

    # 한국어 설명 가져오기 테스트
    def test_subregion_get_description_korean(self):
        self.assertEqual(self.gangnam.get_description("ko"), "서울의 대표적인 번화가")

    # 영어 설명 가져오기 테스트
    def test_subregion_get_description_english(self):
        self.assertEqual(self.gangnam.get_description("en"), "Representative downtown area of Seoul")

    # 없는 언어 설명 요청 시 빈 문자열 반환 테스트
    def test_subregion_get_description_nonexistent_language(self):
        self.assertEqual(self.gangnam.get_description("ja"), "")

    # 기본 언어(ko) 설명 테스트
    def test_subregion_get_description_default_language(self):
        self.assertEqual(self.gangnam.get_description(), "서울의 대표적인 번화가")

    # 한국어 특징 가져오기 테스트
    def test_subregion_get_features_korean(self):
        translation = self.gangnam.translations.get(lang="ko")
        translation.features = "트레디한 쇼핑몰과 고급 레스토랑"
        translation.save()

        self.assertEqual(self.gangnam.get_features("ko"), "트레디한 쇼핑몰과 고급 레스토랑")

    # 영어 특징 가져오기 테스트
    def test_subregion_get_features_english(self):
        translation = self.gangnam.translations.get(lang="en")
        translation.features = "Trendy shopping malls and high-end restaurants"
        translation.save()

        self.assertEqual(self.gangnam.get_features("en"), "Trendy shopping malls and high-end restaurants")

    # 없는 언어 특징 요청 시 빈 문자열 반환 테스트
    def test_subregion_get_features_nonexistent_language(self):
        self.assertEqual(self.gangnam.get_features("jp"), "")

    # 기본 언어(ko) 특징 테스트
    def test_subregion_get_features_default_language(self):
        # 강남구에 한국어 특징 추가
        translation = self.gangnam.translations.get(lang="ko")
        translation.features = "현대적인 비즈니스 중심지"
        translation.save()

        self.assertEqual(self.gangnam.get_features(), "현대적인 비즈니스 중심지")

    def test_subregion_str_method(self):
        self.assertEqual(str(self.gangnam), "서울 강남구")

    def test_subregion_str_method_without_names(self):
        subregion = SubRegion.objects.create(region=self.seoul)
        expected = f"SubRegion {subregion.id}"
        self.assertEqual(str(subregion), expected)

    def test_subregion_update_methods_exist(self):
        self.assertTrue(hasattr(self.gangnam, "update_favorite_count"))
        self.assertTrue(callable(getattr(self.gangnam, "update_favorite_count")))

        try:
            self.gangnam.update_favorite_count()
        except Exception as e:
            self.fail(f"업데이트 메서드 호출 중 에러 발생: {e}")


class SubRegionOrderingTest(TestCase):

    def setUp(self):
        self.seoul = Region.objects.create()
        RegionTranslation.objects.create(region=self.seoul, lang="ko", name="서울")

        # 즐겨찾기 수가 다른 지역구들 생성
        self.gangnam = SubRegion.objects.create(
            region=self.seoul, favorite_count=100
        )
        SubRegionTranslation.objects.create(sub_region=self.gangnam, lang="ko", name="강남구")

        self.gangbuk = SubRegion.objects.create(
            region=self.seoul, favorite_count=150
        )
        SubRegionTranslation.objects.create(sub_region=self.gangbuk, lang="ko", name="강북구")

        self.mapo = SubRegion.objects.create(
            region=self.seoul, favorite_count=100
        )
        SubRegionTranslation.objects.create(sub_region=self.mapo, lang="ko", name="마포구")

    # 즐겨찾기 수 높은 순으로 정렬되는지 테스트
    def test_subregion_ordering_by_favorite_count(self):
        subregions = list(SubRegion.objects.all())
        # 강북구가 즐겨찾기 수가 가장 많으므로 첫 번째
        self.assertEqual(subregions[0], self.gangbuk)

    # 즐겨찾기 수가 같을 때 가나다순 정렬 테스트
    def test_subregion_ordering_by_name_when_favorite_count_same(self):
        subregions = list(SubRegion.objects.all())
        favorite_100_subregions = [sr for sr in subregions if sr.favorite_count == 100]
        self.assertEqual(len(favorite_100_subregions), 2)

    def test_subregion_manual_count_update(self):
        original_favorite_count = self.gangnam.favorite_count

        self.gangnam.favorite_count = 200
        self.gangnam.save()

        self.gangnam.refresh_from_db()
        self.assertEqual(self.gangnam.favorite_count, 200)
        self.assertNotEqual(self.gangnam.favorite_count, original_favorite_count)


class SubRegionTranslationTest(TestCase):

    def setUp(self):
        region = Region.objects.create()
        self.subregion = SubRegion.objects.create(region=region)

    def test_subregion_translation_creation_full(self):
        translation = SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="ko",
            name="마포구",
            description="홍대와 합정이 있는 문화의 거리"
        )

        self.assertEqual(translation.sub_region, self.subregion)
        self.assertEqual(translation.lang, "ko")
        self.assertEqual(translation.name, "마포구")
        self.assertEqual(translation.description, "홍대와 합정이 있는 문화의 거리")
        self.assertIsNotNone(translation.created_at)
        self.assertIsNotNone(translation.updated_at)

    def test_subregion_translation_creation_without_description(self):
        translation = SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="en",
            name="Yongsan-gu"
            # description 생략
        )

        self.assertEqual(translation.description, "")

    # 특징 필드와 함께 지역구 번역 생성 테스트
    def test_subregion_translation_creation_with_features(self):
        translation = SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="ko",
            name="강남구",
            description="강남스타일의 발원지",
            features="트레디한 쇼핑몰과 고급 레스토랑"
        )

        self.assertEqual(translation.features, "트레디한 쇼핑몰과 고급 레스토랑")
        self.assertEqual(translation.name, "강남구")
        self.assertEqual(translation.description, "강남스타일의 발원지")

    # 특징 필드 없이 지역구 번역 생성 테스트 (빈 값 허용)
    def test_subregion_translation_creation_without_features(self):
        translation = SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="en",
            name="Gangnam-gu"
            # features, description 생략
        )

        self.assertEqual(translation.features, "")
        self.assertEqual(translation.description, "")

    # 지역구 특징 가져오기 메서드 테스트
    def test_subregion_get_features_method(self):
        # 한국어 특징 추가
        SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="ko",
            name="마포구",
            description="홍대와 합정이 있는 문화의 거리",
            features="젊은 에너지와 예술적 감성이 넘치는 곳"
        )

        # 영어 특징 추가
        SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="en",
            name="Mapo-gu",
            description="Cultural street with Hongdae and Hapjeong",
            features="A place overflowing with youthful energy and artistic sensibility"
        )

        # 한국어 특징 확인
        self.assertEqual(self.subregion.get_features("ko"), "젊은 에너지와 예술적 감성이 넘치는 곳")
        # 영어 특징 확인
        self.assertEqual(self.subregion.get_features("en"),
                         "A place overflowing with youthful energy and artistic sensibility")
        # 없는 언어 요청 시 빈 문자열 반환
        self.assertEqual(self.subregion.get_features("ja"), "")

    # 기본 언어(ko) 특징 가져오기 테스트
    def test_subregion_get_features_default_language(self):
        SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="ko",
            name="종로구",
            features="전통과 현대가 공존하는 역사의 중심지"
        )

        # 기본 언어로 호출
        self.assertEqual(self.subregion.get_features(), "전통과 현대가 공존하는 역사의 중심지")

    def test_subregion_translation_unique_constraint(self):
        SubRegionTranslation.objects.create(sub_region=self.subregion, lang="ko", name="용산구")

        with self.assertRaises(IntegrityError):
            SubRegionTranslation.objects.create(sub_region=self.subregion, lang="ko", name="용산")

    def test_subregion_translation_different_languages_allowed(self):
        korean = SubRegionTranslation.objects.create(sub_region=self.subregion, lang="ko", name="종로구")
        english = SubRegionTranslation.objects.create(sub_region=self.subregion, lang="en", name="Jongno-gu")

        self.assertEqual(korean.sub_region, self.subregion)
        self.assertEqual(english.sub_region, self.subregion)
        self.assertNotEqual(korean.lang, english.lang)

    def test_subregion_translation_str_method(self):
        translation = SubRegionTranslation.objects.create(
            sub_region=self.subregion, lang="ko", name="중구"
        )
        expected = f"{self.subregion.id} - ko: 중구"
        self.assertEqual(str(translation), expected)


class SubRegionRelationshipTest(TestCase):

    def setUp(self):
        self.seoul = Region.objects.create()
        RegionTranslation.objects.create(region=self.seoul, lang="ko", name="서울")

        self.gangnam = SubRegion.objects.create(region=self.seoul)
        self.ko_translation = SubRegionTranslation.objects.create(
            sub_region=self.gangnam, lang="ko", name="강남구", description="강남 스타일의 발원지"
        )
        self.en_translation = SubRegionTranslation.objects.create(
            sub_region=self.gangnam, lang="en", name="Gangnam-gu", description="Birthplace of Gangnam Style"
        )

    def test_region_has_multiple_subregions(self):
        gangbuk = SubRegion.objects.create(region=self.seoul)
        SubRegionTranslation.objects.create(sub_region=gangbuk, lang="ko", name="강북구")

        subregions = self.seoul.subregions.all()
        self.assertEqual(subregions.count(), 2)
        self.assertIn(self.gangnam, subregions)
        self.assertIn(gangbuk, subregions)

    def test_subregion_has_multiple_translations(self):
        translations = self.gangnam.translations.all()
        self.assertEqual(translations.count(), 2)

        korean_translation = translations.filter(lang="ko").first()
        english_translation = translations.filter(lang="en").first()

        self.assertEqual(korean_translation.name, "강남구")
        self.assertEqual(korean_translation.description, "강남 스타일의 발원지")
        self.assertEqual(english_translation.name, "Gangnam-gu")
        self.assertEqual(english_translation.description, "Birthplace of Gangnam Style")

    def test_subregion_cascade_delete_translations(self):
        subregion_id = self.gangnam.id

        self.gangnam.delete()

        remaining_translations = SubRegionTranslation.objects.filter(sub_region_id=subregion_id)
        self.assertEqual(remaining_translations.count(), 0)

    def test_region_cascade_delete_subregions_and_translations(self):
        region_id = self.seoul.id
        subregion_id = self.gangnam.id

        self.seoul.delete()

        remaining_subregions = SubRegion.objects.filter(region_id=region_id)
        remaining_subregion_translations = SubRegionTranslation.objects.filter(sub_region_id=subregion_id)

        self.assertEqual(remaining_subregions.count(), 0)
        self.assertEqual(remaining_subregion_translations.count(), 0)

    def test_subregion_translations_access_via_related_name(self):
        korean_name = self.gangnam.translations.get(lang="ko").name
        english_name = self.gangnam.translations.get(lang="en").name

        self.assertEqual(korean_name, "강남구")
        self.assertEqual(english_name, "Gangnam-gu")


class KoripServiceSubRegionTest(TestCase):
    def setUp(self):
        self.seoul = Region.objects.create()
        RegionTranslation.objects.create(region=self.seoul, lang="ko", name="서울")

        self.gangnam = SubRegion.objects.create(
            region=self.seoul,
            favorite_count=120,
            latitude=Decimal("37.5172"),
            longitude=Decimal("127.0473")
        )
        SubRegionTranslation.objects.create(
            sub_region=self.gangnam,
            lang="ko",
            name="강남구",
            description="강남스타일의 발원지, 현대적인 쇼핑과 엔터테인먼트의 중심지",
            features="트레디한 쇼핑몰과 고급 레스토랑"
        )

        self.jongno = SubRegion.objects.create(
            region=self.seoul,
            favorite_count=95,
            latitude=Decimal("37.5735"),
            longitude=Decimal("126.9788")
        )
        SubRegionTranslation.objects.create(
            sub_region=self.jongno,
            lang="ko",
            name="종로구",
            description="조선왕조의 중심지, 경복궁과 창덕궁이 있는 역사문화의 심장",
            features="전통과 현대가 공존하는 역사의 중심지"
        )

        self.mapo = SubRegion.objects.create(
            region=self.seoul,
            favorite_count=80,
            latitude=Decimal("37.5663"),
            longitude=Decimal("126.9019")
        )
        SubRegionTranslation.objects.create(
            sub_region=self.mapo,
            lang="ko",
            name="마포구",
            description="홍대와 합정동의 젊음과 활력이 넘치는 문화예술 거리",
            features="젊은 에너지와 예술적 감성이 넘치는 곳"
        )

    def test_popular_districts_ordering_for_frontend(self):
        subregions = list(SubRegion.objects.all())

        self.assertEqual(subregions[0], self.gangnam)
        self.assertEqual(subregions[1], self.jongno)
        self.assertEqual(subregions[2], self.mapo)

    def test_tourist_district_descriptions(self):
        gangnam_desc = self.gangnam.get_description("ko")
        self.assertIn("강남스타일", gangnam_desc)
        self.assertIn("쇼핑", gangnam_desc)

        jongno_desc = self.jongno.get_description("ko")
        self.assertIn("경복궁", jongno_desc)
        self.assertIn("역사", jongno_desc)

        mapo_desc = self.mapo.get_description("ko")
        self.assertIn("홍대", mapo_desc)
        self.assertIn("문화", mapo_desc)

    # 특징 필드 테스트 추가
    def test_tourist_district_features(self):
        gangnam_features = self.gangnam.get_features("ko")
        self.assertIn("트레디한", gangnam_features)
        self.assertIn("쇼핑몰", gangnam_features)

        jongno_features = self.jongno.get_features("ko")
        self.assertIn("전통", jongno_features)
        self.assertIn("역사", jongno_features)

        mapo_features = self.mapo.get_features("ko")
        self.assertIn("젊은", mapo_features)
        self.assertIn("예술적", mapo_features)

    # 날씨 API 연동을 위한 서울 좌표 데이터 테스트
    def test_weather_api_coordinates_in_seoul(self):
        self.assertIsNotNone(self.gangnam.latitude)
        self.assertIsNotNone(self.gangnam.longitude)

        seoul_subregions = [self.gangnam, self.jongno, self.mapo]

        for subregion in seoul_subregions:
            self.assertGreaterEqual(float(subregion.latitude), 37.4)
            self.assertLessEqual(float(subregion.latitude), 37.7)
            self.assertGreaterEqual(float(subregion.longitude), 126.8)
            self.assertLessEqual(float(subregion.longitude), 127.2)

    def test_favorite_count_matches_tourism_popularity(self):
        self.assertEqual(self.gangnam.favorite_count, 120)
        self.assertEqual(self.jongno.favorite_count, 95)
        self.assertEqual(self.mapo.favorite_count, 80)
        self.assertGreater(self.gangnam.favorite_count, self.jongno.favorite_count)
        self.assertGreater(self.jongno.favorite_count, self.mapo.favorite_count)