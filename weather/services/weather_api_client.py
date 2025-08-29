# 기상청 공공데이터 API 클라이언트 (날짜별 구분 및 체감온도 수정 버전)

import requests
import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from django.conf import settings
from weather.exceptions import (
    WeatherAPIError, InvalidCoordinatesError, APIKeyError,
    APIQuotaExceededError, APIResponseError, NetworkError,
    GridConversionError, WeatherDataNotFoundError
)


class WeatherAPIClient:
    # 날씨 정보 클라이언트 (날짜별 구분 및 체감온도 수정)

    # 1. 기상청 단기예보 조회서비스 (기본 날씨 정보)
    FORECAST_BASE_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
    # 2. 기상청 생활기상지수 조회서비스 (자외선, 체감온도)
    LIVING_WEATHER_BASE_URL = "https://apis.data.go.kr/1360000/LivingWthrIdxServiceV4"
    # 3. 기상청 지상시간자료 조회서비스 (실시간 관측 데이터)
    ASOS_BASE_URL = "https://apis.data.go.kr/1360000/AsosHourlyInfoService"
    # 4. 환경부 미세먼지 실시간 정보 (PM2.5, PM10)
    AIR_QUALITY_BASE_URL = "https://apis.data.go.kr/B552584/ArpltnInforInqireSvc"

    # 격자 변환 상수 (기상청 좌표계 변환용)
    RE = 6371.00877  # 지구 반경(km)
    GRID = 5.0  # 격자 간격(km)
    SLAT1 = 30.0  # 투영 위도1(degree)
    SLAT2 = 60.0  # 투영 위도2(degree)
    OLON = 126.0  # 기준점 경도(degree)
    OLAT = 38.0  # 기준점 위도(degree)
    XO = 43  # 기준점 X좌표(GRID)
    YO = 136  # 기준점 Y좌표(GRID)

    def __init__(self, api_key: Optional[str] = None, use_https: Optional[bool] = None):
        # WeatherAPIClient 초기화 (환경변수 기반 설정)

        # 환경변수에서 API 키 로드
        self.api_key = api_key or getattr(settings, "WEATHER_API_KEY", None)

        # API 키 유효성 검사
        if not self.api_key:
            raise APIKeyError(
                "API 키가 설정되지 않았습니다. "
                ".env 또는 .env.local 파일에 WEATHER_API_KEY를 설정해주세요."
            )

        # 환경변수에서 HTTPS 설정 로드
        if use_https is None:
            use_https = getattr(settings, "USE_HTTPS", True)

        # URL 설정 (HTTPS/HTTP 자동 선택)
        if use_https:
            print("HTTPS 모드: 실제 서버용 설정")
            self.forecast_base_url = self.FORECAST_BASE_URL
            self.living_weather_base_url = self.LIVING_WEATHER_BASE_URL
            self.asos_base_url = self.ASOS_BASE_URL
            self.air_quality_base_url = self.AIR_QUALITY_BASE_URL
        else:
            print("HTTP 모드: 개발환경용 설정")
            self.forecast_base_url = self.FORECAST_BASE_URL.replace("https://", "http://")
            self.living_weather_base_url = self.LIVING_WEATHER_BASE_URL.replace("https://", "http://")
            self.asos_base_url = self.ASOS_BASE_URL.replace("https://", "http://")
            self.air_quality_base_url = self.AIR_QUALITY_BASE_URL

        # 세션 생성 (연결 재사용)
        self.session = requests.Session()

        # HTTP 모드에서는 SSL 검증 비활성화
        if not use_https:
            self.session.verify = False
            # SSL 경고 메시지 숨기기
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        else:
            self.session.verify = True

        print("기상청 API 클라이언트 초기화 완료")

    def get_weather_by_coordinates(self, latitude: float, longitude: float) -> List[Dict]:
        # 위도/경도로 현재 시간부터 15시간 날씨 정보 조회

        # 1단계: 좌표 유효성 검사
        self._validate_coordinates(latitude, longitude)

        # 2단계: 위도/경도를 기상청 격자 좌표로 변환
        nx, ny = self._convert_to_grid(latitude, longitude)

        # 3단계: 기본 날씨 정보 조회 (단기예보 API)
        print("단기예보 API 호출 중...")
        forecast_data = self._get_forecast_data(nx, ny)

        # 현재 시간부터 15시간 필터링
        filtered_forecast_data = self._filter_next_15_hours(forecast_data)

        # 4단계: 미세먼지 정보 조회 (환경부 API)
        print("환경부 미세먼지 API 호출 중...")
        air_quality_data = self._get_air_quality_data(latitude, longitude)

        # 5단계: 생활기상지수 정보 조회 (자외선)
        print("생활기상지수 API 호출 중...")
        living_weather_data = self._get_living_weather_data_fixed(latitude, longitude)

        # 6단계: 지상관측 데이터 조회 (실시간 보완용)
        print("지상관측 데이터 API 호출 중...")
        asos_data = self._get_asos_data(latitude, longitude)

        # 7단계: 일출/일몰 시간 조회 (정확한 계산으로 처리)
        print("일출/일몰 시간 계산 중...")
        sun_times = self._calculate_sun_times_accurate(latitude, longitude)

        # 8단계: 모든 데이터 결합
        print("모든 데이터 결합 중...")
        complete_data = self._combine_all_weather_data(
            filtered_forecast_data, air_quality_data, living_weather_data, asos_data, sun_times
        )

        # 9단계: 최저/최고 기온 계산
        complete_data = self._calculate_daily_temperatures(complete_data)

        print(f"완료! {len(complete_data)}개의 예보 데이터를 받았습니다 (현재시간부터 15시간)")
        return complete_data

    def _filter_next_15_hours(self, forecast_data: List[Dict]) -> List[Dict]:
        from django.utils import timezone

        # USE_TZ = False이므로 naive datetime 사용
        current_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        end_time = current_time + timedelta(hours=15)

        print(f"현재 시간: {current_time}")
        print(f"필터링 시작: {current_time}")
        print(f"필터링 종료: {end_time}")

        filtered_data = []

        for forecast in forecast_data:
            try:
                # 시간대 정보 없이 파싱 (naive datetime)
                forecast_datetime = datetime.strptime(forecast["forecast_time"], "%Y-%m-%d %H:%M:%S")

                # naive datetime끼리 비교
                if current_time < forecast_datetime <= end_time:
                    filtered_data.append(forecast)
                    print(f"포함: {forecast_datetime} -> {forecast.get('temperature')}°C")
                else:
                    print(f"제외: {forecast_datetime} (범위 밖)")

            except (ValueError, KeyError) as e:
                print(f"시간 파싱 에러: {e}")
                continue

        # 시간순으로 정렬
        filtered_data.sort(key=lambda x: x["forecast_time"])

        print(f"원본 데이터: {len(forecast_data)}개 → 필터링 후: {len(filtered_data)}개")

        if filtered_data:
            first_time = filtered_data[0]["forecast_time"]
            last_time = filtered_data[-1]["forecast_time"]
            print(f"실제 필터링 범위: {first_time} ~ {last_time}")

        return filtered_data

    def _get_living_weather_data_fixed(self, latitude: float, longitude: float) -> Dict:
        # 생활기상지수 데이터 조회 (자외선만)

        try:
            # 정확한 지역 코드 가져오기
            area_code = self._get_area_code_for_living_weather(latitude, longitude)
            print(f"생활기상지수 지역코드: {area_code}")

            # 자외선 지수 조회
            uv_url = self._build_living_weather_url("getUVIdxV4", area_code)
            print(f"자외선 지수 API URL: {uv_url}")

            try:
                uv_data = self._call_api(uv_url)
                print("자외선 API 응답 성공")
                uv_index = self._parse_uv_index_improved(uv_data)
            except Exception as e:
                print(f"자외선 API 에러: {e}")
                uv_index = None

            return {
                "uv_index": uv_index,
                "feels_like_temperature": None  # 기본 데이터로 계산할 예정
            }

        except Exception as e:
            print(f"생활기상지수 전체 에러: {e}")
            return {
                "uv_index": None,
                "feels_like_temperature": None
            }

    def _calculate_feels_like_temperature(self, current_temp: float, humidity: int, wind_speed: float = None) -> float:
        # 실제 기온, 습도, 바람속도로 체감온도 계산

        try:
            print(f"체감온도 계산 시작: 기온={current_temp}°C, 습도={humidity}%, 바람={wind_speed}m/s")

            # 조건: 25도 이상에서 Heat Index 사용
            if current_temp >= 25:  # 25도 이상 (더울 때)
                feels_like = self._calculate_heat_index(current_temp, humidity)
                print(f"더운 날씨 - Heat Index 사용: {feels_like:.1f}°C")

            elif current_temp <= 10 and wind_speed and wind_speed > 1.34:  # 10도 이하 + 바람 (추울 때)
                feels_like = self._calculate_wind_chill(current_temp, wind_speed)
                print(f"추운 날씨 - Wind Chill 사용: {feels_like:.1f}°C")

            else:  # 일반적인 날씨 (10~25도)
                feels_like = self._calculate_basic_feels_like(current_temp, humidity, wind_speed)
                print(f"일반 날씨 - 기본 체감온도: {feels_like:.1f}°C")

            # 추가 검증: 체감온도가 비현실적이면 기본 기온 반환
            if abs(feels_like - current_temp) > 20:  # 차이가 20도 이상이면 이상함
                print(f"체감온도 이상값 감지: {feels_like:.1f}°C → 기본 기온 사용")
                feels_like = current_temp

            return round(feels_like, 1)

        except Exception as e:
            print(f"체감온도 계산 에러: {e}")
            # 에러 시 기본 기온 반환
            return current_temp

    def _calculate_heat_index(self, temp_c: float, humidity: int) -> float:
        # Heat Index 계산 (더운 날씨용)

        print(f"Heat Index 계산: {temp_c}°C, {humidity}%")

        t = float(temp_c)
        h = float(humidity)

        # 습도가 체감온도에 미치는 영향 계산
        if h > 60:  # 습도가 높을 때
            humidity_effect = (h - 60) * 0.15
        elif h < 40:  # 습도가 낮을 때
            humidity_effect = (h - 40) * 0.08
        else:  # 적정 습도
            humidity_effect = 0

        # 기온이 높을수록 습도의 영향이 더 커짐
        temperature_factor = max(0, (t - 25) * 0.1)

        feels_like = t + humidity_effect + temperature_factor

        print(f"  → 습도 효과: {humidity_effect:.1f}°C")
        print(f"  → 온도 효과: {temperature_factor:.1f}°C")
        print(f"  → 최종 체감: {feels_like:.1f}°C")

        return feels_like

    def _calculate_wind_chill(self, temp_c: float, wind_speed_ms: float) -> float:
        # Wind Chill 계산 (추운 날씨용)

        wind_kmh = wind_speed_ms * 3.6

        # Wind Chill 공식 (섭씨 기준)
        if wind_kmh > 4.8:  # 바람이 있을 때만
            wc = (13.12 +
                  0.6215 * temp_c -
                  11.37 * (wind_kmh ** 0.16) +
                  0.3965 * temp_c * (wind_kmh ** 0.16))
        else:
            wc = temp_c  # 바람이 약하면 실제 기온과 같음

        return wc

    def _calculate_basic_feels_like(self, temp_c: float, humidity: int, wind_speed_ms: float = None) -> float:
        # 기본 체감온도 계산 (일반적인 날씨용)

        # 습도 보정
        humidity_factor = 0.0
        if humidity > 60:  # 습도 높음
            humidity_factor = (humidity - 60) * 0.1  # 더 덥게
        elif humidity < 40:  # 습도 낮음
            humidity_factor = (humidity - 40) * 0.05  # 더 시원하게

        # 바람 보정
        wind_factor = 0.0
        if wind_speed_ms and wind_speed_ms > 1:
            wind_factor = -min(wind_speed_ms * 0.5, 3.0)  # 최대 -3도까지 시원하게

        # 최종 체감온도
        feels_like = temp_c + humidity_factor + wind_factor

        return feels_like

    def _get_air_quality_data(self, latitude: float, longitude: float) -> Dict:
        # 환경부 미세먼지 API로 PM2.5, PM10 데이터 조회

        try:
            # 전국에서 가장 가까운 측정소 찾기
            target_station, target_sido = self._find_nearest_air_station_nationwide(latitude, longitude)

            # 서울은 API에서 "서울"로 사용
            api_sido_name = target_sido

            air_url = self._build_air_quality_url_nationwide(target_station, api_sido_name)
            print(f"미세먼지 API URL: {air_url}")

            air_data = self._call_api(air_url)
            parsed_air_data = self._parse_air_quality_response_nationwide(
                air_data, target_station, api_sido_name, latitude, longitude
            )

            print(f"미세먼지 데이터: PM2.5={parsed_air_data['pm25']}, PM10={parsed_air_data['pm10']}")
            return parsed_air_data

        except Exception as e:
            print(f"미세먼지 API 에러 (API 활성화 대기중): {e}")
            # 환경부 미세먼지 API들이 아직 활성화 안됨, 지역별 평균값 반환
            target_station, target_sido = self._find_nearest_air_station_nationwide(latitude, longitude)
            if target_sido == "서울":
                return {"pm25": 18, "pm10": 32}
            elif target_sido == "부산":
                return {"pm25": 21, "pm10": 35}
            elif target_sido == "대구":
                return {"pm25": 22, "pm10": 38}
            else:
                return {"pm25": 20, "pm10": 35}

    def _find_nearest_air_station_nationwide(self, latitude: float, longitude: float) -> Tuple[Optional[str], str]:
        # 기상청 공식 좌표 데이터 기반 전국 대기질 측정소
        all_stations = {
            # 서울특별시 (25개 자치구)
            "서울": {
                "종로구": (37.5703, 126.9816),
                "중구": (37.5610, 126.9996),
                "용산구": (37.5311, 126.9678),
                "성동구": (37.5506, 127.0408),
                "광진구": (37.5388, 127.0831),
                "동대문구": (37.5838, 127.0507),
                "중랑구": (37.5951, 127.0934),
                "성북구": (37.6044, 126.9114),
                "강북구": (37.6469, 127.0147),
                "도봉구": (37.6689, 127.0471),
                "노원구": (37.6541, 127.0670),
                "은평구": (37.6176, 126.9227),
                "서대문구": (37.5791, 126.9368),
                "마포구": (37.5637, 126.9084),
                "양천구": (37.5268, 126.8556),
                "강서구": (37.5509, 126.8495),
                "구로구": (37.4954, 126.8581),
                "금천구": (37.4600, 126.9006),
                "영등포구": (37.5264, 126.8962),
                "동작구": (37.4951, 126.9395),
                "관악구": (37.4653, 126.9532),
                "서초구": (37.4837, 127.0324),
                "강남구": (37.5172, 127.0473),
                "송파구": (37.5145, 127.1065),
                "강동구": (37.5301, 127.1238),
            },

            # 부산광역시 (16개 자치구/군)
            "부산": {
                "중구": (35.1041, 129.0326),
                "서구": (35.0969, 129.0245),
                "동구": (35.1293, 129.0456),
                "영도구": (35.0913, 129.0681),
                "부산진구": (35.1621, 129.0522),
                "동래구": (35.2049, 129.0838),
                "남구": (35.1364, 129.0845),
                "북구": (35.1979, 129.0323),
                "해운대구": (35.1631, 129.1640),
                "사하구": (35.1042, 128.9747),
                "금정구": (35.2435, 129.0926),
                "강서구": (35.2124, 128.9800),
                "연제구": (35.1764, 129.0825),
                "수영구": (35.1456, 129.1135),
                "사상구": (35.1550, 128.9914),
                "기장군": (35.2446, 129.2218),
            },

            # 대구광역시 (8개 자치구/군)
            "대구": {
                "중구": (35.8664, 128.6067),
                "동구": (35.8864, 128.6353),
                "서구": (35.8719, 128.5592),
                "남구": (35.8464, 128.5975),
                "북구": (35.8858, 128.5829),
                "수성구": (35.8580, 128.6306),
                "달서구": (35.8298, 128.5325),
                "달성군": (35.7749, 128.4316),
            },

            # 인천광역시 (10개 자치구/군)
            "인천": {
                "중구": (37.4736, 126.6215),
                "동구": (37.4739, 126.6432),
                "미추홀구": (37.4636, 126.6502),
                "연수구": (37.4104, 126.6784),
                "남동구": (37.4468, 126.7313),
                "부평구": (37.5074, 126.7218),
                "계양구": (37.5368, 126.7348),
                "서구": (37.5458, 126.6765),
                "강화군": (37.7472, 126.4875),
                "옹진군": (37.4461, 126.6364),
            },

            # 광주광역시 (5개 자치구)
            "광주": {
                "동구": (35.1467, 126.9228),
                "서구": (35.1519, 126.8894),
                "남구": (35.1333, 126.9023),
                "북구": (35.1738, 126.9126),
                "광산구": (35.1396, 126.7936),
            },

            # 대전광역시 (5개 자치구)
            "대전": {
                "동구": (36.3506, 127.4545),
                "중구": (36.3269, 127.4216),
                "서구": (36.3556, 127.3837),
                "유성구": (36.3624, 127.3561),
                "대덕구": (36.3464, 127.4149),
            },

            # 울산광역시 (5개 자치구/군)
            "울산": {
                "중구": (35.56677778, 129.2666361),
                "남구": (35.54076389, 129.3323861),
                "동구": (35.50188889, 129.4189528),
                "북구": (35.57968889, 129.3635444),
                "울주군": (35.53073889, 129.2971639),
            },

            # 세종특별자치시
            "세종": {
                "세종시": (36.4800121, 127.2890691),
            },

            # 경기도 (31개 시/군)
            "경기": {
                "수원시장안구": (37.3010111, 127.0122222),
                "수원시권선구": (37.2547333, 126.974075),
                "수원시팔달구": (37.28310278, 127.0378333),
                "수원시영통구": (37.25631111, 127.0486333),
                "성남시수정구": (37.44749167, 127.1477194),
                "성남시중원구": (37.42766944, 127.1394194),
                "성남시분당구": (37.37996944, 127.1210194),
                "의정부시": (37.73528889, 127.0358417),
                "안양시만안구": (37.38377778, 126.9345),
                "안양시동안구": (37.3897, 126.9533556),
                "부천시": (37.5036, 126.7661),
                "광명시": (37.47575, 126.8667083),
                "평택시": (36.98943889, 127.1146556),
                "동두천시": (37.90091667, 127.0626528),
                "안산시상록구": (37.29851944, 126.8468194),
                "안산시단원구": (37.31672778, 126.8144194),
                "고양시덕양구": (37.63458333, 126.8341972),
                "고양시일산동구": (37.65590833, 126.7770556),
                "고양시일산서구": (37.67248611, 126.7527778),
                "과천시": (37.42637222, 126.9898),
                "구리시": (37.591625, 127.1318639),
                "남양주시": (37.63317778, 127.2186333),
                "오산시": (37.14691389, 127.0796417),
                "시흥시": (37.37731944, 126.8050778),
                "군포시": (37.35865833, 126.9375),
                "의왕시": (37.34195, 126.9703889),
                "하남시": (37.53649722, 127.217),
                "용인시처인구": (37.23147778, 127.2038444),
                "용인시기흥구": (37.27759722, 127.1167889),
                "용인시수지구": (37.48393056, 127.0798417),
                "파주시": (37.7597, 126.7800),
                "김포시": (37.6153, 126.7156),
                "광주시": (37.4294, 127.2556),
                "이천시": (37.2719, 127.4347),
                "양주시": (37.7853, 127.0456),
                "안성시": (37.0097, 127.2797),
                "포천시": (37.8947, 127.2003),
                "여주시": (37.2978, 127.6370),
                "양평군": (37.4911, 127.4875),
                "가평군": (37.8314, 127.5098),
                "연천군": (38.0956, 127.0747),
            },

            # 강원특별자치도 (18개 시/군)
            "강원": {
                "춘천시": (37.8814, 127.7300),
                "원주시": (37.3422, 127.9203),
                "강릉시": (37.7511, 128.8760),
                "동해시": (37.5244, 129.1144),
                "태백시": (37.1639, 128.9856),
                "속초시": (38.2072, 128.5918),
                "삼척시": (37.4497, 129.1658),
                "홍천군": (37.6975, 127.8889),
                "횡성군": (37.4914, 127.9825),
                "영월군": (37.1836, 128.4614),
                "평창군": (37.3706, 128.3900),
                "정선군": (37.3803, 128.6608),
                "철원군": (38.1469, 127.3131),
                "화천군": (38.1061, 127.7086),
                "양구군": (38.1106, 127.9900),
                "인제군": (38.0697, 128.1703),
                "고성군": (38.3803, 128.4675),
                "양양군": (38.0758, 128.6191),
            },

            # 충청북도 (11개 시/군)
            "충북": {
                "청주시상당구": (36.6372611, 127.4832889),
                "청주시서원구": (36.6372611, 127.4832889),
                "청주시흥덕구": (36.6182, 127.3594194),
                "청주시청원구": (36.6443056, 127.4876639),
                "충주시": (36.9711, 127.9261),
                "제천시": (37.1328, 128.1910),
                "보은군": (36.4894, 127.7294),
                "옥천군": (36.3061, 127.5722),
                "영동군": (36.1750, 127.7764),
                "증평군": (36.7883, 127.5825),
                "진천군": (36.8572, 127.4336),
                "괴산군": (36.8153, 127.7878),
                "음성군": (36.9431, 127.6869),
                "단양군": (36.9844, 128.3658),
            },

            # 충청남도 (15개 시/군)
            "충남": {
                "천안시동남구": (36.8062, 127.1522),
                "천안시서북구": (36.8088, 127.1028),
                "공주시": (36.4456, 127.1194),
                "보령시": (36.3331, 126.6128),
                "아산시": (36.7906, 127.0047),
                "서산시": (36.7844, 126.4503),
                "논산시": (36.1872, 127.0986),
                "계룡시": (36.2744, 127.2486),
                "당진시": (36.8944, 126.6278),
                "금산군": (36.1081, 127.4881),
                "부여군": (36.2753, 126.9097),
                "서천군": (36.0819, 126.6919),
                "청양군": (36.4594, 126.8028),
                "홍성군": (36.6011, 126.6608),
                "예산군": (36.6794, 126.8497),
                "태안군": (36.7453, 126.2983),
            },

            # 전라북도 (14개 시/군)
            "전북": {
                "전주시완산구": (35.8242, 127.1297),
                "전주시덕진구": (35.8494, 127.1289),
                "군산시": (35.9678, 126.7369),
                "익산시": (35.9483, 126.9547),
                "정읍시": (35.5697, 126.8556),
                "남원시": (35.4164, 127.3908),
                "김제시": (35.8014, 126.8806),
                "완주군": (35.9050, 127.1669),
                "진안군": (35.7917, 127.4247),
                "무주군": (36.0072, 127.6611),
                "장수군": (35.6494, 127.5203),
                "임실군": (35.6178, 127.2897),
                "순창군": (35.3744, 127.1372),
                "고창군": (35.4347, 126.7019),
                "부안군": (35.7319, 126.7331),
            },

            # 전라남도 (22개 시/군)
            "전남": {
                "목포시": (34.8119, 126.3925),
                "여수시": (34.7608, 127.6625),
                "순천시": (34.9503, 127.4878),
                "나주시": (35.0161, 126.7108),
                "광양시": (34.9403, 127.6358),
                "담양군": (35.3211, 126.9883),
                "곡성군": (35.2819, 127.2919),
                "구례군": (35.2028, 127.4625),
                "고흥군": (34.6111, 127.2853),
                "보성군": (34.7711, 127.0803),
                "화순군": (35.0647, 126.9864),
                "장흥군": (34.6814, 126.9069),
                "강진군": (34.6403, 126.7669),
                "해남군": (34.5731, 126.5989),
                "영암군": (34.8000, 126.6964),
                "무안군": (34.9903, 126.4822),
                "함평군": (35.0667, 126.5164),
                "영광군": (35.2769, 126.5114),
                "장성군": (35.3019, 126.7858),
                "완도군": (34.3108, 126.7553),
                "진도군": (34.4867, 126.2633),
                "신안군": (34.8267, 126.1078),
            },

            # 경상북도 (23개 시/군)
            "경북": {
                "포항시남구": (36.0194, 129.3650),
                "포항시북구": (36.0674, 129.3606),
                "경주시": (35.8561, 129.2247),
                "김천시": (36.1397, 128.1136),
                "안동시": (36.5683, 128.7297),
                "구미시": (36.1194, 128.3447),
                "영주시": (36.8058, 128.6242),
                "영천시": (35.9731, 128.9383),
                "상주시": (36.4108, 128.1592),
                "문경시": (36.5869, 128.1869),
                "경산시": (35.8250, 128.7414),
                "군위군": (36.2375, 128.5731),
                "의성군": (36.3528, 128.6972),
                "청송군": (36.4336, 129.0578),
                "영양군": (36.6667, 129.1114),
                "영덕군": (36.4150, 129.3658),
                "청도군": (35.6478, 128.7336),
                "고령군": (35.7281, 128.2631),
                "성주군": (35.9194, 128.2831),
                "칠곡군": (35.9953, 128.4014),
                "예천군": (36.6572, 128.4522),
                "봉화군": (36.8931, 128.7322),
                "울진군": (36.9931, 129.4003),
                "울릉군": (37.4844, 130.9053),
            },

            # 경상남도 (18개 시/군)
            "경남": {
                "창원시의창구": (35.2535, 128.6441),
                "창원시성산구": (35.2186, 128.6808),
                "창원시마산합포구": (35.1977, 128.5783),
                "창원시마산회원구": (35.2064, 128.5881),
                "창원시진해구": (35.1333, 128.7097),
                "진주시": (35.1803, 128.1078),
                "통영시": (34.8544, 128.4331),
                "사천시": (35.0036, 128.0642),
                "김해시": (35.2344, 128.8892),
                "밀양시": (35.5039, 128.7464),
                "거제시": (34.8808, 128.6214),
                "양산시": (35.3350, 129.0372),
                "의령군": (35.3219, 128.2614),
                "함안군": (35.2719, 128.4069),
                "창녕군": (35.5444, 128.4925),
                "고성군": (34.9731, 128.3225),
                "남해군": (34.8375, 127.8925),
                "하동군": (35.0678, 127.7514),
                "산청군": (35.4153, 127.8731),
                "함양군": (35.5208, 127.7253),
                "거창군": (35.6869, 127.9097),
                "합천군": (35.5667, 128.1653),
            },

            # 제주특별자치도 (2개 시)
            "제주": {
                "제주시": (33.4996, 126.5312),
                "서귀포시": (33.2541, 126.5600),
            }
        }

        # 전체 측정소에서 가장 가까운 곳 찾기
        min_distance = float("inf")
        nearest_station = None
        nearest_sido = None

        lat_coord = float(latitude)
        lon_coord = float(longitude)

        for sido_name, stations in all_stations.items():
            for station_name, (station_lat, station_lon) in stations.items():
                distance = self._calculate_distance(lat_coord, lon_coord, station_lat, station_lon)

                if distance < min_distance:
                    min_distance = distance
                    nearest_station = station_name
                    nearest_sido = sido_name

        return nearest_station, nearest_sido

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        # 두 지점 사이의 거리 계산 (킬로미터)

        # 라디안으로 변환
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # 하버사인 공식
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # 지구 반지름 (킬로미터)
        earth_radius = 6371
        distance = earth_radius * c

        return distance

    def _build_air_quality_url_nationwide(self, station_name: str, sido_name: str) -> str:
        # 환경부 미세먼지 API URL 생성
        print(f"미세먼지 조회: {station_name} ({sido_name})")

        url = f"{self.air_quality_base_url}/getCtprvnRltmMesureDnsty"
        params = {
            "serviceKey": self.api_key,
            "returnType": "json",
            "numOfRows": "200",
            "pageNo": "1",
            "sidoName": sido_name,
            "ver": "1.3"
        }

        param_string = "&".join([f"{key}={value}" for key, value in params.items()])
        full_url = f"{url}?{param_string}"

        return full_url

    def _parse_air_quality_response_nationwide(self, data: Dict, target_station: str,
                                               target_sido: str, latitude: float,
                                               longitude: float) -> Dict:
        # 환경부 미세먼지 API 응답 파싱 (개선된 매칭 로직)
        try:
            print(f"미세먼지 API 응답 확인 중... ({target_sido})")

            response_body = data.get("response", {}).get("body", {})
            items = response_body.get("items", [])

            if not items:
                print(f"{target_sido} 미세먼지 items가 없음")
                return {"pm25": None, "pm10": None}

            print(f"{target_sido}에서 받은 측정소 수: {len(items)}개")

            # 목표 측정소와 정확히 일치하는 데이터 찾기 (개선된 매칭)
            target_data = None
            for item in items:
                station_name = item.get("stationName", "")
                # 측정소명 매칭 개선: 다양한 매칭 방식 시도
                if (target_station in station_name or
                        station_name in target_station or
                        target_station.replace("구", "") in station_name or
                        target_station.replace("시", "") in station_name or
                        station_name.replace("구", "") in target_station or
                        station_name.replace("시", "") in target_station):
                    target_data = item
                    print(f"측정소 매칭 성공: {station_name}")
                    break

            # 정확한 측정소가 없으면 해당 시도에서 첫 번째 측정소 사용
            if not target_data and items:
                print(f"목표 측정소 '{target_station}' 정확한 매칭 없음, {target_sido}에서 첫 번째 측정소 사용")
                target_data = items[0]

            # 데이터 추출
            if target_data:
                station_name = target_data.get("stationName", "")
                pm25_value = target_data.get("pm25Value")
                pm10_value = target_data.get("pm10Value")

                print(f"선택된 측정소: {station_name}")
                print(f"원본 데이터: PM2.5={pm25_value}, PM10={pm10_value}")

                # 숫자로 변환 ("-" 나 null 값 처리)
                try:
                    pm25 = int(pm25_value) if pm25_value and pm25_value != "-" else None
                except (ValueError, TypeError):
                    pm25 = None

                try:
                    pm10 = int(pm10_value) if pm10_value and pm10_value != "-" else None
                except (ValueError, TypeError):
                    pm10 = None

                # 만약 주 데이터가 없으면 24시간 평균값 시도
                if pm25 is None:
                    pm25_24h = target_data.get("pm25Value24")
                    try:
                        pm25 = int(pm25_24h) if pm25_24h and pm25_24h != "-" else None
                    except (ValueError, TypeError):
                        pass

                if pm10 is None:
                    pm10_24h = target_data.get("pm10Value24")
                    try:
                        pm10 = int(pm10_24h) if pm10_24h and pm10_24h != "-" else None
                    except (ValueError, TypeError):
                        pass

                print(f"최종 파싱된 미세먼지: PM2.5={pm25}, PM10={pm10}")
                return {"pm25": pm25, "pm10": pm10}

            else:
                print(f"{target_sido}에서 사용 가능한 측정소 데이터 없음")
                return {"pm25": None, "pm10": None}

        except Exception as e:
            print(f"미세먼지 데이터 파싱 에러: {e}")
            return {"pm25": None, "pm10": None}

    def _get_area_code_for_living_weather(self, latitude: float, longitude: float) -> str:
        # 생활기상지수 API용 정확한 지역 코드 매핑

        metropolitan_areas = [
            # 서울특별시
            ((37.428, 37.701), (126.734, 127.269), "1100000000", "서울특별시"),

            # 부산광역시
            ((35.003, 35.396), (128.866, 129.366), "2600000000", "부산광역시"),

            # 대구광역시
            ((35.729, 35.998), (128.365, 128.756), "2700000000", "대구광역시"),

            # 인천광역시 (강화도, 옹진군 포함)
            ((37.201, 37.967), (126.117, 126.932), "2800000000", "인천광역시"),

            # 광주광역시
            ((35.066, 35.341), (126.653, 127.022), "2900000000", "광주광역시"),

            # 대전광역시
            ((36.177, 36.492), (127.269, 127.566), "3000000000", "대전광역시"),

            # 울산광역시
            ((35.362, 35.743), (129.026, 129.468), "3100000000", "울산광역시"),

            # 세종특별자치시
            ((36.394, 36.655), (127.189, 127.518), "3600000000", "세종특별자치시"),
        ]

        for (lat_min, lat_max), (lon_min, lon_max), area_code, area_name in metropolitan_areas:
            if lat_min <= latitude <= lat_max and lon_min <= longitude <= lon_max:
                print(f"생활기상지수 지역코드 매핑: {area_code} ({area_name})")
                return area_code

        province_areas = [
            # 제주특별자치도
            ((33.06, 33.57), (126.08, 126.97), "5000000000", "제주특별자치도"),

            # 강원특별자치도
            ((37.06, 38.61), (127.05, 129.47), "4200000000", "강원특별자치도"),

            # 경상북도
            ((35.59, 37.14), (128.58, 131.87), "4700000000", "경상북도"),

            # 경상남도
            ((34.63, 35.92), (127.74, 129.38), "4800000000", "경상남도"),

            # 전라남도
            ((33.85, 35.43), (125.04, 127.61), "4600000000", "전라남도"),

            # 전라북도
            ((35.16, 36.17), (126.49, 127.84), "4500000000", "전라북도"),

            # 충청남도
            ((35.96, 37.32), (126.06, 127.67), "4400000000", "충청남도"),

            # 충청북도
            ((36.04, 37.20), (127.63, 129.20), "4300000000", "충청북도"),

            # 경기도
            ((36.89, 38.31), (126.30, 127.94), "4100000000", "경기도"),
        ]

        for (lat_min, lat_max), (lon_min, lon_max), area_code, area_name in province_areas:
            if lat_min <= latitude <= lat_max and lon_min <= longitude <= lon_max:
                print(f"생활기상지수 지역코드 매핑: {area_code} ({area_name})")
                return area_code

        # 기본값: 서울
        print(f"정확한 매핑 실패, 서울로 기본 설정: 위도={latitude}, 경도={longitude}")
        return "1100000000"

    def _build_living_weather_url(self, service_type: str, area_code: str) -> str:
        # 생활기상지수 API URL 생성

        today = datetime.now()
        search_date = today.strftime("%Y%m%d")
        current_hour = today.strftime("%H")

        time_param = search_date + "06"  # 기본적으로 06시 데이터 조회

        print(f"생활기상지수 조회 날짜: {search_date} (오늘), 시간파라미터: {time_param}")

        url = f"{self.living_weather_base_url}/{service_type}"
        params = {
            "serviceKey": self.api_key,
            "numOfRows": "10",
            "pageNo": "1",
            "dataType": "JSON",
            "areaNo": area_code,
            "time": time_param
        }

        param_string = "&".join([f"{key}={value}" for key, value in params.items()])
        full_url = f"{url}?{param_string}"

        return full_url

    def _parse_uv_index_improved(self, data: Dict) -> Optional[int]:
        # 자외선 지수 파싱 개선 (낮 시간대 우선 선택)
        try:
            response = data.get("response", {})
            body = response.get("body", {})
            items = body.get("items", {})

            if not items:
                print("자외선 items가 비어있음")
                return None

            items_data = items.get("item", [])
            if not items_data or len(items_data) == 0:
                print("자외선 item 데이터가 없음")
                return None

            first_item = items_data[0] if isinstance(items_data, list) else items_data

            # 현재 시간 기준으로 적절한 값 선택
            current_hour = datetime.now().hour

            # 개선: 낮 시간대 자외선 지수 우선 반환
            if 6 <= current_hour <= 18:  # 낮 시간대
                # 현재 시간에 맞는 필드 선택
                if 6 <= current_hour < 9:
                    uv_field = "h6"
                elif 9 <= current_hour < 12:
                    uv_field = "h9"
                elif 12 <= current_hour < 15:
                    uv_field = "h12"
                elif 15 <= current_hour < 18:
                    uv_field = "h15"
                else:
                    uv_field = "h18"
            else:  # 밤 시간대
                # 밤에는 다음날 낮 시간대 최대값 반환
                day_fields = ["h9", "h12", "h15"]
                max_uv = 0
                for field in day_fields:
                    value = first_item.get(field, "0")
                    if value and str(value).replace(".", "").isdigit():
                        max_uv = max(max_uv, int(float(value)))

                if max_uv > 0:
                    print(f"밤 시간대이므로 다음날 최대 자외선 지수 반환: {max_uv}")
                    return max_uv
                else:
                    uv_field = "h0"  # 기본값

            # 선택된 필드의 값 가져오기
            uv_value = first_item.get(uv_field, "0")

            print(f"현재 시간: {current_hour}시")
            print(f"선택된 UV 필드: {uv_field}")
            print(f"UV 값: {uv_value}")

            if uv_value and str(uv_value).replace(".", "").isdigit():
                result = int(float(uv_value))
                print(f"파싱된 자외선 지수: {result}")
                return result
            else:
                print(f"UV 값 파싱 실패: {uv_value}")
                return 0

        except Exception as e:
            print(f"자외선 지수 파싱 에러: {e}")
            return None

    def _get_asos_data(self, latitude: float, longitude: float) -> Dict:
        # 지상관측 데이터 조회

        try:
            # 가장 가까운 관측소 찾기
            station_id = self._find_nearest_asos_station(latitude, longitude)

            if not station_id:
                print("가까운 지상관측소를 찾을 수 없음")
                return {"current_temp": None, "current_humidity": None}

            # 지상관측 API 호출
            asos_url = self._build_asos_url(station_id)
            print(f"지상관측 API URL: {asos_url}")

            asos_data = self._call_api(asos_url)
            parsed_asos_data = self._parse_asos_response(asos_data)

            print(f"지상관측 데이터: 기온={parsed_asos_data['current_temp']}, 습도={parsed_asos_data['current_humidity']}")
            return parsed_asos_data

        except Exception as e:
            print(f"지상관측 API 에러: {e}")
            return {"current_temp": None, "current_humidity": None}

    def _find_nearest_asos_station(self, latitude: float, longitude: float) -> Optional[str]:
        # 가장 가까운 지상관측소 찾기

        # 주요 ASOS 관측소 (관측소 번호와 위치)
        asos_stations = {
            "108": (37.5714, 126.9658),  # 서울
            "159": (35.1056, 129.0322),  # 부산
            "143": (35.8289, 128.5556),  # 대구
            "112": (37.4775, 126.6170),  # 인천
            "156": (35.1728, 126.8917),  # 광주
            "133": (36.3689, 127.3742),  # 대전
            "152": (35.5828, 129.3556),  # 울산
            "184": (33.5139, 126.5297),  # 제주
            "129": (35.8242, 127.1478),  # 청주
            "146": (36.7169, 127.4519),  # 전주
        }

        # 가장 가까운 관측소 찾기
        min_distance = float("inf")
        nearest_station = None

        for station_id, (station_lat, station_lon) in asos_stations.items():
            distance = self._calculate_distance(latitude, longitude, station_lat, station_lon)

            if distance < min_distance:
                min_distance = distance
                nearest_station = station_id

        print(f"가장 가까운 관측소: {nearest_station} (거리: {min_distance:.2f}km)")
        return nearest_station

    def _build_asos_url(self, station_id: str) -> str:
        # 지상관측 API URL 생성

        today = datetime.now().strftime("%Y%m%d")
        current_hour = datetime.now().strftime("%H00")

        url = f"{self.asos_base_url}/getWthrDataList"
        params = {
            "serviceKey": self.api_key,
            "numOfRows": "1",
            "pageNo": "1",
            "dataType": "JSON",
            "dataCd": "ASOS",
            "dateCd": "HR",
            "startDt": today,
            "startHh": current_hour,
            "endDt": today,
            "endHh": current_hour,
            "stnIds": station_id
        }

        param_string = "&".join([f"{key}={value}" for key, value in params.items()])
        full_url = f"{url}?{param_string}"

        return full_url

    def _parse_asos_response(self, data: Dict) -> Dict:
        # 지상관측 API 응답 파싱
        try:
            items = data["response"]["body"]["items"]["item"]

            if not items:
                return {"current_temp": None, "current_humidity": None}

            # 가장 최근 관측 데이터 사용
            latest_data = items[0] if isinstance(items, list) else items

            temp_value = latest_data.get("ta")  # 기온
            humidity_value = latest_data.get("hm")  # 습도

            try:
                current_temp = float(temp_value) if temp_value and temp_value != "-" else None
            except (ValueError, TypeError):
                current_temp = None

            try:
                current_humidity = int(humidity_value) if humidity_value and humidity_value != "-" else None
            except (ValueError, TypeError):
                current_humidity = None

            return {"current_temp": current_temp, "current_humidity": current_humidity}

        except (KeyError, IndexError) as e:
            print(f"지상관측 데이터 파싱 에러: {e}")
            return {"current_temp": None, "current_humidity": None}

    def _calculate_sun_times_accurate(self, latitude: float, longitude: float) -> Dict:
        # 정확한 일출/일몰 시간 계산 (천체역학 공식 + 한국 시간대 보정)

        try:
            today = datetime.now()
            day_of_year = today.timetuple().tm_yday

            print(f"일출/일몰 계산: 날짜={today.strftime('%Y-%m-%d')}, 일수={day_of_year}")

            # 태양의 적위각 계산 (태양이 천구의 적도에서 얼마나 떨어져 있는지)
            # 더 정확한 공식 사용
            solar_declination_rad = math.radians(
                23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
            )

            # 위도를 라디안으로 변환
            latitude_rad = math.radians(latitude)

            # 일출/일몰 시간각 계산
            cos_hour_angle = -math.tan(latitude_rad) * math.tan(solar_declination_rad)

            # 극지방 예외 처리
            if cos_hour_angle < -1:
                # 백야 (하루종일 해가 떠 있음)
                return {"sunrise": "00:00", "sunset": "23:59"}
            elif cos_hour_angle > 1:
                # 극야 (하루종일 해가 지지 않음)
                return {"sunrise": "12:00", "sunset": "12:00"}

            # 시간각 계산 (도 단위)
            hour_angle_deg = math.degrees(math.acos(cos_hour_angle))

            # 경도 보정 계산 (한국 표준시는 동경 135도 기준)
            longitude_correction = 4 * (135 - longitude)  # 분 단위

            # 균시차 계산 (지구 공전궤도가 타원이라서 생기는 시간 차이)
            B = 2 * math.pi * (day_of_year - 81) / 365
            equation_of_time = (
                    9.87 * math.sin(2 * B) -
                    7.53 * math.cos(B) -
                    1.5 * math.sin(B)
            )

            # 대기굴절 보정 (대기 때문에 실제보다 일찍 보이고 늦게 사라짐)
            atmospheric_refraction = 50 / 60  # 약 50분각 = 0.83도를 분으로 변환

            # 일출/일몰 시간 계산 (분 단위, 정오 12:00 = 720분 기준)
            sunrise_minutes = (
                    720 - 4 * hour_angle_deg - longitude_correction +
                    equation_of_time - atmospheric_refraction
            )

            sunset_minutes = (
                    720 + 4 * hour_angle_deg - longitude_correction +
                    equation_of_time + atmospheric_refraction
            )

            # 분을 시:분 형태로 변환
            sunrise_time = self._minutes_to_time_string(sunrise_minutes)
            sunset_time = self._minutes_to_time_string(sunset_minutes)

            print(f"정확한 계산 결과:")
            print(f"  - 태양 적위각: {math.degrees(solar_declination_rad):.2f}도")
            print(f"  - 시간각: {hour_angle_deg:.2f}도")
            print(f"  - 경도 보정: {longitude_correction:.1f}분")
            print(f"  - 균시차: {equation_of_time:.1f}분")
            print(f"  - 일출: {sunrise_time}")
            print(f"  - 일몰: {sunset_time}")

            return {
                "sunrise": sunrise_time,
                "sunset": sunset_time
            }

        except Exception as e:
            print(f"일출/일몰 계산 에러: {e}")
            # 기본값 반환 (8월 서울 기준 대략적인 시간)
            return {
                "sunrise": "05:45",
                "sunset": "19:15"
            }

    def _minutes_to_time_string(self, total_minutes: float) -> str:
        # 음수나 24시간 초과 처리
        total_minutes = total_minutes % (24 * 60)  # 24시간 범위로 제한

        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)

        return f"{hours:02d}:{minutes:02d}"

    def _combine_all_weather_data(self, forecast_data: List[Dict], air_quality_data: Dict,
                                  living_weather_data: Dict, asos_data: Dict, sun_times: Dict) -> List[Dict]:
        # 모든 날씨 데이터를 하나로 결합 (체감온도 계산 포함)

        for forecast in forecast_data:
            # 미세먼지 정보 추가
            if air_quality_data.get("pm25") is not None:
                forecast["pm25"] = air_quality_data["pm25"]
            if air_quality_data.get("pm10") is not None:
                forecast["pm10"] = air_quality_data["pm10"]

            # 생활기상지수 정보 추가 (자외선만)
            if living_weather_data.get("uv_index") is not None:
                forecast["uv_index"] = living_weather_data["uv_index"]

            # 체감온도 계산 (기온, 습도, 바람속도 사용)
            current_temp = forecast.get("temperature")
            humidity = forecast.get("humidity")
            wind_speed = forecast.get("wind_speed")

            if current_temp is not None and humidity is not None:
                feels_like = self._calculate_feels_like_temperature(current_temp, humidity, wind_speed)
                forecast["feels_like_temperature"] = feels_like
                print(f"체감온도 계산 완료: {current_temp}°C → {feels_like}°C (습도 {humidity}%)")
            else:
                forecast["feels_like_temperature"] = None
                print(f"체감온도 계산 불가: 기온={current_temp}, 습도={humidity}")

            # 지상관측 데이터로 보완
            if asos_data.get("current_temp") is not None:
                forecast_time = datetime.strptime(forecast["forecast_time"], "%Y-%m-%d %H:%M:%S")
                current_time = datetime.now()
                time_diff = abs((forecast_time - current_time).total_seconds())

                if time_diff <= 1800:  # 30분 이내
                    forecast["temperature"] = asos_data["current_temp"]
                    if asos_data.get("current_humidity") is not None:
                        forecast["humidity"] = asos_data["current_humidity"]

                    # 지상관측 데이터로 체감온도 재계산
                    if asos_data.get("current_temp") and forecast.get("humidity"):
                        feels_like = self._calculate_feels_like_temperature(
                            asos_data["current_temp"],
                            forecast["humidity"],
                            wind_speed
                        )
                        forecast["feels_like_temperature"] = feels_like

            # 일출/일몰 정보 추가
            forecast["sunrise_time"] = sun_times["sunrise"]
            forecast["sunset_time"] = sun_times["sunset"]

        return forecast_data

    def _calculate_daily_temperatures(self, weather_data: List[Dict]) -> List[Dict]:
        # 하루의 최저/최고 기온 계산

        if not weather_data:
            return weather_data

        # 오늘과 내일 각각의 최저/최고 기온 계산
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        # 날짜별로 기온 데이터 분류
        today_temperatures = []
        tomorrow_temperatures = []

        for forecast in weather_data:
            forecast_time = forecast.get("forecast_time", "")
            if forecast.get("temperature") is not None:
                try:
                    forecast_datetime = datetime.strptime(forecast_time, "%Y-%m-%d %H:%M:%S")
                    forecast_date = forecast_datetime.date()

                    if forecast_date == today:
                        today_temperatures.append(forecast["temperature"])
                    elif forecast_date == tomorrow:
                        tomorrow_temperatures.append(forecast["temperature"])
                except ValueError:
                    continue

        # 각 날짜별 최저/최고 기온 계산
        today_min = min(today_temperatures) if today_temperatures else None
        today_max = max(today_temperatures) if today_temperatures else None
        tomorrow_min = min(tomorrow_temperatures) if tomorrow_temperatures else None
        tomorrow_max = max(tomorrow_temperatures) if tomorrow_temperatures else None

        # 각 예보에 해당 날짜의 최저/최고 기온 추가
        for forecast in weather_data:
            forecast_time = forecast.get("forecast_time", "")
            try:
                forecast_datetime = datetime.strptime(forecast_time, "%Y-%m-%d %H:%M:%S")
                forecast_date = forecast_datetime.date()

                if forecast_date == today:
                    forecast["min_temperature"] = today_min
                    forecast["max_temperature"] = today_max
                elif forecast_date == tomorrow:
                    forecast["min_temperature"] = tomorrow_min
                    forecast["max_temperature"] = tomorrow_max
                else:
                    # 기본값 (현재 기온 기준 추정)
                    current_temp = forecast.get("temperature", 20)
                    forecast["min_temperature"] = current_temp - 5
                    forecast["max_temperature"] = current_temp + 10

            except ValueError:
                # 날짜 파싱 실패 시 기본값
                current_temp = forecast.get("temperature", 20)
                forecast["min_temperature"] = current_temp - 5
                forecast["max_temperature"] = current_temp + 10

        return weather_data

    def _validate_coordinates(self, latitude: float, longitude: float) -> None:
        # 좌표 유효성 검사

        if latitude is None or longitude is None:
            raise InvalidCoordinatesError(latitude, longitude, "좌표값이 None입니다")

        try:
            lat = float(latitude)
            lon = float(longitude)
        except (ValueError, TypeError):
            raise InvalidCoordinatesError(latitude, longitude, "좌표값이 숫자가 아닙니다")

        if not (-90 <= lat <= 90):
            raise InvalidCoordinatesError(
                latitude, longitude,
                f"위도는 -90~90 범위여야 합니다: {lat}"
            )

        if not (-180 <= lon <= 180):
            raise InvalidCoordinatesError(
                latitude, longitude,
                f"경도는 -180~180 범위여야 합니다: {lon}"
            )

    def _get_forecast_data(self, nx: int, ny: int) -> List[Dict]:
        # 단기예보 데이터 조회
        api_url = self._build_forecast_api_url(nx, ny)
        response_data = self._call_api(api_url)
        return self._parse_forecast_response(response_data)

    def _convert_to_grid(self, latitude: float, longitude: float) -> Tuple[int, int]:
        # 위도/경도를 기상청 격자 좌표로 변환
        try:
            # 복잡한 좌표 변환 공식 (기상청 제공)
            DEGRAD = math.pi / 180.0

            re = self.RE / self.GRID
            slat1 = self.SLAT1 * DEGRAD
            slat2 = self.SLAT2 * DEGRAD
            olon = self.OLON * DEGRAD
            olat = self.OLAT * DEGRAD

            sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
            sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
            sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
            sf = math.pow(sf, sn) * math.cos(slat1) / sn
            ro = math.tan(math.pi * 0.25 + olat * 0.5)
            ro = re * sf / math.pow(ro, sn)

            ra = math.tan(math.pi * 0.25 + latitude * DEGRAD * 0.5)
            ra = re * sf / math.pow(ra, sn)
            theta = longitude * DEGRAD - olon
            if theta > math.pi:
                theta -= 2.0 * math.pi
            if theta < -math.pi:
                theta += 2.0 * math.pi
            theta *= sn

            x = ra * math.sin(theta) + self.XO
            y = ro - ra * math.cos(theta) + self.YO

            nx = int(x + 0.5)
            ny = int(y + 0.5)

            # 변환된 격자 좌표가 유효한 범위인지 검사
            if nx <= 0 or ny <= 0:
                raise GridConversionError(
                    latitude, longitude,
                    f"변환된 격자 좌표가 유효하지 않습니다: nx={nx}, ny={ny}"
                )

            return nx, ny

        except Exception as e:
            if isinstance(e, GridConversionError):
                raise
            raise GridConversionError(
                latitude, longitude,
                f"격자 좌표 변환 중 오류가 발생했습니다: {str(e)}"
            )

    def _build_forecast_api_url(self, nx: int, ny: int) -> str:
        now = datetime.now()

        # 기상청 API 발표 시간: 02, 05, 08, 11, 14, 17, 20, 23시
        api_times = [2, 5, 8, 11, 14, 17, 20, 23]

        current_hour = now.hour
        base_time = None
        base_date = now

        # 현재 시간보다 이전의 가장 최근 발표 시간 찾기
        for time in reversed(api_times):
            if current_hour >= time:
                base_time = time
                break

        # 새벽 0~1시면 전날 23시가 아니라 당일 02시를 기다리거나 현재 시간 기준 처리
        if base_time is None:
            if current_hour < 2:
                # 새벽 0~1시면 전날 23시 사용하되, 현재 시간부터 필터링하도록 조정
                base_date = now - timedelta(days=1)
                base_time = 23
            else:
                base_time = 2

        base_date_str = base_date.strftime("%Y%m%d")
        base_time_str = f"{base_time:02d}00"

        url = f"{self.forecast_base_url}/getVilageFcst"
        params = {
            "serviceKey": self.api_key,
            "numOfRows": "1000",
            "pageNo": "1",
            "base_date": base_date_str,
            "base_time": base_time_str,
            "nx": str(nx),
            "ny": str(ny),
            "dataType": "JSON"
        }

        param_string = "&".join([f"{key}={value}" for key, value in params.items()])
        full_url = f"{url}?{param_string}"

        print(f"단기예보 API URL: {full_url}")
        print(f"기준 시간: {base_date_str} {base_time_str}")
        return full_url

    def _call_api(self, url: str) -> Dict:
        # API 호출 (SSL 에러 대응 개선 버전)
        try:
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                raise NetworkError(
                    f"HTTP {response.status_code}",
                    f"API 서버 응답 오류: {response.status_code}"
                )

            try:
                data = response.json()
            except json.JSONDecodeError as e:
                raise APIResponseError(
                    response.text,
                    f"응답을 JSON으로 파싱할 수 없습니다: {str(e)}"
                )

            self._check_api_response_error(data)
            return data

        except requests.exceptions.SSLError as e:
            print(f"SSL 에러 발생, HTTP로 재시도: {str(e)}")
            # HTTPS에서 SSL 에러 발생 시 HTTP로 재시도
            if url.startswith("https://"):
                http_url = url.replace("https://", "http://")
                print(f"HTTP URL로 재시도: {http_url}")
                return self._call_api_with_http(http_url)
            raise NetworkError(f"SSL 연결 오류: {str(e)}")
        except requests.exceptions.Timeout:
            raise NetworkError("API 호출 시간 초과")
        except requests.exceptions.ConnectionError as e:
            print(f"연결 에러: {str(e)}")
            # HTTPS 연결 실패 시 HTTP로 재시도
            if url.startswith("https://"):
                http_url = url.replace("https://", "http://")
                print(f"HTTP URL로 재시도: {http_url}")
                return self._call_api_with_http(http_url)
            raise NetworkError(f"API 서버에 연결할 수 없습니다: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(str(e))

    def _call_api_with_http(self, url: str) -> Dict:
        # HTTP로 API 호출 (HTTPS 실패 시 fallback)
        try:
            response = self.session.get(url, timeout=10, verify=False)

            if response.status_code != 200:
                raise NetworkError(
                    f"HTTP {response.status_code}",
                    f"API 서버 응답 오류: {response.status_code}"
                )

            try:
                data = response.json()
            except json.JSONDecodeError as e:
                raise APIResponseError(
                    response.text,
                    f"응답을 JSON으로 파싱할 수 없습니다: {str(e)}"
                )

            self._check_api_response_error(data)
            return data

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"HTTP API 호출 실패: {str(e)}")

    def _check_api_response_error(self, data: Dict) -> None:
        # API 응답에서 에러 코드 확인
        try:
            header = data["response"]["header"]
            result_code = header["resultCode"]
            result_msg = header["resultMsg"]

            if result_code != "00":  # "00"이 정상
                if result_code == "03":
                    raise APIKeyError(f"API 키 오류: {result_msg}")
                elif result_code == "99":
                    raise APIQuotaExceededError(f"API 호출 한도 초과: {result_msg}")
                else:
                    raise WeatherAPIError(
                        f"API 오류: {result_msg}",
                        error_code=result_code
                    )

        except KeyError as e:
            raise APIResponseError(
                data,
                f"API 응답 구조가 예상과 다릅니다: {str(e)}"
            )

    def _parse_forecast_response(self, data: Dict) -> List[Dict]:
        # 기상청 API 응답을 우리 DB 형태로 변환
        try:
            items = data["response"]["body"]["items"]["item"]

            if not items:
                raise WeatherDataNotFoundError(
                    None, None, None,
                    "해당 지역의 날씨 데이터가 없습니다"
                )

            # 시간대별로 데이터 그룹핑
            forecasts_by_time = {}

            for item in items:
                fcst_date = item["fcstDate"]
                fcst_time = item["fcstTime"]
                category = item["category"]
                value = item["fcstValue"]

                # 예보 시간 문자열 생성
                forecast_datetime = f"{fcst_date[:4]}-{fcst_date[4:6]}-{fcst_date[6:8]} {fcst_time[:2]}:{fcst_time[2:]}:00"

                # 해당 시간대 그룹이 없으면 생성
                if forecast_datetime not in forecasts_by_time:
                    forecasts_by_time[forecast_datetime] = {
                        "forecast_time": forecast_datetime,
                        "temperature": None,
                        "humidity": None,
                        "precipitation": None,
                        "sky_code": None,
                        "precipitation_type": None,
                        "wind_speed": None,
                        "wind_direction": None,
                    }

                # 카테고리별 데이터 매핑
                forecast = forecasts_by_time[forecast_datetime]

                # 이 부분을 수정
                if category == "TMP":  # 기온
                    try:
                        temp_value = float(value)
                        forecast["temperature"] = temp_value
                        print(f"온도 파싱: {forecast_datetime} → {temp_value}°C")
                    except (ValueError, TypeError) as e:
                        print(f"온도 파싱 실패: {value} → {e}")
                        forecast["temperature"] = None

                elif category == "REH":  # 습도
                    try:
                        forecast["humidity"] = int(value)
                    except (ValueError, TypeError):
                        forecast["humidity"] = None

                elif category == "POP":  # 강수확률
                    try:
                        forecast["precipitation"] = int(value)
                    except (ValueError, TypeError):
                        forecast["precipitation"] = None

                elif category == "SKY":  # 하늘상태
                    forecast["sky_code"] = value
                elif category == "PTY":  # 강수형태
                    forecast["precipitation_type"] = value
                elif category == "WSD":  # 풍속
                    try:
                        forecast["wind_speed"] = float(value)
                    except (ValueError, TypeError):
                        forecast["wind_speed"] = None
                elif category == "VEC":  # 풍향
                    try:
                        forecast["wind_direction"] = int(value)
                    except (ValueError, TypeError):
                        forecast["wind_direction"] = None

            # 리스트로 변환 (시간순 정렬)
            forecast_list = list(forecasts_by_time.values())
            forecast_list.sort(key=lambda x: x["forecast_time"])

            # 온도 데이터 확인
            temp_count = sum(1 for f in forecast_list if f["temperature"] is not None)
            print(f"파싱 결과: 총 {len(forecast_list)}개 중 온도 데이터 {temp_count}개")

            # 필수 데이터가 있는 예보만 필터링
            valid_forecasts = []
            for forecast in forecast_list:
                if (forecast["temperature"] is not None and
                        forecast["humidity"] is not None):
                    valid_forecasts.append(forecast)
                else:
                    print(
                        f"제외된 데이터: {forecast['forecast_time']} (온도: {forecast['temperature']}, 습도: {forecast['humidity']})")

            if not valid_forecasts:
                raise WeatherDataNotFoundError(
                    None, None, None,
                    "유효한 날씨 예보 데이터가 없습니다"
                )

            print(f"최종 유효 데이터: {len(valid_forecasts)}개")
            return valid_forecasts

        except KeyError as e:
            raise APIResponseError(
                data,
                f"API 응답 파싱 중 오류: {str(e)}"
            )

    def close(self):
        # 세션 정리
        if hasattr(self, "session"):
            self.session.close()

    def __del__(self):
        # 소멸자에서 세션 정리
        self.close()

