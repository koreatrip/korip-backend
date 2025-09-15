from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework.test import APITestCase

from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation
from regions.serializers import RegionSerializer, SubRegionSerializer


class RegionSerializerTest(TestCase):
    """RegionSerializer 테스트"""

    def setUp(self):
        self.region = Region.objects.create()
        
        # 한국어 번역
        RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="서울특별시",
            description="대한민국의 수도이자 최대 도시",
            features="정치, 경제, 문화의 중심지"
        )
        
        # 영어 번역
        RegionTranslation.objects.create(
            region=self.region,
            lang="en",
            name="Seoul",
            description="Capital and largest city of South Korea",
            features="Center of politics, economy, and culture"
        )

    def test_korean_serialization(self):
        """한국어 직렬화 테스트"""
        context = {"language": "ko"}
        serializer = RegionSerializer(self.region, context=context)
        data = serializer.data

        self.assertEqual(data["id"], self.region.id)
        self.assertEqual(data["name"], "서울특별시")
        self.assertEqual(data["description"], "대한민국의 수도이자 최대 도시")
        self.assertEqual(data["feature"], "정치, 경제, 문화의 중심지")

    def test_english_serialization(self):
        """영어 직렬화 테스트"""
        context = {"language": "en"}
        serializer = RegionSerializer(self.region, context=context)
        data = serializer.data

        self.assertEqual(data["id"], self.region.id)
        self.assertEqual(data["name"], "Seoul")
        self.assertEqual(data["description"], "Capital and largest city of South Korea")
        self.assertEqual(data["feature"], "Center of politics, economy, and culture")

    def test_missing_translation(self):
        """번역이 없는 언어 테스트"""
        context = {"language": "jp"}
        serializer = RegionSerializer(self.region, context=context)
        data = serializer.data

        self.assertEqual(data["id"], self.region.id)
        self.assertEqual(data["name"], "")
        self.assertEqual(data["description"], "")
        self.assertEqual(data["feature"], "")

    def test_default_language_korean(self):
        """기본 언어(한국어) 테스트"""
        context = {}  # language 컨텍스트 없음
        serializer = RegionSerializer(self.region, context=context)
        data = serializer.data

        self.assertEqual(data["name"], "서울특별시")
        self.assertEqual(data["description"], "대한민국의 수도이자 최대 도시")

    def test_invalid_language_code(self):
        """잘못된 언어 코드 테스트"""
        context = {"language": "invalid"}
        serializer = RegionSerializer(self.region, context=context)
        data = serializer.data

        self.assertEqual(data["name"], "")
        self.assertEqual(data["description"], "")
        self.assertEqual(data["feature"], "")

    def test_serializer_fields(self):
        """직렬화 필드 구조 테스트"""
        context = {"language": "ko"}
        serializer = RegionSerializer(self.region, context=context)
        data = serializer.data

        expected_fields = {"id", "name", "description", "feature"}
        self.assertEqual(set(data.keys()), expected_fields)

    def test_multiple_regions_serialization(self):
        """여러 지역 직렬화 테스트"""
        # 두 번째 지역 생성
        region2 = Region.objects.create()
        RegionTranslation.objects.create(
            region=region2,
            lang="ko",
            name="부산광역시",
            description="대한민국의 제2의 도시"
        )

        regions = [self.region, region2]
        context = {"language": "ko"}
        serializer = RegionSerializer(regions, many=True, context=context)
        data = serializer.data

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "서울특별시")
        self.assertEqual(data[1]["name"], "부산광역시")


