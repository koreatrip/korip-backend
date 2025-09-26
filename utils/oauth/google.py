import requests
from decouple import config
from utils.oauth.base import OAuthProvider
from users.models import LoginType
import urllib.parse
import logging
logger = logging.getLogger(__name__)


class GoogleOAuth(OAuthProvider):
    client_id = config("GOOGLE_CLIENT_ID")
    client_secret = config("GOOGLE_CLIENT_SECRET")
    redirect_uri = config("GOOGLE_REDIRECT_URI", default="http://localhost:9000/api/auth/google/callback/")

    def get_token(self, code: str) -> str:
        url = "https://oauth2.googleapis.com/token"
        decoded_code = urllib.parse.unquote(code)
        data = {
            "code": decoded_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        res = requests.post(url, data=data)
        logger.info("🛑 Google token response: %s %s", res.status_code, res.text)
        return res.json()["access_token"]

    def get_user_info(self, access_token: str) -> dict:
        res = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = res.json()
        user_info['login_type'] = LoginType.GOOGLE
        return user_info