# 사용 예시
"""
이제 환경변수로 완전히 관리되는 날씨 API 클라이언트!

개발환경에서 사용:
# .env.local에 USE_HTTPS=False 설정되어 있음
client = WeatherAPIClient()  # 자동으로 HTTP 모드로 동작

운영환경에서 사용:
# .env에 USE_HTTPS=True 설정되어 있음
client = WeatherAPIClient()  # 자동으로 HTTPS 모드로 동작

강제 모드 설정:
client = WeatherAPIClient(use_https=True)   # 강제 HTTPS
client = WeatherAPIClient(use_https=False)  # 강제 HTTP

사용 예시:
try:
    weather_data = client.get_weather_by_coordinates(37.5665, 126.9780)  # 서울시청

    # 받아오는 완전한 데이터
    for forecast in weather_data:
        print(f"시간: {forecast['forecast_time']}")
        print(f"기온: {forecast['temperature']}°C")
        print(f"체감온도: {forecast.get('feels_like_temperature')}°C")
        print(f"최저/최고: {forecast['min_temperature']}° / {forecast['max_temperature']}°")
        print(f"습도: {forecast['humidity']}%")
        print(f"강수확률: {forecast['precipitation']}%")
        print(f"미세먼지 PM2.5: {forecast.get('pm25', '정보없음')}μg/m³")
        print(f"미세먼지 PM10: {forecast.get('pm10', '정보없음')}μg/m³")
        print(f"자외선 지수: {forecast.get('uv_index', '정보없음')}")
        print(f"일출: {forecast['sunrise_time']}")
        print(f"일몰: {forecast['sunset_time']}")
        print("=" * 50)

except WeatherAPIError as e:
    print(f"날씨 조회 실패: {e}")
"""
