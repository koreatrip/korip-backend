import requests
from decouple import config
from utils.oauth.base import OAuthProvider
from users.models import LoginType
import urllib.parse
import logging

logger = logging.getLogger(__name__)


class GoogleOAuth(OAuthProvider):
    client_id = config("GOOGLE_OAUTH2_CLIENT_ID")
    client_secret = config("GOOGLE_OAUTH2_CLIENT_SECRET")
    redirect_uri = config("GOOGLE_SOCIAL_LOGIN_REDIRECT_URI")

    def get_token(self, code: str) -> str:
        """구글 OAuth code를 access_token으로 교환"""
        url = "https://oauth2.googleapis.com/token"
        decoded_code = urllib.parse.unquote(code)

        # 디버깅용 상세 로그
        logger.info("=" * 60)
        logger.info("구글 토큰 요청 상세 정보")
        logger.info(f"client_id: {self.client_id[:20]}...")
        logger.info(f"redirect_uri: [{self.redirect_uri}]")
        logger.info(f"redirect_uri 길이: {len(self.redirect_uri)}")
        logger.info(f"code 앞 30자: {decoded_code[:30]}...")
        logger.info("=" * 60)

        data = {
            "code": decoded_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        res = requests.post(url, data=data)

        # 응답 로깅
        logger.info(f"구글 응답 상태코드: {res.status_code}")
        logger.info(f"구글 응답 내용: {res.text}")

        # JSON 파싱
        try:
            response_data = res.json()
        except Exception as e:
            logger.error(f"JSON 파싱 실패: {e}")
            logger.error(f"응답 원본: {res.text}")
            raise Exception(f"구글 응답을 파싱할 수 없습니다: {e}")

        # 에러 체크
        if res.status_code != 200:
            error_msg = response_data.get("error_description", response_data.get("error", "알 수 없는 에러"))
            error_type = response_data.get("error", "unknown")

            logger.error(f"구글 토큰 요청 실패 (상태코드 {res.status_code})")
            logger.error(f"에러 타입: {error_type}")
            logger.error(f"에러 메시지: {error_msg}")
            logger.error(f"전체 응답: {response_data}")

            # redirect_uri_mismatch 에러면 추가 정보 출력
            if error_type == "redirect_uri_mismatch":
                logger.error("=" * 60)
                logger.error("redirect_uri_mismatch 에러 발생!")
                logger.error(f"백엔드가 사용한 redirect_uri: [{self.redirect_uri}]")
                logger.error("프론트엔드가 구글에 보낸 redirect_uri를 확인하세요!")
                logger.error("두 값이 정확히 일치해야 합니다 (공백, 슬래시 등 주의)")
                logger.error("=" * 60)

            raise Exception(f"구글 OAuth 토큰 요청 실패: {error_msg}")

        # access_token 존재 여부 확인
        if "access_token" not in response_data:
            logger.error("access_token이 응답에 없습니다")
            logger.error(f"응답 내용: {response_data}")
            raise Exception(f"access_token이 응답에 없습니다. 응답: {response_data}")

        logger.info("구글 토큰 받기 성공!")
        return response_data["access_token"]

    def get_user_info(self, access_token: str) -> dict:
        """access_token으로 사용자 정보 조회"""
        res = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = res.json()
        user_info["login_type"] = LoginType.GOOGLE
        return user_info
