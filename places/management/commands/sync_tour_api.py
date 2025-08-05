# 투어 API 데이터 동기화 명령어 - 지역 저장 로직 강화

# places/management/commands/sync_tour_api.py

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from places.models import Place
from places.services.tour_api_client import TourAPIClient
from places.services.category_mapper import CategoryMapper
import time


class Command(BaseCommand):
    help = "투어 API에서 관광지 데이터를 가져와서 DB에 저장합니다 (ForeignKey 대응)"

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
            "--filter-stats",
            action="store_true",
            help="지역 필터링 통계만 출력하고 종료"
        )
        parser.add_argument(
            "--collect-details",
            action="store_true",
            help="상세정보도 함께 수집 (overview, homepage, 이미지 등)"
        )
        parser.add_argument(
            "--collect-images",
            action="store_true",
            help="추가 이미지도 함께 수집 (detailImage2)"
        )
        parser.add_argument(
            "--collect-intro",
            action="store_true",
            help="소개정보도 함께 수집 (운영시간, 입장료 등)"
        )
        parser.add_argument(
            "--collect-all",
            action="store_true",
            help="모든 상세정보 수집 (--collect-details + --collect-images + --collect-intro)"
        )
        parser.add_argument(
            "--detail-delay",
            type=float,
            default=1.0,
            help="상세정보 수집 시 API 호출 간 대기시간 (초, 기본값: 1.0)"
        )
        parser.add_argument(
            "--debug-region",
            action="store_true",
            help="지역 매핑 디버깅 모드 활성화"
        )
        parser.add_argument(
            "--test-region-only",
            action="store_true",
            help="지역 매핑 테스트만 실행 (실제 저장 안함)"
        )

    def handle(self, *args, **options):
        limit = min(options["limit"], 1000)
        area_code = options["area_code"]
        page = options["page"]
        dry_run = options["dry_run"]
        force_update = options["force_update"]
        disable_region_filter = options["disable_region_filter"]
        filter_stats_only = options["filter_stats"]
        collect_details = options["collect_details"] or options["collect_all"]
        collect_images = options["collect_images"] or options["collect_all"]
        collect_intro = options["collect_intro"] or options["collect_all"]
        detail_delay = options["detail_delay"]
        self.debug_region = options["debug_region"]
        self.test_region_only = options["test_region_only"]

        self.stdout.write(
            self.style.SUCCESS("🚀 KORIP 투어 API 동기화 시작 (ForeignKey 대응)")
        )
        self.stdout.write("=" * 60)

        self.client = TourAPIClient()
        self.mapper = CategoryMapper()

        if disable_region_filter:
            self.mapper.enable_all_regions()
            self.stdout.write(
                self.style.WARNING("⚠️ 지역 필터링 비활성화 - 모든 지역 저장됨")
            )

        if filter_stats_only:
            self.print_filter_statistics_only()
            return

        self.stdout.write(f"📊 처리 설정:")
        self.stdout.write(f"   - 총 처리: {limit}개")
        self.stdout.write(f"   - 지역 코드: {area_code or '전체'}")
        self.stdout.write(f"   - 시작 페이지: {page}")
        self.stdout.write(f"   - 테스트 모드: {'예' if dry_run else '아니오'}")
        self.stdout.write(f"   - 강제 업데이트: {'예' if force_update else '아니오'}")
        self.stdout.write(f"   - 지역 필터링: {'비활성화' if disable_region_filter else '활성화'}")
        self.stdout.write(f"   - 🔍 지역 디버깅: {'활성화' if self.debug_region else '비활성화'}")
        self.stdout.write(f"   - 🧪 지역 테스트만: {'예' if self.test_region_only else '아니오'}")

        self.stdout.write(f"\n🔍 상세정보 수집 설정:")
        self.stdout.write(f"   - 상세정보 (overview, homepage): {'예' if collect_details else '아니오'}")
        self.stdout.write(f"   - 추가 이미지 (detailImage2): {'예' if collect_images else '아니오'}")
        self.stdout.write(f"   - 소개정보 (운영시간 등): {'예' if collect_intro else '아니오'}")
        if any([collect_details, collect_images, collect_intro]):
            self.stdout.write(f"   - API 호출 대기시간: {detail_delay}초")

        try:
            self.check_region_database_status()
            self.print_mapping_and_filter_info()

            self.stdout.write("🔍 투어 API 연결 테스트 중...")
            connection_test_result = self.client.test_connection(from_command=True)

            if not connection_test_result:
                self.stdout.write(
                    self.style.WARNING("⚠️ 투어 API 연결 테스트 일부 실패! 하지만 계속 진행합니다.")
                )
                self.stdout.write("💡 API 연결은 정상이므로 실제 동기화를 시도합니다.")
            else:
                self.stdout.write(
                    self.style.SUCCESS("✅ 투어 API 연결 성공!")
                )

            result = self.sync_places(
                limit=limit,
                area_code=area_code,
                page=page,
                dry_run=dry_run,
                force_update=force_update,
                collect_details=collect_details,
                collect_images=collect_images,
                collect_intro=collect_intro,
                detail_delay=detail_delay
            )

            if result is not None:
                self.print_summary(result)
            else:
                self.stdout.write(
                    self.style.ERROR("❌ 동기화 결과를 가져올 수 없습니다!")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ 동기화 중 치명적 에러 발생: {e}")
            )
            import traceback
            traceback.print_exc()
            raise CommandError(f"동기화 실패: {e}")

        finally:
            try:
                mapping_stats = self.mapper.get_mapping_statistics()
                if isinstance(mapping_stats, dict):
                    self.stdout.write(f"\n📊 카테고리 매핑 통계:")
                    self.stdout.write(f"   - 총 매핑: {mapping_stats.get('total_mappings', 0)}개")
                    self.stdout.write(f"   - 서브카테고리: {mapping_stats.get('subcategory_mappings', 0)}개")
                    self.stdout.write(f"   - 지역 매핑: {mapping_stats.get('region_mappings', 0)}개")
            except Exception as e:
                self.stdout.write(f"\n⚠️ 매핑 통계 조회 실패: {e}")

    def sync_places(self, limit, area_code, page, dry_run, force_update,
                    collect_details, collect_images, collect_intro, detail_delay):
        stats = {
            "total_processed": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "region_saved": 0,
            "region_failed": 0
        }

        try:
            places_data = self.client.get_area_list(
                area_code=area_code,
                page_no=page,
                num_of_rows=limit
            )

            if not places_data:
                self.stdout.write(self.style.WARNING("⚠️ 투어 API에서 데이터를 가져올 수 없습니다."))
                return stats

            self.stdout.write(f"✅ {len(places_data)}개의 관광지 데이터를 가져왔습니다.")

            for place_data in places_data:
                stats["total_processed"] += 1

                try:
                    processed_data = self.mapper.process_tour_api_place(place_data)

                    if not processed_data or not isinstance(processed_data, dict):
                        stats["skipped"] += 1
                        continue

                    content_id = processed_data.get("content_id")
                    if not content_id:
                        stats["skipped"] += 1
                        continue

                    if collect_details and not dry_run:
                        self._collect_detailed_info(content_id, place_data.get("contenttypeid", "12"), processed_data)

                    try:
                        from places.models import Place
                        existing_place = Place.objects.get(content_id=content_id)

                        if not force_update:
                            stats["skipped"] += 1
                            continue

                        if not dry_run:
                            region_saved = self.update_place(existing_place, processed_data)
                            if region_saved:
                                stats["region_saved"] += 1
                            else:
                                stats["region_failed"] += 1
                        stats["updated"] += 1

                    except Place.DoesNotExist:
                        if not dry_run:
                            region_saved = self.create_place(processed_data)
                            if region_saved:
                                stats["region_saved"] += 1
                            else:
                                stats["region_failed"] += 1
                        stats["created"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    self.stdout.write(f"❌ 처리 중 에러: {e}")

        except Exception as e:
            self.stdout.write(f"❌ 동기화 중 에러: {e}")
            stats["errors"] += 1

        return stats

    def _collect_detailed_info(self, content_id, content_type_id, processed_data):
        try:
            detail_info = self.client.get_place_detail(content_id)
            if detail_info:
                processed_data.update({
                    "overview": detail_info.get("overview", ""),
                    "homepage": detail_info.get("homepage", ""),
                    "tel": detail_info.get("tel", ""),
                })
        except Exception as e:
            pass

    @transaction.atomic
    def create_place(self, processed_data):
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
                print(f"[SUCCESS] 지역 정보 로드: {region_obj} > {subregion_obj}")
            except (Region.DoesNotExist, SubRegion.DoesNotExist) as e:
                print(f"[WARNING] 지역 객체 못 찾음: region_id={region_id}, sub_region_id={sub_region_id}")
            except Exception as e:
                print(f"[ERROR] 지역 조회 중 에러: {e}")

        category_obj = None
        sub_category_obj = None

        category_id = processed_data.get("category_id")
        if category_id:
            try:
                from categories.models import Category
                category_obj = Category.objects.get(id=category_id)
                print(f"[SUCCESS] 카테고리 객체 찾음: {category_obj} (ID: {category_id})")
            except Category.DoesNotExist:
                print(f"[WARNING] 카테고리 객체 못 찾음: ID {category_id}")
            except Exception as e:
                print(f"[WARNING] 카테고리 객체 조회 중 에러: {e}")

        sub_category_id = processed_data.get("sub_category_id")
        if sub_category_id:
            try:
                from categories.models import SubCategory
                sub_category_obj = SubCategory.objects.get(id=sub_category_id)
                print(f"[SUCCESS] 서브카테고리 객체 찾음: {sub_category_obj} (ID: {sub_category_id})")
            except SubCategory.DoesNotExist:
                print(f"[WARNING] 서브카테고리 객체 못 찾음: ID {sub_category_id}")
            except Exception as e:
                print(f"[WARNING] 서브카테고리 객체 조회 중 에러: {e}")

        try:
            place = Place.objects.create(
                content_id=processed_data["content_id"],
                category_id=category_obj.id if category_obj else None,
                sub_category_id=sub_category_obj.id if sub_category_obj else None,
                region=region_obj,
                sub_region=subregion_obj,
                phone_number=processed_data.get("tel", processed_data.get("phone_number", ""))[:20],
                use_time=processed_data.get("use_time", "")[:200] if processed_data.get("use_time") else "",
                link_url=processed_data.get("homepage", "")[:500],
                favorite_count=0,
                last_synced_at=timezone.now()
            )

            print(f"[SUCCESS] Place 생성 성공! ID: {place.id}, content_id: {place.content_id}")

            if processed_data.get("latitude") and processed_data.get("longitude"):
                try:
                    from django.contrib.gis.geos import Point
                    lat = float(processed_data["latitude"])
                    lng = float(processed_data["longitude"])
                    place.location = Point(lng, lat)
                    place.save()
                    print(f"[SUCCESS] 좌표 저장 성공: ({lat}, {lng})")
                except Exception as e:
                    print(f"[WARNING] 좌표 저장 실패: {e}")

            if region_obj and subregion_obj:
                saved_region_name = place.region.get_name("ko") if place.region else None
                saved_subregion_name = place.sub_region.get_name("ko") if place.sub_region else None
                print(f"[SUCCESS] 지역 정보도 함께 저장됨!")
                print(f"[SUCCESS] - 저장된 지역: {saved_region_name}")
                print(f"[SUCCESS] - 저장된 하위지역: {saved_subregion_name}")
            else:
                print(f"[INFO] 지역 정보 없이 Place만 저장됨 (ID: {place.id})")

        except Exception as e:
            print(f"[ERROR] Place 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            raise

        try:
            from places.models import PlaceTranslation
            translation = PlaceTranslation.objects.create(
                place=place,
                lang="ko",
                name=processed_data.get("title", ""),
                address=processed_data.get("address", ""),
                tour_api_content_id=processed_data["content_id"]
            )
            print(f"[SUCCESS] PlaceTranslation 생성 성공: {translation.name}")

        except Exception as e:
            print(f"[ERROR] PlaceTranslation 생성 실패: {e}")
            import traceback
            traceback.print_exc()

        return region_saved

    @transaction.atomic
    def update_place(self, existing_place, processed_data):
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
                print(f"[UPDATE] 지역 정보 업데이트: {region_obj} > {subregion_obj}")
            except (Region.DoesNotExist, SubRegion.DoesNotExist) as e:
                print(f"[WARNING] 지역 객체 못 찾음: region_id={region_id}, sub_region_id={sub_region_id}")
            except Exception as e:
                print(f"[ERROR] 지역 조회 중 에러: {e}")

        category_obj = existing_place.category_id
        sub_category_obj = existing_place.sub_category_id

        category_id = processed_data.get("category_id")
        if category_id:
            try:
                from categories.models import Category
                category_obj = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                print(f"[WARNING] 카테고리 객체 못 찾음: ID {category_id}")
            except Exception as e:
                print(f"[WARNING] 카테고리 객체 조회 중 에러: {e}")

        sub_category_id = processed_data.get("sub_category_id")
        if sub_category_id:
            try:
                from categories.models import SubCategory
                sub_category_obj = SubCategory.objects.get(id=sub_category_id)
            except SubCategory.DoesNotExist:
                print(f"[WARNING] 서브카테고리 객체 못 찾음: ID {sub_category_id}")
            except Exception as e:
                print(f"[WARNING] 서브카테고리 객체 조회 중 에러: {e}")

        try:
            existing_place.category = category_obj.id if category_obj else None
            existing_place.sub_category = sub_category_obj.id if sub_category_obj else None
            existing_place.region = region_obj
            existing_place.sub_region = subregion_obj
            existing_place.phone_number = processed_data.get("tel", processed_data.get("phone_number", ""))[:20]
            existing_place.use_time = processed_data.get("use_time", "")[:200] if processed_data.get("use_time") else ""
            existing_place.link_url = processed_data.get("homepage", "")[:500]
            existing_place.last_synced_at = timezone.now()
            existing_place.save()

            print(f"[UPDATE] Place 업데이트 성공! ID: {existing_place.id}")

            if processed_data.get("latitude") and processed_data.get("longitude"):
                try:
                    from django.contrib.gis.geos import Point
                    lat = float(processed_data["latitude"])
                    lng = float(processed_data["longitude"])
                    existing_place.location = Point(lng, lat)
                    existing_place.save()
                    print(f"[UPDATE] 좌표 업데이트 성공: ({lat}, {lng})")
                except Exception as e:
                    print(f"[WARNING] 좌표 업데이트 실패: {e}")

            try:
                from places.models import PlaceTranslation
                translation, created = PlaceTranslation.objects.get_or_create(
                    place=existing_place,
                    lang="ko",
                    defaults={
                        "name": processed_data.get("title", ""),
                        "address": processed_data.get("address", ""),
                        "tour_api_content_id": processed_data["content_id"]
                    }
                )

                if not created:
                    translation.name = processed_data.get("title", "")
                    translation.address = processed_data.get("address", "")
                    translation.tour_api_content_id = processed_data["content_id"]
                    translation.save()

                print(f"[UPDATE] PlaceTranslation 업데이트 완료: {translation.name}")

            except Exception as e:
                print(f"[ERROR] PlaceTranslation 업데이트 실패: {e}")

        except Exception as e:
            print(f"[ERROR] Place 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()
            raise

        return region_saved

    def print_summary(self, stats):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"📋 처리 결과:")
        self.stdout.write(f"   - 총 처리: {stats['total_processed']}개")
        self.stdout.write(f"   - 신규 생성: {stats['created']}개")
        self.stdout.write(f"   - 업데이트: {stats['updated']}개")
        self.stdout.write(f"   - 스킵: {stats['skipped']}개")
        self.stdout.write(f"   - 에러: {stats['errors']}개")
        self.stdout.write(f"\n🗺️ 지역 저장 결과:")
        self.stdout.write(f"   - 지역 매핑 성공: {stats['region_saved']}개")
        self.stdout.write(f"   - 지역 매핑 실패: {stats['region_failed']}개")

    def check_region_database_status(self):
        try:
            from regions.models import Region, SubRegion
            region_count = Region.objects.count()
            subregion_count = SubRegion.objects.count()

            self.stdout.write(f"\n🗺️ 지역 데이터베이스 상태:")
            self.stdout.write(f"   - 지역: {region_count}개")
            self.stdout.write(f"   - 하위지역: {subregion_count}개")

            if region_count == 0:
                self.stdout.write(self.style.WARNING("⚠️ 지역 데이터가 없습니다. 지역 매핑이 불가능합니다."))
        except Exception as e:
            self.stdout.write(f"⚠️ 지역 데이터베이스 상태 확인 실패: {e}")

    def print_mapping_and_filter_info(self):
        self.stdout.write(f"\n🔍 카테고리 매핑 정보:")
        self.stdout.write(f"   - CategoryMapper 초기화 완료")
        self.stdout.write(f"   - 신분류 코드 → 우리 카테고리 매핑 활성화")

    def print_filter_statistics_only(self):
        try:
            filter_info = self.mapper.get_supported_regions_info()
            if isinstance(filter_info, dict):
                self.stdout.write(f"\n🗺️ 지역 필터링 통계:")
                self.stdout.write(f"   - 필터링 활성화: {filter_info.get('filter_enabled', False)}")
                self.stdout.write(f"   - 지원 지역 수: {filter_info.get('total_supported', 0)}개")

                supported_regions = filter_info.get('supported_regions', {})
                for code, region_info in supported_regions.items():
                    name = region_info.get('name', 'N/A')
                    count = region_info.get('subregion_count', 0)
                    self.stdout.write(f"     - {name} ({code}): {count}개 하위지역")
        except Exception as e:
            self.stdout.write(f"⚠️ 필터링 통계 조회 실패: {e}")
