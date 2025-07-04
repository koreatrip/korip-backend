# Place Admin 기본 테스트
from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from places.models import Place
from places.admin import PlaceAdmin


# Place Admin 기본 설정 테스트
class PlaceAdminBasicTest(TestCase):

# 테스트용 Place 데이터 생성
    def setUp(self):
        self.place = Place.objects.create(
            content_id="admin_test_001",
            category_id=1,
            sub_category_id=10,
            region_id=1,
            view_count=50
        )

        self.site = AdminSite()
        self.admin = PlaceAdmin(Place, self.site)

# list_display에 설정된 필드들이 올바른지 확인
    def test_place_admin_list_display(self):
        expected_fields = [
            "id",
            "content_id",
            "category_id",
            "sub_category_id",
            "region_id",
            "view_count",
            "created_at"
        ]
        self.assertEqual(self.admin.list_display, expected_fields)

# list_filter에 설정된 필드들이 올바른지 확인
    def test_place_admin_list_filter(self):
        expected_filters = [
            "category_id",
            "sub_category_id",
            "region_id",
            "created_at"
        ]
        self.assertEqual(self.admin.list_filter, expected_filters)

# search_fields에 설정된 필드들이 올바른지 확인
    def test_place_admin_search_fields(self):
        expected_search = [
            "content_id",
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

        system_fieldset = fieldsets[3][1]["fields"]
        self.assertIn("last_synced_at", system_fieldset)

    def test_place_admin_has_no_inlines_yet(self):
        self.assertEqual(len(self.admin.inlines), 0)

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
            "opening_hours", "category_id", "sub_category_id", "region_id",
            "view_count", "created_at", "updated_at", "last_synced_at"
        ]

        for field in expected_fields:
            self.assertIn(field, all_fields_in_fieldsets)

    def test_place_admin_filtering(self):
        Place.objects.create(
            content_id="filter_test_place",
            category_id=2,
            sub_category_id=20,
            region_id=2
        )

        self.assertIn("category_id", self.admin.list_filter)
        self.assertIn("sub_category_id", self.admin.list_filter)
        self.assertIn("region_id", self.admin.list_filter)

    def test_place_admin_category_foreign_key_display(self):
        self.assertIn("category_id", self.admin.list_display)
        self.assertIn("sub_category_id", self.admin.list_display)
        self.assertIn("region_id", self.admin.list_display)

    def test_place_admin_view_count_display(self):
        self.assertIn("view_count", self.admin.list_display)

        statistics_fieldset = self.admin.fieldsets[2]
        self.assertEqual(statistics_fieldset[0], "통계")
        self.assertIn("view_count", statistics_fieldset[1]["fields"])

    def test_place_admin_sync_time_management(self):
        self.assertIn("last_synced_at", self.admin.readonly_fields)

        system_fields = self.admin.fieldsets[3][1]["fields"]
        self.assertIn("last_synced_at", system_fields)
