from django.core.management.base import BaseCommand
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation


class Command(BaseCommand):
    help = "전체 지역 데이터를 로드합니다."

    def handle(self, *args, **options):
        self.stdout.write("🌍 전체 지역 데이터 로딩 시작...")

        # 지역 데이터 정의 (기존 구조 유지)
        regions_data = [
            {
                "id": 1,
                "translations": {
                    "ko": {"name": "서울특별시", "description": "대한민국의 수도"},
                    "en": {"name": "Seoul", "description": "Capital of South Korea"},
                    "jp": {"name": "ソウル特別市", "description": "韓国の首都"},
                    "cn": {"name": "首尔特别市", "description": "韩国首都"}
                }
            },
            {
                "id": 2,
                "translations": {
                    "ko": {"name": "부산광역시", "description": "대한민국 제2의 도시"},
                    "en": {"name": "Busan", "description": "Second largest city in South Korea"},
                    "jp": {"name": "釜山広域市", "description": "韓国第二の都市"},
                    "cn": {"name": "釜山广域市", "description": "韩国第二大城市"}
                }
            },
            {
                "id": 3,
                "translations": {
                    "ko": {"name": "인천광역시", "description": "서울과 인접한 항구도시"},
                    "en": {"name": "Incheon", "description": "Port city near Seoul"},
                    "jp": {"name": "仁川広域市", "description": "ソウル近郊の港湾都市"},
                    "cn": {"name": "仁川广域市", "description": "首尔附近的港口城市"}
                }
            },
            {
                "id": 4,
                "translations": {
                    "ko": {"name": "경기도", "description": "서울을 둘러싼 지역"},
                    "en": {"name": "Gyeonggi Province", "description": "Province surrounding Seoul"},
                    "jp": {"name": "京畿道", "description": "ソウルを囲む地域"},
                    "cn": {"name": "京畿道", "description": "环绕首尔的地区"}
                }
            },
            {
                "id": 5,
                "translations": {
                    "ko": {"name": "제주특별자치도", "description": "아름다운 섬 지역"},
                    "en": {"name": "Jeju Special Self-Governing Province", "description": "Beautiful island region"},
                    "jp": {"name": "済州特別自治道", "description": "美しい島地域"},
                    "cn": {"name": "济州特别自治道", "description": "美丽的岛屿地区"}
                }
            }
        ]

        # 서브지역 데이터 (전체 구/군, 번역 포함)
        subregions_data = [
            # ======= 서울특별시 (25개 구) =======
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "강남구", "description": "서울의 대표적인 번화가", "feature": "쇼핑과 엔터테인먼트의 중심지"},
                    "en": {"name": "Gangnam-gu", "description": "Famous district in Seoul", "feature": "Shopping and entertainment hub"},
                    "jp": {"name": "江南区", "description": "ソウルの代表的な繁華街", "feature": "ショッピングとエンターテイメントの中心地"},
                    "cn": {"name": "江南区", "description": "首尔著名商业区", "feature": "购物和娱乐中心"}
                },
                "favorite_count": 15, "latitude": 37.5172, "longitude": 127.0473
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "강동구", "description": "서울 동부의 주거지역", "feature": "천호동과 둔촌동의 아파트 단지"},
                    "en": {"name": "Gangdong-gu", "description": "Eastern residential area", "feature": "Cheonho and Dunchon apartment complexes"},
                    "jp": {"name": "江東区", "description": "ソウル東部の住宅地域", "feature": "千戸洞と屯村洞のアパート団地"},
                    "cn": {"name": "江东区", "description": "首尔东部住宅区", "feature": "千户洞和屯村洞公寓区"}
                },
                "favorite_count": 5, "latitude": 37.5301, "longitude": 127.1238
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "강북구", "description": "서울 북부의 주거지역", "feature": "도봉산과 수유리 맛집거리"},
                    "en": {"name": "Gangbuk-gu", "description": "Northern residential area", "feature": "Dobongsan and Suyu food street"},
                    "jp": {"name": "江北区", "description": "ソウル北部の住宅地域", "feature": "道峰山と水踰里グルメ街"},
                    "cn": {"name": "江北区", "description": "首尔北部住宅区", "feature": "道峰山和水踰里美食街"}
                },
                "favorite_count": 3, "latitude": 37.6398, "longitude": 127.0256
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "강서구", "description": "김포공항이 있는 서부지역", "feature": "김포공항과 마곡산업단지"},
                    "en": {"name": "Gangseo-gu", "description": "Western area with Gimpo Airport", "feature": "Gimpo Airport and Magok Industrial Complex"},
                    "jp": {"name": "江西区", "description": "金浦空港がある西部地域", "feature": "金浦空港と麻谷産業団地"},
                    "cn": {"name": "江西区", "description": "金浦机场所在的西部地区", "feature": "金浦机场和麻谷产业园区"}
                },
                "favorite_count": 4, "latitude": 37.5509, "longitude": 126.8495
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "관악구", "description": "서울대학교가 있는 남부지역", "feature": "서울대학교와 관악산"},
                    "en": {"name": "Gwanak-gu", "description": "Southern area with Seoul National University", "feature": "Seoul National University and Gwanaksan"},
                    "jp": {"name": "冠岳区", "description": "ソウル大学校がある南部地域", "feature": "ソウル大学校と冠岳山"},
                    "cn": {"name": "冠岳区", "description": "首尔大学所在的南部地区", "feature": "首尔大学和冠岳山"}
                },
                "favorite_count": 6, "latitude": 37.4784, "longitude": 126.9516
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "광진구", "description": "건대와 성수동이 있는 지역", "feature": "건대 클럽거리와 성수동 카페"},
                    "en": {"name": "Gwangjin-gu", "description": "Area with Konkuk University and Seongsu", "feature": "Konkuk University club street and Seongsu cafes"},
                    "jp": {"name": "広津区", "description": "建大と聖水洞がある地域", "feature": "建大クラブ街と聖水洞カフェ"},
                    "cn": {"name": "广津区", "description": "建大和圣水洞所在地区", "feature": "建大俱乐部街和圣水洞咖啡"}
                },
                "favorite_count": 7, "latitude": 37.5385, "longitude": 127.0823
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "구로구", "description": "디지털산업단지가 있는 서남부", "feature": "구로디지털단지와 신도림 쇼핑"},
                    "en": {"name": "Guro-gu", "description": "Southwestern area with digital industrial complex", "feature": "Guro Digital Complex and Sindorim shopping"},
                    "jp": {"name": "九老区", "description": "デジタル産業団地がある西南部", "feature": "九老デジタル団地と新道林ショッピング"},
                    "cn": {"name": "九老区", "description": "数字产业园区所在的西南部", "feature": "九老数字园区和新道林购物"}
                },
                "favorite_count": 3, "latitude": 37.4955, "longitude": 126.8876
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "금천구", "description": "가산디지털단지 중심지역", "feature": "가산디지털단지와 시흥대로"},
                    "en": {"name": "Geumcheon-gu", "description": "Gasan Digital Complex area", "feature": "Gasan Digital Complex and Siheung-daero"},
                    "jp": {"name": "衿川区", "description": "加山デジタル団地中心地域", "feature": "加山デジタル団地と始興大路"},
                    "cn": {"name": "衿川区", "description": "加山数字园区中心地区", "feature": "加山数字园区和始兴大路"}
                },
                "favorite_count": 2, "latitude": 37.4570, "longitude": 126.8954
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "노원구", "description": "서울 최북단 주거지역", "feature": "노원역과 상계동 아파트단지"},
                    "en": {"name": "Nowon-gu", "description": "Northernmost residential area", "feature": "Nowon Station and Sanggye apartment complex"},
                    "jp": {"name": "蘆原区", "description": "ソウル最北端住宅地域", "feature": "蘆原駅と上渓洞アパート団地"},
                    "cn": {"name": "芦原区", "description": "首尔最北端住宅区", "feature": "芦原站和上溪洞公寓区"}
                },
                "favorite_count": 4, "latitude": 37.6542, "longitude": 127.0568
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "도봉구", "description": "도봉산 자락의 주거지역", "feature": "도봉산과 창동 차이나타운"},
                    "en": {"name": "Dobong-gu", "description": "Residential area at Dobongsan foothills", "feature": "Dobongsan and Changdong Chinatown"},
                    "jp": {"name": "道峰区", "description": "道峰山麓の住宅地域", "feature": "道峰山と昌洞チャイナタウン"},
                    "cn": {"name": "道峰区", "description": "道峰山脚下的住宅区", "feature": "道峰山和昌洞唐人街"}
                },
                "favorite_count": 2, "latitude": 37.6688, "longitude": 127.0471
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "동대문구", "description": "동대문시장과 청량리가 있는 동북부", "feature": "동대문 패션타운과 경동시장"},
                    "en": {"name": "Dongdaemun-gu", "description": "Northeastern area with Dongdaemun Market", "feature": "Dongdaemun Fashion Town and Gyeongdong Market"},
                    "jp": {"name": "東大門区", "description": "東大門市場と清涼里がある東北部", "feature": "東大門ファッションタウンと京東市場"},
                    "cn": {"name": "东大门区", "description": "东大门市场和清凉里所在的东北部", "feature": "东大门时装城和京东市场"}
                },
                "favorite_count": 8, "latitude": 37.5743, "longitude": 127.0398
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "동작구", "description": "노량진과 사당동이 있는 남부", "feature": "노량진 수산시장과 사당역"},
                    "en": {"name": "Dongjak-gu", "description": "Southern area with Noryangjin and Sadang", "feature": "Noryangjin Fish Market and Sadang Station"},
                    "jp": {"name": "銅雀区", "description": "鷺梁津と舎堂洞がある南部", "feature": "鷺梁津水産市場と舎堂駅"},
                    "cn": {"name": "铜雀区", "description": "鹭梁津和舍堂洞所在的南部", "feature": "鹭梁津水产市场和舍堂站"}
                },
                "favorite_count": 5, "latitude": 37.5124, "longitude": 126.9393
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "마포구", "description": "홍대와 상암의 문화지역", "feature": "젊은 문화와 IT의 중심"},
                    "en": {"name": "Mapo-gu", "description": "Cultural hub with Hongdae", "feature": "Youth culture and IT center"},
                    "jp": {"name": "麻浦区", "description": "弘大と上岩の文化地域", "feature": "若い文化とITの中心"},
                    "cn": {"name": "麻浦区", "description": "弘大和上岩文化区", "feature": "年轻文化和IT中心"}
                },
                "favorite_count": 12, "latitude": 37.5615, "longitude": 126.9087
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "서대문구", "description": "연세대와 이화여대가 있는 서북부", "feature": "대학가 문화와 안산 자락길"},
                    "en": {"name": "Seodaemun-gu", "description": "Northwestern area with Yonsei and Ewha Universities", "feature": "University culture and Ansan trail"},
                    "jp": {"name": "西大門区", "description": "延世大と梨花女大がある西北部", "feature": "大学街文化と鞍山自然道"},
                    "cn": {"name": "西大门区", "description": "延世大学和梨花女大所在的西北部", "feature": "大学街文化和鞍山自然路"}
                },
                "favorite_count": 7, "latitude": 37.5791, "longitude": 126.9368
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "서초구", "description": "법조타운과 교육의 중심", "feature": "서초법조타운과 강남권 교육"},
                    "en": {"name": "Seocho-gu", "description": "Legal and education hub", "feature": "Legal town and education center"},
                    "jp": {"name": "瑞草区", "description": "法曹タウンと教育の中心", "feature": "瑞草法曹タウンと江南圏教育"},
                    "cn": {"name": "瑞草区", "description": "法律和教育中心", "feature": "瑞草法律城和江南教育"}
                },
                "favorite_count": 9, "latitude": 37.4837, "longitude": 127.0324
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "성동구", "description": "한강과 성수동 카페거리", "feature": "성수동 카페거리와 서울숲"},
                    "en": {"name": "Seongdong-gu", "description": "Han River and Seongsu cafe street", "feature": "Seongsu cafe street and Seoul Forest"},
                    "jp": {"name": "城東区", "description": "漢江と聖水洞カフェ街", "feature": "聖水洞カフェ街とソウルの森"},
                    "cn": {"name": "城东区", "description": "汉江和圣水洞咖啡街", "feature": "圣水洞咖啡街和首尔林"}
                },
                "favorite_count": 8, "latitude": 37.5634, "longitude": 127.0366
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "성북구", "description": "성신여대와 한성대 대학가", "feature": "대학로와 정릉 카페거리"},
                    "en": {"name": "Seongbuk-gu", "description": "University area with Sungshin Women's University", "feature": "University street and Jeongneung cafe street"},
                    "jp": {"name": "城北区", "description": "誠信女大と漢城大の大学街", "feature": "大学路と貞陵カフェ街"},
                    "cn": {"name": "城北区", "description": "诚信女大和汉城大学大学街", "feature": "大学路和贞陵咖啡街"}
                },
                "favorite_count": 5, "latitude": 37.5894, "longitude": 127.0167
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "송파구", "description": "잠실과 석촌호수가 있는 동남부", "feature": "롯데월드와 올림픽공원"},
                    "en": {"name": "Songpa-gu", "description": "Southeastern area with Jamsil and Seokchon Lake", "feature": "Lotte World and Olympic Park"},
                    "jp": {"name": "松坡区", "description": "蚕室と石村湖がある東南部", "feature": "ロッテワールドとオリンピック公園"},
                    "cn": {"name": "松坡区", "description": "蚕室和石村湖所在的东南部", "feature": "乐天世界和奥林匹克公园"}
                },
                "favorite_count": 11, "latitude": 37.5145, "longitude": 127.1059
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "양천구", "description": "목동 신시가지가 있는 서남부", "feature": "목동 아파트단지와 양천향교"},
                    "en": {"name": "Yangcheon-gu", "description": "Southwestern area with Mokdong new town", "feature": "Mokdong apartment complex and Yangcheon Hyanggyo"},
                    "jp": {"name": "陽川区", "description": "木洞新市街地がある西南部", "feature": "木洞アパート団地と陽川郷校"},
                    "cn": {"name": "阳川区", "description": "木洞新市区所在的西南部", "feature": "木洞公寓区和阳川乡校"}
                },
                "favorite_count": 3, "latitude": 37.5169, "longitude": 126.8664
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "영등포구", "description": "여의도와 타임스퀘어가 있는 서남부", "feature": "여의도 금융가와 타임스퀘어"},
                    "en": {"name": "Yeongdeungpo-gu", "description": "Southwestern area with Yeouido and Times Square", "feature": "Yeouido financial district and Times Square"},
                    "jp": {"name": "永登浦区", "description": "汝矣島とタイムズスクエアがある西南部", "feature": "汝矣島金融街とタイムズスクエア"},
                    "cn": {"name": "永登浦区", "description": "汝矣岛和时代广场所在的西南部", "feature": "汝矣岛金融区和时代广场"}
                },
                "favorite_count": 8, "latitude": 37.5264, "longitude": 126.8962
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "용산구", "description": "국제적인 비즈니스 지역", "feature": "용산역과 국제비즈니스지구"},
                    "en": {"name": "Yongsan-gu", "description": "International business district", "feature": "Yongsan Station and IBD"},
                    "jp": {"name": "龍山区", "description": "国際的なビジネス地域", "feature": "龍山駅と国際ビジネス地区"},
                    "cn": {"name": "龙山区", "description": "国际商务区", "feature": "龙山站和国际商务区"}
                },
                "favorite_count": 10, "latitude": 37.5326, "longitude": 126.9906
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "은평구", "description": "불광동과 연신내가 있는 서북부", "feature": "북한산 자락과 연신내 뉴타운"},
                    "en": {"name": "Eunpyeong-gu", "description": "Northwestern area with Bulgwang and Yeonsinnae", "feature": "Bukhansan foothills and Yeonsinnae new town"},
                    "jp": {"name": "恩平区", "description": "仏光洞と延新内がある西北部", "feature": "北漢山麓と延新内ニュータウン"},
                    "cn": {"name": "恩平区", "description": "佛光洞和延新内所在的西北部", "feature": "北汉山脚下和延新内新城"}
                },
                "favorite_count": 4, "latitude": 37.6026, "longitude": 126.9292
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "종로구", "description": "서울의 역사적 중심지", "feature": "궁궐과 전통문화의 보고"},
                    "en": {"name": "Jongno-gu", "description": "Historic center of Seoul", "feature": "Home to palaces and traditional culture"},
                    "jp": {"name": "鐘路区", "description": "ソウルの歴史的中心地", "feature": "宮殿と伝統文化の宝庫"},
                    "cn": {"name": "钟路区", "description": "首尔历史中心", "feature": "宫殿和传统文化宝库"}
                },
                "favorite_count": 18, "latitude": 37.5735, "longitude": 126.9788
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "중구", "description": "서울의 중심 상업지역", "feature": "명동과 남대문 쇼핑의 메카"},
                    "en": {"name": "Jung-gu", "description": "Central business district", "feature": "Shopping paradise with Myeongdong"},
                    "jp": {"name": "中区", "description": "ソウルの中心商業地域", "feature": "明洞と南大門ショッピングのメッカ"},
                    "cn": {"name": "中区", "description": "首尔中心商业区", "feature": "明洞和南大门购物天堂"}
                },
                "favorite_count": 14, "latitude": 37.5636, "longitude": 126.9977
            },
            {
                "region_id": 1,
                "translations": {
                    "ko": {"name": "중랑구", "description": "중화역과 상봉역이 있는 동북부", "feature": "묵동과 면목동 주거지역"},
                    "en": {"name": "Jungnang-gu", "description": "Northeastern area with Junghwa and Sangbong stations", "feature": "Mukdong and Myeonmok residential areas"},
                    "jp": {"name": "中浪区", "description": "中和駅と上鳳駅がある東北部", "feature": "墨洞と面木洞住宅地域"},
                    "cn": {"name": "中浪区", "description": "中和站和上凤站所在的东北部", "feature": "墨洞和面木洞住宅区"}
                },
                "favorite_count": 3, "latitude": 37.6063, "longitude": 127.0925
            },

            # ======= 부산광역시 (16개 구/군) =======
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "강서구", "description": "김해공항이 있는 서부지역", "feature": "김해공항과 낙동강 하구"},
                    "en": {"name": "Gangseo-gu", "description": "Western area with Gimhae Airport", "feature": "Gimhae Airport and Nakdong River estuary"},
                    "jp": {"name": "江西区", "description": "金海空港がある西部地域", "feature": "金海空港と洛東江河口"},
                    "cn": {"name": "江西区", "description": "金海机场所在的西部地区", "feature": "金海机场和洛东江河口"}
                },
                "favorite_count": 3, "latitude": 35.2122, "longitude": 128.9802
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "금정구", "description": "금정산이 있는 북동부 지역", "feature": "금정산성과 범어사"},
                    "en": {"name": "Geumjeong-gu", "description": "Northeastern area with Geumjeongsan", "feature": "Geumjeong Fortress and Beomeosa Temple"},
                    "jp": {"name": "金井区", "description": "金井山がある北東部地域", "feature": "金井山城と梵魚寺"},
                    "cn": {"name": "金井区", "description": "金井山所在的东北部地区", "feature": "金井山城和梵鱼寺"}
                },
                "favorite_count": 4, "latitude": 35.2429, "longitude": 129.0927
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "남구", "description": "부산대학교와 경성대가 있는 지역", "feature": "부산대학교와 우암동 소막마을"},
                    "en": {"name": "Nam-gu", "description": "Area with Pusan National University", "feature": "Pusan National University and Uam-dong"},
                    "jp": {"name": "南区", "description": "釜山大学校と慶星大がある地域", "feature": "釜山大学校と牛岩洞小屋村"},
                    "cn": {"name": "南区", "description": "釜山大学和庆星大所在地区", "feature": "釜山大学和牛岩洞小屋村"}
                },
                "favorite_count": 5, "latitude": 35.1336, "longitude": 129.0840
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "동구", "description": "부산역과 초량이바구길이 있는 구도심", "feature": "부산역과 초량이바구길"},
                    "en": {"name": "Dong-gu", "description": "Old downtown with Busan Station", "feature": "Busan Station and Choryang Ibagu-gil"},
                    "jp": {"name": "東区", "description": "釜山駅と草梁イバグキルがある旧都心", "feature": "釜山駅と草梁イバグキル"},
                    "cn": {"name": "东区", "description": "釜山站和草梁故事路所在的老城区", "feature": "釜山站和草梁故事路"}
                },
                "favorite_count": 6, "latitude": 35.1295, "longitude": 129.0454
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "동래구", "description": "온천과 동래읍성이 있는 역사지역", "feature": "동래온천과 복천박물관"},
                    "en": {"name": "Dongnae-gu", "description": "Historic area with hot springs", "feature": "Dongnae Hot Springs and Bokcheon Museum"},
                    "jp": {"name": "東莱区", "description": "温泉と東莱邑城がある歴史地域", "feature": "東莱温泉と福泉博物館"},
                    "cn": {"name": "东莱区", "description": "温泉和东莱邑城所在的历史地区", "feature": "东莱温泉和福泉博物馆"}
                },
                "favorite_count": 6, "latitude": 35.2047, "longitude": 129.0824
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "부산진구", "description": "부산의 중심 상업지역", "feature": "서면 번화가와 쇼핑센터"},
                    "en": {"name": "Busanjin-gu", "description": "Central commercial district", "feature": "Seomyeon downtown and shopping centers"},
                    "jp": {"name": "釜山鎮区", "description": "釜山の中心商業地域", "feature": "西面繁華街とショッピングセンター"},
                    "cn": {"name": "釜山镇区", "description": "釜山中心商业区", "feature": "西面繁华街和购物中心"}
                },
                "favorite_count": 8, "latitude": 35.1621, "longitude": 129.0537
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "북구", "description": "화명과 덕천이 있는 북부지역", "feature": "화명생태공원과 낙동강"},
                    "en": {"name": "Buk-gu", "description": "Northern area with Hwamyeong and Deokcheon", "feature": "Hwamyeong Eco Park and Nakdong River"},
                    "jp": {"name": "北区", "description": "華明と徳川がある北部地域", "feature": "華明生態公園と洛東江"},
                    "cn": {"name": "北区", "description": "华明和德川所在的北部地区", "feature": "华明生态公园和洛东江"}
                },
                "favorite_count": 4, "latitude": 35.1967, "longitude": 128.9897
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "사상구", "description": "서부산터미널이 있는 교통중심지", "feature": "서부산터미널과 삼락생태공원"},
                    "en": {"name": "Sasang-gu", "description": "Transportation hub with West Busan Terminal", "feature": "West Busan Terminal and Samnak Eco Park"},
                    "jp": {"name": "沙上区", "description": "西釜山ターミナルがある交通中心地", "feature": "西釜山ターミナルと三楽生態公園"},
                    "cn": {"name": "沙上区", "description": "西釜山客运站所在的交通中心", "feature": "西釜山客运站和三乐生态公园"}
                },
                "favorite_count": 3, "latitude": 35.1478, "longitude": 128.9918
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "사하구", "description": "다대포해수욕장이 있는 서남부", "feature": "다대포해수욕장과 몰운대"},
                    "en": {"name": "Saha-gu", "description": "Southwestern area with Dadaepo Beach", "feature": "Dadaepo Beach and Molundae"},
                    "jp": {"name": "沙下区", "description": "多大浦海水浴場がある西南部", "feature": "多大浦海水浴場と没雲台"},
                    "cn": {"name": "沙下区", "description": "多大浦海水浴场所在的西南部", "feature": "多大浦海水浴场和没云台"}
                },
                "favorite_count": 4, "latitude": 35.1041, "longitude": 128.9743
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "서구", "description": "송도해수욕장과 암남공원이 있는 곳", "feature": "송도해수욕장과 부산항대교"},
                    "en": {"name": "Seo-gu", "description": "Area with Songdo Beach and Amnam Park", "feature": "Songdo Beach and Busan Harbor Bridge"},
                    "jp": {"name": "西区", "description": "松島海水浴場と岩南公園がある所", "feature": "松島海水浴場と釜山港大橋"},
                    "cn": {"name": "西区", "description": "松岛海水浴场和岩南公园所在地", "feature": "松岛海水浴场和釜山港大桥"}
                },
                "favorite_count": 5, "latitude": 35.0971, "longitude": 129.0244
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "수영구", "description": "광안리해수욕장이 있는 해안지역", "feature": "광안리해수욕장과 광안대교"},
                    "en": {"name": "Suyeong-gu", "description": "Coastal area with Gwangalli Beach", "feature": "Gwangalli Beach and Gwangan Bridge"},
                    "jp": {"name": "水営区", "description": "広安里海水浴場がある海岸地域", "feature": "広安里海水浴場と広安大橋"},
                    "cn": {"name": "水营区", "description": "广安里海水浴场所在的海岸地区", "feature": "广安里海水浴场和广安大桥"}
                },
                "favorite_count": 9, "latitude": 35.1451, "longitude": 129.1134
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "연제구", "description": "연산동과 거제동이 있는 중부지역", "feature": "시민공원과 연산동 먹거리타운"},
                    "en": {"name": "Yeonje-gu", "description": "Central area with Yeonsan and Geoje districts", "feature": "Citizens Park and Yeonsan food town"},
                    "jp": {"name": "蓮堤区", "description": "蓮山洞と巨堤洞がある中部地域", "feature": "市民公園と蓮山洞グルメタウン"},
                    "cn": {"name": "莲堤区", "description": "莲山洞和巨堤洞所在的中部地区", "feature": "市民公园和莲山洞美食城"}
                },
                "favorite_count": 4, "latitude": 35.1764, "longitude": 129.0755
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "영도구", "description": "태종대와 흰여울문화마을이 있는 섬", "feature": "태종대와 흰여울문화마을"},
                    "en": {"name": "Yeongdo-gu", "description": "Island with Taejongdae and Huinnyeoul Village", "feature": "Taejongdae and Huinnyeoul Culture Village"},
                    "jp": {"name": "影島区", "description": "太宗台と白如鷺文化村がある島", "feature": "太宗台と白如鷺文化村"},
                    "cn": {"name": "影岛区", "description": "太宗台和白如鸥文化村所在的岛屿", "feature": "太宗台和白如鸥文化村"}
                },
                "favorite_count": 7, "latitude": 35.0915, "longitude": 129.0679
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "중구", "description": "부산의 역사적 중심지", "feature": "자갈치시장과 부산항"},
                    "en": {"name": "Jung-gu", "description": "Historic center of Busan", "feature": "Jagalchi Market and Busan Port"},
                    "jp": {"name": "中区", "description": "釜山の歴史的中心地", "feature": "チャガルチ市場と釜山港"},
                    "cn": {"name": "中区", "description": "釜山历史中心", "feature": "札嘎其市场和釜山港"}
                },
                "favorite_count": 12, "latitude": 35.1069, "longitude": 129.0321
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "해운대구", "description": "부산의 대표 해변지역", "feature": "아름다운 해변과 리조트"},
                    "en": {"name": "Haeundae-gu", "description": "Famous beach district in Busan", "feature": "Beautiful beaches and resorts"},
                    "jp": {"name": "海雲台区", "description": "釜山の代表的なビーチ地域", "feature": "美しいビーチとリゾート"},
                    "cn": {"name": "海云台区", "description": "釜山著名海滩区", "feature": "美丽的海滩和度假村"}
                },
                "favorite_count": 15, "latitude": 35.1588, "longitude": 129.1603
            },
            {
                "region_id": 2,
                "translations": {
                    "ko": {"name": "기장군", "description": "해동용궁사와 죽성리가 있는 동쪽 끝", "feature": "해동용궁사와 일광해수욕장"},
                    "en": {"name": "Gijang-gun", "description": "Eastern area with Haedong Yonggungsa Temple", "feature": "Haedong Yonggungsa Temple and Ilgwang Beach"},
                    "jp": {"name": "機張郡", "description": "海東龍宮寺と竹城里がある東の端", "feature": "海東龍宮寺と日光海水浴場"},
                    "cn": {"name": "机张郡", "description": "海东龙宫寺和竹城里所在的东端", "feature": "海东龙宫寺和日光海水浴场"}
                },
                "favorite_count": 8, "latitude": 35.2448, "longitude": 129.2224
            },

            # ======= 인천광역시 (10개 구/군) =======
            {
                "region_id": 3,
                "translations": {
                    "ko": {"name": "계양구", "description": "계양산과 아라뱃길이 있는 북부", "feature": "계양산과 경인아라뱃길"},
                    "en": {"name": "Gyeyang-gu", "description": "Northern area with Gyeyangsan and Ara Waterway", "feature": "Gyeyangsan and Gyeongin Ara Waterway"},
                    "jp": {"name": "桂陽区", "description": "桂陽山とアラ船路がある北部", "feature": "桂陽山と京仁アラ船路"},
                    "cn": {"name": "桂阳区", "description": "桂阳山和阿拉船路所在的北部", "feature": "桂阳山和京仁阿拉船路"}
                },
                "favorite_count": 3, "latitude": 37.5376, "longitude": 126.7379
            },
            {
                "region_id": 3,
                "translations": {
                    "ko": {"name": "미추홀구", "description": "인천의 원도심 주안과 도화동", "feature": "주안역과 도화시장"},
                    "en": {"name": "Michuhol-gu", "description": "Original downtown with Juan and Dohwa", "feature": "Juan Station and Dohwa Market"},
                    "jp": {"name": "弥鄒忽区", "description": "仁川の元都心朱安と道化洞", "feature": "朱安駅と道化市場"},
                    "cn": {"name": "弥邹忽区", "description": "仁川原市中心朱安和道化洞", "feature": "朱安站和道化市场"}
                },
                "favorite_count": 4, "latitude": 37.4639, "longitude": 126.6505
            },
            {
                "region_id": 3,
                "translations": {
                    "ko": {"name": "남동구", "description": "구월동과 소래포구가 있는 남동부", "feature": "구월동 로데오거리와 소래포구"},
                    "en": {"name": "Namdong-gu", "description": "Southeastern area with Guwol and Sorae Port", "feature": "Guwol Rodeo Street and Sorae Port"},
                    "jp": {"name": "南東区", "description": "九月洞と蘇莱浦口がある南東部", "feature": "九月洞ロデオ通りと蘇莱浦口"},
                    "cn": {"name": "南东区", "description": "九月洞和苏莱浦口所在的东南部", "feature": "九月洞牛仔街和苏莱浦口"}
                },
                "favorite_count": 5, "latitude": 37.4468, "longitude": 126.7313
            },
            {
                "region_id": 3,
                "translations": {
                    "ko": {"name": "동구", "description": "만석동과 화수부두가 있는 구도심", "feature": "만석부두와 배다리 헌책방골목"},
                    "en": {"name": "Dong-gu", "description": "Old downtown with Manseok and Hwasu Pier", "feature": "Manseok Pier and Baedari used bookstore alley"},
                    "jp": {"name": "東区", "description": "万石洞と花水埠頭がある旧都心", "feature": "万石埠頭と船橋古本屋横丁"},
                    "cn": {"name": "东区", "description": "万石洞和花水码头所在的老城区", "feature": "万石码头和船桥旧书店胡同"}
                },
                "favorite_count": 3, "latitude": 37.4737, "longitude": 126.6433
            },
            {
                "region_id": 3,
                "translations": {
                    "ko": {"name": "부평구", "description": "부평역과 부평깡통시장이 있는 중심가", "feature": "부평깡통시장과 부평문화거리"},
                    "en": {"name": "Bupyeong-gu", "description": "Central area with Bupyeong Station and Can Market", "feature": "Bupyeong Can Market and Culture Street"},
                    "jp": {"name": "富平区", "description": "富平駅と富平カン通市場がある中心街", "feature": "富平カン通市場と富平文化通り"},
                    "cn": {"name": "富平区", "description": "富平站和富平罐头市场所在的市中心", "feature": "富平罐头市场和富平文化街"}
                },
                "favorite_count": 6, "latitude": 37.5074, "longitude": 126.7221
            },
            {
                "region_id": 3,
                "translations": {
                    "ko": {"name": "서구", "description": "검단과 가좌동이 있는 서북부", "feature": "검단신도시와 가정역"},
                    "en": {"name": "Seo-gu", "description": "Northwestern area with Geomdan and Gajwa", "feature": "Geomdan New City and Gajeong Station"},
                    "jp": {"name": "西区", "description": "検丹と加佐洞がある西北部", "feature": "検丹新都市と加佐駅"},
                    "cn": {"name": "西区", "description": "检丹和加佐洞所在的西北部", "feature": "检丹新城和加佐站"}
                },
                "favorite_count": 4, "latitude": 37.5456, "longitude": 126.6765
            },
            {
                "region_id": 3,
                "translations": {
                    "ko": {"name": "연수구", "description": "인천의 신도시 지역", "feature": "송도국제도시와 컨벤시아"},
                    "en": {"name": "Yeonsu-gu", "description": "New town area of Incheon", "feature": "Songdo International City and Convensia"},
                    "jp": {"name": "延寿区", "description": "仁川のニュータウン地域", "feature": "松島国際都市とコンベンシア"},
                    "cn": {"name": "延寿区", "description": "仁川新城区", "feature": "松岛国际城市和会展中心"}
                },
                "favorite_count": 8, "latitude": 37.4106, "longitude": 126.6784
            },
            {
                "region_id": 3,
                "translations": {
                    "ko": {"name": "중구", "description": "인천의 역사와 문화 중심지", "feature": "차이나타운과 인천항"},
                    "en": {"name": "Jung-gu", "description": "Historic and cultural center", "feature": "Chinatown and Incheon Port"},
                    "jp": {"name": "中区", "description": "仁川の歴史と文化の中心地", "feature": "チャイナタウンと仁川港"},
                    "cn": {"name": "中区", "description": "仁川历史文化中心", "feature": "唐人街和仁川港"}
                },
                "favorite_count": 10, "latitude": 37.4738, "longitude": 126.6216
            },
            {
                "region_id": 3,
                "translations": {
                    "ko": {"name": "강화군", "description": "강화도와 역사유적이 있는 섬지역", "feature": "강화도와 고인돌유적"},
                    "en": {"name": "Ganghwa-gun", "description": "Island area with Ganghwa Island and historic sites", "feature": "Ganghwa Island and dolmen sites"},
                    "jp": {"name": "江華郡", "description": "江華島と歴史遺跡がある島地域", "feature": "江華島と支石墓遺跡"},
                    "cn": {"name": "江华郡", "description": "江华岛和历史遗迹所在的岛屿地区", "feature": "江华岛和巨石墓遗址"}
                },
                "favorite_count": 6, "latitude": 37.7473, "longitude": 126.4877
            },
            {
                "region_id": 3,
                "translations": {
                    "ko": {"name": "옹진군", "description": "백령도와 연평도가 있는 도서지역", "feature": "백령도와 대청도"},
                    "en": {"name": "Ongjin-gun", "description": "Island region with Baengnyeong and Yeonpyeong Islands", "feature": "Baengnyeong Island and Daecheong Island"},
                    "jp": {"name": "甕津郡", "description": "白翎島と延坪島がある島嶼地域", "feature": "白翎島と大青島"},
                    "cn": {"name": "瓮津郡", "description": "白翎岛和延坪岛所在的岛屿地区", "feature": "白翎岛和大青岛"}
                },
                "favorite_count": 2, "latitude": 37.4463, "longitude": 126.6374
            },

            # ======= 경기도 (주요 시/군만 선별) =======
            # 수원시 (4개 구)
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "수원시 장안구", "description": "수원 북부의 장안문 일대", "feature": "장안문과 화성행궁"},
                    "en": {"name": "Suwon Jangan-gu", "description": "Northern Suwon with Janganmun Gate", "feature": "Janganmun Gate and Hwaseong Haenggung"},
                    "jp": {"name": "水原市長安区", "description": "水原北部の長安門一帯", "feature": "長安門と華城行宮"},
                    "cn": {"name": "水原市长安区", "description": "水原北部长安门一带", "feature": "长安门和华城行宫"}
                },
                "favorite_count": 5, "latitude": 37.3006, "longitude": 127.0106
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "수원시 권선구", "description": "수원 서남부의 권선동 일대", "feature": "수원월드컵경기장과 인계동"},
                    "en": {"name": "Suwon Gwonseon-gu", "description": "Southwestern Suwon with Gwonseon district", "feature": "Suwon World Cup Stadium and Ingye-dong"},
                    "jp": {"name": "水原市勧善区", "description": "水原西南部の勧善洞一帯", "feature": "水原ワールドカップ競技場と仁溪洞"},
                    "cn": {"name": "水原市劝善区", "description": "水原西南部劝善洞一带", "feature": "水原世界杯体育场和仁溪洞"}
                },
                "favorite_count": 4, "latitude": 37.2618, "longitude": 126.9732
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "수원시 팔달구", "description": "수원화성의 중심 구역", "feature": "화성행궁과 팔달문"},
                    "en": {"name": "Suwon Paldal-gu", "description": "Central district of Hwaseong Fortress", "feature": "Hwaseong Haenggung and Paldalmun"},
                    "jp": {"name": "水原市八達区", "description": "水原華城の中心区域", "feature": "華城行宮と八達門"},
                    "cn": {"name": "水原市八达区", "description": "水原华城的中心区域", "feature": "华城行宫和八达门"}
                },
                "favorite_count": 8, "latitude": 37.2794, "longitude": 127.0136
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "수원시 영통구", "description": "영통과 광교신도시가 있는 동남부", "feature": "광교신도시와 삼성전자"},
                    "en": {"name": "Suwon Yeongtong-gu", "description": "Southeastern area with Yeongtong and Gwanggyo", "feature": "Gwanggyo New City and Samsung Electronics"},
                    "jp": {"name": "水原市霊通区", "description": "霊通と光教新都市がある東南部", "feature": "光教新都市とサムスン電子"},
                    "cn": {"name": "水原市灵通区", "description": "灵通和光教新城所在的东南部", "feature": "光教新城和三星电子"}
                },
                "favorite_count": 9, "latitude": 37.2434, "longitude": 127.0469
            },

            # 성남시 (3개 구)
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "성남시 수정구", "description": "성남의 원도심 수정동 일대", "feature": "성남시청과 탄천"},
                    "en": {"name": "Seongnam Sujeong-gu", "description": "Original downtown of Seongnam", "feature": "Seongnam City Hall and Tancheon"},
                    "jp": {"name": "城南市寿井区", "description": "城南の元都心寿井洞一帯", "feature": "城南市庁と炭川"},
                    "cn": {"name": "城南市寿井区", "description": "城南原市中心寿井洞一带", "feature": "城南市政府和炭川"}
                },
                "favorite_count": 4, "latitude": 37.4500, "longitude": 127.1464
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "성남시 중원구", "description": "성남 중심부의 상업지역", "feature": "성남중앙시장과 신흥역"},
                    "en": {"name": "Seongnam Jungwon-gu", "description": "Central commercial area of Seongnam", "feature": "Seongnam Central Market and Sinheung Station"},
                    "jp": {"name": "城南市中院区", "description": "城南中心部の商業地域", "feature": "城南中央市場と新興駅"},
                    "cn": {"name": "城南市中院区", "description": "城南中心部商业区", "feature": "城南中央市场和新兴站"}
                },
                "favorite_count": 5, "latitude": 37.4278, "longitude": 127.1378
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "성남시 분당구", "description": "IT와 첨단산업의 중심", "feature": "판교테크노밸리와 분당신도시"},
                    "en": {"name": "Seongnam Bundang-gu", "description": "IT and high-tech industry hub", "feature": "Pangyo Techno Valley and Bundang New City"},
                    "jp": {"name": "城南市盆唐区", "description": "ITと先端産業の中心", "feature": "板橋テクノバレーと盆唐ニュータウン"},
                    "cn": {"name": "城南市盆唐区", "description": "IT和高科技产业中心", "feature": "板桥科技谷和盆唐新城"}
                },
                "favorite_count": 12, "latitude": 37.3826, "longitude": 127.1197
            },

            # 고양시 (3개 구)
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "고양시 덕양구", "description": "고양의 서부지역과 원도심", "feature": "화정역과 대화동 주거단지"},
                    "en": {"name": "Goyang Deogyang-gu", "description": "Western area and original downtown of Goyang", "feature": "Hwajeong Station and Daehwa residential complex"},
                    "jp": {"name": "高陽市徳陽区", "description": "高陽の西部地域と元都心", "feature": "花井駅と大化洞住宅団地"},
                    "cn": {"name": "高阳市德阳区", "description": "高阳西部地区和原市中心", "feature": "花井站和大化洞住宅区"}
                },
                "favorite_count": 4, "latitude": 37.6364, "longitude": 126.8327
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "고양시 일산동구", "description": "일산신도시 동쪽 지역", "feature": "정발산역과 장항습지"},
                    "en": {"name": "Goyang Ilsandong-gu", "description": "Eastern area of Ilsan New City", "feature": "Jeongbalsan Station and Janghang Wetland"},
                    "jp": {"name": "高陽市一山東区", "description": "一山新都市東側地域", "feature": "井足山駅と長項湿地"},
                    "cn": {"name": "高阳市一山东区", "description": "一山新城东部地区", "feature": "井足山站和长项湿地"}
                },
                "favorite_count": 8, "latitude": 37.6583, "longitude": 126.7711
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "고양시 일산서구", "description": "일산신도시 서쪽 지역", "feature": "킨텍스와 호수공원"},
                    "en": {"name": "Goyang Ilsanseo-gu", "description": "Western area of Ilsan New City", "feature": "KINTEX and Lake Park"},
                    "jp": {"name": "高陽市一山西区", "description": "一山新都市西側地域", "feature": "キンテックスと湖水公園"},
                    "cn": {"name": "高阳市一山西区", "description": "一山新城西部地区", "feature": "韩国国际展览中心和湖水公园"}
                },
                "favorite_count": 9, "latitude": 37.6694, "longitude": 126.7607
            },

            # 용인시 (3개 구)
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "용인시 처인구", "description": "용인의 원도심과 에버랜드", "feature": "에버랜드와 한국민속촌"},
                    "en": {"name": "Yongin Cheoin-gu", "description": "Original downtown of Yongin with Everland", "feature": "Everland and Korean Folk Village"},
                    "jp": {"name": "龍仁市処仁区", "description": "龍仁の元都心とエバーランド", "feature": "エバーランドと韓国民俗村"},
                    "cn": {"name": "龙仁市处仁区", "description": "龙仁原市中心和爱宝乐园", "feature": "爱宝乐园和韩国民俗村"}
                },
                "favorite_count": 12, "latitude": 37.2348, "longitude": 127.2020
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "용인시 기흥구", "description": "기흥신도시와 보정동 일대", "feature": "신갈오거리와 영덕숲"},
                    "en": {"name": "Yongin Giheung-gu", "description": "Giheung New City and Bojeong area", "feature": "Singal Intersection and Yeongdeok Forest"},
                    "jp": {"name": "龍仁市器興区", "description": "器興新都市と保正洞一帯", "feature": "新葛五差路と永徳の森"},
                    "cn": {"name": "龙仁市器兴区", "description": "器兴新城和保正洞一带", "feature": "新葛五岔路和永德森林"}
                },
                "favorite_count": 7, "latitude": 37.2759, "longitude": 127.1157
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "용인시 수지구", "description": "분당과 인접한 고급 주거지역", "feature": "수지구청과 성복동"},
                    "en": {"name": "Yongin Suji-gu", "description": "Upscale residential area near Bundang", "feature": "Suji District Office and Seongbok-dong"},
                    "jp": {"name": "龍仁市水枝区", "description": "盆唐と隣接した高級住宅地域", "feature": "水枝区庁と聖福洞"},
                    "cn": {"name": "龙仁市水枝区", "description": "与盆唐相邻的高档住宅区", "feature": "水枝区厅和圣福洞"}
                },
                "favorite_count": 8, "latitude": 37.3244, "longitude": 127.0979
            },

            # 안산시 (2개 구)
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "안산시 상록구", "description": "안산 동쪽의 신도시 지역", "feature": "중앙역과 안산식물원"},
                    "en": {"name": "Ansan Sangnok-gu", "description": "Eastern new city area of Ansan", "feature": "Jungang Station and Ansan Botanical Garden"},
                    "jp": {"name": "安山市常緑区", "description": "安山東側の新都市地域", "feature": "中央駅と安山植物園"},
                    "cn": {"name": "安山市常绿区", "description": "安山东部新城区", "feature": "中央站和安山植物园"}
                },
                "favorite_count": 4, "latitude": 37.2969, "longitude": 126.8307
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "안산시 단원구", "description": "안산 서쪽의 원도심과 공단", "feature": "안산역과 시화호"},
                    "en": {"name": "Ansan Danwon-gu", "description": "Western original downtown and industrial complex", "feature": "Ansan Station and Sihwa Lake"},
                    "jp": {"name": "安山市檀園区", "description": "安山西側の元都心と工団", "feature": "安山駅と始華湖"},
                    "cn": {"name": "安山市檀园区", "description": "安山西部原市中心和工业园区", "feature": "安山站和始华湖"}
                },
                "favorite_count": 3, "latitude": 37.3136, "longitude": 126.8016
            },

            # 안양시 (2개 구)
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "안양시 만안구", "description": "안양의 서쪽 구시가지", "feature": "안양역과 안양천"},
                    "en": {"name": "Anyang Manan-gu", "description": "Western old town of Anyang", "feature": "Anyang Station and Anyangcheon"},
                    "jp": {"name": "安養市万安区", "description": "安養の西側旧市街地", "feature": "安養駅と安養川"},
                    "cn": {"name": "安养市万安区", "description": "安养西部老城区", "feature": "安养站和安养川"}
                },
                "favorite_count": 4, "latitude": 37.3897, "longitude": 126.9507
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "안양시 동안구", "description": "안양의 동쪽 신시가지", "feature": "평촌신도시와 인덕원"},
                    "en": {"name": "Anyang Dongan-gu", "description": "Eastern new town of Anyang", "feature": "Pyeongchon New City and Indeogwon"},
                    "jp": {"name": "安養市東安区", "description": "安養の東側新市街地", "feature": "坪村新都市と仁徳院"},
                    "cn": {"name": "安养市东安区", "description": "安养东部新城区", "feature": "坪村新城和仁德院"}
                },
                "favorite_count": 6, "latitude": 37.3914, "longitude": 126.9568
            },

            # 기타 경기도 주요 도시들
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "부천시", "description": "서울과 인접한 위성도시", "feature": "부천역과 중동신도시"},
                    "en": {"name": "Bucheon-si", "description": "Satellite city adjacent to Seoul", "feature": "Bucheon Station and Jungdong New City"},
                    "jp": {"name": "富川市", "description": "ソウルと隣接した衛星都市", "feature": "富川駅と中洞新都市"},
                    "cn": {"name": "富川市", "description": "与首尔相邻的卫星城市", "feature": "富川站和中洞新城"}
                },
                "favorite_count": 6, "latitude": 37.5036, "longitude": 126.7660
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "평택시", "description": "경기 남부의 교통요지", "feature": "평택역과 평택항"},
                    "en": {"name": "Pyeongtaek-si", "description": "Transportation hub in southern Gyeonggi", "feature": "Pyeongtaek Station and Pyeongtaek Port"},
                    "jp": {"name": "平沢市", "description": "京畿南部の交通要地", "feature": "平沢駅と平沢港"},
                    "cn": {"name": "平泽市", "description": "京畿南部交通要地", "feature": "平泽站和平泽港"}
                },
                "favorite_count": 4, "latitude": 36.9923, "longitude": 127.1129
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "화성시", "description": "동탄신도시와 남양만", "feature": "동탄신도시와 제부도"},
                    "en": {"name": "Hwaseong-si", "description": "Dongtan New City and Namyang Bay", "feature": "Dongtan New City and Jebudo Island"},
                    "jp": {"name": "華城市", "description": "東灘新都市と南陽湾", "feature": "東灘新都市と堤夫島"},
                    "cn": {"name": "华城市", "description": "东滩新城和南阳湾", "feature": "东滩新城和堤夫岛"}
                },
                "favorite_count": 5, "latitude": 37.1996, "longitude": 126.8311
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "시흥시", "description": "시화신도시와 월곶포구", "feature": "배곧신도시와 월곶포구"},
                    "en": {"name": "Siheung-si", "description": "Sihwa New City and Wolgot Port", "feature": "Baegot New City and Wolgot Port"},
                    "jp": {"name": "始興市", "description": "始華新都市と月串浦口", "feature": "排串新都市と月串浦口"},
                    "cn": {"name": "始兴市", "description": "始华新城和月串浦口", "feature": "排串新城和月串浦口"}
                },
                "favorite_count": 3, "latitude": 37.3802, "longitude": 126.8031
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "파주시", "description": "DMZ와 임진각이 있는 북부 접경지역", "feature": "임진각과 헤이리마을"},
                    "en": {"name": "Paju-si", "description": "Northern border area with DMZ and Imjingak", "feature": "Imjingak and Heyri Art Village"},
                    "jp": {"name": "坡州市", "description": "DMZと臨津閣がある北部接境地域", "feature": "臨津閣とヘイリ芸術村"},
                    "cn": {"name": "坡州市", "description": "DMZ和临津阁所在的北部边境地区", "feature": "临津阁和海里艺术村"}
                },
                "favorite_count": 7, "latitude": 37.7598, "longitude": 126.7800
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "광명시", "description": "KTX 광명역이 있는 서남부", "feature": "KTX광명역과 광명동굴"},
                    "en": {"name": "Gwangmyeong-si", "description": "Southwestern area with KTX Gwangmyeong Station", "feature": "KTX Gwangmyeong Station and Gwangmyeong Cave"},
                    "jp": {"name": "光明市", "description": "KTX光明駅がある西南部", "feature": "KTX光明駅と光明洞窟"},
                    "cn": {"name": "光明市", "description": "KTX光明站所在的西南部", "feature": "KTX光明站和光明洞窟"}
                },
                "favorite_count": 3, "latitude": 37.4784, "longitude": 126.8644
            },
            {
                "region_id": 4,
                "translations": {
                    "ko": {"name": "김포시", "description": "김포공항과 한강이 있는 서북부", "feature": "김포공항과 애기봉"},
                    "en": {"name": "Gimpo-si", "description": "Northwestern area with Gimpo Airport and Han River", "feature": "Gimpo Airport and Aegibong Peak"},
                    "jp": {"name": "金浦市", "description": "金浦空港と漢江がある西北部", "feature": "金浦空港と愛岐峰"},
                    "cn": {"name": "金浦市", "description": "金浦机场和汉江所在的西北部", "feature": "金浦机场和爱岐峰"}
                },
                "favorite_count": 4, "latitude": 37.6150, "longitude": 126.7155
            },

            # ======= 제주특별자치도 (2개 시) =======
            {
                "region_id": 5,
                "translations": {
                    "ko": {"name": "제주시", "description": "제주도의 중심도시", "feature": "한라산과 성산일출봉"},
                    "en": {"name": "Jeju-si", "description": "Main city of Jeju Island", "feature": "Hallasan and Seongsan Ilchulbong"},
                    "jp": {"name": "済州市", "description": "済州島の中心都市", "feature": "漢拏山と城山日出峰"},
                    "cn": {"name": "济州市", "description": "济州岛中心城市", "feature": "汉拿山和城山日出峰"}
                },
                "favorite_count": 20, "latitude": 33.4996, "longitude": 126.5312
            },
            {
                "region_id": 5,
                "translations": {
                    "ko": {"name": "서귀포시", "description": "제주 남부의 관광도시", "feature": "중문관광단지와 천지연폭포"},
                    "en": {"name": "Seogwipo-si", "description": "Southern tourist city of Jeju", "feature": "Jungmun Resort and Cheonjiyeon Falls"},
                    "jp": {"name": "西帰浦市", "description": "済州南部の観光都市", "feature": "中文観光団地と天地淵滝"},
                    "cn": {"name": "西归浦市", "description": "济州南部旅游城市", "feature": "中文旅游区和天地渊瀑布"}
                },
                "favorite_count": 18, "latitude": 33.2541, "longitude": 126.5600
            }
        ]

        # 기존 데이터 삭제 (중복 방지)
        self.stdout.write("🗑️  기존 데이터 정리 중...")
        SubRegionTranslation.objects.all().delete()
        SubRegion.objects.all().delete()
        RegionTranslation.objects.all().delete()
        Region.objects.all().delete()

        # 지역 생성
        self.stdout.write("🏙️  지역 데이터 생성 중...")
        for region_data in regions_data:
            region = Region.objects.create(id=region_data["id"])
            self.stdout.write(f"✅ Region {region.id} 생성")

            # 번역 생성
            for lang, trans_data in region_data["translations"].items():
                translation = RegionTranslation.objects.create(
                    region=region,
                    lang=lang,
                    name=trans_data["name"],
                    description=trans_data["description"]
                )
                self.stdout.write(f"  ✅ {lang}: {trans_data['name']}")

        # 서브지역 생성
        self.stdout.write("🏘️  서브지역 데이터 생성 중...")
        for subregion_data in subregions_data:
            region = Region.objects.get(id=subregion_data["region_id"])

            subregion = SubRegion.objects.create(
                region=region,
                favorite_count=subregion_data["favorite_count"],
                latitude=subregion_data["latitude"],
                longitude=subregion_data["longitude"]
            )

            # 서브지역 번역 생성 (모든 언어)
            for lang, trans_data in subregion_data["translations"].items():
                SubRegionTranslation.objects.create(
                    sub_region=subregion,
                    lang=lang,
                    name=trans_data["name"],
                    description=trans_data["description"],
                    features=trans_data["feature"]
                )

            korean_name = subregion_data["translations"]["ko"]["name"]
            self.stdout.write(f"✅ SubRegion {subregion.id}: {korean_name}")

        self.stdout.write("🎉 전체 지역 데이터 로딩 완료!")

        # 최종 확인
        self.stdout.write(f"📊 생성된 데이터:")
        self.stdout.write(f"   - Region: {Region.objects.count()}개")
        self.stdout.write(f"   - RegionTranslation: {RegionTranslation.objects.count()}개")
        self.stdout.write(f"   - SubRegion: {SubRegion.objects.count()}개")
        self.stdout.write(f"   - SubRegionTranslation: {SubRegionTranslation.objects.count()}개")
