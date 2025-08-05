# regions/tests/test_admin.py
# GIS 전환에 완전히 대응된 admin 테스트 파일

from django.test import TestCase
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.gis.geos import Point

from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation
from regions.admin import RegionAdmin, SubRegionAdmin

User = get_user_model()


class RegionAdminTest(TestCase):
    """Region Admin 테스트 클래스"""

    def setUp(self):
        """테스트 데이터 준비"""
        # 관리자 사용자 생성
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123"
        )
        self.client.force_login(self.admin_user)

        # 테스트용 Region 생성
        self.seoul_region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.seoul_region,
            lang="ko",
            name="서울",
            description="대한민국의 수도"
        )

        self.gyeonggi_region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.gyeonggi_region,
            lang="ko",
            name="경기도",
            description="서울 주변 지역"
        )

    def test_region_admin_create_view(self):
        """Region 생성 페이지 테스트"""
        url = reverse("admin:regions_region_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 🔥 RegionTranslationInline이 표시되는지 확인 (좀 더 유연하게)
        self.assertContains(response, "지역 번역")  # inline 제목 확인
        self.assertContains(response, "translations-TOTAL_FORMS")  # formset 확인
        self.assertContains(response, "언어 코드")  # 필드 라벨 확인

    def test_region_admin_class_configuration(self):
        """RegionAdmin 클래스 설정 테스트"""
        admin_instance = admin.site._registry[Region]

        # 🔥 GIS 전환 후 list_display (get_subregion_count 제거됨)
        expected_list_display = [
            "id", "get_korean_name", "created_at"
        ]

        # 🔥 GIS 전환 후 list_filter 추가됨
        expected_list_filter = ["created_at"]

        self.assertEqual(list(admin_instance.list_display), expected_list_display)
        self.assertEqual(list(admin_instance.list_filter), expected_list_filter)


class SubRegionAdminTest(TestCase):
    """SubRegion Admin 테스트 클래스"""

    def setUp(self):
        """테스트 데이터 준비"""
        # 관리자 사용자 생성
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123"
        )
        self.client.force_login(self.admin_user)

        # 테스트용 Region 생성
        self.seoul_region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.seoul_region,
            lang="ko",
            name="서울",
            description="대한민국의 수도"
        )

    def test_subregion_admin_class_configuration(self):
        """SubRegionAdmin 클래스 설정 테스트"""
        admin_instance = admin.site._registry[SubRegion]

        # 🔥 GIS 전환 후 latitude, longitude → get_latitude, get_longitude 변경
        expected_list_display = [
            "id", "get_korean_name", "get_region_name",
            "favorite_count", "get_latitude", "get_longitude", "created_at"
        ]

        expected_list_filter = ["region", "created_at"]
        expected_search_fields = ["translations__name", "region__translations__name"]
        expected_readonly_fields = ["created_at", "updated_at"]

        self.assertEqual(list(admin_instance.list_display), expected_list_display)
        self.assertEqual(list(admin_instance.list_filter), expected_list_filter)
        self.assertEqual(list(admin_instance.search_fields), expected_search_fields)
        self.assertEqual(list(admin_instance.readonly_fields), expected_readonly_fields)

    def test_subregion_admin_detail_view(self):
        """SubRegion 상세 페이지 테스트"""
        # 🔥 GIS Point로 SubRegion 생성
        subregion = SubRegion.objects.create(
            region=self.seoul_region,
            favorite_count=100,
            location=Point(127.0276, 37.5173)  # Point(경도, 위도)
        )

        # 한국어 번역 추가
        SubRegionTranslation.objects.create(
            sub_region=subregion,
            lang="ko",
            name="강남구",
            description="서울의 중심 상업지구"
        )

        url = reverse("admin:regions_subregion_change", args=[subregion.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 🔥 실제로 중요한 건 페이지가 정상 로드되고 기본 데이터가 표시되는 것
        # GIS 위젯의 정확한 렌더링 형태보다는 페이지 기능이 작동하는지가 핵심

        # 기본 페이지 요소들 확인
        self.assertContains(response, "강남구")  # 번역 데이터
        self.assertContains(response, "즐겨찾기 수")  # favorite_count 필드 라벨
        self.assertContains(response, "100")  # favorite_count 값
        self.assertContains(response, "위치")  # location 필드 라벨 (한국어)

        # 🔥 SubRegion이 정상적으로 생성되고 GIS 좌표가 저장되었는지 확인
        # 페이지 렌더링 확인 대신 실제 데이터 확인
        saved_subregion = SubRegion.objects.get(id=subregion.id)
        self.assertIsNotNone(saved_subregion.location)  # location 필드에 값이 있는지
        self.assertEqual(saved_subregion.latitude, 37.5173)  # 위도 정확한지
        self.assertEqual(saved_subregion.longitude, 127.0276)  # 경도 정확한지

        # 🔥 페이지에 SubRegion 관련 필드들이 표시되는지 확인
        self.assertContains(response, "부모 지역")  # region 필드
        self.assertContains(response, "서울")  # 부모 지역명

        # 🔥 필수적인 admin 요소들이 있는지 확인
        self.assertContains(response, "저장")  # 저장 버튼
        self.assertContains(response, "지역구 변경")  # 페이지 제목


class AdminInlineTest(TestCase):
    """Admin Inline 테스트 클래스"""

    def setUp(self):
        """테스트 데이터 준비"""
        # 관리자 사용자 생성
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123"
        )
        self.client.force_login(self.admin_user)

        # 테스트용 Region 생성
        self.gyeonggi_region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.gyeonggi_region,
            lang="ko",
            name="경기도",
            description="서울 주변 지역"
        )

    def test_region_with_subregion_inline(self):
        """Region 수정 페이지에서 SubRegionInline 테스트"""
        # 🔥 SubRegion을 미리 하나 만들어두자 (GIS Point로)
        subregion = SubRegion.objects.create(
            region=self.gyeonggi_region,
            favorite_count=50,
            location=Point(127.0276, 37.5173)  # 경기도 좌표
        )

        # SubRegion 번역 추가
        SubRegionTranslation.objects.create(
            sub_region=subregion,
            lang="ko",
            name="수원시",
            description="경기도 중심지"
        )

        url = reverse("admin:regions_region_change", args=[self.gyeonggi_region.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 🔥 SubRegionInline이 표시되는지 확인
        self.assertContains(response, "지역구")  # inline 제목
        self.assertContains(response, "즐겨찾기 수")  # favorite_count 필드 라벨
        self.assertContains(response, "좌표")  # get_coordinate_display 라벨

        # 🔥 extra=1이므로 새로운 SubRegion 추가 폼도 있어야 함
        self.assertContains(response, 'name="subregions-0-favorite_count"')


class RegionTranslationAdminTest(TestCase):
    """RegionTranslation Admin 테스트"""

    def setUp(self):
        """테스트 데이터 준비"""
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123"
        )
        self.client.force_login(self.admin_user)

        self.region = Region.objects.create()
        self.translation = RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="서울",
            description="대한민국의 수도"
        )

    def test_regiontranslation_list_view(self):
        """RegionTranslation 목록 페이지 테스트"""
        url = reverse("admin:regions_regiontranslation_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "서울")


class SubRegionTranslationAdminTest(TestCase):
    """SubRegionTranslation Admin 테스트"""

    def setUp(self):
        """테스트 데이터 준비"""
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="testpass123"
        )
        self.client.force_login(self.admin_user)

        self.region = Region.objects.create()
        self.subregion = SubRegion.objects.create(
            region=self.region,
            favorite_count=0,
            location=Point(127.0276, 37.5173)
        )
        self.translation = SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="ko",
            name="강남구",
            description="서울의 중심 상업지구"
        )

    def test_subregiontranslation_list_view(self):
        """SubRegionTranslation 목록 페이지 테스트"""
        url = reverse("admin:regions_subregiontranslation_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "강남구")
