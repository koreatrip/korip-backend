from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point
from django.db import transaction
from typing import Dict, List, Any, Optional
from django.utils import timezone
import time

from places.models import Place, PlaceTranslation
from places.services.multilang_tour_api_client import MultiLangTourAPIClient
from places.utils.coordinate_matcher import (
    find_matching_place_by_gis,
    calculate_center_point,
    create_point_from_coordinates
)


class Command(BaseCommand):
    help = "투어 API에서 다국어 관광지 데이터를 수집하고 GIS 매칭으로 통합"

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

    def handle(self, *args, **options):
        languages = [lang.strip() for lang in options["languages"].split(",")]
        area_code = options["area_code"]
        limit = options["limit"]
        threshold = options["threshold"]
        dry_run = options["dry_run"]

        self._validate_options(languages, area_code)

        self.stdout.write("다국어 관광지 동기화 시작")
        self.stdout.write(f"지역 코드: {area_code}")
        self.stdout.write(f"언어: {', '.join(languages)}")
        self.stdout.write(f"언어당 최대 수집: {limit}개")
        self.stdout.write(f"GIS 매칭 임계값: {threshold}m")
        if dry_run:
            self.stdout.write("DRY RUN 모드 (실제 저장 안함)")

        start_time = time.time()

        try:
            multilang_data = self._collect_multilang_data(languages, area_code, limit)

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

    def _collect_multilang_data(self, languages: List[str], area_code: int, limit: int) -> Dict[str, Any]:
        self.stdout.write("투어 API에서 다국어 데이터 수집 중...")

        api_client = MultiLangTourAPIClient()
        result = api_client.collect_all_languages(area_code=area_code, num_of_rows=limit)

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
            "gis_matches_found": 0,
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
                        place, created = Place.objects.get_or_create(
                            content_id=content_id,
                            defaults={
                                "location": Point(lng, lat),
                                "phone_number": place_data.get("tel", ""),
                                "last_synced_at": timezone.now()
                            }
                        )

                        if created:
                            stats["new_places_created"] += 1

                        translation, trans_created = PlaceTranslation.objects.get_or_create(
                            place=place,
                            lang="ko",
                            defaults={
                                "name": place_data.get("title", ""),
                                "address": place_data.get("addr1", ""),
                                "tour_api_content_id": content_id
                            }
                        )

                        if trans_created:
                            stats["translations_added"] += 1

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
                            place = Place.objects.create(
                                content_id=place_data.get("contentid", f"new_{lang}_{int(time.time())}"),
                                location=Point(lng, lat),
                                phone_number=place_data.get("tel", ""),
                                last_synced_at=timezone.now()
                            )
                            stats["new_places_created"] += 1

                        translation, trans_created = PlaceTranslation.objects.get_or_create(
                            place=place,
                            lang=lang,
                            defaults={
                                "name": place_data.get("title", ""),
                                "address": place_data.get("addr1", ""),
                                "tour_api_content_id": place_data.get("contentid", "")
                            }
                        )

                        if trans_created:
                            stats["translations_added"] += 1

            except Exception as e:
                stats["processing_errors"].append(f"{place_data.get('title', 'Unknown')}: {str(e)}")

        return stats

    def _print_results(self, stats: Dict[str, Any], elapsed_time: float):
        self.stdout.write("다국어 관광지 동기화 완료")
        self.stdout.write(f"소요 시간: {elapsed_time:.2f}초")
        self.stdout.write(f"처리된 관광지: {stats['total_processed']}개")
        self.stdout.write(f"새로 생성된 Place: {stats['new_places_created']}개")
        self.stdout.write(f"추가된 번역: {stats['translations_added']}개")
        self.stdout.write(f"GIS 매칭 성공: {stats['gis_matches_found']}개")

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
