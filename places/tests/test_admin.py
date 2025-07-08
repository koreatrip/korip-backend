from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib import admin
from places.models import Place, PlaceTranslation
from places.admin import PlaceAdmin, PlaceTranslationAdmin, PlaceTranslationInline


# 테스트용 Place 데이터 생성
class PlaceAdminBasicTest(TestCase):
    def setUp(self):
        self.place = Place.objects.create(
            content_id="admin_test_001",
            category_id=1,
            sub_category_id=10,
            region_id=1,
            region_code="11",
            link_url="https://example.com",
            favorite_count=50
        )

        self.site = AdminSite()
        self.admin = PlaceAdmin(Place, self.site)

# list_display에 설정된 필드들이 올바른지 확인
    def test_place_admin_list_display(self):
        expected_fields = [
            "id",
            "content_id",
            "get_korean_name",
            "category_id",
            "sub_category_id",
            "region_id",
            "favorite_count",
            "region_code",
            "created_at"
        ]
        self.assertEqual(self.admin.list_display, expected_fields)

# list_filter에 설정된 필드들이 올바른지 확인
    def test_place_admin_list_filter(self):
        expected_filters = [
            "category_id",
            "sub_category_id",
            "region_id",
            "region_code",
            "created_at"
        ]
        self.assertEqual(self.admin.list_filter, expected_filters)

# search_fields에 설정된 필드들이 올바른지 확인
    def test_place_admin_search_fields(self):
        expected_search = [
            "content_id",
            "region_code",
            "translations__name",
        ]
        self.assertEqual(self.admin.search_fields, expected_search)

# readonly_fields가 올바르게 설정되었는지 확인
    def test_place_admin_readonly_fields(self):
        expected_readonly = [
            "id",
            "created_at",
            "updated_at",
            "last_synced_at"
        ]
        self.assertEqual(self.admin.readonly_fields, expected_readonly)

# fieldsets 구조가 올바른지 확인
    def test_place_admin_fieldsets_structure(self):
        fieldsets = self.admin.fieldsets

        self.assertEqual(len(fieldsets), 4)

        fieldset_titles = [fieldset[0] for fieldset in fieldsets]
        expected_titles = ["기본 정보", "카테고리 및 지역", "통계", "시스템"]
        self.assertEqual(fieldset_titles, expected_titles)

        basic_info_fields = fieldsets[0][1]["fields"]
        self.assertEqual(basic_info_fields[0], "content_id")
        self.assertIn("use_time", basic_info_fields)
        self.assertIn("link_url", basic_info_fields)

        # 카테고리 및 지역 그룹 확인
        category_fields = fieldsets[1][1]["fields"]
        self.assertIn("region_code", category_fields)

        # 통계 그룹 확인
        stats_fields = fieldsets[2][1]["fields"]
        self.assertIn("favorite_count", stats_fields)

        system_fieldset = fieldsets[3][1]["fields"]
        self.assertIn("last_synced_at", system_fieldset)

    def test_place_admin_has_inlines(self):
        self.assertEqual(len(self.admin.inlines), 1)
        self.assertIn(PlaceTranslationInline, self.admin.inlines)

    def test_admin_site_registration(self):
        from django.contrib import admin

        self.assertIn(Place, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Place], PlaceAdmin)

    def test_place_admin_display_all_fields(self):
        all_fields_in_fieldsets = []
        for fieldset in self.admin.fieldsets:
            all_fields_in_fieldsets.extend(fieldset[1]["fields"])

        expected_fields = [
            "content_id", "latitude", "longitude", "phone_number",
            "use_time", "link_url",
            "category_id", "sub_category_id", "region_id", "region_code",
            "favorite_count",
            "created_at", "updated_at", "last_synced_at"
        ]

        for field in expected_fields:
            self.assertIn(field, all_fields_in_fieldsets)

    def test_place_admin_filtering(self):
        Place.objects.create(
            content_id="filter_test_place",
            category_id=2,
            sub_category_id=20,
            region_id=2,
            region_code="21"
        )

        self.assertIn("category_id", self.admin.list_filter)
        self.assertIn("sub_category_id", self.admin.list_filter)
        self.assertIn("region_id", self.admin.list_filter)
        self.assertIn("region_code", self.admin.list_filter)

    def test_place_admin_category_foreign_key_display(self):
        self.assertIn("category_id", self.admin.list_display)
        self.assertIn("sub_category_id", self.admin.list_display)
        self.assertIn("region_id", self.admin.list_display)

    def test_place_admin_view_count_display(self):
        self.assertIn("favorite_count", self.admin.list_display)

        statistics_fieldset = self.admin.fieldsets[2]
        self.assertEqual(statistics_fieldset[0], "통계")
        self.assertIn("favorite_count", statistics_fieldset[1]["fields"])

    def test_place_admin_sync_time_management(self):
        self.assertIn("last_synced_at", self.admin.readonly_fields)

        system_fields = self.admin.fieldsets[3][1]["fields"]
        self.assertIn("last_synced_at", system_fields)

    def test_place_admin_get_korean_name_method(self):

        PlaceTranslation.objects.create(
            place=self.place,
            lang="ko",
            name="경복궁"
        )

        korean_name = self.admin.get_korean_name(self.place)
        self.assertEqual(korean_name, "경복궁")

        place_no_korean = Place.objects.create(content_id="no_korean_place")
        korean_name_empty = self.admin.get_korean_name(place_no_korean)
        self.assertEqual(korean_name_empty, "(번역 없음)")

    def test_place_translation_inline_configuration(self):
        inline = PlaceTranslationInline(Place, admin_site=self.site)
        self.assertEqual(inline.extra, 4)
        expected_fields = ["lang", "name", "description", "address"]
        self.assertEqual(inline.fields, expected_fields)


