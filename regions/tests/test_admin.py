from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.admin.sites import AdminSite

from regions.models import Region, SubRegion, RegionTranslation, SubRegionTranslation
from regions.admin import RegionAdmin, SubRegionAdmin

User = get_user_model()


class RegionAdminTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123",
            nickname="관리자",
            phone_number="010-1234-5678"
        )

        self.client = Client()
        self.client.force_login(self.superuser)
        self.site = AdminSite()
        self.region = Region.objects.create()

        RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="서울",
            description="대한민국의 수도"
        )
        RegionTranslation.objects.create(
            region=self.region,
            lang="en",
            name="Seoul",
            description="Capital of South Korea"
        )
        RegionTranslation.objects.create(
            region=self.region,
            lang="jp",
            name="ソウル",
            description="韓国の首都"
        )
        RegionTranslation.objects.create(
            region=self.region,
            lang="cn",
            name="首尔",
            description="韩国首都"
        )

    def test_region_admin_list_view(self):
        url = reverse("admin:regions_region_changelist")
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "서울")

    def test_region_admin_detail_view(self):
        url = reverse("admin:regions_region_change", args=[self.region.id])
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "서울")
        self.assertContains(response, "Seoul")
        self.assertContains(response, "ソウル")
        self.assertContains(response, "首尔")

    def test_region_admin_create_view(self):
        url = reverse("admin:regions_region_add")
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="translations-0-lang"')
        self.assertContains(response, 'name="translations-1-lang"')
        self.assertContains(response, 'name="translations-2-lang"')
        self.assertContains(response, 'name="translations-3-lang"')

    def test_region_admin_save_with_translations(self):
        new_region = Region.objects.create()
        RegionTranslation.objects.create(
            region=new_region,
            lang="ko",
            name="부산",
            description="대한민국 제2의 도시"
        )
        RegionTranslation.objects.create(
            region=new_region,
            lang="en",
            name="Busan",
            description="Second largest city in South Korea"
        )

        url = reverse("admin:regions_region_changelist")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "부산")

        detail_url = reverse("admin:regions_region_change", args=[new_region.id])
        response = self.client.get(detail_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "부산")
        self.assertContains(response, "Busan")

        self.assertIsNotNone(new_region)
        korean_translation = RegionTranslation.objects.get(
            region=new_region, lang="ko"
        )
        self.assertEqual(korean_translation.name, "부산")

        english_translation = RegionTranslation.objects.get(
            region=new_region, lang="en"
        )
        self.assertEqual(english_translation.name, "Busan")

    def test_region_admin_search_functionality(self):
        url = reverse("admin:regions_region_changelist")

        response = self.client.get(url, {"q": "서울"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "서울")

        response = self.client.get(url, {"q": "Seoul"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "서울")

    def test_region_admin_class_configuration(self):
        admin_instance = RegionAdmin(Region, self.site)

        expected_list_display = ["id", "get_korean_name", "get_subregion_count", "created_at"]
        self.assertEqual(list(admin_instance.list_display), expected_list_display)

        expected_search_fields = ["translations__name"]
        self.assertEqual(list(admin_instance.search_fields), expected_search_fields)

        expected_list_filter = ["created_at"]
        self.assertEqual(list(admin_instance.list_filter), expected_list_filter)


class SubRegionAdminTest(TestCase):
    def setUp(self):

        self.superuser = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123",
            nickname="관리자",
            phone_number="010-1234-5678"
        )
        self.client = Client()
        self.client.force_login(self.superuser)
        self.site = AdminSite()

        self.region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="서울",
            description="대한민국의 수도"
        )

        self.subregion = SubRegion.objects.create(
            region=self.region,
            favorite_count=100,
            latitude=37.5173,
            longitude=127.0473
        )

        SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="ko",
            name="강남구",
            description="서울의 중심 상업지구",
            features="쇼핑, 비즈니스, 강남스타일"
        )

    def test_subregion_admin_list_view(self):

        url = reverse("admin:regions_subregion_changelist")
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "강남구")

    def test_subregion_admin_detail_view(self):

        url = reverse("admin:regions_subregion_change", args=[self.subregion.id])
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "강남구")
        self.assertContains(response, "100")
        self.assertContains(response, "37.5173")
        self.assertContains(response, "127.0473")

    def test_subregion_admin_create_with_parent_region(self):
        new_subregion = SubRegion.objects.create(
            region=self.region,
            favorite_count=50,
            latitude=37.5665,
            longitude=126.9780
        )
        SubRegionTranslation.objects.create(
            sub_region=new_subregion,
            lang="ko",
            name="종로구",
            description="서울의 중심지",
            features="역사, 문화, 전통"
        )

        url = reverse("admin:regions_subregion_changelist")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "종로구")

        detail_url = reverse("admin:regions_subregion_change", args=[new_subregion.id])
        response = self.client.get(detail_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "종로구")
        self.assertContains(response, "50")
        self.assertIsNotNone(new_subregion)
        self.assertEqual(new_subregion.region, self.region)

        translation = SubRegionTranslation.objects.get(
            sub_region=new_subregion, lang="ko"
        )
        self.assertEqual(translation.name, "종로구")

    def test_subregion_admin_class_configuration(self):
        admin_instance = SubRegionAdmin(SubRegion, self.site)

        expected_list_display = [
            "id", "get_korean_name", "get_region_name",
            "favorite_count", "latitude", "longitude", "created_at"
        ]
        self.assertEqual(list(admin_instance.list_display), expected_list_display)


class AdminInlineTest(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123",
            nickname="관리자",
            phone_number="010-1234-5678"
        )

        self.client = Client()
        self.client.force_login(self.superuser)

    def test_region_with_subregion_inline(self):
        region = Region.objects.create()
        RegionTranslation.objects.create(
            region=region, lang="ko", name="경기도", description="서울 주변 지역"
        )

        url = reverse("admin:regions_region_change", args=[region.id])
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="subregions-0-favorite_count"')
        self.assertContains(response, 'name="subregions-0-latitude"')
        self.assertContains(response, 'name="subregions-0-longitude"')

    def test_translation_inline_language_choices(self):
        region = Region.objects.create()
        url = reverse("admin:regions_region_change", args=[region.id])
        response = self.client.get(url, follow=True)

        self.assertContains(response, 'value="ko"')
        self.assertContains(response, 'value="en"')
        self.assertContains(response, 'value="jp"')
        self.assertContains(response, 'value="cn"')
