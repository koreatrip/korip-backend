# 날씨 API 관련 예외 클래스들


class WeatherAPIError(Exception):
    # 날씨 API 관련 기본 예외 클래스


    def __init__(self, message, error_code=None, detail=None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code  # 기상청 API 에러 코드
        self.detail = detail  # 상세 에러 정보

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class InvalidCoordinatesError(WeatherAPIError):
    # 잘못된 좌표 예외

    def __init__(self, latitude, longitude, message=None):
        if message is None:
            message = f"잘못된 좌표입니다: 위도={latitude}, 경도={longitude}"
        super().__init__(message)
        self.latitude = latitude
        self.longitude = longitude


class APIKeyError(WeatherAPIError):
    # API 키 관련 예외

    def __init__(self, message=None):
        if message is None:
            message = "기상청 API 키가 유효하지 않습니다"
        super().__init__(message, error_code="API_KEY_ERROR")


class APIQuotaExceededError(WeatherAPIError):
    # API 호출 한도 초과 예외


    def __init__(self, message=None):
        if message is None:
            message = "기상청 API 일일 호출 한도를 초과했습니다"
        super().__init__(message, error_code="QUOTA_EXCEEDED")


class APIResponseError(WeatherAPIError):
    # API 응답 파싱 예외

    def __init__(self, response_data=None, message=None):
        if message is None:
            message = "기상청 API 응답을 파싱하는 중 오류가 발생했습니다"
        super().__init__(message, error_code="RESPONSE_PARSE_ERROR")
        self.response_data = response_data


class NetworkError(WeatherAPIError):
    # 네트워크 연결 예외

    def __init__(self, original_error=None, message=None):
        if message is None:
            message = "기상청 API 서버와 연결할 수 없습니다"
        super().__init__(message, error_code="NETWORK_ERROR")
        self.original_error = original_error


class GridConversionError(WeatherAPIError):
    # 격자 좌표 변환 예외

    def __init__(self, latitude, longitude, message=None):
        if message is None:
            message = f"좌표를 격자로 변환할 수 없습니다: 위도={latitude}, 경도={longitude}"
        super().__init__(message, error_code="GRID_CONVERSION_ERROR")
        self.latitude = latitude
        self.longitude = longitude


class WeatherDataNotFoundError(WeatherAPIError):
    # 날씨 데이터 없음 예외

    def __init__(self, latitude, longitude, forecast_time=None, message=None):
        if message is None:
            if forecast_time:
                message = f"해당 시간의 날씨 데이터를 찾을 수 없습니다: {forecast_time}"
            else:
                message = f"해당 지역의 날씨 데이터를 찾을 수 없습니다: 위도={latitude}, 경도={longitude}"
        super().__init__(message, error_code="DATA_NOT_FOUND")
        self.latitude = latitude
        self.longitude = longitude
        self.forecast_time = forecast_time


# 예외 클래스 사용 예시들

"""
사용 예시:

1. 잘못된 좌표 체크:
try:
    client.get_weather_by_coordinates(91.0, 200.0)  # 잘못된 좌표
except InvalidCoordinatesError as e:
    print(f"좌표 에러: {e}")

2. API 키 문제:
try:
    client = WeatherAPIClient(api_key="wrong_key")
except APIKeyError as e:
    print(f"API 키 에러: {e}")

3. 네트워크 문제:
try:
    weather_data = client.get_weather_by_coordinates(37.5665, 126.9780)
except NetworkError as e:
    print(f"네트워크 에러: {e}")
    # 재시도 로직 또는 캐시된 데이터 사용

4. 전체 예외 처리:
try:
    weather_data = client.get_weather_by_coordinates(37.5665, 126.9780)
except WeatherAPIError as e:
    # 모든 날씨 API 예외를 한 번에 처리
    print(f"날씨 API 에러: {e}")
    # 로그 기록, 알림 발송 등
"""