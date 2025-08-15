from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point
from django.db import transaction
from typing import Dict, List, Any, Optional, Tuple
from django.utils import timezone
import time

from places.models import Place, PlaceTranslation
from places.services.multilang_tour_api_client import MultiLangTourAPIClient
from places.services.category_mapper import CategoryMapper
from places.utils.coordinate_matcher import (
    find_matching_place_by_gis,
    calculate_center_point,
    create_point_from_coordinates
)
from categories.models import Category, SubCategory
from regions.models import Region, SubRegion


class Command(BaseCommand):
    help = "투어 API에서 다국어 관광지 데이터를 수집하고 GIS 매칭으로 통합"

    def __init__(self):
        super().__init__()
        # CategoryMapper 인스턴스 생성 - 완전한 매핑 테이블 사용!
        self.category_mapper = CategoryMapper()

    def add_arguments(self, parser):
        parser.add_argument(
            "--languages",
            type=str,
            default="ko,en,jp,cn",
            help="수집할 언어 목록 (쉼표로 구분, 기본값: ko,en,jp,cn)"
        )
        parser.add_argument(
            "--area-code",
            type=int,
            default=1,
            help="지역 코드 (1=서울, 2=인천, ..., 기본값: 1)"
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="언어당 수집할 최대 관광지 수 (기본값: 100)"
        )
        parser.add_argument(
            "--threshold",
            type=int,
            default=100,
            help="GIS 매칭 임계값 (미터 단위, 기본값: 100m)"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="실제 저장 없이 시뮬레이션만 실행"
        )
        parser.add_argument(
            "--collect-details",
            action="store_true",
            help="상세정보도 함께 수집"
        )

    def handle(self, *args, **options):
        languages = [lang.strip() for lang in options["languages"].split(",")]
        area_code = options["area_code"]
        limit = options["limit"]
        threshold = options["threshold"]
        dry_run = options["dry_run"]
        collect_details = options["collect_details"]

        self._validate_options(languages, area_code)

        self.stdout.write("다국어 관광지 동기화 시작")
        self.stdout.write(f"지역 코드: {area_code}")
        self.stdout.write(f"언어: {', '.join(languages)}")
        self.stdout.write(f"언어당 최대 수집: {limit}개")
        self.stdout.write(f"GIS 매칭 임계값: {threshold}m")
        self.stdout.write(f"상세정보 수집: {'예' if collect_details else '아니오'}")
        if dry_run:
            self.stdout.write("DRY RUN 모드 (실제 저장 안함)")

        start_time = time.time()

        try:
            multilang_data = self._collect_multilang_data(languages, area_code, limit, collect_details)

            if multilang_data["status"] != "success":
                raise CommandError(f"데이터 수집 실패: {multilang_data.get('errors', [])}")

            integration_result = self._integrate_multilang_places(
                multilang_data["data"], threshold, dry_run
            )

            self._print_results(integration_result, time.time() - start_time)

        except Exception as e:
            raise CommandError(f"동기화 실패: {str(e)}")

    def _validate_options(self, languages: List[str], area_code: int):
        supported_languages = ["ko", "en", "jp", "cn"]
        invalid_languages = [lang for lang in languages if lang not in supported_languages]
        if invalid_languages:
            raise CommandError(
                f"지원하지 않는 언어: {invalid_languages} (지원 언어: {supported_languages})"
            )

        if not (1 <= area_code <= 39):
            raise CommandError(f"잘못된 지역 코드: {area_code} (1-39 사이 값 입력)")

    def _collect_multilang_data(self, languages: List[str], area_code: int, limit: int, collect_details: bool) -> Dict[
        str, Any]:
        self.stdout.write("투어 API에서 다국어 데이터 수집 중...")

        api_client = MultiLangTourAPIClient()
        result = api_client.collect_all_languages(area_code=area_code, num_of_rows=limit)

        if result["status"] == "success" and collect_details:
            self.stdout.write("상세정보 수집 중...")
            for lang, places in result["data"].items():
                for i, place_data in enumerate(places):
                    content_id = place_data.get("contentid")
                    content_type_id = place_data.get("contenttypeid", "12")
                    if content_id:
                        # detailCommon2 호출 (overview 등)
                        detail_result = api_client.get_place_detail_common(content_id, lang)
                        if detail_result["status"] == "success":
                            detail_data = detail_result["data"]
                            place_data.update(detail_data)

                        time.sleep(0.1)

                        # detailIntro2 호출 (전화번호, 이용시간, 홈페이지 등)
                        intro_result = api_client.get_place_detail_intro(content_id, content_type_id, lang)
                        if intro_result["status"] == "success":
                            intro_data = intro_result["data"]
                            place_data.update(intro_data)

                        time.sleep(0.1)

        if result["status"] == "success":
            total_places = sum(len(places) for places in result["data"].values())
            self.stdout.write(f"총 {total_places}개 관광지 수집 완료")

            for lang, places in result["data"].items():
                count = len(places)
                if count > 0:
                    self.stdout.write(f"  {lang.upper()}: {count}개")
        else:
            self.stdout.write(f"데이터 수집 실패: {result.get('errors', [])}")

        return result

    def _integrate_multilang_places(self, multilang_data: Dict[str, List[Dict]],
                                    threshold: int, dry_run: bool) -> Dict[str, Any]:
        self.stdout.write("다국어 관광지 GIS 매칭 중...")

        integration_stats = {
            "total_processed": 0,
            "new_places_created": 0,
            "translations_added": 0,
            "translations_updated": 0,
            "places_updated": 0,
            "gis_matches_found": 0,
            "category_mappings": 0,
            "region_mappings": 0,
            "processing_errors": []
        }

        if "ko" in multilang_data and multilang_data["ko"]:
            self.stdout.write("한국어 관광지 기준점 생성 중...")
            integration_stats = self._process_korean_places(
                multilang_data["ko"], integration_stats, dry_run
            )

        for lang in ["en", "jp", "cn"]:
            if lang in multilang_data and multilang_data[lang]:
                self.stdout.write(f"{lang.upper()} 관광지 매칭 중...")
                integration_stats = self._process_other_language_places(
                    multilang_data[lang], lang, threshold, integration_stats, dry_run
                )

        return integration_stats

    def _map_categories(self, place_data: Dict) -> Tuple[Optional[Category], Optional[SubCategory]]:
        """
        CategoryMapper를 사용해서 정확한 카테고리 매핑
        VE, NA, FD, SH 등 모든 신분류 코드 지원!
        """
        try:
            # CategoryMapper의 완전한 매핑 테이블 사용
            processed_data = self.category_mapper.process_tour_api_place(place_data)

            category_id = processed_data.get("category_id")
            subcategory_id = processed_data.get("sub_category_id")

            category = None
            subcategory = None

            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    pass

            if subcategory_id:
                try:
                    subcategory = SubCategory.objects.get(id=subcategory_id)
                except SubCategory.DoesNotExist:
                    pass

            # 서브카테고리가 없으면 이름 기반 추론 시도
            if category and not subcategory:
                place_name = place_data.get("title", "")
                subcategory = self._infer_subcategory_from_name(category, place_name)

            return category, subcategory

        except Exception as e:
            # CategoryMapper 실패시 기존 방식으로 대체
            return self._map_categories_fallback(place_data)

    def _infer_subcategory_from_name(self, category: Category, place_name: str) -> Optional[SubCategory]:
        """관광지 이름에서 서브카테고리 추론"""
        try:
            # 카테고리 이름 확인
            category_translation = category.translations.filter(lang="ko").first()
            if not category_translation:
                return None

            category_name = category_translation.name

            if category_name == "음식":
                # 음식 서브카테고리 키워드 매핑 (대폭 확장)
                food_keywords = {
                    "한식": ["돈까스", "김치", "불고기", "비빔밥", "냉면", "갈비", "삼겹살", "한정식", "국밥", "찌개",
                           "백반", "순대", "족발", "보쌈", "치킨", "닭", "한우", "곱창", "막창", "순두부", "떡볶이",
                           "한식", "국수", "쌀국수", "김밥", "라면", "육개장", "설렁탕", "곰탕", "추어탕", "매운탕"],
                    "일식": ["스시", "라멘", "우동", "카레", "규동", "덴푸라", "야키토리", "사시미", "초밥", "돈부리",
                           "이자카야", "사케", "테리야키", "가츠", "모츠", "야끼니꾸", "일식", "소바", "타코야키",
                           "미소", "돈코츠", "롯데리아", "초밥집", "회집"],
                    "중식": ["짬뽕", "짜장", "탕수육", "마파두부", "딤섬", "볶음밥", "만두", "깐풍기", "양장피",
                           "유린기", "라조기", "팔보채", "고추잡채", "중식", "중국", "차이나", "마라", "훠궈"],
                    "양식": ["스테이크", "파스타", "피자", "햄버거", "리조또", "샐러드", "브런치", "카페", "베이커리",
                           "와인", "스파게티", "파니니", "샌드위치", "브레드", "양식", "이탈리안", "아메리칸",
                           "버거", "커피", "디저트", "케이크", "빵집", "cafe", "coffee"]
                }

                for subcategory_name, keywords in food_keywords.items():
                    for keyword in keywords:
                        if keyword in place_name:
                            # 해당 서브카테고리 찾기
                            subcategory = SubCategory.objects.filter(
                                category=category,
                                translations__name=subcategory_name,
                                translations__lang="ko"
                            ).first()
                            if subcategory:
                                return subcategory

            elif category_name == "문화":
                # 문화 서브카테고리 키워드 매핑 (대폭 확장)
                culture_keywords = {
                    "박물관": ["박물관", "기념관", "전시관", "역사관", "문화관", "체험관", "뮤지엄", "museum",
                            "과학관", "자연사", "어린이박물관", "민속박물관", "전쟁기념관", "체험", "코스",
                            "프로그램", "교육", "워크샵", "클래스"],
                    "미술관": ["미술관", "갤러리", "아트", "Gallery", "Art", "화랑", "전시장", "아트센터",
                            "예술관", "창작", "작품", "artist", "gallery", "전시", "스페이스", "드로잉"],
                    "역사": ["궁", "성", "고궁", "사적", "유적", "문화재", "왕릉", "능", "조선", "고려",
                           "역사", "왕", "선조", "태조", "세종", "이순신", "고인돌", "성곽", "성벽"],
                    "종교": ["절", "사찰", "교회", "성당", "종교", "암자", "대웅전", "법당", "사원",
                           "불교", "기독교", "천주교", "temple", "church"],
                    "전통문화": ["한옥", "전통", "민속", "국악", "전통공예", "문화원", "체험", "공방",
                             "문화", "전통시장", "민속촌", "한국전통", "문화체험", "옛집", "고택",
                             "한옥마을", "전통가옥", "민가", "고가", "고건축"],
                    "궁궐": ["궁", "궁궐", "창덕궁", "경복궁", "덕수궁", "창경궁", "종묘", "왕궁", "palace"]
                }

                for subcategory_name, keywords in culture_keywords.items():
                    for keyword in keywords:
                        if keyword in place_name:
                            subcategory = SubCategory.objects.filter(
                                category=category,
                                translations__name=subcategory_name,
                                translations__lang="ko"
                            ).first()
                            if subcategory:
                                return subcategory

            elif category_name == "자연":
                # 자연 서브카테고리 키워드 매핑 (대폭 확장)
                nature_keywords = {
                    "산": ["산", "봉", "악", "등산로", "mountain", "등산", "트레킹", "hiking", "산책로",
                          "산림", "숲길", "능선", "정상", "산봉우리"],
                    "바다": ["해변", "해수욕장", "바다", "연안", "beach", "해안", "모래사장", "갯벌",
                           "바닷가", "해변가", "ocean", "sea"],
                    "강": ["강", "하천", "계곡", "river", "stream", "개울", "물길", "강변", "하구"],
                    "호수": ["호수", "저수지", "연못", "lake", "pond", "담수호", "인공호수"],
                    "계곡": ["계곡", "valley", "협곡", "골짜기", "물놀이", "계곡물", "시원한"],
                    "공원": ["공원", "park", "숲", "정원", "garden", "휴식", "산책", "자연공원",
                           "도시공원", "생태공원", "테마공원", "어린이공원", "체육공원"],
                    "숲": ["숲", "forest", "나무", "자연", "산림욕", "힐링", "치유", "생태",
                          "자연림", "인공림", "수목원"]
                }

                for subcategory_name, keywords in nature_keywords.items():
                    for keyword in keywords:
                        if keyword in place_name:
                            subcategory = SubCategory.objects.filter(
                                category=category,
                                translations__name=subcategory_name,
                                translations__lang="ko"
                            ).first()
                            if subcategory:
                                return subcategory

            elif category_name == "쇼핑":
                # 쇼핑 서브카테고리 키워드 매핑 (대폭 확장)
                shopping_keywords = {
                    "백화점": ["백화점", "department", "롯데백화점", "현대백화점", "신세계", "몰", "mall",
                            "센터", "center", "플라자", "plaza", "타워", "tower", "라이프", "life",
                            "마트", "mart", "쇼핑센터", "쇼핑몰", "복합쇼핑몰", "상가", "빌딩"],
                    "전통시장": ["시장", "market", "전통", "재래시장", "5일장", "야시장", "먹거리",
                             "전통시장", "민속시장", "향토시장", "골목시장"],
                    "면세점": ["면세점", "duty free", "면세", "공항면세점", "시내면세점", "dutyfree"],
                    "아울렛": ["아울렛", "outlet", "프리미엄", "premium", "할인", "세일"],
                    "기념품": ["기념품", "선물", "특산품", "토산품", "souvenir", "gift", "선물가게"],
                    "패션": ["패션", "의류", "옷", "브랜드", "fashion", "스타일", "style", "clothing",
                           "패션몰", "브랜드샵", "편집샵"],
                    "화장품": ["화장품", "뷰티", "cosmetic", "beauty", "올리브영", "에뛰드", "코스메틱",
                            "향수", "스킨케어", "makeup"]
                }

                for subcategory_name, keywords in shopping_keywords.items():
                    for keyword in keywords:
                        if keyword in place_name:
                            subcategory = SubCategory.objects.filter(
                                category=category,
                                translations__name=subcategory_name,
                                translations__lang="ko"
                            ).first()
                            if subcategory:
                                return subcategory

            elif category_name == "액티비티":
                # 액티비티 서브카테고리 키워드 매핑 (대폭 확장)
                activity_keywords = {
                    "캠핑": ["캠핑", "글램핑", "펜션", "리조트", "camping", "glamping", "캠프",
                           "오토캠핑", "카라반", "방갈로", "휴양"],
                    "테마파크": ["테마파크", "놀이공원", "파크", "랜드", "월드", "amusement", "theme",
                             "어뮤즈먼트", "워터파크", "물놀이", "롤러코스터", "놀이기구"],
                    "동물원": ["동물원", "zoo", "사파리", "safari", "동물", "animal", "야생동물",
                            "동물체험", "생태체험"],
                    "수족관": ["수족관", "aquarium", "해양", "바다생물", "물고기", "marine",
                            "아쿠아리움", "해양생물", "해양체험"],
                    "놀이공원": ["놀이공원", "유원지", "어뮤즈먼트", "amusement", "롤러코스터",
                             "바이킹", "회전목마", "범퍼카", "게임", "오락"]
                }

                for subcategory_name, keywords in activity_keywords.items():
                    for keyword in keywords:
                        if keyword in place_name:
                            subcategory = SubCategory.objects.filter(
                                category=category,
                                translations__name=subcategory_name,
                                translations__lang="ko"
                            ).first()
                            if subcategory:
                                return subcategory

        except Exception as e:
            pass

        return None

    def _map_categories_fallback(self, place_data: Dict) -> Tuple[Optional[Category], Optional[SubCategory]]:
        """기존 방식 (CategoryMapper 실패시 사용)"""
        from categories.models import CategoryTranslation

        cat1 = place_data.get("cat1", "")
        cat2 = place_data.get("cat2", "")
        lclsSystm1 = place_data.get("lclsSystm1", "")

        category_mapping = {
            "A01": "자연",
            "A02": "문화",
            "A03": "액티비티",
            "A04": "쇼핑",
            "A05": "음식",
            "FD": "음식",
            "SH": "쇼핑",
            "VE": "문화",
            "NA": "자연",
            "AC": "문화"
        }

        category_name = category_mapping.get(cat1) or category_mapping.get(lclsSystm1)
        if category_name:
            try:
                translation = CategoryTranslation.objects.get(lang="ko", name=category_name)
                return translation.category, None
            except CategoryTranslation.DoesNotExist:
                pass

        return None, None

    def _map_regions(self, place_data: Dict) -> Tuple[Optional[Region], Optional[SubRegion]]:
        """
        CategoryMapper를 사용해서 정확한 지역 매핑
        시군구 코드까지 정확하게 매핑!
        """
        try:
            # CategoryMapper의 완전한 지역 매핑 사용
            processed_data = self.category_mapper.process_tour_api_place(place_data)

            region_id = processed_data.get("region_id")
            subregion_id = processed_data.get("sub_region_id")

            region = None
            subregion = None

            if region_id:
                try:
                    region = Region.objects.get(id=region_id)
                except Region.DoesNotExist:
                    pass

            if subregion_id:
                try:
                    subregion = SubRegion.objects.get(id=subregion_id)
                except SubRegion.DoesNotExist:
                    pass

            return region, subregion

        except Exception as e:
            # CategoryMapper 실패시 기존 방식으로 대체
            return self._map_regions_fallback(place_data)

    def _map_regions_fallback(self, place_data: Dict) -> Tuple[Optional[Region], Optional[SubRegion]]:
        """기존 방식 (CategoryMapper 실패시 사용)"""
        from regions.models import RegionTranslation

        area_code = place_data.get("areacode", "")

        region_mapping = {
            "1": "서울",
            "2": "인천",
            "3": "대전",
            "4": "대구",
            "5": "광주",
            "6": "부산",
            "7": "울산",
            "8": "세종",
            "31": "경기",
            "32": "강원",
            "33": "충북",
            "34": "충남",
            "35": "경북",
            "36": "경남",
            "37": "전북",
            "38": "전남",
            "39": "제주"
        }

        region_name = region_mapping.get(area_code)
        if region_name:
            try:
                translation = RegionTranslation.objects.get(lang="ko", name=region_name)
                return translation.region, None
            except RegionTranslation.DoesNotExist:
                pass

        return None, None

    def _get_field_by_category(self, place_data: Dict, field_type: str) -> str:
        """
        대분류에 따라 정확한 필드명으로 데이터 가져오기

        Args:
            place_data: 투어 API 응답 데이터
            field_type: "time", "phone", "homepage" 중 하나

        Returns:
            str: 해당 필드의 값 (없으면 빈 문자열)
        """
        # 우리 카테고리 매핑 먼저 확인
        cat1 = place_data.get("cat1", "")
        lclsSystm1 = place_data.get("lclsSystm1", "")

        # 투어 API 카테고리 → 우리 대분류 매핑
        category_mapping = {
            "A01": "자연", "NA": "자연",
            "A02": "문화", "VE": "문화", "AC": "문화",
            "A03": "액티비티",
            "A04": "쇼핑", "SH": "쇼핑",
            "A05": "음식", "FD": "음식"
        }

        our_category = category_mapping.get(cat1) or category_mapping.get(lclsSystm1)

        # 대분류별 필드 매핑
        field_mappings = {
            "time": {
                "자연": ["usetime", "opentime"],
                "문화": ["usetimeculture", "opentime"],
                "액티비티": ["usetimeleports", "usetime", "opentime"],
                "쇼핑": ["opentime", "opendateshopping"],
                "음식": ["opentimefood", "opentime"]
            },
            "phone": {
                "자연": ["infocenter", "tel"],
                "문화": ["infocenterculture", "tel"],
                "액티비티": ["infocenterleports", "tel"],
                "쇼핑": ["infocentershopping", "tel"],
                "음식": ["infocenterfood", "tel"]
            },
            "homepage": {
                # 모든 카테고리에서 homepage 필드 사용
                "자연": ["homepage"],
                "문화": ["homepage"],
                "액티비티": ["homepage"],
                "쇼핑": ["homepage"],
                "음식": ["homepage"]
            }
        }

        # 기본 필드 (카테고리 매핑 실패시 사용)
        default_fields = {
            "time": ["usetime", "opentime", "opentimefood", "checkintime", "eventstartdate"],
            "phone": ["tel", "infocenter", "infocenterlodging", "infocentershopping", "infocenterculture"],
            "homepage": ["homepage"]
        }

        # 해당 카테고리의 필드 목록 가져오기
        if our_category and our_category in field_mappings.get(field_type, {}):
            fields_to_check = field_mappings[field_type][our_category]
        else:
            # 카테고리 매핑 실패시 기본 필드 사용
            fields_to_check = default_fields.get(field_type, [])

        # 첫 번째로 값이 있는 필드 반환
        for field in fields_to_check:
            value = place_data.get(field, "").strip()
            if value:
                return value

        return ""

    def _get_use_time_field(self, place_data: Dict) -> str:
        """대분류별 이용시간 필드 매핑"""
        return self._get_field_by_category(place_data, "time")

    def _get_phone_field(self, place_data: Dict) -> str:
        """대분류별 전화번호 필드 매핑"""
        return self._get_field_by_category(place_data, "phone")

    def _get_homepage_field(self, place_data: Dict) -> str:
        """대분류별 홈페이지 필드 매핑"""
        return self._get_field_by_category(place_data, "homepage")

    def _process_korean_places(self, korean_places: List[Dict], stats: Dict, dry_run: bool) -> Dict:
        for place_data in korean_places:
            try:
                stats["total_processed"] += 1

                lat = float(place_data.get("mapy", 0))
                lng = float(place_data.get("mapx", 0))

                if not lat or not lng:
                    stats["processing_errors"].append(f"{place_data.get('title', 'Unknown')}: 좌표 없음")
                    continue

                content_id = place_data.get("contentid")
                if not content_id:
                    stats["processing_errors"].append("content_id 없음")
                    continue

                if not dry_run:
                    with transaction.atomic():
                        category, sub_category = self._map_categories(place_data)
                        region, sub_region = self._map_regions(place_data)

                        if category:
                            stats["category_mappings"] += 1
                        if region:
                            stats["region_mappings"] += 1

                        place, created = Place.objects.get_or_create(
                            content_id=content_id,
                            defaults={
                                "location": Point(lng, lat),
                                "phone_number": self._get_phone_field(place_data),
                                "use_time": self._get_use_time_field(place_data),
                                "link_url": self._get_homepage_field(place_data),
                                "category": category,
                                "sub_category": sub_category,
                                "region": region,
                                "sub_region": sub_region,
                                "last_synced_at": timezone.now()
                            }
                        )

                        if created:
                            stats["new_places_created"] += 1
                        else:
                            updated = False
                            current_phone = self._get_phone_field(place_data)
                            if place.phone_number != current_phone:
                                place.phone_number = current_phone
                                updated = True
                            current_use_time = self._get_use_time_field(place_data)
                            if place.use_time != current_use_time:
                                place.use_time = current_use_time
                                updated = True
                            current_homepage = self._get_homepage_field(place_data)
                            if place.link_url != current_homepage:
                                place.link_url = current_homepage
                                updated = True
                            if place.category != category:
                                place.category = category
                                updated = True
                            if place.region != region:
                                place.region = region
                                updated = True

                            if updated:
                                place.last_synced_at = timezone.now()
                                place.save()
                                stats["places_updated"] += 1

                        translation, trans_created = PlaceTranslation.objects.get_or_create(
                            place=place,
                            lang="ko",
                            defaults={
                                "name": place_data.get("title", ""),
                                "address": place_data.get("addr1", ""),
                                "description": place_data.get("overview", ""),
                                "tour_api_content_id": content_id
                            }
                        )

                        if trans_created:
                            stats["translations_added"] += 1
                        else:
                            updated = False
                            if translation.name != place_data.get("title", ""):
                                translation.name = place_data.get("title", "")
                                updated = True
                            if translation.address != place_data.get("addr1", ""):
                                translation.address = place_data.get("addr1", "")
                                updated = True
                            current_description = place_data.get("overview", "")
                            if translation.description != current_description:
                                translation.description = current_description
                                updated = True

                            if updated:
                                translation.save()
                                stats["translations_updated"] += 1

            except Exception as e:
                stats["processing_errors"].append(f"{place_data.get('title', 'Unknown')}: {str(e)}")

        return stats

    def _process_other_language_places(self, places: List[Dict], lang: str, threshold: int,
                                       stats: Dict, dry_run: bool) -> Dict:
        for place_data in places:
            try:
                stats["total_processed"] += 1

                lat = float(place_data.get("mapy", 0))
                lng = float(place_data.get("mapx", 0))

                if not lat or not lng:
                    stats["processing_errors"].append(f"{place_data.get('title', 'Unknown')}: 좌표 없음")
                    continue

                matching_place = find_matching_place_by_gis(lat, lng, threshold)

                if not dry_run:
                    with transaction.atomic():
                        if matching_place:
                            stats["gis_matches_found"] += 1
                            place = matching_place

                            existing_coords = []
                            if place.location:
                                existing_coords.append((place.location.y, place.location.x))
                            existing_coords.append((lat, lng))

                            center_point = calculate_center_point(existing_coords)
                            if center_point:
                                place.location = center_point
                                place.save()

                        else:
                            category, sub_category = self._map_categories(place_data)
                            region, sub_region = self._map_regions(place_data)

                            if category:
                                stats["category_mappings"] += 1
                            if region:
                                stats["region_mappings"] += 1

                            place = Place.objects.create(
                                content_id=place_data.get("contentid", f"new_{lang}_{int(time.time())}"),
                                location=Point(lng, lat),
                                phone_number=self._get_phone_field(place_data),
                                use_time=self._get_use_time_field(place_data),
                                link_url=self._get_homepage_field(place_data),
                                category=category,
                                sub_category=sub_category,
                                region=region,
                                sub_region=sub_region,
                                last_synced_at=timezone.now()
                            )
                            stats["new_places_created"] += 1

                        translation, trans_created = PlaceTranslation.objects.get_or_create(
                            place=place,
                            lang=lang,
                            defaults={
                                "name": place_data.get("title", ""),
                                "address": place_data.get("addr1", ""),
                                "description": place_data.get("overview", ""),
                                "tour_api_content_id": place_data.get("contentid", "")
                            }
                        )

                        if trans_created:
                            stats["translations_added"] += 1
                        else:
                            updated = False
                            if translation.name != place_data.get("title", ""):
                                translation.name = place_data.get("title", "")
                                updated = True
                            if translation.address != place_data.get("addr1", ""):
                                translation.address = place_data.get("addr1", "")
                                updated = True
                            current_description = place_data.get("overview", "")
                            if translation.description != current_description:
                                translation.description = current_description
                                updated = True

                            if updated:
                                translation.save()
                                stats["translations_updated"] += 1

            except Exception as e:
                stats["processing_errors"].append(f"{place_data.get('title', 'Unknown')}: {str(e)}")

        return stats

    def _print_results(self, stats: Dict[str, Any], elapsed_time: float):
        self.stdout.write("다국어 관광지 동기화 완료")
        self.stdout.write(f"소요 시간: {elapsed_time:.2f}초")
        self.stdout.write(f"처리된 관광지: {stats['total_processed']}개")
        self.stdout.write(f"새로 생성된 Place: {stats['new_places_created']}개")
        self.stdout.write(f"업데이트된 Place: {stats['places_updated']}개")
        self.stdout.write(f"추가된 번역: {stats['translations_added']}개")
        self.stdout.write(f"업데이트된 번역: {stats['translations_updated']}개")
        self.stdout.write(f"GIS 매칭 성공: {stats['gis_matches_found']}개")
        self.stdout.write(f"카테고리 매핑: {stats['category_mappings']}개")
        self.stdout.write(f"지역 매핑: {stats['region_mappings']}개")

        if stats["processing_errors"]:
            self.stdout.write(f"처리 에러: {len(stats['processing_errors'])}개")
            for error in stats["processing_errors"][:3]:
                self.stdout.write(f"  {error}")
            if len(stats["processing_errors"]) > 3:
                self.stdout.write(f"  ... 및 {len(stats['processing_errors']) - 3}개 더")

        total_places = Place.objects.count()
        total_translations = PlaceTranslation.objects.count()
        self.stdout.write(f"현재 DB 현황:")
        self.stdout.write(f"  전체 관광지: {total_places}개")
        self.stdout.write(f"  전체 번역: {total_translations}개")

        for lang in ["ko", "en", "jp", "cn"]:
            lang_count = PlaceTranslation.objects.filter(lang=lang).count()
            if lang_count > 0:
                self.stdout.write(f"  {lang.upper()} 번역: {lang_count}개")
