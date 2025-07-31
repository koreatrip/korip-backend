from utils.oauth.google import GoogleOAuth
from exceptions.error_code import ErrorCode
from exceptions.custom_exception_handler import RequestError

def get_provider(provider_name: str):
    if provider_name == "google":
        return GoogleOAuth()
    else:
        raise RequestError(ErrorCode.UNSUPPORTED_PROVIDER)
