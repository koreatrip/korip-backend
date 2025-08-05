from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class Command(BaseCommand):
    help = "투어 API와 매핑되는 지역 데이터를 자동으로 생성합니다"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="기존 데이터가 있어도 강제로 재생성"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="실제 생성하지 않고 테스트만 실행"
        )
        parser.add_argument(
            "--update-translations",
            action="store_true",
            help="기존 데이터는 유지하고 번역만 추가/업데이트"
        )

    def handle(self, *args, **options):
        force = options["force"]
        dry_run = options["dry_run"]
        update_translations = options["update_translations"]

        existing_regions = Region.objects.count()

        if update_translations:
            self.stdout.write("번역 데이터만 업데이트합니다...")
        elif existing_regions > 0 and not force:
            self.stdout.write("이미 지역 데이터가 존재합니다.")
            self.stdout.write("--force 옵션 또는 --update-translations 옵션을 사용하세요.")
            return

        if force and existing_regions > 0:
            self.stdout.write("기존 데이터를 삭제하고 재생성합니다...")
            if not dry_run:
                Region.objects.all().delete()
                SubRegion.objects.all().delete()

        try:
            if update_translations:
                result = self.update_translations_only(dry_run)
            else:
                result = self.create_regions(dry_run)
            self.print_summary(result, dry_run, update_translations)
        except Exception as e:
            self.stdout.write(f"오류 발생: {e}")
            raise CommandError(f"지역 데이터 생성 중 오류 발생: {e}")

    def get_hierarchical_translations(self):
        return {
            "서울": {
                "region_translations": {"en": "Seoul", "jp": "ソウル", "cn": "首尔"},
                "subregions": {
                    "종로구": {"en": "Jongno-gu", "jp": "鍾路区", "cn": "钟路区"},
                    "중구": {"en": "Jung-gu", "jp": "中区", "cn": "中区"},
                    "용산구": {"en": "Yongsan-gu", "jp": "龍山区", "cn": "龙山区"},
                    "성동구": {"en": "Seongdong-gu", "jp": "城東区", "cn": "城东区"},
                    "광진구": {"en": "Gwangjin-gu", "jp": "広津区", "cn": "广津区"},
                    "동대문구": {"en": "Dongdaemun-gu", "jp": "東大門区", "cn": "东大门区"},
                    "중랑구": {"en": "Jungnang-gu", "jp": "中浪区", "cn": "中浪区"},
                    "성북구": {"en": "Seongbuk-gu", "jp": "城北区", "cn": "城北区"},
                    "강북구": {"en": "Gangbuk-gu", "jp": "江北区", "cn": "江北区"},
                    "도봉구": {"en": "Dobong-gu", "jp": "道峰区", "cn": "道峰区"},
                    "노원구": {"en": "Nowon-gu", "jp": "蘆原区", "cn": "芦原区"},
                    "은평구": {"en": "Eunpyeong-gu", "jp": "恩平区", "cn": "恩平区"},
                    "서대문구": {"en": "Seodaemun-gu", "jp": "西大門区", "cn": "西大门区"},
                    "마포구": {"en": "Mapo-gu", "jp": "麻浦区", "cn": "麻浦区"},
                    "양천구": {"en": "Yangcheon-gu", "jp": "陽川区", "cn": "阳川区"},
                    "강서구": {"en": "Gangseo-gu", "jp": "江西区", "cn": "江西区"},
                    "구로구": {"en": "Guro-gu", "jp": "九老区", "cn": "九老区"},
                    "금천구": {"en": "Geumcheon-gu", "jp": "衿川区", "cn": "衿川区"},
                    "영등포구": {"en": "Yeongdeungpo-gu", "jp": "永登浦区", "cn": "永登浦区"},
                    "동작구": {"en": "Dongjak-gu", "jp": "銅雀区", "cn": "铜雀区"},
                    "관악구": {"en": "Gwanak-gu", "jp": "冠岳区", "cn": "冠岳区"},
                    "서초구": {"en": "Seocho-gu", "jp": "瑞草区", "cn": "瑞草区"},
                    "강남구": {"en": "Gangnam-gu", "jp": "江南区", "cn": "江南区"},
                    "송파구": {"en": "Songpa-gu", "jp": "松坡区", "cn": "松坡区"},
                    "강동구": {"en": "Gangdong-gu", "jp": "江東区", "cn": "江东区"},
                }
            },
            "인천": {
                "region_translations": {"en": "Incheon", "jp": "仁川", "cn": "仁川"},
                "subregions": {
                    "중구": {"en": "Jung-gu", "jp": "中区", "cn": "中区"},
                    "동구": {"en": "Dong-gu", "jp": "東区", "cn": "东区"},
                    "미추홀구": {"en": "Michuhol-gu", "jp": "彌鄒忽区", "cn": "弥邹忽区"},
                    "연수구": {"en": "Yeonsu-gu", "jp": "延寿区", "cn": "延寿区"},
                    "남동구": {"en": "Namdong-gu", "jp": "南東区", "cn": "南东区"},
                    "부평구": {"en": "Bupyeong-gu", "jp": "富平区", "cn": "富平区"},
                    "계양구": {"en": "Gyeyang-gu", "jp": "桂陽区", "cn": "桂阳区"},
                    "서구": {"en": "Seo-gu", "jp": "西区", "cn": "西区"},
                    "강화군": {"en": "Ganghwa-gun", "jp": "江華郡", "cn": "江华郡"},
                    "옹진군": {"en": "Ongjin-gun", "jp": "甕津郡", "cn": "瓮津郡"},
                }
            },
            "부산": {
                "region_translations": {"en": "Busan", "jp": "釜山", "cn": "釜山"},
                "subregions": {
                    "중구": {"en": "Jung-gu", "jp": "中区", "cn": "中区"},
                    "서구": {"en": "Seo-gu", "jp": "西区", "cn": "西区"},
                    "동구": {"en": "Dong-gu", "jp": "東区", "cn": "东区"},
                    "영도구": {"en": "Yeongdo-gu", "jp": "影島区", "cn": "影岛区"},
                    "부산진구": {"en": "Busanjin-gu", "jp": "釜山鎮区", "cn": "釜山镇区"},
                    "동래구": {"en": "Dongnae-gu", "jp": "東萊区", "cn": "东莱区"},
                    "남구": {"en": "Nam-gu", "jp": "南区", "cn": "南区"},
                    "북구": {"en": "Buk-gu", "jp": "北区", "cn": "北区"},
                    "해운대구": {"en": "Haeundae-gu", "jp": "海雲台区", "cn": "海云台区"},
                    "사하구": {"en": "Saha-gu", "jp": "沙下区", "cn": "沙下区"},
                    "금정구": {"en": "Geumjeong-gu", "jp": "金井区", "cn": "金井区"},
                    "강서구": {"en": "Gangseo-gu", "jp": "江西区", "cn": "江西区"},
                    "연제구": {"en": "Yeonje-gu", "jp": "蓮堤区", "cn": "莲堤区"},
                    "수영구": {"en": "Suyeong-gu", "jp": "水営区", "cn": "水营区"},
                    "사상구": {"en": "Sasang-gu", "jp": "沙上区", "cn": "沙上区"},
                    "기장군": {"en": "Gijang-gun", "jp": "機張郡", "cn": "机张郡"},
                }
            },
            "경기": {
                "region_translations": {"en": "Gyeonggi", "jp": "京畿道", "cn": "京畿道"},
                "subregions": {
                    "수원시 장안구": {"en": "Suwon Jangan-gu", "jp": "水原市長安区", "cn": "水原市长安区"},
                    "수원시 권선구": {"en": "Suwon Gwonseon-gu", "jp": "水原市勧善区", "cn": "水原市劝善区"},
                    "수원시 팔달구": {"en": "Suwon Paldal-gu", "jp": "水原市八達区", "cn": "水原市八达区"},
                    "수원시 영통구": {"en": "Suwon Yeongtong-gu", "jp": "水原市霊通区", "cn": "水原市灵通区"},
                    "성남시 수정구": {"en": "Seongnam Sujeong-gu", "jp": "城南市修井区", "cn": "城南市修井区"},
                    "성남시 중원구": {"en": "Seongnam Jungwon-gu", "jp": "城南市中院区", "cn": "城南市中院区"},
                    "성남시 분당구": {"en": "Seongnam Bundang-gu", "jp": "城南市盆唐区", "cn": "城南市盆唐区"},
                    "의정부시": {"en": "Uijeongbu-si", "jp": "議政府市", "cn": "议政府市"},
                    "안양시 만안구": {"en": "Anyang Manan-gu", "jp": "安養市万安区", "cn": "安养市万安区"},
                    "안양시 동안구": {"en": "Anyang Dongan-gu", "jp": "安養市東安区", "cn": "安养市东安区"},
                    "부천시": {"en": "Bucheon-si", "jp": "富川市", "cn": "富川市"},
                    "광명시": {"en": "Gwangmyeong-si", "jp": "光明市", "cn": "光明市"},
                    "평택시": {"en": "Pyeongtaek-si", "jp": "平沢市", "cn": "平泽市"},
                    "동두천시": {"en": "Dongducheon-si", "jp": "東豆川市", "cn": "东豆川市"},
                    "안산시 상록구": {"en": "Ansan Sangnok-gu", "jp": "安山市常緑区", "cn": "安山市常绿区"},
                    "안산시 단원구": {"en": "Ansan Danwon-gu", "jp": "安山市檀園区", "cn": "安山市檀园区"},
                    "고양시 덕양구": {"en": "Goyang Deogyang-gu", "jp": "高陽市徳陽区", "cn": "高阳市德阳区"},
                    "고양시 일산동구": {"en": "Goyang Ilsandong-gu", "jp": "高陽市一山東区", "cn": "高阳市一山东区"},
                    "고양시 일산서구": {"en": "Goyang Ilsanseo-gu", "jp": "高陽市一山西区", "cn": "高阳市一山西区"},
                    "과천시": {"en": "Gwacheon-si", "jp": "果川市", "cn": "果川市"},
                    "구리시": {"en": "Guri-si", "jp": "九里市", "cn": "九里市"},
                    "남양주시": {"en": "Namyangju-si", "jp": "南楊州市", "cn": "南杨州市"},
                    "오산시": {"en": "Osan-si", "jp": "烏山市", "cn": "乌山市"},
                    "시흥시": {"en": "Siheung-si", "jp": "始興市", "cn": "始兴市"},
                    "군포시": {"en": "Gunpo-si", "jp": "軍浦市", "cn": "军浦市"},
                    "의왕시": {"en": "Uiwang-si", "jp": "義王市", "cn": "义王市"},
                    "하남시": {"en": "Hanam-si", "jp": "河南市", "cn": "河南市"},
                    "용인시 처인구": {"en": "Yongin Cheoin-gu", "jp": "龍仁市処仁区", "cn": "龙仁市处仁区"},
                    "용인시 기흥구": {"en": "Yongin Giheung-gu", "jp": "龍仁市器興区", "cn": "龙仁市器兴区"},
                    "용인시 수지구": {"en": "Yongin Suji-gu", "jp": "龍仁市水枝区", "cn": "龙仁市水枝区"},
                    "파주시": {"en": "Paju-si", "jp": "坡州市", "cn": "坡州市"},
                    "이천시": {"en": "Icheon-si", "jp": "利川市", "cn": "利川市"},
                    "안성시": {"en": "Anseong-si", "jp": "安城市", "cn": "安城市"},
                    "김포시": {"en": "Gimpo-si", "jp": "金浦市", "cn": "金浦市"},
                    "화성시": {"en": "Hwaseong-si", "jp": "華城市", "cn": "华城市"},
                    "광주시": {"en": "Gwangju-si", "jp": "広州市", "cn": "广州市"},
                    "양주시": {"en": "Yangju-si", "jp": "楊州市", "cn": "杨州市"},
                    "포천시": {"en": "Pocheon-si", "jp": "抱川市", "cn": "抱川市"},
                    "여주시": {"en": "Yeoju-si", "jp": "驪州市", "cn": "骊州市"},
                    "연천군": {"en": "Yeoncheon-gun", "jp": "漣川郡", "cn": "涟川郡"},
                    "가평군": {"en": "Gapyeong-gun", "jp": "加平郡", "cn": "加平郡"},
                    "양평군": {"en": "Yangpyeong-gun", "jp": "楊平郡", "cn": "杨平郡"},
                }
            },
            "제주": {
                "region_translations": {"en": "Jeju", "jp": "済州島", "cn": "济州岛"},
                "subregions": {
                    "제주시": {"en": "Jeju-si", "jp": "済州市", "cn": "济州市"},
                    "서귀포시": {"en": "Seogwipo-si", "jp": "西帰浦市", "cn": "西归浦市"},
                }
            }
        }

    def create_regions(self, dry_run=False):
        regions_data = {
            "1": {
                "region_name": "서울",
                "subregions": {
                    "1": "강남구", "2": "강동구", "3": "강북구", "4": "강서구", "5": "관악구",
                    "6": "광진구", "7": "구로구", "8": "금천구", "9": "노원구", "10": "도봉구",
                    "11": "동대문구", "12": "동작구", "13": "마포구", "14": "서대문구", "15": "서초구",
                    "16": "성동구", "17": "성북구", "18": "송파구", "19": "양천구", "20": "영등포구",
                    "21": "용산구", "22": "은평구", "23": "종로구", "24": "중구", "25": "중랑구",
                }
            },
            "2": {
                "region_name": "인천",
                "subregions": {
                    "1": "중구", "2": "동구", "3": "미추홀구", "4": "연수구", "5": "남동구",
                    "6": "부평구", "7": "계양구", "8": "서구", "9": "강화군", "10": "옹진군",
                }
            },
            "6": {
                "region_name": "부산",
                "subregions": {
                    "1": "중구", "2": "서구", "3": "동구", "4": "영도구", "5": "부산진구",
                    "6": "동래구", "7": "남구", "8": "북구", "9": "해운대구", "10": "사하구",
                    "11": "금정구", "12": "강서구", "13": "연제구", "14": "수영구", "15": "사상구", "16": "기장군",
                }
            },
            "31": {
                "region_name": "경기",
                "subregions": {
                    "1": "수원시 장안구", "2": "수원시 권선구", "3": "수원시 팔달구", "4": "수원시 영통구",
                    "5": "성남시 수정구", "6": "성남시 중원구", "7": "성남시 분당구", "8": "의정부시",
                    "9": "안양시 만안구", "10": "안양시 동안구", "11": "부천시", "12": "광명시",
                    "13": "평택시", "14": "동두천시", "15": "안산시 상록구", "16": "안산시 단원구",
                    "17": "고양시 덕양구", "18": "고양시 일산동구", "19": "고양시 일산서구", "20": "과천시",
                    "21": "구리시", "22": "남양주시", "23": "오산시", "24": "시흥시", "25": "군포시",
                    "26": "의왕시", "27": "하남시", "28": "용인시 처인구", "29": "용인시 기흥구", "30": "용인시 수지구",
                    "31": "파주시", "32": "이천시", "33": "안성시", "34": "김포시", "35": "화성시",
                    "36": "광주시", "37": "양주시", "38": "포천시", "39": "여주시", "40": "연천군",
                    "41": "가평군", "42": "양평군",
                }
            },
            "39": {
                "region_name": "제주",
                "subregions": {
                    "1": "제주시", "2": "서귀포시",
                }
            }
        }

        hierarchical_translations = self.get_hierarchical_translations()
        stats = {
            "regions_created": 0,
            "subregions_created": 0,
            "region_translations_created": 0,
            "subregion_translations_created": 0,
        }

        for area_code, region_data in regions_data.items():
            region_name = region_data["region_name"]
            subregions = region_data["subregions"]

            if not dry_run:
                with transaction.atomic():
                    region = Region.objects.create()
                    RegionTranslation.objects.create(region=region, lang="ko", name=region_name)
                    stats["region_translations_created"] += 1

                    if region_name in hierarchical_translations:
                        region_translations = hierarchical_translations[region_name]["region_translations"]
                        for lang, translated_name in region_translations.items():
                            RegionTranslation.objects.create(region=region, lang=lang, name=translated_name)
                            stats["region_translations_created"] += 1

                    stats["regions_created"] += 1

                    for subregion_code, subregion_name in subregions.items():
                        subregion = SubRegion.objects.create(region=region, favorite_count=0, location=None)
                        SubRegionTranslation.objects.create(sub_region=subregion, lang="ko", name=subregion_name)
                        stats["subregion_translations_created"] += 1

                        if (region_name in hierarchical_translations and
                                subregion_name in hierarchical_translations[region_name]["subregions"]):
                            translations = hierarchical_translations[region_name]["subregions"][subregion_name]
                            for lang, translated_name in translations.items():
                                SubRegionTranslation.objects.create(sub_region=subregion, lang=lang,
                                                                    name=translated_name)
                                stats["subregion_translations_created"] += 1

                        stats["subregions_created"] += 1
            else:
                stats["regions_created"] += 1
                stats["subregions_created"] += len(subregions)
                stats["region_translations_created"] += 4
                stats["subregion_translations_created"] += len(subregions) * 4

        return stats

    def update_translations_only(self, dry_run=False):
        hierarchical_translations = self.get_hierarchical_translations()
        stats = {
            "regions_created": 0,
            "subregions_created": 0,
            "region_translations_created": 0,
            "subregion_translations_created": 0,
        }

        existing_subregions = SubRegion.objects.all()
        for subregion in existing_subregions:
            ko_name = subregion.get_name("ko")
            region_name = subregion.region.get_name("ko") if subregion.region else None

            if ko_name and region_name:
                if (region_name in hierarchical_translations and
                        ko_name in hierarchical_translations[region_name]["subregions"]):
                    translations = hierarchical_translations[region_name]["subregions"][ko_name]

                    if not dry_run:
                        with transaction.atomic():
                            for lang, translated_name in translations.items():
                                existing_translation = SubRegionTranslation.objects.filter(
                                    sub_region=subregion, lang=lang
                                ).first()

                                if existing_translation:
                                    existing_translation.name = translated_name
                                    existing_translation.save()
                                else:
                                    SubRegionTranslation.objects.create(
                                        sub_region=subregion, lang=lang, name=translated_name
                                    )
                                    stats["subregion_translations_created"] += 1
                    else:
                        stats["subregion_translations_created"] += len(translations)

        return stats

    def print_summary(self, result, dry_run, update_only=False):
        if update_only:
            self.stdout.write("번역 업데이트 완료")
        else:
            self.stdout.write("지역 데이터 생성 완료")

        mode = "테스트 모드" if dry_run else "실제 처리"
        self.stdout.write(f"처리 결과 ({mode}):")

        if not update_only:
            self.stdout.write(f"  지역: {result['regions_created']}개")
            self.stdout.write(f"  하위지역: {result['subregions_created']}개")

        self.stdout.write(f"  지역 번역: {result.get('region_translations_created', 0)}개")
        self.stdout.write(f"  하위지역 번역: {result.get('subregion_translations_created', 0)}개")

        if not dry_run:
            total_regions = Region.objects.count()
            total_subregions = SubRegion.objects.count()
            self.stdout.write(f"DB 확인: 지역 {total_regions}개, 하위지역 {total_subregions}개")
