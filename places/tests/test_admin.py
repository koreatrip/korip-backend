# places/tests/test_admin.py

from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib import admin
from django.contrib.gis.geos import Point
from places.models import Place, PlaceTranslation
from places.admin import PlaceAdmin, PlaceTranslationAdmin, PlaceTranslationInline
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation
from categories.models import Category, CategoryTranslation, SubCategory, SubCategoryTranslation


class PlaceAdminTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="문화"
        )

        self.sub_category = SubCategory.objects.create(category=self.category)
        SubCategoryTranslation.objects.create(
            sub_category=self.sub_category,
            lang="ko",
            name="궁궐"
        )

        self.region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="서울"
        )

        self.sub_region = SubRegion.objects.create(
            region=self.region,
            favorite_count=0,
            location=Point(126.9780, 37.5665)
        )
        SubRegionTranslation.objects.create(
            sub_region=self.sub_region,
            lang="ko",
            name="강남구"
        )

        self.place = Place.objects.create(
            content_id="admin_test_001",
            category=self.category,
            sub_category=self.sub_category,
            location=Point(126.9780, 37.5665),
            region=self.region,
            sub_region=self.sub_region,
            link_url="https://example.com",
            favorite_count=50
        )

        self.site = AdminSite()
        self.admin = PlaceAdmin(Place, self.site)

    def test_list_display(self):
        expected_fields = [
            "id",
            "content_id",
            "get_korean_name",
            "category",      # category_id → category
            "sub_category",  # sub_category_id → sub_category
            "region",
            "sub_region",
            "favorite_count",
            "get_coordinates",
            "created_at"
        ]
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_list_filter(self):
        expected_filters = ["region", "sub_region", "category", "created_at"]  # category_id → category
        self.assertEqual(self.admin.list_filter, expected_filters)

    def test_search_fields(self):
        expected_search = ["content_id", "translations__name"]
        self.assertEqual(self.admin.search_fields, expected_search)

    def test_readonly_fields(self):
        expected_readonly = ["created_at", "updated_at", "get_coordinates_display"]  # get_coordinates_display 추가
        self.assertEqual(self.admin.readonly_fields, expected_readonly)

    def test_fieldsets_structure(self):
        fieldsets = self.admin.fieldsets
        self.assertEqual(len(fieldsets), 7)  # 6 → 7 (위치 설정 섹션 추가)

        fieldset_titles = [fieldset[0] for fieldset in fieldsets]
        expected_titles = ["기본 정보", "위치 설정", "카테고리", "지역", "연락처/링크", "통계", "날짜"]  # 위치 설정 추가
        self.assertEqual(fieldset_titles, expected_titles)

        # 인덱스가 아닌 제목으로 찾는 방식으로 변경 (더 안전함)
        fieldset_dict = {fieldset[0]: fieldset[1]["fields"] for fieldset in fieldsets}

        # 기본 정보
        self.assertEqual(fieldset_dict["기본 정보"], ("content_id",))  # location 제거됨

        # 위치 설정 (새로 추가된 섹션)
        self.assertEqual(fieldset_dict["위치 설정"], ("location", "get_coordinates_display"))

        # 카테고리
        self.assertEqual(fieldset_dict["카테고리"], ("category", "sub_category"))  # category_id → category

        # 지역
        self.assertEqual(fieldset_dict["지역"], ("region", "sub_region"))

        # 연락처/링크
        self.assertEqual(fieldset_dict["연락처/링크"], ("phone_number", "use_time", "link_url"))

        # 통계
        self.assertEqual(fieldset_dict["통계"], ("favorite_count", "last_synced_at"))

        # 날짜
        self.assertEqual(fieldset_dict["날짜"], ("created_at", "updated_at"))

    def test_has_inlines(self):
        self.assertEqual(len(self.admin.inlines), 1)
        self.assertIn(PlaceTranslationInline, self.admin.inlines)

    def test_admin_registration(self):
        self.assertIn(Place, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Place], PlaceAdmin)

    def test_all_fields_in_fieldsets(self):
        all_fields_in_fieldsets = []
        for fieldset in self.admin.fieldsets:
            all_fields_in_fieldsets.extend(fieldset[1]["fields"])

        expected_fields = [
            "content_id", "location", "get_coordinates_display", "phone_number", "use_time", "link_url",
            "category", "sub_category", "region", "sub_region",  # category_id → category
            "favorite_count", "last_synced_at", "created_at", "updated_at"
        ]

        for field in expected_fields:
            self.assertIn(field, all_fields_in_fieldsets)

    def test_filtering(self):
        region2 = Region.objects.create()
        sub_region2 = SubRegion.objects.create(
            region=region2,
            favorite_count=0,
            location=Point(129.0756, 35.1796)
        )

        Place.objects.create(
            content_id="filter_test_place",
            category=self.category,
            sub_category=self.sub_category,
            location=Point(129.0756, 35.1796),
            region=region2,
            sub_region=sub_region2
        )

        self.assertIn("category", self.admin.list_filter)  # category_id → category
        self.assertIn("region", self.admin.list_filter)
        self.assertIn("sub_region", self.admin.list_filter)

    def test_category_foreign_key_display(self):
        self.assertIn("category", self.admin.list_display)      # category_id → category
        self.assertIn("sub_category", self.admin.list_display)  # sub_category_id → sub_category
        self.assertIn("region", self.admin.list_display)
        self.assertIn("sub_region", self.admin.list_display)

    def test_favorite_count_display(self):
        self.assertIn("favorite_count", self.admin.list_display)

        # 인덱스 대신 제목으로 찾기 (더 안전함)
        statistics_fieldset = None
        for fieldset in self.admin.fieldsets:
            if fieldset[0] == "통계":
                statistics_fieldset = fieldset
                break

        self.assertIsNotNone(statistics_fieldset)
        self.assertEqual(statistics_fieldset[0], "통계")
        self.assertIn("favorite_count", statistics_fieldset[1]["fields"])

    def test_sync_time_management(self):
        # 인덱스 대신 제목으로 찾기
        statistics_fieldset = None
        for fieldset in self.admin.fieldsets:
            if fieldset[0] == "통계":
                statistics_fieldset = fieldset
                break

        self.assertIsNotNone(statistics_fieldset)
        system_fields = statistics_fieldset[1]["fields"]
        self.assertIn("last_synced_at", system_fields)

    def test_get_korean_name_method(self):
        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁"
        )

        korean_name = self.admin.get_korean_name(self.place)
        self.assertEqual(korean_name, "경복궁")

        place_no_korean = Place.objects.create(content_id="no_korean_place")
        korean_name_empty = self.admin.get_korean_name(place_no_korean)
        self.assertEqual(korean_name_empty, "-")

    def test_get_coordinates_display_method(self):
        """새로 추가된 get_coordinates_display 메서드 테스트"""
        coordinates_display = self.admin.get_coordinates_display(self.place)
        expected = f"위도: {self.place.location.y:.6f}, 경도: {self.place.location.x:.6f}"
        self.assertEqual(coordinates_display, expected)

        # 좌표가 없는 경우
        place_no_coords = Place.objects.create(content_id="no_coords_place")
        coordinates_display_empty = self.admin.get_coordinates_display(place_no_coords)
        self.assertEqual(coordinates_display_empty, "좌표 없음")

    def test_translation_inline_configuration(self):
        inline = PlaceTranslationInline(Place, admin_site=self.site)
        self.assertEqual(inline.extra, 1)
        expected_fields = ("lang", "name", "description", "address")
        self.assertEqual(inline.fields, expected_fields)


class PlaceTranslationAdminTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create()
        CategoryTranslation.objects.create(
            category=self.category,
            lang="ko",
            name="문화"
        )

        self.sub_category = SubCategory.objects.create(category=self.category)
        SubCategoryTranslation.objects.create(
            sub_category=self.sub_category,
            lang="ko",
            name="궁궐"
        )

        self.place = Place.objects.create(
            content_id="translation_admin_test",
            category=self.category,
            sub_category=self.sub_category,
            use_time="24시간",
            favorite_count=0
        )

        self.translation = PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁",
            description="조선 왕조의 법궁으로 600년 역사를 자랑하는 대한민국 대표 궁궐입니다.",
            address="서울특별시 종로구 사직로 161"
        )

        self.site = AdminSite()
        self.admin = PlaceTranslationAdmin(PlaceTranslation, self.site)

    def test_list_display(self):
        expected_fields = ["place", "lang", "name", "tour_api_content_id", "get_short_description", "created_at"]
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_list_filter(self):
        expected_filters = ["lang", "created_at"]
        self.assertEqual(self.admin.list_filter, expected_filters)

    def test_search_fields(self):
        expected_search = ["name", "description", "place__content_id", "tour_api_content_id"]
        self.assertEqual(self.admin.search_fields, expected_search)

    def test_readonly_fields(self):
        expected_readonly = ["created_at", "updated_at"]
        self.assertEqual(self.admin.readonly_fields, expected_readonly)

    def test_get_short_description_method(self):
        # 50자를 넘는 긴 설명 테스트
        long_description = "조선 왕조의 법궁으로 1395년 태조 이성계에 의해 창건된 조선왕조 제일의 법궁입니다. 경복궁은 동궐이나 서궐에 비해 위치상 북궐이라 불리기도 했습니다."
        self.translation.description = long_description

        result = self.admin.get_short_description(self.translation)

        self.assertGreater(len(long_description), 50)
        self.assertTrue(result.endswith("..."))
        self.assertEqual(len(result), 53)  # 50자 + "..."

        # 정확히 50자인 경우
        exactly_50_chars = "A" * 50
        self.translation.description = exactly_50_chars

        result = self.admin.get_short_description(self.translation)
        self.assertEqual(result, exactly_50_chars)
        self.assertFalse(result.endswith("..."))

        # 50자 미만인 경우
        short_description = "짧은 설명"
        self.translation.description = short_description

        result = self.admin.get_short_description(self.translation)
        self.assertEqual(result, short_description)

        # 빈 문자열인 경우
        self.translation.description = ""

        result = self.admin.get_short_description(self.translation)
        self.assertEqual(result, "-")

        # None인 경우
        self.translation.description = None

        result = self.admin.get_short_description(self.translation)
        self.assertEqual(result, "-")

    def test_admin_registration(self):
        self.assertIn(PlaceTranslation, admin.site._registry)
        self.assertIsInstance(admin.site._registry[PlaceTranslation], PlaceTranslationAdmin)