class PlaceTranslationAdminTest(TestCase):
    def setUp(self):
        self.place = Place.objects.create(
            content_id="translation_admin_test",
            category_id=1,
            sub_category_id=10,
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

    def test_place_translation_admin_list_display(self):
        expected_fields = ["place", "lang", "name", "get_short_description", "created_at"]
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_place_translation_admin_list_filter(self):
        expected_filters = ["lang", "created_at"]
        self.assertEqual(self.admin.list_filter, expected_filters)

    def test_place_translation_admin_search_fields(self):
        expected_search = ["name", "description", "place__content_id"]
        self.assertEqual(self.admin.search_fields, expected_search)

    def test_place_translation_admin_readonly_fields(self):
        expected_readonly = ["created_at", "updated_at"]
        self.assertEqual(self.admin.readonly_fields, expected_readonly)

    def test_get_short_description_method(self):
        # 50자를 넘는 긴 설명 (실제 확인된 85자 문자열)
        long_description = "조선 왕조의 법궁으로 1395년 태조 이성계에 의해 창건된 조선왕조 제일의 법궁입니다. 경복궁은 동궐이나 서궐에 비해 위치상 북궐이라 불리기도 했습니다."
        self.translation.description = long_description

        result = self.admin.get_short_description(self.translation)

        self.assertGreater(len(long_description), 50)
        self.assertTrue(result.endswith("..."))
        self.assertEqual(len(result), 53)


        exactly_50_chars = "A" * 50
        self.translation.description = exactly_50_chars

        result = self.admin.get_short_description(self.translation)
        self.assertEqual(result, exactly_50_chars)
        self.assertFalse(result.endswith("..."))

        short_description = "짧은 설명"
        self.translation.description = short_description

        result = self.admin.get_short_description(self.translation)
        self.assertEqual(result, short_description)

        self.translation.description = ""

        result = self.admin.get_short_description(self.translation)
        self.assertEqual(result, "-")

        self.translation.description = None

        result = self.admin.get_short_description(self.translation)
        self.assertEqual(result, "-")

# PlaceTranslation Admin 등록 확인
    def test_place_translation_admin_registration(self):
        from django.contrib import admin

        self.assertIn(PlaceTranslation, admin.site._registry)
        self.assertIsInstance(admin.site._registry[PlaceTranslation], PlaceTranslationAdmin)
