import requests
import json
from urllib.parse import quote_plus
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Visit Korea API 테스트"

    def __init__(self):
        super().__init__()
        # Visit Korea API 올바른 URL
        self.base_url = "https://api.visitkorea.or.kr"
        # 발급받은 API 키
        self.service_key = "pcaidHGQK+oZx5Q5MAY1z4zQ+8sM51ko78WrcDpVfAwXHQmNZYS3CAQoI+G/nI6wnTIcqO0sXmxNwSIS9Qrp6A=="

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=5,
            help="가져올 데이터 개수"
        )
        parser.add_argument(
            "--area",
            type=str,
            default="1",
            help="지역 코드 (1:서울, 6:부산)"
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        area_code = options["area"]

        self.stdout.write(
            self.style.SUCCESS(f"🚀 Visit Korea API 테스트 시작!")
        )

        # 여러 API 경로 시도
        self.test_various_endpoints(area_code, limit)

    def test_various_endpoints(self, area_code, limit):
        """여러 API 엔드포인트 시도"""

        # 시도할 API 경로들
        endpoints = [
            # 기본 관광지 정보
            "openapi/service/rest/KorService1/areaBasedList1",
            "openapi/service/rest/KorService1/areaCode1",
            "openapi/service/rest/KorService1/categoryCode1",
            "openapi/service/rest/KorService1/searchKeyword1",
            # KorService 버전들
            "openapi/service/rest/KorService/areaBasedList",
            "openapi/service/rest/KorService/areaCode",
            "openapi/service/rest/KorService/categoryCode",
            # 다른 서비스들
            "openapi/service/rest/EngService1/areaBasedList1",
            "openapi/service/rest/GoCamping/basedList1"
        ]

        for endpoint in endpoints:
            self.stdout.write(f"\n🔍 {endpoint} 시도 중...")

            success = self.test_single_endpoint(endpoint, area_code, limit)
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ 성공! {endpoint}")
                )
                return

        self.stdout.write(
            self.style.ERROR("❌ 모든 엔드포인트 시도 실패")
        )

        # 기본 연결 테스트
        self.test_basic_connection()

    def test_single_endpoint(self, endpoint, area_code, limit):
        """단일 엔드포인트 테스트"""

        # URL 인코딩된 키와 원본 키 둘 다 시도
        keys_to_try = [
            ("원본 키", self.service_key),
            ("인코딩된 키", quote_plus(self.service_key))
        ]

        for key_type, key in keys_to_try:
            self.stdout.write(f"  🔑 {key_type}로 시도...")

            params = {
                "serviceKey": key,
                "numOfRows": limit,
                "pageNo": 1,
                "MobileOS": "ETC",
                "MobileApp": "KORIP",
                "areaCode": area_code,
                "_type": "json"
            }

            try:
                url = f"{self.base_url}/{endpoint}"
                self.stdout.write(f"  📡 URL: {url}")

                response = requests.get(url, params=params, timeout=15)

                self.stdout.write(f"  📊 상태코드: {response.status_code}")

                if response.status_code == 200:
                    # 응답 내용 확인
                    content = response.text[:300]
                    self.stdout.write(f"  📄 응답: {content}")

                    # 성공 응답인지 확인
                    if self.is_successful_response(response.text):
                        self.print_success_response(response.text)
                        return True
                    else:
                        self.stdout.write(f"  ❌ 서비스 에러: {response.text[:100]}")
                        # 에러여도 계속 진행

                elif response.status_code == 404:
                    self.stdout.write("  ❌ 404 - 엔드포인트 없음")
                else:
                    self.stdout.write(f"  ❌ HTTP 에러: {response.status_code}")

            except requests.exceptions.ConnectionError:
                self.stdout.write("  ❌ 연결 실패")
            except requests.exceptions.Timeout:
                self.stdout.write("  ❌ 타임아웃")
            except Exception as e:
                self.stdout.write(f"  ❌ 오류: {str(e)}")

        return False

    def is_successful_response(self, response_text):
        """응답이 성공인지 확인"""
        # XML 에러 응답 체크
        error_indicators = [
            "SERVICE ERROR",
            "SERVICE_KEY_IS_NOT_REGISTERED_ERROR",
            "SERVICE_ACCESS_DENIED_ERROR",
            "soapenv:Fault",
            "Policy Falsified",
            "NO_OPENAPI_SERVICE_ERROR"  # 추가!
        ]

        for error in error_indicators:
            if error in response_text:
                return False

        # JSON 응답에서 성공 코드 확인
        try:
            data = json.loads(response_text)
            result_code = data.get("resultCode", "")

            # resultCode가 "0000" 또는 "00"이면 성공
            if result_code in ["0000", "00", "0"]:
                return True
            else:
                # 에러 코드면 실패
                return False
        except:
            # JSON이 아니면서 에러 메시지가 없으면 OK
            return True

    def print_success_response(self, response_text):
        """성공 응답 출력"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("🎉 API 호출 성공!")
        self.stdout.write("=" * 50)

        try:
            # JSON 응답 시도
            data = json.loads(response_text)
            self.stdout.write("📋 JSON 응답:")
            self.stdout.write(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
        except:
            # XML 또는 기타 응답
            self.stdout.write("📋 응답 내용:")
            self.stdout.write(response_text[:1000])

    def test_basic_connection(self):
        """기본 연결 테스트"""
        self.stdout.write("\n🌐 기본 연결 테스트...")

        try:
            # Visit Korea API 루트 접속
            response = requests.get(self.base_url, timeout=10)
            self.stdout.write(f"📡 루트 접속: {response.status_code}")

            if response.status_code in [200, 404, 403]:
                self.stdout.write("✅ 서버 연결 성공")
            else:
                self.stdout.write(f"❌ 서버 응답 이상: {response.status_code}")

        except Exception as e:
            self.stdout.write(f"❌ 서버 연결 실패: {str(e)}")

        # 대안 제시
        self.stdout.write("\n💡 해결 방안:")
        self.stdout.write("1. Visit Korea API 문서에서 정확한 엔드포인트 확인")
        self.stdout.write("2. API 키 상태 재확인")
        self.stdout.write("3. 다른 관광 API 서비스 신청 고려")
