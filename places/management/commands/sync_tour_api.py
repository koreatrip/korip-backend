# places/management/commands/sync_tour_api.py

import math
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from places.models import Place, PlaceTranslation
from places.services.tour_api_client import TourAPIClient
from places.services.category_mapper import CategoryMapper
import time


class Command(BaseCommand):
    help = "투어 API에서 관광지 데이터를 가져와서 DB에 저장합니다 (다국어 지원)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="한 번에 처리할 최대 개수 (기본값: 100, 최대: 1000)"
        )
        parser.add_argument(
            "--area-code",
            type=str,
            default=None,
            help="특정 지역만 처리 (1=서울, 2=인천, 6=부산, 31=경기, 39=제주)"
        )
        parser.add_argument(
            "--page",
            type=int,
            default=1,
            help="시작 페이지 번호 (기본값: 1)"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="실제 저장하지 않고 테스트만 실행"
        )
        parser.add_argument(
            "--force-update",
            action="store_true",
            help="이미 존재하는 데이터도 강제 업데이트"
        )
        parser.add_argument(
            "--disable-region-filter",
            action="store_true",
            help="지역 필터링을 비활성화 (모든 지역 저장)"
        )
        parser.add_argument(
            "--collect-all",
            action="store_true",
            help="모든 상세정보 수집"
        )
        parser.add_argument(
            "--detail-delay",
            type=float,
            default=1.0,
            help="상세정보 수집 시 API 호출 간 대기시간 (초, 기본값: 1.0)"
        )
        parser.add_argument(
            "--language",
            type=str,
            default="all",
            choices=["ko", "en", "jp", "cn", "all"],
            help="수집할 언어 (기본값: all - 모든 언어)"
        )
        parser.add_argument(
            "--incremental-all",
            action="store_true",
            help="전국 증분 동기화 모드"
        )
        parser.add_argument(
            "--daily-limit",
            type=int,
            default=1000,
            help="증분 모드 일일 수집 제한 (기본값: 1000)"
        )
        parser.add_argument(
            "--collect-all-pages",
            action="store_true",
            help="해당 지역의 모든 페이지 자동 수집 (페이지네이션)"
        )
        parser.add_argument(
            "--max-total-items",
            type=int,
            default=10000,
            help="전체 수집 제한 개수 (기본값: 10000)"
        )

    def handle(self, *args, **options):
        limit = min(options["limit"], 1000)
        area_code = options["area_code"]
        page = options["page"]
        dry_run = options["dry_run"]
        force_update = options["force_update"]
        disable_region_filter = options["disable_region_filter"]
        collect_all = options["collect_all"]
        detail_delay = options["detail_delay"]
        language = options["language"]
        incremental_all = options["incremental_all"]
        daily_limit = options["daily_limit"]

        collect_all_pages = options["collect_all_pages"]
        max_total_items = options["max_total_items"]

        # 전체 페이지 수집 모드
        if collect_all_pages:
            return self.handle_collect_all_pages(
                area_code, max_total_items, dry_run, collect_all, detail_delay, language
            )

        # 증분 동기화 모드
        if incremental_all:
            return self.handle_incremental_all(daily_limit, dry_run, collect_all, detail_delay)

        self.stdout.write("KORIP 투어 API 동기화 시작 (다국어 지원)")
        self.stdout.write("=" * 60)

        self.client = TourAPIClient()
        self.mapper = CategoryMapper()

        if disable_region_filter:
            self.mapper.enable_all_regions()
            self.stdout.write("지역 필터링 비활성화 - 모든 지역 저장됨")

        # 언어 설정 (증분 모드에서는 단일 언어 처리)
        single_language = None  # 기본값 설정
        if single_language:
            self.languages = [single_language]
        elif language == "all":
            self.languages = ["ko", "en", "jp", "cn"]
        else:
            self.languages = [language]

        self.stdout.write(f"처리 설정:")
        self.stdout.write(f"   - 총 처리: {limit}개")
        self.stdout.write(f"   - 지역 코드: {area_code or '전체'}")
        self.stdout.write(f"   - 언어: {', '.join(self.languages)}")
        self.stdout.write(f"   - 상세정보 수집: {'예' if collect_all else '아니오'}")

        try:
            self.check_region_database_status()

            self.stdout.write("투어 API 연결 테스트 중...")
            connection_test_result = self.client.test_connection(from_command=True)

            if not connection_test_result:
                self.stdout.write("투어 API 연결 테스트 일부 실패! 하지만 계속 진행합니다.")
            else:
                self.stdout.write("투어 API 연결 성공!")

            result = self.sync_places_multilang(
                limit=limit,
                area_code=area_code,
                page=page,
                dry_run=dry_run,
                force_update=force_update,
                collect_all=collect_all,
                detail_delay=detail_delay
            )

            if result is not None:
                self.print_summary(result)

        except Exception as e:
            self.stdout.write(f"동기화 중 치명적 에러 발생: {e}")
            import traceback
            traceback.print_exc()
            raise CommandError(f"동기화 실패: {e}")

    def handle_incremental_all(self, daily_limit, dry_run, collect_all, detail_delay):
        # 전국 증분 동기화 처리
        from places.models import SyncProgress

        # 전국 지역 코드
        KOREA_AREAS = [
            ("1", "서울특별시"), ("2", "인천광역시"), ("3", "대전광역시"),
            ("4", "대구광역시"), ("5", "광주광역시"), ("6", "부산광역시"),
            ("7", "울산광역시"), ("8", "세종특별자치시"), ("31", "경기도"),
            ("32", "강원특별자치도"), ("33", "충청북도"), ("34", "충청남도"),
            ("35", "경상북도"), ("36", "경상남도"), ("37", "전북특별자치도"),
            ("38", "전라남도"), ("39", "제주특별자치도")
        ]

        self.stdout.write("KORIP 전국 증분 동기화 시작")
        self.stdout.write("=" * 60)
        self.stdout.write(f"일일 수집 한도: {daily_limit}개")
        self.stdout.write(f"전국 {len(KOREA_AREAS)}개 지역 처리")

        # 지역당 언어별 수집량 계산
        per_area_limit = max(1, daily_limit // len(KOREA_AREAS) // 4)
        self.stdout.write(f"지역당 언어별 수집량: {per_area_limit}개")

        total_stats = {
            "total_processed": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "translations_created": 0,
            "translations_updated": 0
        }

        # 각 지역별 처리
        for area_code, area_name in KOREA_AREAS:
            self.stdout.write(f"\n{area_name} (지역코드: {area_code}) 처리 시작")

            try:
                area_stats = self.process_area_incremental(
                    area_code, per_area_limit, dry_run, collect_all, detail_delay
                )

                # 통계 합산
                for key in total_stats:
                    if key in area_stats:
                        total_stats[key] += area_stats[key]

                self.stdout.write(f"{area_name} 완료: 신규 {area_stats['created']}개")

                # API 부하 방지 딜레이
                import time
                time.sleep(1)

            except Exception as e:
                self.stdout.write(f"{area_name} 처리 실패: {e}")
                total_stats["errors"] += 1

        # 최종 결과 출력
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("전국 증분 동기화 완료")
        self.stdout.write("=" * 60)
        self.stdout.write(f"총 처리: {total_stats['total_processed']}개")
        self.stdout.write(f"신규 생성: {total_stats['created']}개")
        self.stdout.write(f"업데이트: {total_stats['updated']}개")
        self.stdout.write(f"번역 생성: {total_stats['translations_created']}개")
        self.stdout.write(f"에러: {total_stats['errors']}개")

        return None

    def process_area_incremental(self, area_code, per_area_limit, dry_run, collect_all, detail_delay):
        # 특정 지역의 증분 처리
        from places.models import SyncProgress

        languages = ["ko", "en", "jp", "cn"]
        area_stats = {
            "total_processed": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "translations_created": 0,
            "translations_updated": 0
        }

        for lang in languages:
            try:
                # 다음 페이지 번호 가져오기
                next_page = SyncProgress.get_next_page(area_code, lang)

                self.stdout.write(f"  [{lang.upper()}] 페이지 {next_page} 수집 중...")

                # 클래스 속성 임시 설정
                self.client = TourAPIClient()
                self.mapper = CategoryMapper()

                # languages 속성도 설정
                self.languages = [lang]

                # 지역 필터링 비활성화 설정
                if hasattr(self.mapper, 'enable_all_regions'):
                    self.mapper.enable_all_regions()

                # 기존 동기화 로직 호출 (단일 언어)
                result = self.sync_places_multilang(
                    limit=per_area_limit,
                    area_code=area_code,
                    page=next_page,
                    dry_run=dry_run,
                    force_update=False,
                    collect_all=collect_all,
                    detail_delay=detail_delay,
                    single_language=lang
                )

                if result:
                    # 진행 상태 업데이트
                    collected_count = result.get("created", 0) + result.get("updated", 0)
                    if collected_count > 0:
                        SyncProgress.update_progress(area_code, lang, next_page, collected_count)

                    # 통계 합산
                    for key in area_stats:
                        if key in result:
                            area_stats[key] += result[key]

            except Exception as e:
                self.stdout.write(f"  [{lang.upper()}] 에러: {e}")
                area_stats["errors"] += 1

        return area_stats

    def sync_places_multilang(self, limit, area_code, page, dry_run, force_update, collect_all, detail_delay,
                              single_language=None):
        stats = {
            "total_processed": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "region_saved": 0,
            "region_failed": 0,
            "translations_created": 0,
            "translations_updated": 0
        }

        # 각 언어별로 데이터 수집하고 GIS로 매칭
        all_places_data = {}

        for lang in self.languages:
            try:
                self.stdout.write(f"[{lang.upper()}] 언어 데이터 수집 중...")

                # TourAPIClient의 다국어 메서드 사용
                places_data = self.client.get_area_list_by_language(
                    area_code=area_code,
                    page_no=page,
                    num_of_rows=limit,
                    lang=lang
                )

                if not places_data:
                    self.stdout.write(f"[{lang.upper()}] 데이터를 가져올 수 없습니다.")
                    continue

                self.stdout.write(f"[{lang.upper()}] {len(places_data)}개의 관광지 데이터를 가져왔습니다.")

                # GIS 기반으로 같은 장소 매핑
                for place_data in places_data:
                    lat = place_data.get("mapy")
                    lng = place_data.get("mapx")

                    if not lat or not lng:
                        continue

                    current_lat = float(lat)
                    current_lng = float(lng)

                    print(f"[{lang.upper()}] 처리 중: {place_data.get('title')} (좌표: {current_lat}, {current_lng})")

                    # 수동 거리 계산 우선 (GIS 매칭 문제로 인해)
                    found_existing = False
                    matched_key = None
                    existing_place_from_gis = None

                    # 1. 기존 DB에서 500m 이내 관광지 찾기 (수동 계산)
                    existing_places = Place.objects.exclude(location__isnull=True)
                    for existing_place in existing_places:
                        if existing_place.location:
                            existing_lat = existing_place.location.y
                            existing_lng = existing_place.location.x
                            distance = self.calculate_distance_simple(current_lat, current_lng, existing_lat,
                                                                      existing_lng)

                            if distance <= 500:  # 500m 이내
                                print(
                                    f"[{lang.upper()}] DB 매칭 발견: {place_data.get('title')} <-> 기존 Place {existing_place.id} (거리: {distance:.0f}m)")
                                existing_place_from_gis = existing_place
                                break

                    # 2. all_places_data에서도 찾기
                    if not existing_place_from_gis:
                        for existing_key, existing_data in all_places_data.items():
                            existing_lat = existing_data["lat"]
                            existing_lng = existing_data["lng"]

                            # 500m 이내인지 수동 계산 (반경 확대)
                            distance = self.calculate_distance_simple(current_lat, current_lng, existing_lat,
                                                                      existing_lng)
                            if distance <= 500:  # 500m 이내로 확대
                                # 이름 유사도도 체크 (핵심 키워드 매칭)
                                current_title = place_data.get('title', '').lower()
                                existing_title = existing_data['base_data'].get('title', '').lower()

                                # 숫자나 특수문자 제거해서 핵심 단어만 추출
                                import re
                                current_clean = re.sub(r'[^a-zA-Z가-힣]', '', current_title)
                                existing_clean = re.sub(r'[^a-zA-Z가-힣]', '', existing_title)

                                # 괄호 안 한국어 매칭 우선 체크
                                if self.is_same_place_by_korean_name(current_title, existing_title, distance):
                                    print(
                                        f"[{lang.upper()}] 괄호 한국어 매칭 성공: {place_data.get('title')} <-> {existing_data['base_data'].get('title')} (거리: {distance:.0f}m)")
                                    found_existing = True
                                    matched_key = existing_key
                                    break
                                # 일반 제목 유사도 체크
                                elif (len(current_clean) >= 2 and len(existing_clean) >= 2 and
                                      self.is_similar_place(current_clean, existing_clean, distance)):
                                    print(
                                        f"[{lang.upper()}] 일반 매칭 성공: {place_data.get('title')} <-> {existing_data['base_data'].get('title')} (거리: {distance:.0f}m, 제목 유사)")
                                    found_existing = True
                                    matched_key = existing_key
                                    break
                                else:
                                    print(
                                        f"[{lang.upper()}] 거리는 가깝지만 제목이 달라서 제외: {current_title} vs {existing_title} (거리: {distance:.0f}m)")
                            elif distance <= 1000:  # 1km 이내는 로그만 출력
                                print(
                                    f"[{lang.upper()}] 근처 장소 발견: {place_data.get('title')} vs {existing_data['base_data'].get('title')} (거리: {distance:.0f}m)")

                    if existing_place_from_gis:
                        # 기존 관광지와 매칭됨
                        existing_lat, existing_lng = existing_place_from_gis.location.y, existing_place_from_gis.location.x
                        existing_coord_key = f"{existing_lat:.3f},{existing_lng:.3f}"

                        # all_places_data에서 해당 키 찾기
                        for key, data in all_places_data.items():
                            if abs(data["lat"] - existing_lat) < 0.001 and abs(data["lng"] - existing_lng) < 0.001:
                                found_existing = True
                                matched_key = key
                                print(
                                    f"[{lang.upper()}] GIS 매칭 성공: {place_data.get('title')} <-> {data['base_data'].get('title')} (Place ID: {existing_place_from_gis.id})")
                                break

                        # all_places_data에 없으면 새로 추가 (기존 DB 관광지용)
                        if not found_existing:
                            matched_key = existing_coord_key
                            all_places_data[matched_key] = {
                                "base_data": place_data.copy(),
                                "translations": {},
                                "detailed_translations": {},
                                "lat": existing_lat,
                                "lng": existing_lng,
                                "existing_place_id": existing_place_from_gis.id
                            }
                            found_existing = True
                            print(
                                f"[{lang.upper()}] 기존 DB 관광지와 매칭: {place_data.get('title')} (Place ID: {existing_place_from_gis.id})")

                    if not found_existing:
                        # 새로운 관광지
                        coord_key = f"{current_lat:.3f},{current_lng:.3f}"
                        all_places_data[coord_key] = {
                            "base_data": place_data.copy(),
                            "translations": {},
                            "detailed_translations": {},
                            "lat": current_lat,
                            "lng": current_lng
                        }
                        print(f"[{lang.upper()}] 새로운 관광지 생성: {place_data.get('title')}")
                        matched_key = coord_key

                    # 번역 정보 저장 (기본 정보)
                    all_places_data[matched_key]["translations"][lang] = {
                        "content_id": place_data.get("contentid"),
                        "title": place_data.get("title", ""),
                        "addr1": place_data.get("addr1", ""),
                        "overview": place_data.get("overview", "")
                    }

                    # 상세정보 수집 (언어별로 별도 저장)
                    if collect_all and place_data.get("contentid"):
                        detailed_info = self.collect_detailed_info_by_language(
                            place_data.get("contentid"),
                            place_data.get("contenttypeid", "12"),
                            lang
                        )
                        all_places_data[matched_key]["detailed_translations"][lang] = detailed_info
                        time.sleep(detail_delay)

            except Exception as e:
                self.stdout.write(f"[{lang.upper()}] 에러: {e}")
                stats["errors"] += 1

        # 통합된 데이터로 Place 생성/업데이트
        for coord_key, place_info in all_places_data.items():
            stats["total_processed"] += 1

            try:
                base_data = place_info["base_data"]
                translations = place_info["translations"]
                detailed_translations = place_info["detailed_translations"]

                # Place 생성/업데이트 시 한국어 content_id를 우선 사용하되, 없으면 첫 번째 언어 사용
                ko_data = translations.get("ko")
                if not ko_data:
                    for priority_lang in ["en", "jp", "cn"]:
                        if priority_lang in translations:
                            ko_data = translations[priority_lang]
                            break

                    if not ko_data:
                        ko_data = next(iter(translations.values()), {})

                if not ko_data or not ko_data.get("content_id"):
                    stats["skipped"] += 1
                    continue

                print(f"=== CategoryMapper 처리 전 ===")
                print(f"사용할 메인 언어: {next((lang for lang, data in translations.items() if data == ko_data), 'unknown')}")
                print(f"메인 content_id: {ko_data.get('content_id')}")

                # 한국어 상세정보를 base_data에 병합
                if "ko" in detailed_translations:
                    base_data.update(detailed_translations["ko"])

                # CategoryMapper가 상세정보가 포함된 base_data를 처리
                processed_data = self.mapper.process_tour_api_place(base_data)
                if not processed_data:
                    stats["skipped"] += 1
                    continue

                # 메인 content_id 설정 (한국어 우선, 없으면 첫 번째 언어)
                main_content_id = ko_data.get("content_id")
                processed_data["content_id"] = main_content_id
                processed_data["latitude"] = place_info["lat"]
                processed_data["longitude"] = place_info["lng"]

                # Place 생성/업데이트
                try:
                    # 기존 Place가 있는지 확인
                    existing_place = None
                    if "existing_place_id" in place_info:
                        try:
                            existing_place = Place.objects.get(id=place_info["existing_place_id"])
                            print(f"기존 GIS 매칭된 Place 사용: ID {existing_place.id}")
                        except Place.DoesNotExist:
                            print(f"GIS 매칭된 Place {place_info['existing_place_id']}를 찾을 수 없음")

                    # content_id로도 확인 (모든 언어의 content_id 확인)
                    if not existing_place:
                        for lang, trans_data in translations.items():
                            content_id = trans_data.get("content_id")
                            if content_id:
                                try:
                                    existing_place = Place.objects.get(content_id=content_id)
                                    print(f"content_id로 기존 Place 찾음: {content_id} (언어: {lang})")
                                    break
                                except Place.DoesNotExist:
                                    continue

                    if existing_place:
                        if force_update:
                            if not dry_run:
                                region_saved = self.update_place(existing_place, processed_data, translations,
                                                                 detailed_translations)
                                if region_saved:
                                    stats["region_saved"] += 1
                                else:
                                    stats["region_failed"] += 1
                                stats["translations_updated"] += len(translations)
                            stats["updated"] += 1
                        else:
                            # 기존 Place가 있으면 번역만 업데이트
                            if not dry_run:
                                trans_stats = self.update_translations_with_details(existing_place, translations,
                                                                                    detailed_translations)
                                stats["translations_updated"] += trans_stats
                            stats["skipped"] += 1
                    else:
                        # 새로운 Place 생성
                        if not dry_run:
                            place, region_saved = self.create_place_with_detailed_translations(processed_data,
                                                                                               translations,
                                                                                               detailed_translations)
                            if place:
                                stats["translations_created"] += len(translations)
                                if region_saved:
                                    stats["region_saved"] += 1
                                else:
                                    stats["region_failed"] += 1
                        stats["created"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    self.stdout.write(f"처리 중 에러: {e}")

            except Exception as e:
                stats["errors"] += 1
                self.stdout.write(f"처리 중 에러: {e}")

        return stats

    def find_matching_place_by_gis(self, lat, lng, radius_meters):
        # GIS를 사용해서 반경 내 기존 Place 찾기 (개선된 버전)
        try:
            # Point 생성 (lng, lat 순서 주의!)
            point = Point(lng, lat)

            # 1. PostGIS distance 사용 (정확한 계산)
            try:
                nearby_places = Place.objects.filter(
                    location__distance_lte=(point, D(m=radius_meters))
                ).exclude(location__isnull=True)

                if nearby_places.exists():
                    closest_place = nearby_places.first()
                    print(f"GIS 매칭 성공 (PostGIS): Place ID {closest_place.id}")
                    return closest_place

            except Exception as e:
                print(f"PostGIS 계산 실패: {e}, 대안 방법 사용")

                # 2. 대안: bbox로 범위 검색 후 수동 거리 계산
                try:
                    # 대략적인 bbox 계산 (1도 ≈ 111km)
                    degree_diff = radius_meters / 111000.0

                    bbox_places = Place.objects.filter(
                        location__latitude__range=(lat - degree_diff, lat + degree_diff),
                        location__longitude__range=(lng - degree_diff, lng + degree_diff)
                    ).exclude(location__isnull=True)

                    for place in bbox_places:
                        if place.location:
                            place_lat = place.location.y
                            place_lng = place.location.x
                            distance = self.calculate_distance_simple(lat, lng, place_lat, place_lng)

                            if distance <= radius_meters:
                                print(f"GIS 매칭 성공 (수동 계산): Place ID {place.id}, 거리: {distance:.0f}m")
                                return place

                except Exception as e2:
                    print(f"대안 방법도 실패: {e2}")

            print(f"GIS 매칭 실패: 반경 {radius_meters}m 내에 기존 Place 없음")
            return None

        except Exception as e:
            print(f"GIS 매칭 중 에러: {e}")
            return None

    def collect_detailed_info_by_language(self, content_id, content_type_id, lang):
        # 언어별로 상세정보를 별도 수집
        detailed_info = {}

        try:
            print(f"[{lang.upper()}] 상세정보 수집: content_id={content_id}")

            # detailCommon2 호출
            detail_info = self.client.get_place_detail(content_id, lang)
            if detail_info:
                overview = detail_info.get('overview', '')
                print(f"[{lang.upper()}] overview: {overview[:50]}...")

                detailed_info.update({
                    "overview": overview,
                    "homepage": detail_info.get("homepage", ""),
                    "tel": detail_info.get("tel", ""),
                    "firstimage": detail_info.get("firstimage", ""),
                    "firstimage2": detail_info.get("firstimage2", "")
                })

            # detailIntro2 호출
            intro_info = self.client.get_place_detail_intro(content_id, content_type_id, lang)
            if intro_info:
                detailed_info.update({
                    "usetime": intro_info.get("usetime", ""),
                    "usetimeculture": intro_info.get("usetimeculture", ""),
                    "usetimeleports": intro_info.get("usetimeleports", ""),
                    "opentime": intro_info.get("opentime", ""),
                    "opentimefood": intro_info.get("opentimefood", ""),
                    "infocenter": intro_info.get("infocenter", ""),
                    "infocenterlodging": intro_info.get("infocenterlodging", ""),
                    "infocentershopping": intro_info.get("infocentershopping", ""),
                    "infocenterculture": intro_info.get("infocenterculture", ""),
                    "infocenterfood": intro_info.get("infocenterfood", ""),
                    "infocenterleports": intro_info.get("infocenterleports", ""),
                })

        except Exception as e:
            print(f"[{lang.upper()}] 상세정보 수집 실패: {e}")

        return detailed_info

    def create_place_with_detailed_translations(self, processed_data, translations, detailed_translations):
        region_saved = False
        region_obj = None
        subregion_obj = None

        # 지역 정보 처리
        region_id = processed_data.get("region_id")
        sub_region_id = processed_data.get("sub_region_id")

        if region_id and sub_region_id:
            try:
                from regions.models import Region, SubRegion
                region_obj = Region.objects.get(id=region_id)
                subregion_obj = SubRegion.objects.get(id=sub_region_id)
                region_saved = True
                print(f"지역 정보 로드: {region_obj} > {subregion_obj}")
            except (Region.DoesNotExist, SubRegion.DoesNotExist) as e:
                print(f"지역 객체 못 찾음: region_id={region_id}, sub_region_id={sub_region_id}")
            except Exception as e:
                print(f"지역 조회 중 에러: {e}")

        # 카테고리 정보 처리
        category_obj = None
        sub_category_obj = None

        category_id = processed_data.get("category_id")
        if category_id:
            try:
                from categories.models import Category
                category_obj = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                print(f"카테고리 객체 못 찾음: ID {category_id}")

        sub_category_id = processed_data.get("sub_category_id")
        if sub_category_id:
            try:
                from categories.models import SubCategory
                sub_category_obj = SubCategory.objects.get(id=sub_category_id)
            except SubCategory.DoesNotExist:
                print(f"서브카테고리 객체 못 찾음: ID {sub_category_id}")

        # 카테고리별 전화번호 처리
        phone_number = self.get_phone_by_category(processed_data)

        # 카테고리별 운영시간 처리
        use_time = self.get_usetime_by_category(processed_data)

        # Place 생성
        try:
            place = Place.objects.create(
                content_id=processed_data["content_id"],
                category_id=category_obj.id if category_obj else None,
                sub_category_id=sub_category_obj.id if sub_category_obj else None,
                region=region_obj,
                sub_region=subregion_obj,
                image_url=processed_data.get("image_url", "")[:500],
                phone_number=phone_number[:20] if phone_number else "",
                use_time=use_time[:200] if use_time else "",
                link_url=processed_data.get("homepage", "")[:500],
                favorite_count=0,
                last_synced_at=timezone.now()
            )

            print(f"Place 생성 성공! ID: {place.id}, content_id: {place.content_id}")
            print(f"저장된 전화번호: {place.phone_number}")
            print(f"저장된 운영시간: {place.use_time}")

            # 좌표 저장
            if processed_data.get("latitude") and processed_data.get("longitude"):
                try:
                    lat = float(processed_data["latitude"])
                    lng = float(processed_data["longitude"])
                    place.location = Point(lng, lat)
                    place.save()
                    print(f"좌표 저장 성공: ({lat}, {lng})")
                except Exception as e:
                    print(f"좌표 저장 실패: {e}")

            # 다국어 번역 생성
            self.create_translations_with_details(place, translations, detailed_translations)

            return place, region_saved

        except Exception as e:
            print(f"Place 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            return None, False

    def create_translations_with_details(self, place, translations, detailed_translations):
        # 각 언어별 번역 생성
        for lang, trans_data in translations.items():
            try:
                # 해당 언어의 상세정보에서 설명 가져오기
                detailed_info = detailed_translations.get(lang, {})
                description = detailed_info.get("overview", trans_data.get("overview", ""))

                translation = PlaceTranslation.objects.create(
                    place=place,
                    lang=lang,
                    name=trans_data.get("title", ""),
                    address=trans_data.get("addr1", ""),
                    description=description,
                    tour_api_content_id=trans_data.get("content_id", "")
                )
                print(f"[{lang.upper()}] 번역 생성: {translation.name}")

            except Exception as e:
                print(f"[{lang.upper()}] 번역 생성 실패: {e}")
                import traceback
                traceback.print_exc()

    def update_translations_with_details(self, place, translations, detailed_translations):
        updated_count = 0

        for lang, trans_data in translations.items():
            try:
                # 해당 언어의 상세정보에서 설명 가져오기
                detailed_info = detailed_translations.get(lang, {})
                description = detailed_info.get("overview", trans_data.get("overview", ""))

                translation, created = PlaceTranslation.objects.get_or_create(
                    place=place,
                    lang=lang,
                    defaults={
                        "name": trans_data.get("title", ""),
                        "address": trans_data.get("addr1", ""),
                        "description": description,
                        "tour_api_content_id": trans_data.get("content_id", "")
                    }
                )

                if not created:
                    # 기존 번역 업데이트
                    translation.name = trans_data.get("title", "")
                    translation.address = trans_data.get("addr1", "")
                    translation.description = description
                    translation.tour_api_content_id = trans_data.get("content_id", "")
                    translation.save()

                updated_count += 1
                print(f"[{lang.upper()}] 번역 업데이트: {translation.name}")

            except Exception as e:
                print(f"[{lang.upper()}] 번역 업데이트 실패: {e}")

        return updated_count

    def get_phone_by_category(self, processed_data):
        # 카테고리별 전화번호 필드 우선순위 처리
        if processed_data.get("tel"):
            return processed_data["tel"]

        phone_priority = [
            "infocenterfood",
            "infocentershopping",
            "infocenterculture",
            "infocenterleports",
            "infocenter",
            "infocenterlodging"
        ]

        for field in phone_priority:
            if processed_data.get(field):
                return processed_data[field]

        return ""

    def get_usetime_by_category(self, processed_data):
        # 카테고리별 운영시간 필드 우선순위 처리
        time_priority = [
            "opentimefood",
            "opentime",
            "usetimeculture",
            "usetimeleports",
            "usetime",
            "opendateshopping",
            "checkintime",
        ]

        for field in time_priority:
            if processed_data.get(field):
                return processed_data[field]

        return ""

    def update_place(self, existing_place, processed_data, translations, detailed_translations):
        region_saved = False
        region_obj = None
        subregion_obj = None

        region_id = processed_data.get("region_id")
        sub_region_id = processed_data.get("sub_region_id")

        if region_id and sub_region_id:
            try:
                from regions.models import Region, SubRegion
                region_obj = Region.objects.get(id=region_id)
                subregion_obj = SubRegion.objects.get(id=sub_region_id)
                region_saved = True
            except (Region.DoesNotExist, SubRegion.DoesNotExist):
                pass

        # 카테고리별 전화번호/운영시간 처리
        phone_number = self.get_phone_by_category(processed_data)
        use_time = self.get_usetime_by_category(processed_data)

        try:
            existing_place.region = region_obj
            existing_place.sub_region = subregion_obj
            existing_place.phone_number = phone_number[:20] if phone_number else ""
            existing_place.use_time = use_time[:200] if use_time else ""
            existing_place.link_url = processed_data.get("homepage", "")[:500]
            existing_place.last_synced_at = timezone.now()
            existing_place.save()

            print(f"Place 업데이트 성공! ID: {existing_place.id}")

            if processed_data.get("latitude") and processed_data.get("longitude"):
                try:
                    lat = float(processed_data["latitude"])
                    lng = float(processed_data["longitude"])
                    existing_place.location = Point(lng, lat)
                    existing_place.save()
                except Exception as e:
                    print(f"좌표 업데이트 실패: {e}")

            # 번역 정보 업데이트 (핵심 수정 부분)
            self.update_translations_with_details(existing_place, translations, detailed_translations)

        except Exception as e:
            print(f"Place 업데이트 실패: {e}")
            raise

        return region_saved

    def is_same_place_by_korean_name(self, title1, title2, distance):
        # 괄호 안 한국어로 같은 장소인지 체크
        korean1 = self.extract_korean_from_parentheses(title1)
        korean2 = self.extract_korean_from_parentheses(title2)

        # 둘 다 괄호 안 한국어가 있으면 비교
        if korean1 and korean2:
            # 완전 일치하거나 한쪽이 다른쪽을 포함
            if korean1 == korean2:
                return True
            if korean1 in korean2 or korean2 in korean1:
                return True

        # 한쪽만 괄호 한국어가 있으면 다른쪽 전체 제목과 비교
        if korean1 and not korean2:
            # title2에서 한글 부분 추출
            korean_part2 = self.extract_korean_part(title2)
            if korean1 in korean_part2 or korean_part2 in korean1:
                return True

        if korean2 and not korean1:
            # title1에서 한글 부분 추출
            korean_part1 = self.extract_korean_part(title1)
            if korean2 in korean_part1 or korean_part1 in korean2:
                return True

        return False

    def extract_korean_from_parentheses(self, title):
        # 괄호 안 한국어 추출: "60Hz(60헤르츠)" -> "60헤르츠"
        import re

        # 다양한 괄호 패턴 매칭
        patterns = [
            r'\(([^)]*[가-힣][^)]*)\)',  # (한글포함)
            r'\（([^）]*[가-힣][^）]*)\）',  # （한글포함）
            r'\[([^\]]*[가-힣][^\]]*)\]',  # [한글포함]
        ]

        for pattern in patterns:
            matches = re.findall(pattern, title)
            for match in matches:
                # 한글이 포함된 것만 반환
                if re.search(r'[가-힣]', match):
                    # 공백과 특수문자 정리
                    cleaned = re.sub(r'[^\w가-힣]', '', match)
                    if len(cleaned) >= 2:
                        return cleaned

        return None

    def extract_korean_part(self, title):
        # 제목에서 한글 부분만 추출
        import re
        korean_chars = re.findall(r'[가-힣]+', title)
        return ''.join(korean_chars)

    def is_similar_place(self, name1, name2, distance):
        # 관광지 전용 매칭 로직 (거리 + 이름 조합)
        if not name1 or not name2:
            return False

        # 거리별 유사도 임계값 조정
        if distance <= 100:  # 100m 이내면 유연하게
            similarity_threshold = 0.3
        elif distance <= 300:  # 300m 이내면 보통
            similarity_threshold = 0.5
        else:  # 500m 이내면 엄격하게
            similarity_threshold = 0.7

        # 완전히 다른 업종인지 체크 (음식점끼리는 구분)
        if self.is_different_business_type(name1, name2):
            return False

        # 핵심 키워드 매칭
        return self.calculate_place_similarity(name1, name2) >= similarity_threshold

    def is_different_business_type(self, name1, name2):
        # 명확히 다른 업종만 구분 (같은 관광지의 다른 언어 번역 허용)
        clear_business_keywords = {
            "medical": ["약국", "병원", "의원", "한의원", "치과", "pharmacy", "hospital", "clinic"],
            "food_specific": ["막창", "갈비", "치킨", "피자", "족발", "makchang", "galbi", "chicken"],
        }

        name1_type = None
        name2_type = None

        for biz_type, keywords in clear_business_keywords.items():
            for keyword in keywords:
                if keyword in name1.lower():
                    name1_type = biz_type
                if keyword in name2.lower():
                    name2_type = biz_type

        # 명확히 다른 업종이면 다른 업체
        return (name1_type and name2_type and name1_type != name2_type)

    def calculate_place_similarity(self, name1, name2):
        # 관광지 이름 유사도 계산 (더 유연)
        if not name1 or not name2:
            return 0.0

        # 숫자 제거 (168계단, 40계단 등에서 숫자 부분)
        import re
        clean1 = re.sub(r'\d+', '', name1).strip()
        clean2 = re.sub(r'\d+', '', name2).strip()

        # 한쪽이 다른쪽을 포함하면 높은 유사도
        shorter = clean1 if len(clean1) < len(clean2) else clean2
        longer = clean2 if len(clean1) < len(clean2) else clean1

        if shorter in longer and len(shorter) >= 2:
            return 0.8

        # 문자 단위 유사도 계산
        if len(longer) == 0:
            return 1.0

        common_chars = 0
        for char in shorter:
            if char in longer:
                common_chars += 1

        return common_chars / len(longer)

    def is_similar_business(self, name1, name2):
        # 엄격한 업체명 유사도 검사
        if not name1 or not name2:
            return False

        # 서로 다른 업종 키워드가 있으면 다른 업체로 판단
        business_keywords = {
            "food": ["고기", "막창", "갈비", "치킨", "피자", "족발", "보쌈", "삼겹", "곱창", "순대"],
            "medical": ["약국", "병원", "의원", "한의원", "치과", "안과", "내과", "정형외과"],
            "shop": ["마트", "편의점", "상점", "가게", "매장", "스토어", "샵"],
            "cafe": ["카페", "커피", "coffee", "cafe", "다방", "찻집"],
            "hotel": ["호텔", "펜션", "모텔", "게스트", "리조트", "콘도"]
        }

        name1_category = None
        name2_category = None

        # 각 이름의 업종 분류
        for category, keywords in business_keywords.items():
            for keyword in keywords:
                if keyword in name1:
                    name1_category = category
                if keyword in name2:
                    name2_category = category

        # 서로 다른 업종이면 다른 업체
        if name1_category and name2_category and name1_category != name2_category:
            return False

        # 핵심 키워드가 포함되어야 함
        shorter = name1 if len(name1) < len(name2) else name2
        longer = name2 if len(name1) < len(name2) else name1

        # 짧은 이름의 70% 이상이 긴 이름에 포함되어야 함
        if len(shorter) >= 3:
            match_count = 0
            for char in shorter:
                if char in longer:
                    match_count += 1
            similarity = match_count / len(shorter)
            return similarity >= 0.7

        return False

    def calculate_distance_simple(self, lat1, lng1, lat2, lng2):
        # 간단한 거리 계산 (미터 단위)
        import math
        R = 6371000  # 지구 반지름 (미터)

        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)

        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def calculate_title_similarity(self, title1, title2):
        # 제목 유사도 계산 (간단한 문자열 매칭)
        if not title1 or not title2:
            return 0.0

        # 더 긴 문자열을 기준으로 유사도 계산
        longer = title1 if len(title1) > len(title2) else title2
        shorter = title2 if len(title1) > len(title2) else title1

        if len(longer) == 0:
            return 1.0

        # 공통 문자 개수 계산
        common_chars = 0
        for char in shorter:
            if char in longer:
                common_chars += 1

        return common_chars / len(longer)

    def print_summary(self, stats):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"처리 결과:")
        self.stdout.write(f"   - 총 처리: {stats['total_processed']}개")
        self.stdout.write(f"   - 신규 생성: {stats['created']}개")
        self.stdout.write(f"   - 업데이트: {stats['updated']}개")
        self.stdout.write(f"   - 스킵: {stats['skipped']}개")
        self.stdout.write(f"   - 에러: {stats['errors']}개")
        self.stdout.write(f"\n다국어 번역 결과:")
        self.stdout.write(f"   - 번역 생성: {stats['translations_created']}개")
        self.stdout.write(f"   - 번역 업데이트: {stats['translations_updated']}개")
        self.stdout.write(f"\n지역 저장 결과:")
        self.stdout.write(f"   - 지역 매핑 성공: {stats['region_saved']}개")
        self.stdout.write(f"   - 지역 매핑 실패: {stats['region_failed']}개")

    def handle_collect_all_pages(self, area_code, max_total_items, dry_run, collect_all, detail_delay, language):
        self.stdout.write("투어 API 전체 페이지 수집 모드 시작")
        self.stdout.write("=" * 60)

        self.client = TourAPIClient()
        self.mapper = CategoryMapper()
        self.mapper.enable_all_regions()

        if language == "all":
            self.languages = ["ko", "en", "jp", "cn"]
        else:
            self.languages = [language]

        try:
            first_page_result = self.client.get_area_list_by_language(
                area_code=area_code, page_no=1, num_of_rows=10, lang="ko"
            )

            if not first_page_result:
                self.stdout.write("첫 페이지 데이터를 가져올 수 없습니다.")
                return

            total_count = getattr(self.client, 'last_total_count', 0)
            if total_count == 0:
                self.stdout.write("전체 데이터 개수를 확인할 수 없습니다.")
                return

            actual_limit = min(total_count, max_total_items)
            per_page = 1000
            total_pages = math.ceil(actual_limit / per_page)

            self.stdout.write(f"전체 관광지: {total_count:,}개")
            self.stdout.write(f"수집 예정: {actual_limit:,}개")
            self.stdout.write(f"처리할 페이지: {total_pages}개")

            if dry_run:
                self.stdout.write("시뮬레이션 모드: 실제 저장하지 않음")
                return

            total_stats = {
                "total_processed": 0, "created": 0, "updated": 0,
                "skipped": 0, "errors": 0, "translations_created": 0, "translations_updated": 0
            }

            for page_no in range(1, total_pages + 1):
                self.stdout.write(f"\n페이지 {page_no}/{total_pages} 처리 중...")

                remaining_items = actual_limit - total_stats["total_processed"]
                current_page_size = min(per_page, remaining_items)

                try:
                    page_stats = self.sync_places_multilang(
                        limit=current_page_size, area_code=area_code, page=page_no,
                        dry_run=dry_run, force_update=False,
                        collect_all=collect_all, detail_delay=detail_delay
                    )

                    if page_stats:
                        for key in total_stats:
                            if key in page_stats:
                                total_stats[key] += page_stats[key]

                    self.stdout.write(f"페이지 {page_no}: 신규 {page_stats.get('created', 0)}개")

                    if total_stats["total_processed"] >= actual_limit:
                        self.stdout.write(f"목표 개수({actual_limit}개) 달성으로 수집 완료")
                        break

                    time.sleep(detail_delay)

                except Exception as e:
                    self.stdout.write(f"페이지 {page_no} 처리 실패: {e}")
                    total_stats["errors"] += 1
                    continue

            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("전체 페이지 수집 완료")
            self.print_summary(total_stats)

        except Exception as e:
            self.stdout.write(f"전체 페이지 수집 중 에러: {e}")
            raise CommandError(f"수집 실패: {e}")

    def check_region_database_status(self):
        try:
            from regions.models import Region, SubRegion
            region_count = Region.objects.count()
            subregion_count = SubRegion.objects.count()

            self.stdout.write(f"지역 데이터베이스 상태:")
            self.stdout.write(f"   - 지역: {region_count}개")
            self.stdout.write(f"   - 하위지역: {subregion_count}개")

            if region_count == 0:
                self.stdout.write("지역 데이터가 없습니다. 지역 매핑이 불가능합니다.")
        except Exception as e:
            self.stdout.write(f"지역 데이터베이스 상태 확인 실패: {e}")
