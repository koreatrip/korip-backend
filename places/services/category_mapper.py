# 투어 API 신분류 코드와 지역 코드를 우리 카테고리/지역으로 매핑하는 로직


from typing import Dict, Optional, Tuple
from categories.models import Category, SubCategory
from regions.models import Region, SubRegion


class CategoryMapper:
    def __init__(self):
        self.category_mapping = {
            # 자연 관련 (NA, VN)
            "NA": "자연",
            "NA01": "자연",
            "NA010100": "자연",
            "NA010200": "자연",
            "NA010300": "자연",
            "NA010400": "자연",
            "NA010500": "자연",
            "NA02": "자연",
            "NA020100": "자연",
            "NA020200": "자연",
            "NA020300": "자연",
            "NA020400": "자연",
            "NA020500": "자연",
            "NA020600": "자연",
            "NA020700": "자연",
            "NA020800": "자연",
            "NA020900": "자연",
            "NA03": "자연",
            "NA030100": "자연",
            "NA030200": "자연",
            "NA030300": "자연",
            "NA030400": "자연",
            "NA030500": "자연",
            "NA04": "자연",
            "NA040100": "자연",
            "NA040200": "자연",
            "NA040300": "자연",
            "NA040400": "자연",
            "NA040500": "자연",
            "NA040600": "자연",
            "NA040700": "자연",
            "NA05": "자연",
            "NA050100": "자연",
            "VN": "자연",
            "VN01": "자연",
            "VN010100": "자연",
            "VN010200": "자연",
            "VN010300": "자연",
            "VN010400": "자연",
            "VN010500": "자연",
            "VN010600": "자연",
            "VN010700": "자연",
            "VN010800": "자연",
            "VN010900": "자연",
            "A01": "자연",
            "A0101": "자연",
            "A01011300": "자연",

            # 문화 관련 (VE, EV, HS, A02, C01)
            "VE": "문화",
            "VE01": "문화",
            "VE02": "문화",
            "VE03": "문화",
            "VE04": "문화",
            "VE05": "문화",
            "VE06": "문화",
            "VE07": "문화",
            "VE08": "문화",
            "VE09": "문화",
            "VE10": "문화",
            "VE010100": "문화",
            "VE010200": "문화",
            "VE010300": "문화",
            "VE010400": "문화",
            "VE030500": "문화",
            "VE040100": "문화",
            "VE050100": "문화",
            "VE050200": "문화",
            "VE060100": "문화",
            "VE060200": "문화",
            "VE070100": "문화",
            "VE070200": "문화",
            "VE070300": "문화",
            "VE070400": "문화",
            "VE070500": "문화",
            "VE070600": "문화",
            "VE080600": "문화",
            "VE090100": "문화",
            "VE090200": "문화",
            "VE090300": "문화",
            "VE090400": "문화",
            "VE090500": "문화",
            "VE090600": "문화",
            "VE100100": "문화",
            "VE100200": "문화",
            "EV": "문화",
            "EV01": "문화",
            "EV02": "문화",
            "HS": "문화",
            "HS02": "문화",
            "HS020100": "문화",
            "A02": "문화",
            "A0205": "문화",
            "A02050200": "문화",
            "A02050300": "문화",
            "C01": "문화",

            # 음식 관련 (FD, A05)
            "FD": "음식",
            "FD01": "음식",
            "FD02": "음식",
            "FD03": "음식",
            "FD04": "음식",
            "FD05": "음식",
            "FD010100": "음식",
            "FD010200": "음식",
            "FD010300": "음식",
            "FD010400": "음식",
            "A05": "음식",
            "A0501": "음식",
            "A0502": "음식",
            "A05020100": "음식",

            # 액티비티 관련 (RS, EX, LS)
            "RS": "액티비티",
            "RS01": "액티비티",
            "RS02": "액티비티",
            "RS03": "액티비티",
            "RS030100": "액티비티",
            "RS030200": "액티비티",
            "RS030300": "액티비티",
            "RS04": "액티비티",
            "RS040100": "액티비티",
            "RS040200": "액티비티",
            "EX": "액티비티",
            "LS": "액티비티",

            # 쇼핑 관련 (SH)
            "SH": "쇼핑",
            "SH01": "쇼핑",
            "SH010100": "쇼핑",
            "SH010200": "쇼핑",
            "SH010300": "쇼핑",
            "SH010400": "쇼핑",
            "SH010500": "쇼핑",
            "SH02": "쇼핑",  # 쇼핑몰 추가
            "SH020100": "쇼핑",  # 복합쇼핑몰
            "SH020200": "쇼핑",  # 아웃렛
            "SH03": "쇼핑",  # 대형마트 추가
            "SH030100": "쇼핑",
            "SH04": "쇼핑",  # 면세점 추가
            "SH040100": "쇼핑",  # 공항면세점
            "SH040200": "쇼핑",  # 시내면세점

            # 숙박 관련 (AC)
            "AC": "숙박",
            "AC01": "숙박",
            "AC010100": "숙박",
            "AC02": "숙박",
            "AC020100": "숙박",
            "AC020200": "숙박",
            "AC03": "숙박",
            "AC030100": "숙박",
            "AC030200": "숙박",
            "AC030300": "숙박",
            "AC030400": "숙박",
            "AC04": "숙박",
            "AC040100": "숙박",
            "AC05": "숙박",
            "AC050100": "숙박",
            "AC050200": "숙박",
            "AC050300": "숙박",
            "AC050400": "숙박",
            "AC06": "숙박",
            "AC060100": "숙박",
            "AC060200": "숙박",
        }

        self.subcategory_mapping = {
            # === 문화 서브카테고리 확장 ===
            "VE070100": ("문화", "박물관"),
            "VE070200": ("문화", "박물관"),  # 전문박물관
            "VE070300": ("문화", "박물관"),  # 기념관
            "VE070400": ("문화", "박물관"),  # 전시관
            "VE070500": ("문화", "박물관"),  # 기타박물관
            "VE070600": ("문화", "미술관"),
            "VE01": ("문화", "역사"),
            "VE010100": ("문화", "역사"),   # 궁궐
            "VE010200": ("문화", "역사"),   # 유적지
            "VE010300": ("문화", "역사"),   # 문화재
            "VE010400": ("문화", "역사"),   # 사찰
            "VE02": ("문화", "전통문화"),
            "VE03": ("문화", "전통문화"),   # 전통체험
            "VE05": ("문화", "복합관광시설"),
            "VE050100": ("문화", "복합관광시설"),
            "VE050200": ("문화", "복합관광시설"),
            "VE06": ("문화", "공연시설"),
            "VE060100": ("문화", "공연시설"),  # 공연장
            "VE060200": ("문화", "공연시설"),  # 아트홀 추가
            "VE07": ("문화", "박물관"),
            "VE08": ("문화", "미술관"),       # 갤러리 등
            "VE080600": ("문화", "미술관"),
            "VE09": ("문화", "전통문화"),     # 전통시장 등
            "VE090100": ("문화", "전통문화"),
            "VE090200": ("문화", "전통문화"),
            "VE090300": ("문화", "전통문화"),
            "VE090400": ("문화", "전통문화"),
            "VE090500": ("문화", "전통문화"),
            "VE090600": ("문화", "전통문화"),
            "VE10": ("문화", "복합관광시설"), # 관광특구
            "VE100100": ("문화", "복합관광시설"),
            "VE100200": ("문화", "복합관광시설"),
            "EV01": ("문화", "축제"),
            "EV02": ("문화", "공연"),
            "HS02": ("문화", "역사"),        # 종교시설
            "HS020100": ("문화", "역사"),
            "A02": ("문화", "역사"),
            "A0205": ("문화", "역사"),
            "A02050200": ("문화", "역사"),
            "A02050300": ("문화", "역사"),
            "C01": ("문화", "축제"),         # 문화관광축제

            # === 음식 서브카테고리 확장 ===
            "FD01": ("음식", "한식"),
            "FD010100": ("음식", "한식"),   # 한정식
            "FD010200": ("음식", "한식"),   # 백반/한정식
            "FD010300": ("음식", "한식"),   # 떡/한과
            "FD010400": ("음식", "한식"),   # 기타한식
            "FD02": ("음식", "일식"),
            "FD03": ("음식", "중식"),
            "FD04": ("음식", "양식"),
            "FD05": ("음식", "카페"),       # 카페 추가
            "A05": ("음식", "한식"),        # 기본 음식점
            "A0501": ("음식", "한식"),      # 한식
            "A0502": ("음식", "카페"),      # 카페/찻집 추가
            "A05020100": ("음식", "카페"),  # 찻집

            # === 자연 서브카테고리 확장 ===
            "VN010400": ("자연", "산"),
            "VN010800": ("자연", "바다"),
            "VN010500": ("자연", "강"),
            "VN010600": ("자연", "호수"),
            "VN010700": ("자연", "계곡"),
            "VN010100": ("자연", "공원"),
            "VN010200": ("자연", "공원"),
            "VN010300": ("자연", "공원"),
            "VN010900": ("자연", "바다"),   # 해수욕장
            "NA01": ("자연", "산"),         # 산
            "NA010100": ("자연", "산"),     # 국립공원(산)
            "NA010200": ("자연", "산"),     # 도립공원(산)
            "NA010300": ("자연", "산"),     # 군립공원(산)
            "NA010400": ("자연", "산"),     # 산
            "NA010500": ("자연", "강"),     # 계곡
            "NA02": ("자연", "바다"),       # 자연관광지(해변)
            "NA020100": ("자연", "강"),     # 강
            "NA020200": ("자연", "호수"),   # 호수
            "NA020300": ("자연", "계곡"),   # 계곡
            "NA020400": ("자연", "강"),     # 폭포
            "NA020500": ("자연", "바다"),   # 해변
            "NA020600": ("자연", "바다"),   # 바다
            "NA020700": ("자연", "바다"),   # 해안절경
            "NA020800": ("자연", "바다"),   # 해수욕장
            "NA020900": ("자연", "바다"),   # 섬
            "NA03": ("자연", "바다"),       # 온천
            "NA030100": ("자연", "바다"),   # 온천
            "NA030200": ("자연", "바다"),   # 해수온천
            "NA030300": ("자연", "바다"),   # 스파
            "NA030400": ("자연", "바다"),   # 찜질방
            "NA030500": ("자연", "바다"),   # 기타온천
            "NA04": ("자연", "공원"),       # 자연공원
            "NA040100": ("자연", "공원"),   # 국립공원
            "NA040200": ("자연", "공원"),   # 도립공원
            "NA040300": ("자연", "공원"),   # 군립공원
            "NA040400": ("자연", "공원"),   # 수변공원
            "NA040500": ("자연", "공원"),   # 생태관광지
            "NA040600": ("자연", "공원"),   # 자연휴양림
            "NA040700": ("자연", "공원"),   # 수목원/정원
            "NA05": ("자연", "공원"),       # 기타자연관광
            "NA050100": ("자연", "공원"),
            "A01": ("자연", "공원"),        # 자연관광지
            "A0101": ("자연", "공원"),
            "A01011300": ("자연", "공원"),

            # === 액티비티 서브카테고리 확장 ===
            "RS01": ("액티비티", "등산"),     # 산/등산
            "RS02": ("액티비티", "수상스포츠"), # 해수욕장/수상스포츠
            "RS03": ("액티비티", "동물원"),   # 동물원/수족관
            "RS030100": ("액티비티", "동물원"),
            "RS030200": ("액티비티", "수족관"),
            "RS030300": ("액티비티", "농장"),  # 농장체험
            "RS04": ("액티비티", "테마파크"), # 테마파크
            "RS040100": ("액티비티", "테마파크"),
            "RS040200": ("액티비티", "놀이공원"),
            "EX": ("액티비티", "체험"),       # 체험관광
            "LS": ("액티비티", "스포츠"),     # 레포츠

            # === 쇼핑 서브카테고리 확장 ===
            "SH01": ("쇼핑", "백화점"),      # 백화점
            "SH010100": ("쇼핑", "백화점"),
            "SH010200": ("쇼핑", "면세점"),  # 기존 매핑 수정
            "SH010300": ("쇼핑", "면세점"),
            "SH010400": ("쇼핑", "아울렛"),
            "SH010500": ("쇼핑", "기념품"),
            "SH02": ("쇼핑", "쇼핑몰"),      # 쇼핑몰 추가
            "SH020100": ("쇼핑", "쇼핑몰"),  # 복합쇼핑몰
            "SH020200": ("쇼핑", "아울렛"),  # 아웃렛
            "SH03": ("쇼핑", "마트"),        # 대형마트 추가
            "SH030100": ("쇼핑", "마트"),
            "SH04": ("쇼핑", "면세점"),      # 면세점 확장
            "SH040100": ("쇼핑", "면세점"),  # 공항면세점
            "SH040200": ("쇼핑", "면세점"),  # 시내면세점 (Tax Refund Shop 포함!)

            # === 숙박 서브카테고리 확장 ===
            "AC01": ("숙박", "호텔"),
            "AC010100": ("숙박", "호텔"),
            "AC02": ("숙박", "리조트"),      # 콘도미니엄 → 리조트로 매핑
            "AC020100": ("숙박", "리조트"),  # 콘도 → 리조트로 매핑
            "AC020200": ("숙박", "리조트"),  # 레지던스 → 리조트로 매핑
            "AC03": ("숙박", "펜션"),
            "AC030100": ("숙박", "펜션"),
            "AC030200": ("숙박", "펜션"),    # 한옥스테이 → 펜션으로 매핑
            "AC030300": ("숙박", "펜션"),    # 농어촌민박 → 펜션으로 매핑
            "AC030400": ("숙박", "펜션"),    # 홈스테이 → 펜션으로 매핑
            "AC04": ("숙박", "모텔"),
            "AC040100": ("숙박", "모텔"),
            "AC05": ("숙박", "캠핑"),        # 캠핑 별도 카테고리
            "AC050100": ("숙박", "캠핑"),    # 일반야영장
            "AC050200": ("숙박", "캠핑"),    # 오토캠핑장
            "AC050300": ("숙박", "캠핑"),    # 카라반
            "AC050400": ("숙박", "캠핑"),    # 글램핑장
            "AC06": ("숙박", "게스트하우스"),
            "AC060100": ("숙박", "게스트하우스"),  # 유스호스텔 → 게스트하우스로 매핑
            "AC060200": ("숙박", "게스트하우스"),
        }

        self.region_mapping = {
            "1": {
                "region_name": "서울특별시",
                "subregions": {
                    "1": "강남구",
                    "2": "강동구",
                    "3": "강북구",
                    "4": "강서구",
                    "5": "관악구",
                    "6": "광진구",
                    "7": "구로구",
                    "8": "금천구",
                    "9": "노원구",
                    "10": "도봉구",
                    "11": "동대문구",
                    "12": "동작구",
                    "13": "마포구",
                    "14": "서대문구",
                    "15": "서초구",
                    "16": "성동구",
                    "17": "성북구",
                    "18": "송파구",
                    "19": "양천구",
                    "20": "영등포구",
                    "21": "용산구",
                    "22": "은평구",
                    "23": "종로구",
                    "24": "중구",
                    "25": "중랑구"
                }
            },
            "2": {
                "region_name": "인천광역시",
                "subregions": {
                    "1": "강화군",
                    "2": "계양구",
                    "3": "미추홀구",
                    "4": "남동구",
                    "5": "동구",
                    "6": "부평구",
                    "7": "서구",
                    "8": "연수구",
                    "9": "옹진군",
                    "10": "중구"
                }
            },
            "3": {
                "region_name": "대전광역시",
                "subregions": {
                    "1": "대덕구",
                    "2": "동구",
                    "3": "서구",
                    "4": "유성구",
                    "5": "중구"
                }
            },
            "4": {
                "region_name": "대구광역시",
                "subregions": {
                    "1": "남구",
                    "2": "달서구",
                    "3": "달성군",
                    "4": "동구",
                    "5": "북구",
                    "6": "서구",
                    "7": "수성구",
                    "8": "중구",
                    "9": "군위군"
                }
            },
            "5": {
                "region_name": "광주광역시",
                "subregions": {
                    "1": "광산구",
                    "2": "남구",
                    "3": "동구",
                    "4": "북구",
                    "5": "서구"
                }
            },
            "6": {
                "region_name": "부산광역시",
                "subregions": {
                    "1": "강서구",
                    "2": "금정구",
                    "3": "기장군",
                    "4": "남구",
                    "5": "동구",
                    "6": "동래구",
                    "7": "부산진구",
                    "8": "북구",
                    "9": "사상구",
                    "10": "사하구",
                    "11": "서구",
                    "12": "수영구",
                    "13": "연제구",
                    "14": "영도구",
                    "15": "중구",
                    "16": "해운대구"
                }
            },
            "7": {
                "region_name": "울산광역시",
                "subregions": {
                    "1": "중구",
                    "2": "남구",
                    "3": "동구",
                    "4": "북구",
                    "5": "울주군"
                }
            },
            "8": {
                "region_name": "세종특별자치시",
                "subregions": {
                    "1": "세종특별자치시"
                }
            },
            "31": {
                "region_name": "경기도",
                "subregions": {
                    "1": "가평군",
                    "2": "고양시",
                    "3": "과천시",
                    "4": "광명시",
                    "5": "광주시",
                    "6": "구리시",
                    "7": "군포시",
                    "8": "김포시",
                    "9": "남양주시",
                    "10": "동두천시",
                    "11": "부천시",
                    "12": "성남시",
                    "13": "수원시",
                    "14": "시흥시",
                    "15": "안산시",
                    "16": "안성시",
                    "17": "안양시",
                    "18": "양주시",
                    "19": "양평군",
                    "20": "여주시",
                    "21": "연천군",
                    "22": "오산시",
                    "23": "용인시",
                    "24": "의왕시",
                    "25": "의정부시",
                    "26": "이천시",
                    "27": "파주시",
                    "28": "평택시",
                    "29": "포천시",
                    "30": "하남시",
                    "31": "화성시"
                }
            },
            "32": {
                "region_name": "강원특별자치도",
                "subregions": {
                    "1": "강릉시",
                    "2": "고성군",
                    "3": "동해시",
                    "4": "삼척시",
                    "5": "속초시",
                    "6": "양구군",
                    "7": "양양군",
                    "8": "영월군",
                    "9": "원주시",
                    "10": "인제군",
                    "11": "정선군",
                    "12": "철원군",
                    "13": "춘천시",
                    "14": "태백시",
                    "15": "평창군",
                    "16": "홍천군",
                    "17": "화천군",
                    "18": "횡성군"
                }
            },
            "33": {
                "region_name": "충청북도",
                "subregions": {
                    "1": "괴산군",
                    "2": "단양군",
                    "3": "보은군",
                    "4": "영동군",
                    "5": "옥천군",
                    "6": "음성군",
                    "7": "제천시",
                    "8": "진천군",
                    "9": "청원군",
                    "10": "청주시",
                    "11": "충주시",
                    "12": "증평군"
                }
            },
            "34": {
                "region_name": "충청남도",
                "subregions": {
                    "1": "공주시",
                    "2": "금산군",
                    "3": "논산시",
                    "4": "당진시",
                    "5": "보령시",
                    "6": "부여군",
                    "7": "서산시",
                    "8": "서천군",
                    "9": "아산시",
                    "11": "예산군",
                    "12": "천안시",
                    "13": "청양군",
                    "14": "태안군",
                    "15": "홍성군",
                    "16": "계룡시"
                }
            },
            "35": {
                "region_name": "경상북도",
                "subregions": {
                    "1": "경산시",
                    "2": "경주시",
                    "3": "고령군",
                    "4": "구미시",
                    "6": "김천시",
                    "7": "문경시",
                    "8": "봉화군",
                    "9": "상주시",
                    "10": "성주군",
                    "11": "안동시",
                    "12": "영덕군",
                    "13": "영양군",
                    "14": "영주시",
                    "15": "영천시",
                    "16": "예천군",
                    "17": "울릉군",
                    "18": "울진군",
                    "19": "의성군",
                    "20": "청도군",
                    "21": "청송군",
                    "22": "칠곡군",
                    "23": "포항시"
                }
            },
            "36": {
                "region_name": "경상남도",
                "subregions": {
                    "1": "거제시",
                    "2": "거창군",
                    "3": "고성군",
                    "4": "김해시",
                    "5": "남해군",
                    "6": "마산시",
                    "7": "밀양시",
                    "8": "사천시",
                    "9": "산청군",
                    "10": "양산시",
                    "12": "의령군",
                    "13": "진주시",
                    "14": "진해시",
                    "15": "창녕군",
                    "16": "창원시",
                    "17": "통영시",
                    "18": "하동군",
                    "19": "함안군",
                    "20": "함양군",
                    "21": "합천군"
                }
            },
            "37": {
                "region_name": "전북특별자치도",
                "subregions": {
                    "1": "고창군",
                    "2": "군산시",
                    "3": "김제시",
                    "4": "남원시",
                    "5": "무주군",
                    "6": "부안군",
                    "7": "순창군",
                    "8": "완주군",
                    "9": "익산시",
                    "10": "임실군",
                    "11": "장수군",
                    "12": "전주시",
                    "13": "정읍시",
                    "14": "진안군"
                }
            },
            "38": {
                "region_name": "전라남도",
                "subregions": {
                    "1": "강진군",
                    "2": "고흥군",
                    "3": "곡성군",
                    "4": "광양시",
                    "5": "구례군",
                    "6": "나주시",
                    "7": "담양군",
                    "8": "목포시",
                    "9": "무안군",
                    "10": "보성군",
                    "11": "순천시",
                    "12": "신안군",
                    "13": "여수시",
                    "16": "영광군",
                    "17": "영암군",
                    "18": "완도군",
                    "19": "장성군",
                    "20": "장흥군",
                    "21": "진도군",
                    "22": "함평군",
                    "23": "해남군",
                    "24": "화순군"
                }
            },
            "39": {
                "region_name": "제주특별자치도",
                "subregions": {
                    "1": "제주시",
                    "2": "서귀포시"
                }
            }
        }

        # 현재 지원하는 지역 코드 (서울, 인천, 대전, 대구, 광주)
        self.supported_area_codes = ["1", "2", "3", "4", "5"]
        self.enable_region_filter = True

    def enable_all_regions(self):
        # 모든 지역 허용하도록 설정
        self.enable_region_filter = False

    def is_supported_region(self, area_code: str) -> bool:
        # 지원하는 지역인지 확인
        if not self.enable_region_filter:
            return True
        return area_code in self.supported_area_codes

    def map_region(self, area_code: str, sigungu_code: str = None) -> Tuple[Optional[str], Optional[str]]:
        # 지역 코드를 지역명으로 변환
        region_name = None
        subregion_name = None

        if area_code and area_code in self.region_mapping:
            region_info = self.region_mapping[area_code]
            region_name = region_info["region_name"]

            if sigungu_code and sigungu_code in region_info["subregions"]:
                subregion_name = region_info["subregions"][sigungu_code]

        return (region_name, subregion_name)

    def get_region_ids(self, region_name: str, subregion_name: str = None) -> Tuple[Optional[int], Optional[int]]:
        # 지역명을 데이터베이스 ID로 변환
        region_id = None
        subregion_id = None

        try:
            if region_name:
                region = Region.objects.filter(
                    translations__name=region_name,
                    translations__lang="ko"
                ).first()

                if region:
                    region_id = region.id

                    if subregion_name:
                        subregion = SubRegion.objects.filter(
                            region=region,
                            translations__name=subregion_name,
                            translations__lang="ko"
                        ).first()

                        if subregion:
                            subregion_id = subregion.id

        except Exception as e:
            print(f"지역 ID 조회 실패: {e}")

        return (region_id, subregion_id)

    def map_category(self, lclssystm1: str, lclssystm2: str = None, lclssystm3: str = None) -> Optional[str]:
        # 신분류 코드를 우리 대분류 카테고리로 변환
        if lclssystm3 and lclssystm3 in self.category_mapping:
            return self.category_mapping[lclssystm3]
        elif lclssystm2 and lclssystm2 in self.category_mapping:
            return self.category_mapping[lclssystm2]
        elif lclssystm1 and lclssystm1 in self.category_mapping:
            return self.category_mapping[lclssystm1]
        return None

    def map_subcategory(self, lclssystm1: str, lclssystm2: str = None, lclssystm3: str = None) -> Optional[
        Tuple[str, str]]:
        # 신분류 코드를 우리 서브카테고리로 변환
        if lclssystm3 and lclssystm3 in self.subcategory_mapping:
            return self.subcategory_mapping[lclssystm3]
        elif lclssystm2 and lclssystm2 in self.subcategory_mapping:
            return self.subcategory_mapping[lclssystm2]
        elif lclssystm1 and lclssystm1 in self.subcategory_mapping:
            return self.subcategory_mapping[lclssystm1]

        # 서브카테고리 매핑이 안 되면 대분류만이라도 반환
        main_category = self.map_category(lclssystm1, lclssystm2, lclssystm3)
        if main_category:
            return (main_category, None)

        return None

    def get_category_ids(self, category_name: str, subcategory_name: str = None) -> Tuple[Optional[int], Optional[int]]:
        # 카테고리명을 데이터베이스 ID로 변환
        category_id = None
        subcategory_id = None

        try:
            if category_name:
                category = Category.objects.filter(
                    translations__name=category_name,
                    translations__lang="ko"
                ).first()

                if category:
                    category_id = category.id

                    if subcategory_name:
                        subcategory = SubCategory.objects.filter(
                            category=category,
                            translations__name=subcategory_name,
                            translations__lang="ko"
                        ).first()

                        if subcategory:
                            subcategory_id = subcategory.id

        except Exception as e:
            print(f"카테고리 ID 조회 실패: {e}")

        return (category_id, subcategory_id)

    def process_tour_api_place(self, place_data: Dict) -> Dict:
        # 투어 API 응답 데이터를 우리 형식으로 변환하는 메인 함수 (상세정보 보존)
        content_id = place_data.get("contentid", "")

        # 신분류 코드 추출
        lclssystm1 = place_data.get("lclsSystm1", "")
        lclssystm2 = place_data.get("lclsSystm2", "")
        lclssystm3 = place_data.get("lclsSystm3", "")

        # 카테고리 매핑
        category_name = self.map_category(lclssystm1, lclssystm2, lclssystm3)
        subcategory_name = None

        category_result = self.map_subcategory(lclssystm1, lclssystm2, lclssystm3)
        if category_result:
            category_name, subcategory_name = category_result

        category_id, subcategory_id = self.get_category_ids(category_name, subcategory_name)

        # 지역 매핑
        area_code = place_data.get("areacode", "")
        sigungu_code = place_data.get("sigungucode", "")

        region_id = None
        subregion_id = None

        if area_code:
            region_name, subregion_name = self.map_region(area_code, sigungu_code)
            region_id, subregion_id = self.get_region_ids(region_name, subregion_name)

        # 최종 데이터 구성
        processed_data = {
            "content_id": content_id,
            "title": place_data.get("title", ""),
            "address": place_data.get("addr1", ""),
            "latitude": self._convert_to_decimal(place_data.get("mapy")),
            "longitude": self._convert_to_decimal(place_data.get("mapx")),
            "category_id": category_id,
            "sub_category_id": subcategory_id,
            "region_id": region_id,
            "sub_region_id": subregion_id,
            "phone_number": place_data.get("tel", ""),
            "image_url": place_data.get("firstimage", ""),  # 메인 이미지
            "image_url2": place_data.get("firstimage2", ""),  # 보조 이미지
            "use_time": "",
            "link_url": "",
        }

        # 상세정보 필드 보존 (모든 가능한 필드 포함)
        detail_fields = [
            # 전화번호 관련
            "infocenterfood", "infocenter", "infocenterlodging",
            "infocentershopping", "infocenterculture", "infocenterleports",

            # 운영시간 관련
            "opentimefood", "usetime", "opentime", "usetimeculture",
            "usetimeleports", "opendateshopping", "checkintime", "checkouttime",

            # 기타 상세정보
            "homepage", "overview", "restdatefood", "restdate",
            "firstmenu", "treatmenu", "packing", "reservation",
            "reservationfood", "parkingfood", "parking",
            "firstimage", "firstimage2", "tel"
        ]

        for field in detail_fields:
            if field in place_data and place_data[field]:
                processed_data[field] = place_data[field]

        return processed_data

    def _convert_to_decimal(self, coord_str: str) -> Optional[float]:
        # 좌표 문자열을 실수로 변환
        try:
            if coord_str and coord_str.strip():
                return float(coord_str)
        except (ValueError, TypeError):
            pass
        return None

    def get_mapping_statistics(self) -> Dict:
        # 매핑 통계 정보 반환
        return {
            "total_mappings": len(self.category_mapping),
            "main_categories": list(set(self.category_mapping.values())),
            "subcategory_mappings": len(self.subcategory_mapping),
            "region_mappings": len(self.region_mapping),
            "coverage": {
                "문화": len([k for k, v in self.category_mapping.items() if v == "문화"]),
                "자연": len([k for k, v in self.category_mapping.items() if v == "자연"]),
                "액티비티": len([k for k, v in self.category_mapping.items() if v == "액티비티"]),
                "쇼핑": len([k for k, v in self.category_mapping.items() if v == "쇼핑"]),
                "음식": len([k for k, v in self.category_mapping.items() if v == "음식"]),
                "숙박": len([k for k, v in self.category_mapping.items() if v == "숙박"]),
            },
            "supported_regions": [info["region_name"] for info in self.region_mapping.values()],
            "successful_mappings": 0,
            "failed_mappings": 0,
        }

    def get_supported_regions_info(self) -> Dict:
        # 지원 지역 정보 반환
        return {
            "filter_enabled": self.enable_region_filter,
            "total_supported": len(self.supported_area_codes),
            "supported_regions": {
                code: {
                    "name": self.region_mapping[code]["region_name"],
                    "subregion_count": len(self.region_mapping[code]["subregions"])
                }
                for code in self.supported_area_codes
                if code in self.region_mapping
            }
        }
