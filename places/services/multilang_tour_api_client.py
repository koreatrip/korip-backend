import requests
import time
from typing import Dict, List, Any, Optional
from urllib.parse import unquote
from django.conf import settings


class MultiLangTourAPIClient:
    """다국어 투어 API 클라이언트"""

    BASE_URLS = {
        "ko": "http://apis.data.go.kr/B551011/KorService2",
        "en": "http://apis.data.go.kr/B551011/EngService2",
        "jp": "http://apis.data.go.kr/B551011/JpnService2",
        "cn": "http://apis.data.go.kr/B551011/ChsService2",
    }

    MOBILE_OS = "ETC"
    MOBILE_APP = "KORIP"
    SUPPORTED_LANGUAGES = ["ko", "en", "jp", "cn"]
    DAILY_LIMIT_PER_LANGUAGE = 1000
    REQUEST_DELAY = 0.1

    def __init__(self):
        self.base_urls = self.BASE_URLS
        self.service_key = getattr(settings, "TOUR_API_SERVICE_KEY", None)
        self.mobile_os = self.MOBILE_OS
        self.mobile_app = self.MOBILE_APP
        self.supported_languages = self.SUPPORTED_LANGUAGES

        if not self.service_key:
            raise ValueError("TOUR_API_SERVICE_KEY가 settings에 설정되지 않았습니다.")

        self.api_call_count_by_language = {lang: 0 for lang in self.supported_languages}
        self.last_call_time = None

    @property
    def base_url(self):
        return self.base_urls.get("ko")

    @property
    def api_call_count(self):
        return sum(self.api_call_count_by_language.values())

    @api_call_count.setter
    def api_call_count(self, value):
        per_language = value // len(self.supported_languages)
        remainder = value % len(self.supported_languages)

        for i, lang in enumerate(self.supported_languages):
            self.api_call_count_by_language[lang] = per_language
            if i < remainder:
                self.api_call_count_by_language[lang] += 1

    def get_places_by_language(self, area_code: int = 1, lang: str = "ko",
                               num_of_rows: int = 10, page_no: int = 1) -> Dict[str, Any]:
        """언어별 관광지 목록 조회"""
        if lang not in self.supported_languages:
            return {
                "status": "error",
                "error": f"지원하지 않는 언어 코드: {lang}. 지원 언어: {self.supported_languages}"
            }

        if self.api_call_count_by_language.get(lang, 0) >= self.DAILY_LIMIT_PER_LANGUAGE:
            return {
                "status": "error",
                "error": f"{lang.upper()} 언어 일일 API 호출 제한 초과 ({self.DAILY_LIMIT_PER_LANGUAGE}회)"
            }

        try:
            url = self._build_api_url(lang, "areaBasedList2", {
                "areaCode": area_code,
                "numOfRows": num_of_rows,
                "pageNo": page_no
            })

            self._apply_request_delay()

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            self.api_call_count_by_language[lang] += 1

            response_data = response.json()
            items = self._extract_items_from_response(response_data)
            items_with_language = self._add_language_metadata(items, lang)

            return {
                "status": "success",
                "data": items_with_language,
                "total_count": len(items_with_language),
                "language": lang,
                "area_code": area_code
            }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": f"API 호출 실패: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"데이터 처리 실패: {str(e)}"
            }

    def get_place_detail_by_language(self, content_id: str, lang: str = "ko") -> Dict[str, Any]:
        """언어별 관광지 상세 정보 조회"""
        if lang not in self.supported_languages:
            return {
                "status": "error",
                "error": f"지원하지 않는 언어 코드: {lang}"
            }

        if self.api_call_count_by_language.get(lang, 0) >= self.DAILY_LIMIT_PER_LANGUAGE:
            return {
                "status": "error",
                "error": f"{lang.upper()} 언어 일일 API 호출 제한 초과 ({self.DAILY_LIMIT_PER_LANGUAGE}회)"
            }

        try:
            url = self._build_api_url(lang, "detailCommon2", {
                "contentId": content_id
            })

            self._apply_request_delay()

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            self.api_call_count_by_language[lang] += 1

            response_data = response.json()
            items = self._extract_items_from_response(response_data)

            if items:
                detail_with_language = self._add_language_metadata([items[0]], lang)[0]

                return {
                    "status": "success",
                    "data": detail_with_language,
                    "language": lang,
                    "content_id": content_id
                }
            else:
                return {
                    "status": "error",
                    "error": f"관광지 상세정보를 찾을 수 없습니다 (content_id: {content_id})"
                }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": f"API 호출 실패: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"데이터 처리 실패: {str(e)}"
            }

    def get_place_detail_intro(self, content_id: str, content_type_id: str, lang: str = "ko") -> Dict[str, Any]:
        """관광지 소개정보 조회 (전화번호, 이용시간, 홈페이지 등)"""
        if lang not in self.supported_languages:
            return {
                "status": "error",
                "error": f"지원하지 않는 언어 코드: {lang}"
            }

        if self.api_call_count_by_language.get(lang, 0) >= self.DAILY_LIMIT_PER_LANGUAGE:
            return {
                "status": "error",
                "error": f"{lang.upper()} 언어 일일 API 호출 제한 초과 ({self.DAILY_LIMIT_PER_LANGUAGE}회)"
            }

        try:
            url = self._build_api_url(lang, "detailIntro2", {
                "contentId": content_id,
                "contentTypeId": content_type_id
            })

            self._apply_request_delay()

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            self.api_call_count_by_language[lang] += 1

            response_data = response.json()
            items = self._extract_items_from_response(response_data)

            return {
                "status": "success",
                "data": items[0] if items else {},
                "language": lang,
                "content_id": content_id
            }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": f"소개정보 조회 실패: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"데이터 처리 실패: {str(e)}"
            }

    def get_place_detail_common(self, content_id: str, lang: str = "ko") -> Dict[str, Any]:
        """관광지 상세 공통정보 조회 (overview, usetime, homepage 등)"""
        if lang not in self.supported_languages:
            return {
                "status": "error",
                "error": f"지원하지 않는 언어 코드: {lang}"
            }

        if self.api_call_count_by_language.get(lang, 0) >= self.DAILY_LIMIT_PER_LANGUAGE:
            return {
                "status": "error",
                "error": f"{lang.upper()} 언어 일일 API 호출 제한 초과 ({self.DAILY_LIMIT_PER_LANGUAGE}회)"
            }

        try:
            url = self._build_api_url(lang, "detailCommon2", {
                "contentId": content_id
            })

            self._apply_request_delay()

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            self.api_call_count_by_language[lang] += 1

            response_data = response.json()
            items = self._extract_items_from_response(response_data)

            return {
                "status": "success",
                "data": items[0] if items else {},
                "language": lang,
                "content_id": content_id
            }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": f"상세정보 조회 실패: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"데이터 처리 실패: {str(e)}"
            }

    def collect_all_languages(self, area_code: int = 1, num_of_rows: int = 10) -> Dict[str, Any]:
        """모든 언어로 관광지 데이터 수집"""
        all_language_data = {}
        errors = []

        for lang in self.supported_languages:
            result = self.get_places_by_language(
                area_code=area_code,
                lang=lang,
                num_of_rows=num_of_rows
            )

            if result["status"] == "success":
                all_language_data[lang] = result["data"]
            else:
                errors.append(f"{lang}: {result['error']}")
                all_language_data[lang] = []

        successful_languages = [lang for lang, data in all_language_data.items() if data]
        total_places = sum(len(data) for data in all_language_data.values())

        return {
            "status": "success" if successful_languages else "error",
            "data": all_language_data,
            "total_languages": len(self.supported_languages),
            "successful_languages": successful_languages,
            "total_places": total_places,
            "errors": errors,
            "api_calls_by_language": self.api_call_count_by_language,
            "total_api_calls": sum(self.api_call_count_by_language.values())
        }

    def search_places_by_keyword(self, keyword: str, lang: str = "ko",
                                 num_of_rows: int = 10) -> Dict[str, Any]:
        """키워드로 관광지 검색"""
        if lang not in self.supported_languages:
            return {
                "status": "error",
                "error": f"지원하지 않는 언어 코드: {lang}"
            }

        if self.api_call_count_by_language.get(lang, 0) >= self.DAILY_LIMIT_PER_LANGUAGE:
            return {
                "status": "error",
                "error": f"{lang.upper()} 언어 일일 API 호출 제한 초과 ({self.DAILY_LIMIT_PER_LANGUAGE}회)"
            }

        try:
            url = self._build_api_url(lang, "searchKeyword2", {
                "keyword": keyword,
                "numOfRows": num_of_rows,
                "pageNo": 1
            })

            self._apply_request_delay()

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            self.api_call_count_by_language[lang] += 1

            response_data = response.json()
            items = self._extract_items_from_response(response_data)

            items_with_language = self._add_language_metadata(items, lang)

            return {
                "status": "success",
                "data": items_with_language,
                "total_count": len(items_with_language),
                "language": lang,
                "keyword": keyword
            }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": f"API 호출 실패: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"데이터 처리 실패: {str(e)}"
            }

    def _build_api_url(self, lang: str, endpoint: str, params: Dict[str, Any]) -> str:
        """API URL 생성"""
        base_url = self.base_urls.get(lang)
        if not base_url:
            raise ValueError(f"지원하지 않는 언어: {lang}")

        base_params = {
            "serviceKey": self.service_key,
            "MobileOS": self.mobile_os,
            "MobileApp": self.mobile_app,
            "_type": "json"
        }

        all_params = {**base_params, **params}
        url = f"{base_url}/{endpoint}?"
        param_strings = [f"{key}={value}" for key, value in all_params.items()]
        url += "&".join(param_strings)

        return url

    def _extract_items_from_response(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """API 응답에서 아이템 추출"""
        try:
            header = response_data.get("response", {}).get("header", {})

            if header.get("resultCode") != "0000":
                return []

            body = response_data.get("response", {}).get("body", {})
            items = body.get("items", {})
            item_data = items.get("item", [])
            if isinstance(item_data, dict):
                item_data = [item_data]
            elif not isinstance(item_data, list):
                item_data = []

            return item_data

        except Exception:
            return []

    def _add_language_metadata(self, items: List[Dict[str, Any]], lang: str) -> List[Dict[str, Any]]:
        """아이템에 언어 메타데이터 추가"""
        items_with_language = []

        for item in items:
            item_with_lang = item.copy()
            item_with_lang["_language"] = lang
            item_with_lang["_collected_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            item_with_lang["_tour_api_content_id"] = item.get("contentid", "")

            items_with_language.append(item_with_lang)

        return items_with_language

    def _apply_request_delay(self):
        """요청 간 딜레이 적용"""
        current_time = time.time()

        if self.last_call_time is not None:
            elapsed = current_time - self.last_call_time
            if elapsed < self.REQUEST_DELAY:
                sleep_time = self.REQUEST_DELAY - elapsed
                time.sleep(sleep_time)

        self.last_call_time = time.time()

    def get_api_usage_stats(self) -> Dict[str, Any]:
        """API 사용 통계 반환"""
        total_calls = sum(self.api_call_count_by_language.values())
        max_possible_calls = len(self.supported_languages) * self.DAILY_LIMIT_PER_LANGUAGE

        return {
            "calls_by_language": self.api_call_count_by_language,
            "total_calls": total_calls,
            "max_calls_per_language": self.DAILY_LIMIT_PER_LANGUAGE,
            "max_total_calls": max_possible_calls,
            "remaining_calls_total": max_possible_calls - total_calls,
            "usage_percentage": round((total_calls / max_possible_calls) * 100, 2),
            "daily_limit": self.DAILY_LIMIT_PER_LANGUAGE
        }

    def reset_api_counter(self):
        """API 카운터 리셋"""
        self.api_call_count_by_language = {lang: 0 for lang in self.supported_languages}