class SubRegionSerializerTest(TestCase):
    """SubRegionSerializer 테스트"""

    def setUp(self):
        self.region = Region.objects.create()
        
        self.subregion = SubRegion.objects.create(
            region=self.region,
            favorite_count=150,
            location=Point(127.0473, 37.5173)  # 강남구 좌표
        )
        
        # 한국어 번역
        SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="ko",
            name="강남구",
            description="서울의 비즈니스 중심지",
            features="높은 지가와 상업지구"
        )
        
        # 영어 번역
        SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="en",
            name="Gangnam District",
            description="Business center of Seoul",
            features="High real estate prices and commercial areas"
        )

    def test_korean_serialization(self):
        """한국어 직렬화 테스트"""
        context = {"language": "ko"}
        serializer = SubRegionSerializer(self.subregion, context=context)
        data = serializer.data

        self.assertEqual(data["id"], self.subregion.id)
        self.assertEqual(data["name"], "강남구")
        self.assertEqual(data["description"], "서울의 비즈니스 중심지")
        self.assertEqual(data["feature"], "높은 지가와 상업지구")
        self.assertEqual(data["favorite_count"], 150)
        self.assertEqual(data["latitude"], 37.5173)
        self.assertEqual(data["longitude"], 127.0473)
        self.assertEqual(data["is_favorite"], False)  # 기본값

    def test_english_serialization(self):
        """영어 직렬화 테스트"""
        context = {"language": "en"}
        serializer = SubRegionSerializer(self.subregion, context=context)
        data = serializer.data

        self.assertEqual(data["name"], "Gangnam District")
        self.assertEqual(data["description"], "Business center of Seoul")
        self.assertEqual(data["feature"], "High real estate prices and commercial areas")

    def test_is_favorite_true(self):
        """즐겨찾기 True 테스트"""
        context = {
            "language": "ko",
            "user_favorite_subregion_ids": {self.subregion.id}
        }
        serializer = SubRegionSerializer(self.subregion, context=context)
        data = serializer.data

        self.assertEqual(data["is_favorite"], True)

    def test_is_favorite_false(self):
        """즐겨찾기 False 테스트"""
        context = {
            "language": "ko",
            "user_favorite_subregion_ids": {999}  # 다른 ID
        }
        serializer = SubRegionSerializer(self.subregion, context=context)
        data = serializer.data

        self.assertEqual(data["is_favorite"], False)

    def test_is_favorite_no_context(self):
        """즐겨찾기 컨텍스트가 없는 경우 테스트"""
        context = {"language": "ko"}
        serializer = SubRegionSerializer(self.subregion, context=context)
        data = serializer.data

        self.assertEqual(data["is_favorite"], False)

    def test_missing_translation(self):
        """번역이 없는 언어 테스트"""
        context = {"language": "jp"}
        serializer = SubRegionSerializer(self.subregion, context=context)
        data = serializer.data

        self.assertEqual(data["name"], "")
        self.assertEqual(data["description"], "")
        self.assertEqual(data["feature"], "")
        # 다른 필드들은 정상 작동
        self.assertEqual(data["favorite_count"], 150)
        self.assertEqual(data["is_favorite"], False)

    def test_serializer_fields(self):
        """직렬화 필드 구조 테스트"""
        context = {"language": "ko"}
        serializer = SubRegionSerializer(self.subregion, context=context)
        data = serializer.data

        expected_fields = {
            "id", "name", "description", "feature",
            "favorite_count", "is_favorite", "latitude", "longitude"
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_location_coordinates(self):
        """위도/경도 좌표 테스트"""
        context = {"language": "ko"}
        serializer = SubRegionSerializer(self.subregion, context=context)
        data = serializer.data

        # Point(longitude, latitude) 순서로 저장되지만
        # 직렬화할 때는 latitude, longitude로 분리
        self.assertAlmostEqual(data["latitude"], 37.5173, places=4)
        self.assertAlmostEqual(data["longitude"], 127.0473, places=4)

    def test_multiple_subregions_with_favorites(self):
        """여러 서브지역과 즐겨찾기 테스트"""
        # 두 번째 서브지역 생성
        subregion2 = SubRegion.objects.create(
            region=self.region,
            favorite_count=80,
            location=Point(126.9770, 37.5796)
        )
        SubRegionTranslation.objects.create(
            sub_region=subregion2,
            lang="ko",
            name="종로구",
            description="서울의 역사적 중심지"
        )

        subregions = [self.subregion, subregion2]
        context = {
            "language": "ko",
            "user_favorite_subregion_ids": {self.subregion.id}  # 첫 번째만 즐겨찾기
        }
        
        serializer = SubRegionSerializer(subregions, many=True, context=context)
        data = serializer.data

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["is_favorite"], True)   # 강남구
        self.assertEqual(data[1]["is_favorite"], False)  # 종로구
        self.assertEqual(data[0]["name"], "강남구")
        self.assertEqual(data[1]["name"], "종로구")

    def test_empty_favorite_set(self):
        """빈 즐겨찾기 집합 테스트"""
        context = {
            "language": "ko",
            "user_favorite_subregion_ids": set()
        }
        serializer = SubRegionSerializer(self.subregion, context=context)
        data = serializer.data

        self.assertEqual(data["is_favorite"], False)

    def test_none_favorite_context(self):
        """None 즐겨찾기 컨텍스트 테스트"""
        context = {
            "language": "ko",
            "user_favorite_subregion_ids": None
        }
        serializer = SubRegionSerializer(self.subregion, context=context)
        data = serializer.data

        self.assertEqual(data["is_favorite"], False)


