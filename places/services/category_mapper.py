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
        }

        self.subcategory_mapping = {
            # 문화 서브카테고리
            "VE070100": ("문화", "박물관"),
            "VE070600": ("문화", "미술관"),
            "VE01": ("문화", "역사"),
            "VE02": ("문화", "전통문화"),
            "VE05": ("문화", "복합관광시설"),
            "VE06": ("문화", "공연시설"),
            "VE07": ("문화", "박물관"),
            "EV01": ("문화", "축제"),
            "EV02": ("문화", "공연"),

            # 음식 서브카테고리
            "FD01": ("음식", "한식"),
            "FD02": ("음식", "일식"),
            "FD03": ("음식", "중식"),
            "FD04": ("음식", "양식"),

            # 자연 서브카테고리
            "VN010400": ("자연", "산"),
            "VN010800": ("자연", "바다"),
            "VN010500": ("자연", "강"),
            "VN010600": ("자연", "호수"),
            "VN010700": ("자연", "계곡"),
            "VN010100": ("자연", "공원"),
            "VN010200": ("자연", "공원"),
            "VN010300": ("자연", "공원"),
            "NA010400": ("자연", "산"),
            "NA020800": ("자연", "바다"),
            "NA020100": ("자연", "강"),
            "NA020200": ("자연", "호수"),
            "NA020300": ("자연", "계곡"),
            "NA040100": ("자연", "공원"),
            "NA040200": ("자연", "공원"),
            "NA040300": ("자연", "공원"),
            "NA040600": ("자연", "공원"),
            "NA040700": ("자연", "공원"),

            # 액티비티 서브카테고리
            "RS030100": ("액티비티", "동물원"),
            "RS030200": ("액티비티", "수족관"),
            "RS040100": ("액티비티", "테마파크"),
            "RS040200": ("액티비티", "놀이공원"),
            "RS01": ("액티비티", "등산"),

            # 쇼핑 서브카테고리
            "SH010100": ("쇼핑", "전통시장"),
            "SH010200": ("쇼핑", "백화점"),
            "SH010300": ("쇼핑", "면세점"),
            "SH010400": ("쇼핑", "아울렛"),
            "SH010500": ("쇼핑", "기념품"),
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
                    "25": "중랑구",
                }
            },
            "2": {
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
                    "16": "해운대구",
                }
            },
            "3": {
                "region_name": "인천광역시",
                "subregions": {
                    "1": "계양구",
                    "2": "미추홀구",
                    "3": "남동구",
                    "4": "동구",
                    "5": "부평구",
                    "6": "서구",
                    "7": "연수구",
                    "8": "중구",
                    "9": "강화군",
                    "10": "옹진군",
                }
            },
            "4": {
                "region_name": "경기도",
                "subregions": {
                    "1": "수원시 장안구",
                    "2": "수원시 권선구",
                    "3": "수원시 팔달구",
                    "4": "수원시 영통구",
                    "5": "성남시 수정구",
                    "6": "성남시 중원구",
                    "7": "성남시 분당구",
                    "8": "의정부시",
                    "9": "안양시 만안구",
                    "10": "안양시 동안구",
                    "11": "부천시",
                    "12": "광명시",
                    "13": "평택시",
                    "14": "동두천시",
                    "15": "안산시 상록구",
                    "16": "안산시 단원구",
                    "17": "고양시 덕양구",
                    "18": "고양시 일산동구",
                    "19": "고양시 일산서구",
                    "20": "과천시",
                    "21": "구리시",
                    "22": "남양주시",
                    "23": "오산시",
                    "24": "시흥시",
                    "25": "군포시",
                    "26": "의왕시",
                    "27": "하남시",
                    "28": "용인시 처인구",
                    "29": "용인시 기흥구",
                    "30": "용인시 수지구",
                    "31": "파주시",
                    "32": "이천시",
                    "33": "안성시",
                    "34": "김포시",
                    "35": "화성시",
                    "36": "광주시",
                    "37": "양주시",
                    "38": "포천시",
                    "39": "여주시",
                    "40": "연천군",
                    "41": "가평군",
                    "42": "양평군",
                }
            },
            "5": {
                "region_name": "제주특별자치도",
                "subregions": {
                    "1": "제주시",
                    "2": "서귀포시",
                }
            }
        }


        self.supported_area_codes = ["1", "2", "3", "4", "5"]
        self.enable_region_filter = True

    def enable_all_regions(self):
        self.enable_region_filter = False

    def is_supported_region(self, area_code: str) -> bool:
        if not self.enable_region_filter:
            return True
        return area_code in self.supported_area_codes

    def map_region(self, area_code: str, sigungu_code: str = None) -> Tuple[Optional[str], Optional[str]]:
        region_name = None
        subregion_name = None

        if area_code and area_code in self.region_mapping:
            region_info = self.region_mapping[area_code]
            region_name = region_info["region_name"]

            if sigungu_code and sigungu_code in region_info["subregions"]:
                subregion_name = region_info["subregions"][sigungu_code]

        return (region_name, subregion_name)

    def get_region_ids(self, region_name: str, subregion_name: str = None) -> Tuple[Optional[int], Optional[int]]:
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
        if lclssystm3 and lclssystm3 in self.category_mapping:
            return self.category_mapping[lclssystm3]
        elif lclssystm2 and lclssystm2 in self.category_mapping:
            return self.category_mapping[lclssystm2]
        elif lclssystm1 and lclssystm1 in self.category_mapping:
            return self.category_mapping[lclssystm1]
        return None

    def map_subcategory(self, lclssystm1: str, lclssystm2: str = None, lclssystm3: str = None) -> Optional[
        Tuple[str, str]]:
        if lclssystm3 and lclssystm3 in self.subcategory_mapping:
            return self.subcategory_mapping[lclssystm3]
        elif lclssystm2 and lclssystm2 in self.subcategory_mapping:
            return self.subcategory_mapping[lclssystm2]
        elif lclssystm1 and lclssystm1 in self.subcategory_mapping:
            return self.subcategory_mapping[lclssystm1]

        main_category = self.map_category(lclssystm1, lclssystm2, lclssystm3)
        if main_category:
            return (main_category, None)

        return None

    def get_category_ids(self, category_name: str, subcategory_name: str = None) -> Tuple[Optional[int], Optional[int]]:
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
        content_id = place_data.get("contentid", "")

        lclssystm1 = place_data.get("lclsSystm1", "")
        lclssystm2 = place_data.get("lclsSystm2", "")
        lclssystm3 = place_data.get("lclsSystm3", "")

        category_name = self.map_category(lclssystm1, lclssystm2, lclssystm3)
        subcategory_name = None

        category_result = self.map_subcategory(lclssystm1, lclssystm2, lclssystm3)
        if category_result:
            category_name, subcategory_name = category_result

        category_id, subcategory_id = self.get_category_ids(category_name, subcategory_name)
        area_code = place_data.get("areacode", "")
        sigungu_code = place_data.get("sigungucode", "")

        region_id = None
        subregion_id = None

        if area_code:
            region_name, subregion_name = self.map_region(area_code, sigungu_code)
            region_id, subregion_id = self.get_region_ids(region_name, subregion_name)

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
            "image_url": place_data.get("firstimage", ""),
            "use_time": "",
            "link_url": "",
        }

        return processed_data

    def _convert_to_decimal(self, coord_str: str) -> Optional[float]:
        try:
            if coord_str and coord_str.strip():
                return float(coord_str)
        except (ValueError, TypeError):
            pass
        return None

    def get_mapping_statistics(self) -> Dict:
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
            },
            "supported_regions": [info["region_name"] for info in self.region_mapping.values()],
            "successful_mappings": 0,
            "failed_mappings": 0,
        }
