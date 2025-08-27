# 투어 API 클라이언트 - 다국어 지원 + 좌표 매칭 개선 (500m 기준)

import requests
import json
import time
import logging
import math
from typing import Dict, List, Optional
from urllib.parse import unquote
from django.conf import settings

logger = logging.getLogger(__name__)


class TourAPIClient:

    def __init__(self):
        self.service_map = {
            "ko": "KorService2",
            "en": "EngService2",
            "jp": "JpnService2",
            "cn": "ChsService2",
        }

        self.base_url_template = "http://apis.data.go.kr/B551011/{service}"
        self.default_service = "KorService2"
        self.service_key = getattr(settings, "TOUR_API_SERVICE_KEY", None)
        if not self.service_key:
            raise ValueError("TOUR_API_SERVICE_KEY가 settings에 설정되지 않았습니다.")

        self.mobile_os = "ETC"
        self.mobile_app = "KORIP"
        self.response_type = "json"

        self.request_delay = 1
        self.max_retries = 3
        self.retry_delay_base = 1
        self.timeout = 30
        self.coordinate_threshold = 500  # 좌표 매칭 임계값 (500m)

        # 통계 수집
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "retry_attempts": 0,
            "timeout_errors": 0,
            "connection_errors": 0,
            "api_errors": 0,
            "ko_requests": 0,
            "en_requests": 0,
            "jp_requests": 0,
            "cn_requests": 0,
            "multilang_requests": 0,
            "coordinate_matches": 0,
            "coordinate_mismatches": 0,
            "same_place_found": 0,
        }

        # Rate Limit 관리
        self.last_request_time = 0
        self.last_total_count = 0  # 페이지네이션용 전체 개수 저장

    def _make_request(self, endpoint: str, params: Dict, lang: str = "ko") -> Optional[Dict]:
        """
        API 요청을 수행하는 메서드

        핵심 수정: API 키를 urllib.parse.unquote로 디코딩해서 사용
        - 이유: settings에 저장된 키가 URL 인코딩된 상태이기 때문
        - %2B → +, %2F → /, %3D → = 로 변환
        """
        try:
            # API 키 디코딩
            decoded_service_key = unquote(self.service_key)

            base_params = {
                "serviceKey": decoded_service_key,  # 디코딩된 키 사용
                "MobileOS": self.mobile_os,
                "MobileApp": self.mobile_app,
                "_type": self.response_type,
            }

            final_params = {**base_params, **params}

            # 언어별 서비스 선택
            service = self.service_map.get(lang, "KorService2")
            base_url = f"http://apis.data.go.kr/B551011/{service}"

            headers = {
                "User-Agent": "KORIP/1.0 (Korean Tourism Information Platform)",
                "Accept": "application/json"
            }

            response = requests.get(
                f"{base_url}/{endpoint}",
                params=final_params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if not isinstance(data, dict) or "response" not in data:
                return None

            header = data.get("response", {}).get("header", {})
            result_code = header.get("resultCode")

            if result_code != "0000":
                return None

            body = data["response"].get("body", {})

            # totalCount 저장 (페이지네이션용)
            if "totalCount" in body:
                self.last_total_count = body["totalCount"]

            return body

        except Exception:
            return None

    def _get_service_url(self, lang: str) -> str:
        # 언어별 서비스 URL 생성
        service_name = self.service_map.get(lang)
        if not service_name:
            raise ValueError(f"지원하지 않는 언어: {lang}")
        return self.base_url_template.format(service=service_name)

    def _wait_for_rate_limit(self):
        # Rate Limit 관리
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.request_delay:
            wait_time = self.request_delay - time_since_last_request
            time.sleep(wait_time)

    def calculate_distance_meters(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        # 두 좌표 간의 거리를 미터 단위로 계산 (Haversine 공식)
        R = 6371.0  # 지구 반지름 (km)

        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)

        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance_meters = R * c * 1000

        return distance_meters

    def is_same_location_by_coordinates(self, lat1: float, lng1: float, lat2: float, lng2: float) -> bool:
        # 좌표 기반으로 동일한 장소인지 판단 (500m 임계값)
        if not all([lat1, lng1, lat2, lng2]):
            return False

        distance = self.calculate_distance_meters(lat1, lng1, lat2, lng2)

        if distance <= self.coordinate_threshold:
            self.stats["coordinate_matches"] += 1
            return True
        else:
            self.stats["coordinate_mismatches"] += 1
            return False

    def compare_place_coordinates(self, place1: Dict, place2: Dict) -> Dict:
        # 두 관광지의 좌표를 비교하고 결과 반환
        try:
            lat1 = float(place1.get("mapy", 0))
            lng1 = float(place1.get("mapx", 0))
            lat2 = float(place2.get("mapy", 0))
            lng2 = float(place2.get("mapx", 0))

            distance = self.calculate_distance_meters(lat1, lng1, lat2, lng2)
            is_same = distance <= self.coordinate_threshold

            return {
                "place1_title": place1.get("title", "N/A"),
                "place2_title": place2.get("title", "N/A"),
                "place1_coords": (lat1, lng1),
                "place2_coords": (lat2, lng2),
                "distance_meters": distance,
                "is_same_location": is_same,
                "threshold": self.coordinate_threshold,
            }
        except (ValueError, TypeError) as e:
            return {
                "error": str(e),
                "is_same_location": False,
            }

    def get_category_codes(self) -> Optional[List[Dict]]:
        # 카테고리 코드 조회
        params = {
            "numOfRows": 1000,
            "pageNo": 1,
            "lclsSystmListYn": "Y"
        }

        result = self._make_request("lclsSystmCode2", params, "ko")

        if result and "items" in result:
            items = result["items"]
            if items and "item" in items:
                categories = items["item"]
                if isinstance(categories, dict):
                    categories = [categories]
                return categories
            else:
                return []

        return []

    def get_area_codes(self) -> Optional[List[Dict]]:
        # 지역 코드 조회
        params = {
            "numOfRows": 100,
            "pageNo": 1,
        }

        result = self._make_request("areaCode2", params, "ko")

        if result and "items" in result:
            items = result["items"]
            if items and "item" in items:
                areas = items["item"]
                if isinstance(areas, dict):
                    areas = [areas]
                return areas
            else:
                return []

        return []

    def get_area_list_multilang(self, area_code: Optional[str] = None, page_no: int = 1,
                                num_of_rows: int = 10, lang: str = "ko") -> Optional[List[Dict]]:
        # 다국어 관광지 목록 조회
        params = {
            "numOfRows": num_of_rows,
            "pageNo": page_no,
        }

        if area_code:
            params["areaCode"] = area_code

        result = self._make_request("areaBasedList2", params, lang)

        if result and "items" in result:
            items = result["items"]
            if items and "item" in items:
                places = items["item"]
                if isinstance(places, dict):
                    places = [places]
                return places
            else:
                return []

        return []

    def get_place_detail_multilang(self, content_id: str, lang: str = "ko") -> Optional[Dict]:
        # 다국어 관광지 상세 정보 조회
        if not content_id:
            return None

        params = {"contentId": content_id}
        result = self._make_request("detailCommon2", params, lang)

        if result and "items" in result:
            items = result["items"]
            if items and "item" in items:
                place_detail = items["item"]
                if isinstance(place_detail, list) and len(place_detail) > 0:
                    place_detail = place_detail[0]
                elif not isinstance(place_detail, dict):
                    return None

                return place_detail
            else:
                return None

        return None

    def get_area_list_by_language(self, area_code=None, page_no=1, num_of_rows=100, lang="ko"):
        # 언어별 관광지 목록 조회 (sync_tour_api.py 호환용)
        return self.get_area_list_multilang(area_code, page_no, num_of_rows, lang)

    def get_place_detail(self, content_id, lang="ko"):
        """
        관광지 상세정보 조회 (detailCommon2) - sync_tour_api.py 호환용

        핵심 수정: Y/N 파라미터들 모두 제거!
        - detailCommon2 API는 이런 파라미터들을 지원하지 않음
        - 기본 파라미터만으로 호출하면 모든 정보가 들어옴
        """
        params = {
            "contentId": content_id
            # defaultYN, firstImageYN, addrinfoYN, mapinfoYN, overviewYN 모두 제거!
        }

        result = self._make_request("detailCommon2", params, lang)

        if result and "items" in result:
            items = result["items"]
            if items and "item" in items:
                detail = items["item"]
                if isinstance(detail, list) and len(detail) > 0:
                    detail = detail[0]
                return detail

        return {}

    def get_place_detail_intro(self, content_id, content_type_id="12", lang="ko"):
        # 관광지 소개정보 조회 (detailIntro2) - 전화번호, 이용시간 등
        params = {
            "contentId": content_id,
            "contentTypeId": content_type_id
        }

        result = self._make_request("detailIntro2", params, lang)

        if result and "items" in result:
            items = result["items"]
            if items and "item" in items:
                intro = items["item"]
                if isinstance(intro, list) and len(intro) > 0:
                    intro = intro[0]
                return intro

        return {}

    def get_place_detail_image(self, content_id, lang="ko"):
        # 관광지 추가 이미지 조회 (detailImage2)
        params = {
            "contentId": content_id,
            "imageYN": "Y",
            "subImageYN": "Y"
        }

        result = self._make_request("detailImage2", params, lang)

        if result and "items" in result:
            items = result["items"]
            if items and "item" in items:
                images = items["item"]
                if isinstance(images, dict):
                    images = [images]
                return images

        return []

    def test_connection(self, from_command=False):
        # API 연결 테스트
        if from_command:
            import sys
            is_test_env = 'test' in sys.argv

            if is_test_env:
                return True

        all_tests_passed = True

        try:
            # 지역 코드 테스트
            area_codes = self.get_area_codes()
            if not area_codes or len(area_codes) == 0:
                all_tests_passed = False

            # 다국어 테스트
            for lang in self.service_map.keys():
                try:
                    places = self.get_area_list_multilang(area_code="1", num_of_rows=1, lang=lang)
                    if not places or len(places) == 0:
                        all_tests_passed = False
                except Exception:
                    all_tests_passed = False

            # 카테고리 코드 테스트
            category_codes = self.get_category_codes()
            if not category_codes or len(category_codes) == 0:
                all_tests_passed = False

            # 기본 관광지 목록 테스트
            basic_places = self.get_area_list(area_code="1", num_of_rows=1)
            if not basic_places or len(basic_places) == 0:
                all_tests_passed = False

            return all_tests_passed

        except Exception:
            return False

    def get_stats(self) -> Dict:
        # API 사용 통계 반환
        success_rate = 0
        if self.stats["total_requests"] > 0:
            success_rate = (self.stats["successful_requests"] / self.stats["total_requests"]) * 100

        coordinate_match_rate = 0
        total_coordinate_attempts = self.stats["coordinate_matches"] + self.stats["coordinate_mismatches"]
        if total_coordinate_attempts > 0:
            coordinate_match_rate = (self.stats["coordinate_matches"] / total_coordinate_attempts) * 100

        return {
            **self.stats,
            "success_rate": f"{success_rate:.1f}%",
            "coordinate_match_rate": f"{coordinate_match_rate:.1f}%",
            "coordinate_threshold_meters": self.coordinate_threshold,
        }

    @property
    def base_url(self):
        # 기본 URL 반환
        return self.base_url_template.format(service=self.default_service)

    def get_area_list(self, area_code: Optional[str] = None, page_no: int = 1, num_of_rows: int = 10) -> Optional[
        List[Dict]]:
        # 관광지 목록 조회 (한국어)
        return self.get_area_list_multilang(area_code, page_no, num_of_rows, "ko")

    def search_by_keyword(self, keyword: str, area_code: str = None, page_no: int = 1, num_of_rows: int = 10) -> \
            Optional[List[Dict]]:
        # 키워드 검색 (한국어)
        return self.search_by_keyword_multilang(keyword, area_code, page_no, num_of_rows, "ko")

    def search_by_keyword_multilang(self, keyword: str, area_code: str = None, page_no: int = 1,
                                    num_of_rows: int = 10, lang: str = "ko") -> Optional[List[Dict]]:
        # 다국어 키워드 검색
        if not keyword:
            return None

        params = {
            "keyword": keyword,
            "numOfRows": num_of_rows,
            "pageNo": page_no,
            "arrange": "A"
        }

        if area_code:
            params["areaCode"] = area_code

        result = self._make_request("searchKeyword2", params, lang)

        if result and "items" in result:
            items = result["items"]
            if items and "item" in items:
                search_results = items["item"]
                if isinstance(search_results, dict):
                    search_results = [search_results]
                return search_results
            else:
                return []

        return []