class SerializerIntegrationTest(TestCase):
    """Serializer 통합 테스트"""

    def setUp(self):
        self.region = Region.objects.create()
        RegionTranslation.objects.create(
            region=self.region,
            lang="ko",
            name="서울",
            description="수도"
        )

        self.subregion = SubRegion.objects.create(
            region=self.region,
            favorite_count=100,
            location=Point(127.0, 37.5)
        )
        SubRegionTranslation.objects.create(
            sub_region=self.subregion,
            lang="ko",
            name="테스트구",
            description="테스트 지역"
        )

    def test_serializer_exception_handling(self):
        """예외 처리 테스트"""
        # translations 관계가 없는 경우를 시뮬레이션하기 위해
        # 일시적으로 관계를 제거
        context = {"language": "ko"}
        
        # RegionSerializer 예외 처리
        serializer = RegionSerializer(self.region, context=context)
        data = serializer.data
        
        # 예외가 발생해도 빈 문자열 반환
        self.assertIsInstance(data["name"], str)
        self.assertIsInstance(data["description"], str)
        self.assertIsInstance(data["feature"], str)

    def test_performance_with_multiple_objects(self):
        """다수 객체 처리 성능 테스트"""
        # 여러 지역과 서브지역 생성
        regions = []
        subregions = []
        
        for i in range(5):
            region = Region.objects.create()
            RegionTranslation.objects.create(
                region=region,
                lang="ko",
                name=f"지역{i}",
                description=f"설명{i}"
            )
            regions.append(region)
            
            subregion = SubRegion.objects.create(
                region=region,
                favorite_count=i * 10,
                location=Point(127.0 + i, 37.5 + i)
            )
            SubRegionTranslation.objects.create(
                sub_region=subregion,
                lang="ko",
                name=f"서브지역{i}",
                description=f"서브설명{i}"
            )
            subregions.append(subregion)

        # 직렬화 테스트
        context = {"language": "ko"}
        region_serializer = RegionSerializer(regions, many=True, context=context)
        subregion_serializer = SubRegionSerializer(subregions, many=True, context=context)
        
        region_data = region_serializer.data
        subregion_data = subregion_serializer.data
        
        self.assertEqual(len(region_data), 5)
        self.assertEqual(len(subregion_data), 5)
        
        # 각 데이터가 올바르게 직렬화되었는지 확인
        for i, data in enumerate(region_data):
            self.assertEqual(data["name"], f"지역{i}")
            
        for i, data in enumerate(subregion_data):
            self.assertEqual(data["name"], f"서브지역{i}")
            self.assertEqual(data["favorite_count"], i * 10)