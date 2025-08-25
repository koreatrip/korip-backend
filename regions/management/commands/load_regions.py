from django.core.management.base import BaseCommand
from regions.models import Region, RegionTranslation, SubRegion, SubRegionTranslation
from django.contrib.gis.geos import Point


class Command(BaseCommand):
    help = "전국 17개 시도와 모든 구/군 데이터를 로드합니다."

    def handle(self, *args, **options):
        self.stdout.write("🇰🇷 전국 지역 데이터 로딩 시작...")

        # 전국 17개 시도 지역 데이터 정의
        regions_data = [
            # 특별시/광역시 (8개)
            {"id": 1, "tour_api_code": "1", "translations": {
                "ko": {"name": "서울특별시", "description": "전통과 현대가 공존하는 도시", "feature": "대한민국의 수도이자, 문화·경제·정치의 중심지입니다. 고궁과 한옥마을, 현대적인 쇼핑몰과 마천루, 트렌디한 카페 골목과 전통시장까지 다양한 매력을 하루 안에 모두 경험할 수 있는 도시입니다."},
                "en": {"name": "Seoul", "description": "A City Where Tradition and Modernity Coexist", "feature": "As the capital of South Korea, Seoul is the center of culture, economy, and politics. It's a city where you can experience a diverse range of attractions all in one day, from ancient palaces and traditional Hanok villages to modern shopping malls and skyscrapers."},
                "jp": {"name": "ソウル特別市", "description": "伝統と現代が共存する都市", "feature": "大韓民国の首都であり、文化・経済・政治の中心地です。古宮や韓屋村、現代的なショッピングモールや高層ビル、トレンディなカフェ通りや伝統市場まで、多様な魅力を一日で体験できる都市です。"},
                "cn": {"name": "首尔特别市", "description": "传统与现代共存的都市", "feature": "作为韩国的首都，是文化、经济、政治的中心。从古宫和韩屋村，到现代化的购物中心和摩天大楼，再到新潮的咖啡街和传统市场，这座城市让您能在一天之内体验其万千魅力。"}
            }},
            {"id": 2, "tour_api_code": "2", "translations": {
                "ko": {"name": "인천광역시", "description": "하늘과 바다가 만나는 관문 도시", "feature": "대한민국의 관문, 인천국제공항이 위치한 도시입니다. 아름다운 서해의 섬들과 개항기 역사가 살아있는 차이나타운, 송도 국제도시의 미래적인 스카이라인 등 과거와 미래가 공존하는 특별한 경험을 선사합니다."},
                "en": {"name": "Incheon", "description": "Gateway City Where Sky Meets Sea", "feature": "Home to Incheon International Airport, the gateway to Korea. It offers unique experiences where past and future coexist, featuring beautiful islands of the West Sea, a historic Chinatown from the port's opening era, and the futuristic skyline of Songdo International City."},
                "jp": {"name": "仁川広域市", "description": "空と海が出会う玄関都市", "feature": "大韓民国の玄関口、仁川国際空港が位置する都市です。美しい西海の島々や開港期の歴史が息づくチャイナタウン、松島国際都市の未来的なスカイラインなど、過去と未来が共存する特別な経験を提供します。"},
                "cn": {"name": "仁川广域市", "description": "天空与大海交汇的门户城市", "feature": "这里是韩国的门户，仁川国际机场的所在地。美丽的西海诸岛、开港时期历史气息浓郁的唐人街、松岛国际城的未来派天际线等，为您呈现过去与未来共存的特别体验。"}
            }},
            {"id": 3, "tour_api_code": "3", "translations": {
                "ko": {"name": "대전광역시", "description": "대한민국의 미래를 여는 과학 도시", "feature": "대한민국 과학 기술의 심장부로, 대덕연구단지와 KAIST가 자리하고 있습니다. 국립중앙과학관에서 과학의 신비를 체험하고, 한밭수목원에서 도심 속 여유를 즐길 수 있는 지적인 매력의 도시입니다."},
                "en": {"name": "Daejeon", "description": "Science and technology hub in central Korea", "feature": ""},
                "jp": {"name": "大田広域市", "description": "大韓民国の未来を開く科学都市", "feature": "大韓民国科学技術の心臓部で、大徳研究団地とKAISTが位置しています。国立中央科学館で科学の神秘を体験し、ハンバッ樹木園で都心の中の余裕を楽しむことができる知的な魅力の都市です。"},
                "cn": {"name": "大田广域市", "description": "开启韩国未来的科学之城", "feature": "作为韩国科学技术的心脏，大德研究园区和韩国科学技术院（KAIST）坐落于此。在国立中央科学馆体验科学的奥秘，在韩밭树木园享受都市中的闲暇，是一座充满知性魅力的城市。"}
            }},
            {"id": 4, "tour_api_code": "4", "translations": {
                "ko": {"name": "대구광역시", "description": "열정과 젊음이 넘치는 패션 도시", "feature": "과거 섬유 산업의 중심지에서 이제는 대한민국 문화 트렌드를 이끄는 도시로 거듭났습니다. 동성로의 활기찬 거리, 김광석 거리의 감성, 팔공산의 아름다운 자연 속에서 대구의 뜨거운 에너지를 느껴보세요."},
                "en": {"name": "Daegu", "description": "A Fashionable City Full of Passion and Youth", "feature": "Once the center of the textile industry, Daegu has transformed into a city leading Korea's cultural trends. Feel the vibrant energy of Daegu on the lively streets of Dongseongno, the nostalgic Kim Kwang-seok Street, and within the beautiful nature of Palgongsan Mountain."},
                "jp": {"name": "大邱広域市", "description": "情熱と若さあふれるファッション都市", "feature": "過去の繊維産業の中心地から、今や大韓民国の文化トレンドをリードする都市へと生まれ変わりました。東城路の活気ある通り、キム・グァンソク通りの感性、八公山の美しい自然の中で、大邱の熱いエネルギーを感じてみてください。"},
                "cn": {"name": "大邱广域市", "description": "充满热情与活力的时尚之都", "feature": "从过去的纺织工业中心，如今已蜕变为引领韩国文化潮流的城市。在东城路充满活力的街头、在金光石路的感性氛围中、在八公山美丽的自然风光里，感受大邱的火热能量吧。"}
            }},
            {"id": 5, "tour_api_code": "5", "translations": {
                "ko": {"name": "광주광역시", "description": "예술과 민주주의, 맛의 고장", "feature": "예로부터 예향(藝鄕)이라 불린 예술의 도시이자 대한민국 민주주의의 성지입니다. 세계적인 광주 비엔날레와 아시아문화전당에서 예술적 영감을 얻고, 풍요로운 남도 음식으로 미식 여행을 완성해보세요."},
                "en": {"name": "Gwangju", "description": "The Home of Arts, Democracy, and Flavor", "feature": "Known as the 'Home of Arts' and a sacred site for Korean democracy. Gain artistic inspiration from the world-renowned Gwangju Biennale and the Asia Culture Center, and complete your culinary journey with rich Namdo cuisine."},
                "jp": {"name": "光州広域市", "description": "芸術と民主主義、味の故郷", "feature": "古くから芸郷と呼ばれた芸術の都市であり、大韓民国民主主義の聖地です。世界的な光州ビエンナーレやアジア文化殿堂で芸術的なインスピレーションを得て、豊かな南道料理で美食の旅を完成させてみてください。"},
                "cn": {"name": "光州广域市", "description": "艺术、民主与美食之乡", "feature": "自古便被称为“艺乡”的艺术之都，同时也是韩国民主主义的圣地。在世界性的光州双年展和亚洲文化殿堂获取艺术灵感，再以丰盛的南道美食为您的美食之旅画上圆满的句号。"}
            }},
            {"id": 6, "tour_api_code": "6", "translations": {
                "ko": {"name": "부산광역시", "description": "바다와 영화, 낭만의 도시", "feature": "대한민국 제2의 도시이자 최대 항구도시입니다. 끝없이 펼쳐진 해운대와 광안리 해변, 신선한 해산물이 가득한 자갈치 시장, 세계적인 영화제가 열리는 영화의 전당까지, 부산의 낭만은 끝이 없습니다."},
                "en": {"name": "Busan", "description": "City of Sea, Film, and Romance", "feature": "South Korea's second-largest city and largest port. From the vast Haeundae and Gwangalli beaches and Jagalchi Market full of fresh seafood to the Busan Cinema Center where international film festivals are held, the city's romance is endless."},
                "jp": {"name": "釜山広域市", "description": "海と映画、ロマンの都市", "feature": "大韓民国第2の都市であり、最大の港町です。果てしなく広がる海雲台と広安里のビーチ、新鮮な海産物でいっぱいのチャガルチ市場、世界的な映画祭が開かれる映画の殿堂まで、釜山のロマンは尽きることがありません。"},
                "cn": {"name": "釜山广域市", "description": "海洋、电影与浪漫之都", "feature": "韩国第二大城市及最大港口城市。从一望无际的海云台和广安里海滩，到满是新鲜海产的札嘎其市场，再到举办世界级电影节的电影殿堂，釜山的浪漫永不止息。"}
            }},
            {"id": 7, "tour_api_code": "7", "translations": {
                "ko": {"name": "울산광역시", "description": "산업의 심장, 자연과 함께 숨쉬다", "feature": "세계적인 자동차, 조선 산업의 중심지인 동시에 아름다운 생태 환경을 자랑합니다. 태화강 국가정원에서 십리대숲을 거닐고, 장생포에서 고래를 만나고, 간절곶에서 가장 먼저 떠오르는 해를 맞이해보세요."},
                "en": {"name": "Ulsan", "description": "The Heart of Industry, Breathing with Nature", "feature": "A global hub for the automotive and shipbuilding industries that also boasts a beautiful ecological environment. Stroll through the bamboo forest at Taehwagang National Garden, meet whales at Jangsaengpo, and greet the earliest sunrise at Ganjeolgot Cape."},
                "jp": {"name": "蔚山広域市", "description": "産業の心臓、自然と共に息づく", "feature": "世界的な自動車、造船産業の中心地であると同時に、美しい生態環境を誇ります。太和江国家庭園で十里竹林を散策し、長生浦でクジラに会い、艮絶岬で最も早く昇る太陽を迎えてみてください。"},
                "cn": {"name": "蔚山广역市", "description": "产业心脏，与自然同呼吸", "feature": "这里是世界级的汽车、造船产业中心，同时拥有优美的生态环境。漫步于太和江国家花园的十里竹林，在长生浦邂逅鲸鱼，在艮绝岬迎接第一缕曙光。"}
            }},
            {"id": 8, "tour_api_code": "8", "translations": {
                "ko": {"name": "세종특별자치시", "description": "스마트 행정수도, 여유로운 삶의 중심", "feature": "대한민국의 새로운 행정 중심지로, 젊고 계획된 스마트 도시입니다. 아시아 최대 규모의 인공호수인 세종호수공원을 중심으로 녹지 공간이 풍부하여, 쾌적하고 여유로운 도시 여행을 즐길 수 있습니다."},
                "en": {"name": "Sejong Special Self-Governing City", "description": "The Smart Administrative Capital, Center of a Relaxed Life",
                       "feature": "As the new administrative heart of South Korea, Sejong is a young and well-planned smart city. Centered around Sejong Lake Park, the largest man-made lake in Asia, it offers abundant green spaces for a pleasant and leisurely city trip."},
                "jp": {"name": "世宗特別自治市", "description": "スマート行政首都、ゆとりのある生活の中心", "feature": "大韓民国の新しい行政中心地で、若くて計画的なスマート都市です。アジア最大規模の人工湖である世宗湖水公園を中心に緑地空間が豊富で、快適でゆとりのある都市旅行を楽しむことができます。"},
                "cn": {"name": "世宗特别自治市", "description": "智能行政首都，悠闲生活的中心", "feature": "作为韩国新的行政中心，是一座年轻且规划完善的智能城市。以亚洲最大的人工湖世宗湖水公园为中心，绿地空间丰富，让您能享受到舒适惬意的城市之旅。"}
            }},

            # 도 지역 (9개)
            {"id": 9, "tour_api_code": "31", "translations": {
                "ko": {"name": "경기도", "description": "수도권을 아우르는 다채로운 매력", "feature": "서울을 감싸고 있는 경기도는 유네스코 세계문화유산인 수원화성부터 현대적인 도시, 아름다운 자연 휴양림까지 각양각색의 여행지를 품고 있습니다. 다이나믹한 도시 여행과 평화로운 자연 속 휴식을 동시에 즐겨보세요."},
                "en": {"name": "Gyeonggi Province", "description": "Diverse Charms Embracing the Capital Area", "feature": "Surrounding Seoul, Gyeonggi Province offers a wide variety of destinations, from the UNESCO World Heritage Suwon Hwaseong Fortress to modern cities and beautiful natural recreation forests. Enjoy both dynamic city tours and peaceful relaxation in nature."},
                "jp": {"name": "京畿道", "description": "首都圏を網羅する多彩な魅力", "feature": "ソウルを取り囲む京畿道は、ユネスコ世界文化遺産の水原華城から現代的な都市、美しい自然休養林まで、様々な旅行地を抱いています。ダイナミックな都市旅行と、平和な自然の中での休息を同時に楽しんでみてください。"},
                "cn": {"name": "京畿道", "description": "环绕首都圈的多元魅力", "feature": "环绕着首尔的京畿道，拥有从联合国教科文组织世界文化遗产水原华城到现代化都市、美丽的自然休养林等各式各样的旅游景点。在这里，您可以同时享受到充满活力的城市旅游与宁静自然中的休憩。"}
            }},
            {"id": 10, "tour_api_code": "32", "translations": {
                "ko": {"name": "강원특별자치도", "description": "산과 바다가 그린 청정 자연의 쉼터", "feature": "설악산, 오대산 등 웅장한 산맥과 푸른 동해바다가 어우러진 천혜의 자연을 자랑합니다. 사계절 내내 레저 스포츠를 즐길 수 있으며, 깨끗한 공기와 고요한 분위기 속에서 완벽한 힐링을 경험할 수 있습니다."},
                "en": {"name": "Gangwon Special Self-Governing Province",
                       "description": "A Haven of Clean Nature Painted by Mountains and Sea", "feature": "Boasting a natural paradise where majestic mountain ranges like Seoraksan and Odaesan meet the blue East Sea. You can enjoy leisure sports all year round and experience perfect healing amidst clean air and a tranquil atmosphere."},
                "jp": {"name": "江原特別自治道", "description": "山と海が描く清浄な自然の休息地", "feature": "雪岳山、五台山などの壮大な山脈と青い東海が調和した天恵の自然を誇ります。四季を通じてレジャースポーツを楽しむことができ、きれいな空気と静かな雰囲気の中で完璧な癒しを体験できます。"},
                "cn": {"name": "江原特别自治道", "description": "山海描绘的清净自然休憩地", "feature": "雪岳山、五台山等雄伟的山脉与蔚蓝的东海相映成趣，拥有得天独厚的自然风光。这里一年四季都可享受休闲运动，在清新的空气和宁静的氛围中体验完美的治愈之旅。"}
            }},
            {"id": 11, "tour_api_code": "33", "translations": {
                "ko": {"name": "충청북도", "description": "호수와 산이 어우러진 내륙의 보석", "feature": "바다가 없는 대신 충주호, 대청호 등 아름다운 호수가 마음을 사로잡는 곳입니다. 월악산, 속리산 국립공원의 절경을 감상하고, 고즈넉한 법주사에서 평화로운 시간을 보내기에 완벽한 여행지입니다."},
                "en": {"name": "Chungcheongbuk-do", "description": "An Inland Jewel of Lakes and Mountains", "feature": "Though without a sea, its beautiful lakes like Chungjuho and Daecheongho captivate the heart. It's the perfect destination to admire the stunning scenery of Woraksan and Songnisan National Parks and to spend a peaceful time at the serene Beopjusa Temple."},
                "jp": {"name": "忠清北道", "description": "湖と山が調和した内陸の宝石", "feature": "海がない代わりに、忠州湖、大清湖などの美しい湖が心を捉える場所です。月岳山、俗離山国立公園の絶景を鑑賞し、静かな法住寺で平和な時間を過ごすのに最適な旅行地です。"},
                "cn": {"name": "忠清北道", "description": "湖光山色相映的内陆瑰宝", "feature": "这里虽然没有大海，但忠州湖、大清湖等美丽的湖泊却令人心醉。欣赏月岳山、俗离山国立公园的绝景，在宁静的法住寺度过平和的时光，是完美的旅游目的地。"}
            }},
            {"id": 12, "tour_api_code": "34", "translations": {
                "ko": {"name": "충청남도", "description": "백제의 숨결과 서해의 낭만이 깃든 곳", "feature": "찬란했던 백제 문화의 중심지로 공주와 부여에 수많은 유적이 남아있습니다. 세계적인 보령머드축제를 즐기고, 태안의 아름다운 해변을 따라 드라이브하며 서해의 고즈넉한 낭만을 만끽할 수 있습니다."},
                "en": {"name": "Chungcheongnam-do", "description": "Where the Spirit of Baekje and the Romance of the West Sea Reside", "feature": "As the center of the brilliant Baekje culture, numerous historical sites remain in Gongju and Buyeo. You can enjoy the world-famous Boryeong Mud Festival and savor the tranquil romance of the West Sea while driving along the beautiful coastline of Taean."},
                "jp": {"name": "忠清南道", "description": "百済の息吹と西海のロマンが宿る場所", "feature": "輝かしい百済文化の中心地で、公州と扶余に数多くの遺跡が残っています。世界的な保寧マッドフェスティバルを楽しみ、泰安の美しいビーチに沿ってドライブしながら、西海の静かなロマンを満喫できます。"},
                "cn": {"name": "忠清南道", "description": "百济气息与西海浪漫的栖息地", "feature": "作为灿烂百济文化的中心，公州和扶余留下了无数遗迹。您可以在世界性的保宁泥浆节尽情狂欢，也可以沿着泰安美丽的海岸线驱车，享受西海宁静的浪漫。"}
            }},
            {"id": 13, "tour_api_code": "35", "translations": {
                "ko": {"name": "경상북도", "description": "신라의 역사와 유교 문화의 본고장", "feature": "천년고도 경주와 선비 정신이 살아있는 안동을 품은, 한국 정신문화의 뿌리입니다. 하회마을에서 전통을 체험하고, 동해안의 웅장한 해안 절경을 따라 낭만적인 드라이브를 즐겨보세요."},
                "en": {"name": "Gyeongsangbuk-do", "description": "The Cradle of Silla History and Confucian Culture", "feature": "The root of Korean spiritual culture, embracing the ancient capital Gyeongju and Andong, where the spirit of the seonbi (scholar) lives on. Experience tradition at Hahoe Village and enjoy a romantic drive along the majestic coastline of the East Sea."},
                "jp": {"name": "慶尚北道", "description": "新羅の歴史と儒教文化の本場", "feature": "千年古都の慶州と、ソンビの精神が生きる安東を抱いた、韓国精神文化の根源です。河回村で伝統を体験し、東海沿岸の壮大な海岸絶景に沿ってロマンチックなドライブを楽しんでみてください。"},
                "cn": {"name": "庆尚北道", "description": "新罗历史与儒教文化的发源地", "feature": "怀抱千年古都庆州与儒生精神传承地安东，是韩国精神文化的根基。在河回村体验传统，沿着东海岸雄壮的海岸绝景享受浪漫的驾车之旅。"}
            }},
            {"id": 14, "tour_api_code": "36", "translations": {
                "ko": {"name": "경상남도", "description": "남해의 비경과 첨단 산업이 공존하는 곳", "feature": "한려해상국립공원의 그림 같은 풍경과 거제, 통영, 남해 등 아름다운 섬들이 가득합니다. 지리산의 웅장함을 느끼고, 창원의 계획된 도시미를 둘러보는 등 다채로운 매력을 가진 지역입니다."},
                "en": {"name": "Gyeongsangnam-do", "description": "Where the Scenic Beauty of the South Sea Meets High-Tech Industry",
                       "feature": "Filled with the picturesque scenery of Hallyeohaesang National Park and beautiful islands like Geoje, Tongyeong, and Namhae. It is a region of diverse charms, where you can feel the majesty of Jirisan Mountain and explore the planned urban beauty of Changwon."},
                "jp": {"name": "慶尚南道", "description": "南海の秘境と先端産業が共存する場所", "feature": "閑麗海上国立公園の絵のような風景と、巨済、統営、南海などの美しい島々がいっぱいです。智異山の雄大さを感じ、昌原の計画的な都市美を巡るなど、多彩な魅力を持つ地域です。"},
                "cn": {"name": "庆尚南道", "description": "南海秘境与尖端产业共存之地", "feature": "拥有闲丽海上国立公园如画的风景，以及巨济、统营、南海等美丽的岛屿。在这里可以感受智异山的雄伟，也可以领略昌原的规划城市之美，是一个充满多彩魅力的地区。"}
            }},
            {"id": 15, "tour_api_code": "37", "translations": {
                "ko": {"name": "전북특별자치도", "description": "한국의 맛과 멋이 살아있는 풍요의 땅", "feature": "전주 한옥마을의 고풍스러운 멋과 풍성한 먹거리, 내장산의 황홀한 단풍까지. 한국의 전통과 자연의 아름다움이 가장 잘 보존된 곳 중 하나로, 오감을 만족시키는 풍요로운 여행을 약속합니다."},
                "en": {"name": "Jeonbuk Special Self-Governing Province",
                       "description": "A Land of Plenty Where Korean Flavor and Style Come Alive", "feature": "From the classic beauty and rich cuisine of Jeonju Hanok Village to the breathtaking autumn foliage of Naejangsan Mountain. It is one of the best-preserved places of Korean tradition and natural beauty, promising a fulfilling journey that satisfies all five senses."},
                "jp": {"name": "全北特別自治道", "description": "韓国の味と趣が生きる豊饒の地", "feature": "全州韓屋村の古風な趣と豊かなグルメ、内蔵山の幻想的な紅葉まで。韓国の伝統と自然の美しさが最もよく保存されている場所の一つで、五感を満たす豊かな旅行を約束します。"},
                "cn": {"name": "全北特别自治道", "description": "韩国风味与格调盎然的丰饶之地", "feature": "从全州韩屋村的古朴风情和丰富美食，到内藏山令人陶醉的枫叶。这里是韩国传统与自然之美保存最完好的地方之一，承诺为您带来一场满足五感的丰盛之旅。"}
            }},
            {"id": 16, "tour_api_code": "38", "translations": {
                "ko": {"name": "전라남도", "description": "쪽빛 바다와 녹색 평야가 펼쳐진 남도의 땅", "feature": "다도해의 수많은 섬들이 보석처럼 박힌 남해안과 보성 녹차밭의 푸른 물결이 인상적인 곳입니다. 대한민국 최고의 맛을 자랑하는 남도 한정식을 맛보며 느림의 미학을 경험할 수 있는 최고의 힐링 여행지입니다."},
                "en": {"name": "Jeollanam-do", "description": "The Southern Land of Indigo Seas and Green Plains", "feature": "A place of impressive scenery, featuring the jewel-like islands of the Dadohae archipelago and the green waves of the Boseong Green Tea Fields. It is the ultimate healing destination where you can experience the aesthetics of slowness while savoring the best of Korean cuisine."},
                "jp": {"name": "全羅南道", "description": "藍色の海と緑の平野が広がる南道の地", "feature": "多島海の数多くの島々が宝石のように散りばめられた南海沿岸と、宝城緑茶畑の青い波が印象的な場所です。大韓民国最高の味を誇る南道韓定食を味わいながら、スローライフの美学を体験できる最高のヒーリング旅行地です。"},
                "cn": {"name": "全罗南道", "description": "靛蓝大海与绿色平原展开的南道之地", "feature": "多岛海的无数岛屿如宝石般点缀在南海岸，宝城绿茶园的碧波荡漾，景象令人印象深刻。在这里品尝韩国最顶级的南道韩定食，体验慢生活的美学，是绝佳的治愈系旅游地。"}
            }},
            {"id": 17, "tour_api_code": "39", "translations": {
                "ko": {"name": "제주특별자치도", "description": "화산이 빚은 신비의 섬", "feature": "유네스코 세계자연유산에 빛나는 대한민국 최대의 섬. 한라산과 오름, 에메랄드빛 해변과 독특한 해안절경이 방문하는 모든 이들에게 잊지 못할 감동을 선사하는 최고의 휴양지입니다."},
                "en": {"name": "Jeju Special Self-Governing Province", "description": "The Mysterious Island Forged by a Volcano",
                       "feature": "South Korea's largest island and a shining UNESCO World Natural Heritage site. It is the ultimate vacation destination, offering unforgettable impressions to all visitors with Hallasan Mountain, numerous volcanic cones (oreum), and emerald beaches."},
                "jp": {"name": "済州特別自治道", "description": "火山が創り出した神秘の島", "feature": "ユネスコ世界自然遺産に輝く大韓民国最大の島。漢拏山とオルム、エメラルド色のビーチと独特の海岸絶景が、訪れるすべての人々に忘れられない感動を与える最高の休養地です。"},
                "cn": {"name": "济州特别自治道", "description": "火山塑造的神秘之岛", "feature": "作为联合国教科文组织世界自然遗产，是韩国最大的岛屿。汉拿山、岳麓、翡翠色的海滩和独特的海岸绝景，为所有到访者带来难忘的感动，是顶级的休养胜地。"}
            }},
        ]

        # 서브지역 데이터 (전체 구/군, 번역 포함)
        subregions_data = [

            # ======= 서울특별시 (25개 구) =======
            {
                "region_id": 1,
                "tour_api_subcode": "1",
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
                "tour_api_subcode": "2",
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
                "tour_api_subcode": "3",
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
                "tour_api_subcode": "4",
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
                "tour_api_subcode": "5",
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
                "tour_api_subcode": "6",
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
                "tour_api_subcode": "7",
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
                "tour_api_subcode": "8",
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
                "tour_api_subcode": "9",
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
                "tour_api_subcode": "10",
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
                "tour_api_subcode": "11",
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
                "tour_api_subcode": "12",
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
                "tour_api_subcode": "13",
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
                "tour_api_subcode": "14",
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
                "tour_api_subcode": "15",
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
                "tour_api_subcode": "16",
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
                "tour_api_subcode": "17",
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
                "tour_api_subcode": "18",
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
                "tour_api_subcode": "19",
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
                "tour_api_subcode": "20",
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
                "tour_api_subcode": "21",
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
                "tour_api_subcode": "22",
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
                "tour_api_subcode": "23",
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
                "tour_api_subcode": "24",
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
                "tour_api_subcode": "25",
                "translations": {
                    "ko": {"name": "중랑구", "description": "중화역과 상봉역이 있는 동북부", "feature": "묵동과 면목동 주거지역"},
                    "en": {"name": "Jungnang-gu", "description": "Northeastern area with Junghwa and Sangbong stations", "feature": "Mukdong and Myeonmok residential areas"},
                    "jp": {"name": "中浪区", "description": "中和駅と上鳳駅がある東北部", "feature": "墨洞と面木洞住宅地域"},
                    "cn": {"name": "中浪区", "description": "中和站和上凤站所在的东北部", "feature": "墨洞和面木洞住宅区"}
                },
                "favorite_count": 3, "latitude": 37.6063, "longitude": 127.0925
            },

            # ======= 인천광역시 (10개 구/군) =======
            {
                "region_id": 2,
                "tour_api_subcode": "1",
                "translations": {
                    "ko": {"name": "강화군", "description": "강화도와 역사유적이 있는 섬지역", "feature": "강화도와 고인돌유적"},
                    "en": {"name": "Ganghwa-gun", "description": "Island area with Ganghwa Island and historic sites", "feature": "Ganghwa Island and dolmen sites"},
                    "jp": {"name": "江華郡", "description": "江華島と歴史遺跡がある島地域", "feature": "江華島と支石墓遺跡"},
                    "cn": {"name": "江华郡", "description": "江华岛和历史遗迹所在的岛屿地区", "feature": "江华岛和巨石墓遗址"}
                },
                "favorite_count": 6, "latitude": 37.7473, "longitude": 126.4877
            },
            {
                "region_id": 2,
                "tour_api_subcode": "2",
                "translations": {
                    "ko": {"name": "계양구", "description": "계양산과 아라뱃길이 있는 북부", "feature": "계양산과 경인아라뱃길"},
                    "en": {"name": "Gyeyang-gu", "description": "Northern area with Gyeyangsan and Ara Waterway", "feature": "Gyeyangsan and Gyeongin Ara Waterway"},
                    "jp": {"name": "桂陽区", "description": "桂陽山とアラ船路がある北部", "feature": "桂陽山と京仁アラ船路"},
                    "cn": {"name": "桂阳区", "description": "桂阳山和阿拉船路所在的北部", "feature": "桂阳山和京仁阿拉船路"}
                },
                "favorite_count": 3, "latitude": 37.5376, "longitude": 126.7379
            },
            {
                "region_id": 2,
                "tour_api_subcode": "3",
                "translations": {
                    "ko": {"name": "미추홀구", "description": "인천의 원도심 주안과 도화동", "feature": "주안역과 도화시장"},
                    "en": {"name": "Michuhol-gu", "description": "Original downtown with Juan and Dohwa", "feature": "Juan Station and Dohwa Market"},
                    "jp": {"name": "弥鄒忽区", "description": "仁川の元都心朱安と道化洞", "feature": "朱安駅と道化市場"},
                    "cn": {"name": "弥邹忽区", "description": "仁川原市中心朱安和道化洞", "feature": "朱安站和道化市场"}
                },
                "favorite_count": 4, "latitude": 37.4639, "longitude": 126.6505
            },
            {
                "region_id": 2,
                "tour_api_subcode": "4",
                "translations": {
                    "ko": {"name": "남동구", "description": "구월동과 소래포구가 있는 남동부", "feature": "구월동 로데오거리와 소래포구"},
                    "en": {"name": "Namdong-gu", "description": "Southeastern area with Guwol and Sorae Port", "feature": "Guwol Rodeo Street and Sorae Port"},
                    "jp": {"name": "南東区", "description": "九月洞と蘇莱浦口がある南東部", "feature": "九月洞ロデオ通りと蘇莱浦口"},
                    "cn": {"name": "南东区", "description": "九月洞和苏莱浦口所在的东南部", "feature": "九月洞牛仔街和苏莱浦口"}
                },
                "favorite_count": 5, "latitude": 37.4468, "longitude": 126.7313
            },
            {
                "region_id": 2,
                "tour_api_subcode": "5",
                "translations": {
                    "ko": {"name": "동구", "description": "만석동과 화수부두가 있는 구도심", "feature": "만석부두와 배다리 헌책방골목"},
                    "en": {"name": "Dong-gu", "description": "Old downtown with Manseok and Hwasu Pier", "feature": "Manseok Pier and Baedari used bookstore alley"},
                    "jp": {"name": "東区", "description": "万石洞と花水埠頭がある旧都心", "feature": "万石埠頭と船橋古本屋横丁"},
                    "cn": {"name": "东区", "description": "万石洞和花水码头所在的老城区", "feature": "万石码头和船桥旧书店胡同"}
                },
                "favorite_count": 3, "latitude": 37.4737, "longitude": 126.6433
            },
            {
                "region_id": 2,
                "tour_api_subcode": "6",
                "translations": {
                    "ko": {"name": "부평구", "description": "부평역과 부평깡통시장이 있는 중심가", "feature": "부평깡통시장과 부평문화거리"},
                    "en": {"name": "Bupyeong-gu", "description": "Central area with Bupyeong Station and Can Market", "feature": "Bupyeong Can Market and Culture Street"},
                    "jp": {"name": "富平区", "description": "富平駅と富平カン通市場がある中心街", "feature": "富平カン通市場と富平文化通り"},
                    "cn": {"name": "富平区", "description": "富平站和富平罐头市场所在的市中心", "feature": "富平罐头市场和富平文化街"}
                },
                "favorite_count": 6, "latitude": 37.5074, "longitude": 126.7221
            },
            {
                "region_id": 2,
                "tour_api_subcode": "7",
                "translations": {
                    "ko": {"name": "서구", "description": "검단과 가좌동이 있는 서북부", "feature": "검단신도시와 가정역"},
                    "en": {"name": "Seo-gu", "description": "Northwestern area with Geomdan and Gajwa", "feature": "Geomdan New City and Gajeong Station"},
                    "jp": {"name": "西区", "description": "検丹と加佐洞がある西北部", "feature": "検丹新都市と加佐駅"},
                    "cn": {"name": "西区", "description": "检丹和加佐洞所在的西北部", "feature": "检丹新城和加佐站"}
                },
                "favorite_count": 4, "latitude": 37.5456, "longitude": 126.6765
            },
            {
                "region_id": 2,
                "tour_api_subcode": "8",
                "translations": {
                    "ko": {"name": "연수구", "description": "인천의 신도시 지역", "feature": "송도국제도시와 컨벤시아"},
                    "en": {"name": "Yeonsu-gu", "description": "New town area of Incheon", "feature": "Songdo International City and Convensia"},
                    "jp": {"name": "延寿区", "description": "仁川のニュータウン地域", "feature": "松島国際都市とコンベンシア"},
                    "cn": {"name": "延寿区", "description": "仁川新城区", "feature": "松岛国际城市和会展中心"}
                },
                "favorite_count": 8, "latitude": 37.4106, "longitude": 126.6784
            },
            {
                "region_id": 2,
                "tour_api_subcode": "9",
                "translations": {
                    "ko": {"name": "옹진군", "description": "백령도와 연평도가 있는 도서지역", "feature": "백령도와 대청도"},
                    "en": {"name": "Ongjin-gun", "description": "Island region with Baengnyeong and Yeonpyeong Islands", "feature": "Baengnyeong Island and Daecheong Island"},
                    "jp": {"name": "甕津郡", "description": "白翎島と延坪島がある島嶼地域", "feature": "白翎島と大青島"},
                    "cn": {"name": "瓮津郡", "description": "白翎岛和延坪岛所在的岛屿地区", "feature": "白翎岛和大青岛"}
                },
                "favorite_count": 2, "latitude": 37.4463, "longitude": 126.6374
            },
            {
                "region_id": 2,
                "tour_api_subcode": "10",
                "translations": {
                    "ko": {"name": "중구", "description": "인천의 역사와 문화 중심지", "feature": "차이나타운과 인천항"},
                    "en": {"name": "Jung-gu", "description": "Historic and cultural center", "feature": "Chinatown and Incheon Port"},
                    "jp": {"name": "中区", "description": "仁川の歴史と文化の中心地", "feature": "チャイナタウンと仁川港"},
                    "cn": {"name": "中区", "description": "仁川历史文化中心", "feature": "唐人街和仁川港"}
                },
                "favorite_count": 10, "latitude": 37.4738, "longitude": 126.6216
            },

            # ===== 대전광역시 (5개 구) =====
            {"region_id": 3, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "대덕구", "description": "대덕연구개발특구가 있는 북동부", "feature": "한국과학기술원(KAIST)과 연구단지"},
                "en": {"name": "Daedeok-gu", "description": "Northeast area with Daedeok R&D Special Zone",
                       "feature": "KAIST and research complex"},
                "jp": {"name": "大徳区", "description": "大徳研究開発特区がある北東部",
                       "feature": "韓国科学技術院(KAIST)と研究団地"},
                "cn": {"name": "大德区", "description": "大德研发特区所在的东北部",
                       "feature": "韩国科学技术院(KAIST)和研究园区"}
            }, "favorite_count": 4, "latitude": 36.3464, "longitude": 127.4151},

            {"region_id": 3, "tour_api_subcode": "2", "translations": {
                "ko": {"name": "동구", "description": "대전의 원도심 지역", "feature": "중앙시장과 대전역"},
                "en": {"name": "Dong-gu", "description": "Original downtown area of Daejeon",
                       "feature": "Central Market and Daejeon Station"},
                "jp": {"name": "東区", "description": "大田の元都心地域", "feature": "中央市場と大田駅"},
                "cn": {"name": "东区", "description": "大田原市中心区", "feature": "中央市场和大田站"}
            }, "favorite_count": 3, "latitude": 36.3504, "longitude": 127.4371},

            {"region_id": 3, "tour_api_subcode": "3", "translations": {
                "ko": {"name": "서구", "description": "대전시청이 있는 행정중심지", "feature": "대전시청과 만년동"},
                "en": {"name": "Seo-gu", "description": "Administrative center with Daejeon City Hall",
                       "feature": "Daejeon City Hall and Mannyeon-dong"},
                "jp": {"name": "西区", "description": "大田市庁がある行政中心地", "feature": "大田市庁と万年洞"},
                "cn": {"name": "西区", "description": "大田市政府所在的行政中心", "feature": "大田市政府和万年洞"}
            }, "favorite_count": 5, "latitude": 36.3551, "longitude": 127.3839},

            {"region_id": 3, "tour_api_subcode": "4", "translations": {
                "ko": {"name": "유성구", "description": "온천과 대학가가 있는 서북부", "feature": "유성온천과 충남대학교"},
                "en": {"name": "Yuseong-gu", "description": "Northwest area with hot springs and university district",
                       "feature": "Yuseong Hot Springs and Chungnam National University"},
                "jp": {"name": "儒城区", "description": "温泉と大学街がある西北部", "feature": "儒城温泉と忠南大学校"},
                "cn": {"name": "儒城区", "description": "温泉和大学区所在的西北部", "feature": "儒城温泉和忠南大学"}
            }, "favorite_count": 7, "latitude": 36.3624, "longitude": 127.3558},

            {"region_id": 3, "tour_api_subcode": "5", "translations": {
                "ko": {"name": "중구", "description": "대전의 중심 상업지역", "feature": "으네성과 중앙로 상권"},
                "en": {"name": "Jung-gu", "description": "Central commercial area of Daejeon",
                       "feature": "Eunhaseong and Jungang-ro commercial district"},
                "jp": {"name": "中区", "description": "大田の中心商業地域", "feature": "銀河城と中央路商圏"},
                "cn": {"name": "中区", "description": "大田中心商业区", "feature": "银河城和中央路商圈"}
            }, "favorite_count": 6, "latitude": 36.3255, "longitude": 127.4214},

            # ===== 대구광역시 (8개 구/군) =====
            {"region_id": 4, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "남구", "description": "앞산과 대명동이 있는 남부", "feature": "앞산공원과 대명공연문화거리"},
                "en": {"name": "Nam-gu", "description": "Southern area with Apsan and Daemyeong-dong",
                       "feature": "Apsan Park and Daemyeong Performance Culture Street"},
                "jp": {"name": "南区", "description": "前山と大明洞がある南部", "feature": "前山公園と大明公演文化街"},
                "cn": {"name": "南区", "description": "前山和大明洞所在的南部", "feature": "前山公园和大明演出文化街"}
            }, "favorite_count": 5, "latitude": 35.8464, "longitude": 128.5943},

            {"region_id": 4, "tour_api_subcode": "2", "translations": {
                "ko": {"name": "달서구", "description": "대구의 서남부 신도시", "feature": "월성동과 성서공단"},
                "en": {"name": "Dalseo-gu", "description": "Southwest new town of Daegu",
                       "feature": "Wolseong-dong and Seongso Industrial Complex"},
                "jp": {"name": "達西区", "description": "大邱の西南部新都市", "feature": "月城洞と城西工団"},
                "cn": {"name": "达西区", "description": "大邱西南部新城", "feature": "月城洞和城西工团"}
            }, "favorite_count": 4, "latitude": 35.8300, "longitude": 128.5323},

            {"region_id": 4, "tour_api_subcode": "3", "translations": {
                "ko": {"name": "달성군", "description": "대구 외곽의 농촌지역", "feature": "비슬산과 마비정벽화마을"},
                "en": {"name": "Dalseong-gun", "description": "Rural area on the outskirts of Daegu",
                       "feature": "Biseulsan Mountain and Mabijeong Mural Village"},
                "jp": {"name": "達城郡", "description": "大邱郊外の農村地域", "feature": "琵瑟山と馬飛亭壁画村"},
                "cn": {"name": "达城郡", "description": "大邱郊外农村地区", "feature": "琵瑟山和马飞亭壁画村"}
            }, "favorite_count": 3, "latitude": 35.7749, "longitude": 128.4314},

            {"region_id": 4, "tour_api_subcode": "4", "translations": {
                "ko": {"name": "동구", "description": "신천과 팔공산이 있는 동부", "feature": "신천둔치와 팔공산"},
                "en": {"name": "Dong-gu", "description": "Eastern area with Sincheon and Palgongsan",
                       "feature": "Sincheon Waterside Park and Palgongsan Mountain"},
                "jp": {"name": "東区", "description": "新川と八公山がある東部", "feature": "新川屯地と八公山"},
                "cn": {"name": "东区", "description": "新川和八公山所在的东部", "feature": "新川河滩和八公山"}
            }, "favorite_count": 4, "latitude": 35.8869, "longitude": 128.6357},

            {"region_id": 4, "tour_api_subcode": "5", "translations": {
                "ko": {"name": "북구", "description": "경북대학교가 있는 북부", "feature": "경북대학교와 칠성시장"},
                "en": {"name": "Buk-gu", "description": "Northern area with Kyungpook National University",
                       "feature": "Kyungpook National University and Chilseong Market"},
                "jp": {"name": "北区", "description": "慶北大学校がある北部", "feature": "慶北大学校と七星市場"},
                "cn": {"name": "北区", "description": "庆北大学所在的北部", "feature": "庆北大学和七星市场"}
            }, "favorite_count": 6, "latitude": 35.8858, "longitude": 128.5829},

            {"region_id": 4, "tour_api_subcode": "6", "translations": {
                "ko": {"name": "서구", "description": "계명대학교와 서문시장이 있는 서부", "feature": "서문시장과 계명대학교"},
                "en": {"name": "Seo-gu", "description": "Western area with Keimyung University and Seomun Market",
                       "feature": "Seomun Market and Keimyung University"},
                "jp": {"name": "西区", "description": "啓明大学校と西門市場がある西部",
                       "feature": "西門市場と啓明大学校"},
                "cn": {"name": "西区", "description": "启明大学和西门市场所在的西部", "feature": "西门市场和启明大学"}
            }, "favorite_count": 5, "latitude": 35.8717, "longitude": 128.5592},

            {"region_id": 4, "tour_api_subcode": "7", "translations": {
                "ko": {"name": "수성구", "description": "대구의 고급 주거지역", "feature": "수성못과 범어동"},
                "en": {"name": "Suseong-gu", "description": "Upscale residential area of Daegu",
                       "feature": "Suseong Lake and Beomeo-dong"},
                "jp": {"name": "寿城区", "description": "大邱の高級住宅地域", "feature": "寿城池と凡魚洞"},
                "cn": {"name": "寿城区", "description": "大邱高档住宅区", "feature": "寿城池和凡鱼洞"}
            }, "favorite_count": 8, "latitude": 35.8581, "longitude": 128.6305},

            {"region_id": 4, "tour_api_subcode": "8", "translations": {
                "ko": {"name": "중구", "description": "대구의 중심 상업지역", "feature": "동성로와 대구역"},
                "en": {"name": "Jung-gu", "description": "Central commercial area of Daegu",
                       "feature": "Dongseong-ro and Daegu Station"},
                "jp": {"name": "中区", "description": "大邱の中心商業地域", "feature": "東城路と大邱駅"},
                "cn": {"name": "中区", "description": "大邱中心商业区", "feature": "东城路和大邱站"}
            }, "favorite_count": 9, "latitude": 35.8663, "longitude": 128.5928},

            {"region_id": 4, "tour_api_subcode": "9", "translations": {
                "ko": {"name": "군위군", "description": "화산산성과 삼국유사테마파크가 있는 문화군", "feature": "화산산성과 삼국유사테마파크"},
                "en": {"name": "Gunwi-gun",
                       "description": "Cultural county with Hwasan Fortress and Samguk Yusa Theme Park",
                       "feature": "Hwasan Fortress and Samguk Yusa Theme Park"},
                "jp": {"name": "軍威郡", "description": "花山山城と三国遺事テーマパークがある文化郡",
                       "feature": "花山山城と三国遺事テーマパーク"},
                "cn": {"name": "军威郡", "description": "花山山城和三国遗事主题公园所在的文化郡",
                       "feature": "花山山城和三国遗事主题公园"}
            }, "favorite_count": 6, "latitude": 36.2365, "longitude": 128.5717},

            # ======= 광주광역시 (5개 구/군) =======
            {
                "region_id": 5,
                "tour_api_subcode": "1",
                "translations": {
                    "ko": {"name": "광산구", "description": "광주송정역과 1913송정역시장이 있는 서북부", "feature": "1913송정역시장과 광주송정역(KTX)"},
                    "en": {"name": "Gwangsan-gu", "description": "Northwestern area with Gwangju-Songjeong Station & 1913 Market", "feature": "1913 Songjeong Station Market and Gwangju-Songjeong Station"},
                    "jp": {"name": "光山区", "description": "光州松汀駅と1913松汀駅市場がある西北部", "feature": "1913松汀駅市場と光州松汀駅"},
                    "cn": {"name": "光山区", "description": "有光州松汀站和1913松汀站市场的西北部", "feature": "1913松汀站市场与光州松汀站"}
                },
                "favorite_count": 9, "latitude": 35.1616, "longitude": 126.8081
            },
            {
                "region_id": 5,
                "tour_api_subcode": "2",
                "translations": {
                    "ko": {"name": "남구", "description": "양림동 역사문화마을과 광주천이 있는 남부", "feature": "양림동 역사문화마을과 광주천"},
                    "en": {"name": "Nam-gu", "description": "Southern area with Yangnim-dong History Village & Gwangju Stream", "feature": "Yangnim-dong History & Culture Village and Gwangju Stream"},
                    "jp": {"name": "南区", "description": "楊林洞歴史文化村と光州川がある南部", "feature": "楊林洞歴史文化村と光州川"},
                    "cn": {"name": "南区", "description": "有杨林洞历史文化村和光州川的南部", "feature": "杨林洞历史文化村与光州川"}
                },
                "favorite_count": 7, "latitude": 35.1017, "longitude": 126.8892
            },
            {
                "region_id": 5,
                "tour_api_subcode": "3",
                "translations": {
                    "ko": {"name": "동구", "description": "국립아시아문화전당과 충장로가 있는 도심 동부", "feature": "국립아시아문화전당과 무등산(증심사 지구)"},
                    "en": {"name": "Dong-gu", "description": "Eastern downtown with ACC and Chungjang-ro", "feature": "Asia Culture Center & Mudeungsan (Jeungsimsa)"},
                    "jp": {"name": "東区", "description": "国立アジア文化殿堂と忠壮路がある都心東部", "feature": "国立アジア文化殿堂と無等山（證心寺）"},
                    "cn": {"name": "东区", "description": "拥有国立亚洲文化殿堂和忠壮路的市中心东部", "feature": "国立亚洲文化殿堂与无等山（证心寺）"}
                },
                "favorite_count": 6, "latitude": 35.1489, "longitude": 126.9142
            },
            {
                "region_id": 5,
                "tour_api_subcode": "4",
                "translations": {
                    "ko": {"name": "북구", "description": "중외공원과 비엔날레 전시관이 있는 북부", "feature": "광주비엔날레전시관과 중외공원"},
                    "en": {"name": "Buk-gu", "description": "Northern area with Jungoe Park & Biennale Hall", "feature": "Gwangju Biennale Exhibition Hall and Jungoe Park"},
                    "jp": {"name": "北区", "description": "中外公園とビエンナーレ展示館がある北部", "feature": "光州ビエンナーレ展示館と中外公園"},
                    "cn": {"name": "北区", "description": "有中外公园和光州双年展会馆的北部", "feature": "光州双年展展馆与中外公园"}
                },
                "favorite_count": 8, "latitude": 35.2103, "longitude": 126.8940
            },
            {
                "region_id": 5,
                "tour_api_subcode": "5",
                "translations": {
                    "ko": {"name": "서구", "description": "상무지구와 월드컵경기장이 있는 서부지역", "feature": "광주월드컵경기장과 상무지구"},
                    "en": {"name": "Seo-gu", "description": "Western area with Sangmu district & World Cup Stadium", "feature": "Gwangju World Cup Stadium and Sangmu"},
                    "jp": {"name": "西区", "description": "尚武地区とワールドカップ競技場がある西部地域", "feature": "ワールドカップ競技場と尚武地区"},
                    "cn": {"name": "西区", "description": "有尚武商圈和世界杯体育场的西部地区", "feature": "世界杯体育场与尚武商圈"}
                },
                "favorite_count": 5, "latitude": 35.1525, "longitude": 126.8911
            },

            # ======= 부산광역시 (16개 구/군) =======
            {
                "region_id": 6,
                "tour_api_subcode": "1",
                "translations": {
                    "ko": {"name": "강서구", "description": "김해공항이 있는 서부지역", "feature": "김해공항과 낙동강 하구"},
                    "en": {"name": "Gangseo-gu", "description": "Western area with Gimhae Airport", "feature": "Gimhae Airport and Nakdong River estuary"},
                    "jp": {"name": "江西区", "description": "金海空港がある西部地域", "feature": "金海空港と洛東江河口"},
                    "cn": {"name": "江西区", "description": "金海机场所在的西部地区", "feature": "金海机场和洛东江河口"}
                },
                "favorite_count": 3, "latitude": 35.2122, "longitude": 128.9802
            },
            {
                "region_id": 6,
                "tour_api_subcode": "2",
                "translations": {
                    "ko": {"name": "금정구", "description": "금정산이 있는 북동부 지역", "feature": "금정산성과 범어사"},
                    "en": {"name": "Geumjeong-gu", "description": "Northeastern area with Geumjeongsan", "feature": "Geumjeong Fortress and Beomeosa Temple"},
                    "jp": {"name": "金井区", "description": "金井山がある北東部地域", "feature": "金井山城と梵魚寺"},
                    "cn": {"name": "金井区", "description": "金井山所在的东北部地区", "feature": "金井山城和梵鱼寺"}
                },
                "favorite_count": 4, "latitude": 35.2429, "longitude": 129.0927
            },
            {
                "region_id": 6,
                "tour_api_subcode": "3",
                "translations": {
                    "ko": {"name": "기장군", "description": "해동용궁사와 죽성리가 있는 동쪽 끝", "feature": "해동용궁사와 일광해수욕장"},
                    "en": {"name": "Gijang-gun", "description": "Eastern area with Haedong Yonggungsa Temple", "feature": "Haedong Yonggungsa Temple and Ilgwang Beach"},
                    "jp": {"name": "機張郡", "description": "海東龍宮寺と竹城里がある東の端", "feature": "海東龍宮寺と日光海水浴場"},
                    "cn": {"name": "机张郡", "description": "海东龙宫寺和竹城里所在的东端", "feature": "海东龙宫寺和日光海水浴场"}
                },
                "favorite_count": 8, "latitude": 35.2448, "longitude": 129.2224
            },
            {
                "region_id": 6,
                "tour_api_subcode": "4",
                "translations": {
                    "ko": {"name": "남구", "description": "부산대학교와 경성대가 있는 지역", "feature": "부산대학교와 우암동 소막마을"},
                    "en": {"name": "Nam-gu", "description": "Area with Pusan National University", "feature": "Pusan National University and Uam-dong"},
                    "jp": {"name": "南区", "description": "釜山大学校と慶星大がある地域", "feature": "釜山大学校と牛岩洞小屋村"},
                    "cn": {"name": "南区", "description": "釜山大学和庆星大所在地区", "feature": "釜山大学和牛岩洞小屋村"}
                },
                "favorite_count": 5, "latitude": 35.1336, "longitude": 129.0840
            },
            {
                "region_id": 6,
                "tour_api_subcode": "5",
                "translations": {
                    "ko": {"name": "동구", "description": "부산역과 초량이바구길이 있는 구도심", "feature": "부산역과 초량이바구길"},
                    "en": {"name": "Dong-gu", "description": "Old downtown with Busan Station", "feature": "Busan Station and Choryang Ibagu-gil"},
                    "jp": {"name": "東区", "description": "釜山駅と草梁イバグキルがある旧都心", "feature": "釜山駅と草梁イバグキル"},
                    "cn": {"name": "东区", "description": "釜山站和草梁故事路所在的老城区", "feature": "釜山站和草梁故事路"}
                },
                "favorite_count": 6, "latitude": 35.1295, "longitude": 129.0454
            },
            {
                "region_id": 6,
                "tour_api_subcode": "6",
                "translations": {
                    "ko": {"name": "동래구", "description": "온천과 동래읍성이 있는 역사지역", "feature": "동래온천과 복천박물관"},
                    "en": {"name": "Dongnae-gu", "description": "Historic area with hot springs", "feature": "Dongnae Hot Springs and Bokcheon Museum"},
                    "jp": {"name": "東莱区", "description": "温泉と東莱邑城がある歴史地域", "feature": "東莱温泉と福泉博物館"},
                    "cn": {"name": "东莱区", "description": "温泉和东莱邑城所在的历史地区", "feature": "东莱温泉和福泉博物馆"}
                },
                "favorite_count": 6, "latitude": 35.2047, "longitude": 129.0824
            },
            {
                "region_id": 6,
                "tour_api_subcode": "7",
                "translations": {
                    "ko": {"name": "부산진구", "description": "부산의 중심 상업지역", "feature": "서면 번화가와 쇼핑센터"},
                    "en": {"name": "Busanjin-gu", "description": "Central commercial district", "feature": "Seomyeon downtown and shopping centers"},
                    "jp": {"name": "釜山鎮区", "description": "釜山の中心商業地域", "feature": "西面繁華街とショッピングセンター"},
                    "cn": {"name": "釜山镇区", "description": "釜山中心商业区", "feature": "西面繁华街和购物中心"}
                },
                "favorite_count": 8, "latitude": 35.1621, "longitude": 129.0537
            },
            {
                "region_id": 6,
                "tour_api_subcode": "8",
                "translations": {
                    "ko": {"name": "북구", "description": "화명과 덕천이 있는 북부지역", "feature": "화명생태공원과 낙동강"},
                    "en": {"name": "Buk-gu", "description": "Northern area with Hwamyeong and Deokcheon", "feature": "Hwamyeong Eco Park and Nakdong River"},
                    "jp": {"name": "北区", "description": "華明と徳川がある北部地域", "feature": "華明生態公園と洛東江"},
                    "cn": {"name": "北区", "description": "华明和德川所在的北部地区", "feature": "华明生态公园和洛东江"}
                },
                "favorite_count": 4, "latitude": 35.1967, "longitude": 128.9897
            },
            {
                "region_id": 6,
                "tour_api_subcode": "9",
                "translations": {
                    "ko": {"name": "사상구", "description": "서부산터미널이 있는 교통중심지", "feature": "서부산터미널과 삼락생태공원"},
                    "en": {"name": "Sasang-gu", "description": "Transportation hub with West Busan Terminal", "feature": "West Busan Terminal and Samnak Eco Park"},
                    "jp": {"name": "沙上区", "description": "西釜山ターミナルがある交通中心地", "feature": "西釜山ターミナルと三楽生態公園"},
                    "cn": {"name": "沙上区", "description": "西釜山客运站所在的交通中心", "feature": "西釜山客运站和三乐生态公园"}
                },
                "favorite_count": 3, "latitude": 35.1478, "longitude": 128.9918
            },
            {
                "region_id": 6,
                "tour_api_subcode": "10",
                "translations": {
                    "ko": {"name": "사하구", "description": "다대포해수욕장이 있는 서남부", "feature": "다대포해수욕장과 몰운대"},
                    "en": {"name": "Saha-gu", "description": "Southwestern area with Dadaepo Beach", "feature": "Dadaepo Beach and Molundae"},
                    "jp": {"name": "沙下区", "description": "多大浦海水浴場がある西南部", "feature": "多大浦海水浴場と没雲台"},
                    "cn": {"name": "沙下区", "description": "多大浦海水浴场所在的西南部", "feature": "多大浦海水浴场和没云台"}
                },
                "favorite_count": 4, "latitude": 35.1041, "longitude": 128.9743
            },
            {
                "region_id": 6,
                "tour_api_subcode": "11",
                "translations": {
                    "ko": {"name": "서구", "description": "송도해수욕장과 암남공원이 있는 곳", "feature": "송도해수욕장과 부산항대교"},
                    "en": {"name": "Seo-gu", "description": "Area with Songdo Beach and Amnam Park", "feature": "Songdo Beach and Busan Harbor Bridge"},
                    "jp": {"name": "西区", "description": "松島海水浴場と岩南公園がある所", "feature": "松島海水浴場と釜山港大橋"},
                    "cn": {"name": "西区", "description": "松岛海水浴场和岩南公园所在地", "feature": "松岛海水浴场和釜山港大桥"}
                },
                "favorite_count": 5, "latitude": 35.0971, "longitude": 129.0244
            },
            {
                "region_id": 6,
                "tour_api_subcode": "12",
                "translations": {
                    "ko": {"name": "수영구", "description": "광안리해수욕장이 있는 해안지역", "feature": "광안리해수욕장과 광안대교"},
                    "en": {"name": "Suyeong-gu", "description": "Coastal area with Gwangalli Beach", "feature": "Gwangalli Beach and Gwangan Bridge"},
                    "jp": {"name": "水営区", "description": "広安里海水浴場がある海岸地域", "feature": "広安里海水浴場と広安大橋"},
                    "cn": {"name": "水营区", "description": "广安里海水浴场所在的海岸地区", "feature": "广安里海水浴场和广安大桥"}
                },
                "favorite_count": 9, "latitude": 35.1451, "longitude": 129.1134
            },
            {
                "region_id": 6,
                "tour_api_subcode": "13",
                "translations": {
                    "ko": {"name": "연제구", "description": "연산동과 거제동이 있는 중부지역", "feature": "시민공원과 연산동 먹거리타운"},
                    "en": {"name": "Yeonje-gu", "description": "Central area with Yeonsan and Geoje districts", "feature": "Citizens Park and Yeonsan food town"},
                    "jp": {"name": "蓮堤区", "description": "蓮山洞と巨堤洞がある中部地域", "feature": "市民公園と蓮山洞グルメタウン"},
                    "cn": {"name": "莲堤区", "description": "莲山洞和巨堤洞所在的中部地区", "feature": "市民公园和莲山洞美食城"}
                },
                "favorite_count": 4, "latitude": 35.1764, "longitude": 129.0755
            },
            {
                "region_id": 6,
                "tour_api_subcode": "14",
                "translations": {
                    "ko": {"name": "영도구", "description": "태종대와 흰여울문화마을이 있는 섬", "feature": "태종대와 흰여울문화마을"},
                    "en": {"name": "Yeongdo-gu", "description": "Island with Taejongdae and Huinnyeoul Village", "feature": "Taejongdae and Huinnyeoul Culture Village"},
                    "jp": {"name": "影島区", "description": "太宗台と白如鷺文化村がある島", "feature": "太宗台と白如鷺文化村"},
                    "cn": {"name": "影岛区", "description": "太宗台和白如鸥文化村所在的岛屿", "feature": "太宗台和白如鸥文化村"}
                },
                "favorite_count": 7, "latitude": 35.0915, "longitude": 129.0679
            },
            {
                "region_id": 6,
                "tour_api_subcode": "15",
                "translations": {
                    "ko": {"name": "중구", "description": "부산의 역사적 중심지", "feature": "자갈치시장과 부산항"},
                    "en": {"name": "Jung-gu", "description": "Historic center of Busan", "feature": "Jagalchi Market and Busan Port"},
                    "jp": {"name": "中区", "description": "釜山の歴史的中心地", "feature": "チャガルチ市場と釜山港"},
                    "cn": {"name": "中区", "description": "釜山历史中心", "feature": "札嘎其市场和釜山港"}
                },
                "favorite_count": 12, "latitude": 35.1069, "longitude": 129.0321
            },
            {
                "region_id": 6,
                "tour_api_subcode": "16",
                "translations": {
                    "ko": {"name": "해운대구", "description": "부산의 대표 해변지역", "feature": "아름다운 해변과 리조트"},
                    "en": {"name": "Haeundae-gu", "description": "Famous beach district in Busan", "feature": "Beautiful beaches and resorts"},
                    "jp": {"name": "海雲台区", "description": "釜山の代表的なビーチ地域", "feature": "美しいビーチとリゾート"},
                    "cn": {"name": "海云台区", "description": "釜山著名海滩区", "feature": "美丽的海滩和度假村"}
                },
                "favorite_count": 15, "latitude": 35.1588, "longitude": 129.1603
            },

            # ======= 울산광역시 (5개 구/군) =======
            {"region_id": 7, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "중구", "description": "울산시청이 있는 행정중심지", "feature": "태화강과 울산시청"},
                "en": {"name": "Jung-gu", "description": "Administrative center with Ulsan City Hall",
                       "feature": "Taehwa River and Ulsan City Hall"},
                "jp": {"name": "中区", "description": "蔚山市庁がある行政中心地", "feature": "太和江と蔚山市庁"},
                "cn": {"name": "中区", "description": "蔚山市政府所在的行政中心", "feature": "太和江和蔚山市政府"}
            }, "favorite_count": 5, "latitude": 35.5665, "longitude": 129.3328},

            {"region_id": 7, "tour_api_subcode": "2", "translations": {
                "ko": {"name": "남구", "description": "울산의 중심 상업지역", "feature": "신정시장과 삼산동"},
                "en": {"name": "Nam-gu", "description": "Central commercial area of Ulsan",
                       "feature": "Sinjeong Market and Samsan-dong"},
                "jp": {"name": "南区", "description": "蔚山の中心商業地域", "feature": "新井市場と三山洞"},
                "cn": {"name": "南区", "description": "蔚山中心商业区", "feature": "新井市场和三山洞"}
            }, "favorite_count": 5, "latitude": 35.5467, "longitude": 129.3293},

            {"region_id": 7, "tour_api_subcode": "3", "translations": {
                "ko": {"name": "동구", "description": "울산의 원도심과 현대중공업", "feature": "현대중공업과 일산해수욕장"},
                "en": {"name": "Dong-gu", "description": "Original downtown of Ulsan and Hyundai Heavy Industries",
                       "feature": "Hyundai Heavy Industries and Ilsan Beach"},
                "jp": {"name": "東区", "description": "蔚山の元都心と現代重工業",
                       "feature": "現代重工業と一山海水浴場"},
                "cn": {"name": "东区", "description": "蔚山原市中心和现代重工业", "feature": "现代重工业和日山海水浴场"}
            }, "favorite_count": 4, "latitude": 35.5049, "longitude": 129.4164},

            {"region_id": 7, "tour_api_subcode": "4", "translations": {
                "ko": {"name": "북구", "description": "울산대학교와 정자해수욕장이 있는 북부", "feature": "울산대학교와 정자해수욕장"},
                "en": {"name": "Buk-gu", "description": "Northern area with University of Ulsan and Jeongja Beach",
                       "feature": "University of Ulsan and Jeongja Beach"},
                "jp": {"name": "北区", "description": "蔚山大学校と亭子海水浴場がある北部",
                       "feature": "蔚山大学校と亭子海水浴場"},
                "cn": {"name": "北区", "description": "蔚山大学和亭子海水浴场所在的北部",
                       "feature": "蔚山大学和亭子海水浴场"}
            }, "favorite_count": 6, "latitude": 35.5825, "longitude": 129.3615},

            {"region_id": 7, "tour_api_subcode": "5", "translations": {
                "ko": {"name": "울주군", "description": "간절곶과 영남알프스가 있는 외곽", "feature": "간절곶과 신불산"},
                "en": {"name": "Ulju-gun", "description": "Outskirts with Ganjeolgot and Yeongnam Alps",
                       "feature": "Ganjeolgot Cape and Sinbulsan Mountain"},
                "jp": {"name": "蔚州郡", "description": "艮絶岬と嶺南アルプスがある郊外", "feature": "艮絶岬と神仏山"},
                "cn": {"name": "蔚州郡", "description": "艮绝岬和岭南阿尔卑斯所在的郊外", "feature": "艮绝岬和神佛山"}
            }, "favorite_count": 8, "latitude": 35.5219, "longitude": 129.2427},

            # ===== 세종특별자치시 (1개 시) =====
            {"region_id": 8, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "세종시", "description": "대한민국의 행정수도", "feature": "정부세종청사와 호수공원"},
                "en": {"name": "Sejong City", "description": "Administrative capital of South Korea",
                       "feature": "Government Sejong Complex and Lake Park"},
                "jp": {"name": "世宗市", "description": "大韓民国の行政首都", "feature": "政府世宗庁舎と湖水公園"},
                "cn": {"name": "世宗市", "description": "大韩民国行政首都", "feature": "政府世宗办公楼和湖水公园"}
            }, "favorite_count": 10, "latitude": 36.4875, "longitude": 127.2831},

            # ===== 경기도 (31개 시/군) =====
            {"region_id": 9, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "가평군", "description": "북한강과 자라섬이 있는 휴양지", "feature": "자라섬과 아침고요수목원"},
                "en": {"name": "Gapyeong-gun", "description": "Resort area with Bukhan River and Jara Island",
                       "feature": "Jara Island and Garden of Morning Calm"},
                "jp": {"name": "加平郡", "description": "北漢江と自羅島がある休養地",
                       "feature": "自羅島と朝の静けさ樹木園"},
                "cn": {"name": "加平郡", "description": "北汉江和自拉岛所在的休养地", "feature": "自拉岛和晨静树木园"}
            }, "favorite_count": 9, "latitude": 37.8315, "longitude": 127.5109},

            {"region_id": 9, "tour_api_subcode": "2", "translations": {
                "ko": {"name": "고양시", "description": "킨텍스와 호수공원이 있는 일산신도시", "feature": "킨텍스와 일산호수공원"},
                "en": {"name": "Goyang-si", "description": "Ilsan New City with KINTEX and Lake Park",
                       "feature": "KINTEX and Ilsan Lake Park"},
                "jp": {"name": "高陽市", "description": "キンテックスと湖水公園がある一山新都市",
                       "feature": "キンテックスと一山湖水公園"},
                "cn": {"name": "高阳市", "description": "金泰克斯和湖水公园所在的一山新城",
                       "feature": "金泰克斯和一山湖水公园"}
            }, "favorite_count": 12, "latitude": 37.6584, "longitude": 126.8320},

            {"region_id": 9, "tour_api_subcode": "3", "translations": {
                "ko": {"name": "과천시", "description": "서울대공원과 경마장이 있는 도시", "feature": "서울대공원과 과천경마공원"},
                "en": {"name": "Gwacheon-si", "description": "City with Seoul Grand Park and racecourse",
                       "feature": "Seoul Grand Park and Gwacheon Racecourse"},
                "jp": {"name": "果川市", "description": "ソウル大公園と競馬場がある都市",
                       "feature": "ソウル大公園と果川競馬公園"},
                "cn": {"name": "果川市", "description": "首尔大公园和赛马场所在的城市",
                       "feature": "首尔大公园和果川赛马公园"}
            }, "favorite_count": 8, "latitude": 37.4292, "longitude": 126.9878},

            {"region_id": 9, "tour_api_subcode": "4", "translations": {
                "ko": {"name": "광명시", "description": "KTX광명역이 있는 교통중심지", "feature": "광명역과 광명동굴"},
                "en": {"name": "Gwangmyeong-si", "description": "Transportation hub with KTX Gwangmyeong Station",
                       "feature": "Gwangmyeong Station and Gwangmyeong Cave"},
                "jp": {"name": "光明市", "description": "KTX光明駅がある交通の中心地", "feature": "光明駅と光明洞窟"},
                "cn": {"name": "光明市", "description": "KTX光明站所在的交通枢纽", "feature": "光明站和光明洞窟"}
            }, "favorite_count": 6, "latitude": 37.4781, "longitude": 126.8642},

            {"region_id": 9, "tour_api_subcode": "5", "translations": {
                "ko": {"name": "광주시", "description": "남한산성과 곤지암도자공원이 있는 도시", "feature": "남한산성과 곤지암도자공원"},
                "en": {"name": "Gwangju-si", "description": "City with Namhansanseong and Gonjiam Ceramic Park",
                       "feature": "Namhansanseong Fortress and Gonjiam Ceramic Park"},
                "jp": {"name": "広州市", "description": "南漢山城と昆池岩陶磁公園がある都市",
                       "feature": "南漢山城と昆池岩陶磁公園"},
                "cn": {"name": "广州市", "description": "南汉山城和昆池岩陶瓷公园所在的城市",
                       "feature": "南汉山城和昆池岩陶瓷公园"}
            }, "favorite_count": 7, "latitude": 37.4296, "longitude": 127.2552},

            {"region_id": 9, "tour_api_subcode": "6", "translations": {
                "ko": {"name": "구리시", "description": "동구릉과 아차산이 있는 역사도시", "feature": "동구릉과 아차산"},
                "en": {"name": "Guri-si", "description": "Historic city with Donggureung and Achasan",
                       "feature": "Donggureung Royal Tombs and Achasan Mountain"},
                "jp": {"name": "九里市", "description": "東九陵と峨嵯山がある歴史都市", "feature": "東九陵と峨嵯山"},
                "cn": {"name": "九里市", "description": "东九陵和峨嵯山所在的历史城市", "feature": "东九陵和峨嵯山"}
            }, "favorite_count": 5, "latitude": 37.5943, "longitude": 127.1296},

            {"region_id": 9, "tour_api_subcode": "7", "translations": {
                "ko": {"name": "군포시", "description": "수리산과 반월호수가 있는 도시", "feature": "수리산과 반월호수"},
                "en": {"name": "Gunpo-si", "description": "City with Surisan and Banwol Lake",
                       "feature": "Surisan Mountain and Banwol Lake"},
                "jp": {"name": "軍浦市", "description": "修理山と半月湖がある都市", "feature": "修理山と半月湖"},
                "cn": {"name": "军浦市", "description": "修理山和半月湖所在的城市", "feature": "修理山和半月湖"}
            }, "favorite_count": 4, "latitude": 37.3616, "longitude": 126.9352},

            {"region_id": 9, "tour_api_subcode": "8", "translations": {
                "ko": {"name": "김포시", "description": "한강하구와 김포국제조각공원이 있는 도시", "feature": "김포국제조각공원과 애기봉"},
                "en": {"name": "Gimpo-si",
                       "description": "City with Han River estuary and Gimpo International Sculpture Park",
                       "feature": "Gimpo International Sculpture Park and Aegibong Peak"},
                "jp": {"name": "金浦市", "description": "漢江河口と金浦国際彫刻公園がある都市",
                       "feature": "金浦国際彫刻公園と愛妓峰"},
                "cn": {"name": "金浦市", "description": "汉江河口和金浦国际雕塑公园所在的城市",
                       "feature": "金浦国际雕塑公园和爱妓峰"}
            }, "favorite_count": 6, "latitude": 37.6150, "longitude": 126.7156},

            {"region_id": 9, "tour_api_subcode": "9", "translations": {
                "ko": {"name": "남양주시", "description": "정약용유적지와 다산생태공원이 있는 도시", "feature": "정약용유적지와 다산생태공원"},
                "en": {"name": "Namyangju-si",
                       "description": "City with Jeong Yak-yong Historic Site and Dasan Ecological Park",
                       "feature": "Jeong Yak-yong Historic Site and Dasan Ecological Park"},
                "jp": {"name": "南楊州市", "description": "丁若鏞遺跡地と茶山生態公園がある都市",
                       "feature": "丁若鏞遺跡地と茶山生態公園"},
                "cn": {"name": "南杨州市", "description": "丁若镛遗址和茶山生态公园所在的城市",
                       "feature": "丁若镛遗址和茶山生态公园"}
            }, "favorite_count": 8, "latitude": 37.6366, "longitude": 127.2164},

            {"region_id": 9, "tour_api_subcode": "10", "translations": {
                "ko": {"name": "동두천시", "description": "소요산과 자유수호평화박물관이 있는 도시", "feature": "소요산과 자유수호평화박물관"},
                "en": {"name": "Dongducheon-si", "description": "City with Soyosan and Freedom Protection Peace Museum",
                       "feature": "Soyosan Mountain and Freedom Protection Peace Museum"},
                "jp": {"name": "東豆川市", "description": "逍遥山と自由守護平和博物館がある都市",
                       "feature": "逍遥山と自由守護平和博物館"},
                "cn": {"name": "东豆川市", "description": "逍遥山和自由守护和平博物馆所在的城市",
                       "feature": "逍遥山和自由守护和平博物馆"}
            }, "favorite_count": 4, "latitude": 37.9036, "longitude": 127.0606},

            {"region_id": 9, "tour_api_subcode": "11", "translations": {
                "ko": {"name": "부천시", "description": "판타지아와 아인스월드가 있는 문화도시", "feature": "판타지아와 아인스월드"},
                "en": {"name": "Bucheon-si", "description": "Cultural city with Fantasia and Aiins World",
                       "feature": "Fantasia and Aiins World"},
                "jp": {"name": "富川市", "description": "ファンタジアとアインスワールドがある文化都市",
                       "feature": "ファンタジアとアインスワールド"},
                "cn": {"name": "富川市", "description": "幻想曲和艾因斯世界所在的文化城市",
                       "feature": "幻想曲和艾因斯世界"}
            }, "favorite_count": 8, "latitude": 37.4989, "longitude": 126.7831},

            {"region_id": 9, "tour_api_subcode": "12", "translations": {
                "ko": {"name": "성남시", "description": "판교테크노밸리와 분당신도시가 있는 IT중심지", "feature": "판교테크노밸리와 분당중앙공원"},
                "en": {"name": "Seongnam-si", "description": "IT hub with Pangyo Techno Valley and Bundang New City",
                       "feature": "Pangyo Techno Valley and Bundang Central Park"},
                "jp": {"name": "城南市", "description": "板橋テクノバレーと盆唐新都市があるIT中心地",
                       "feature": "板橋テクノバレーと盆唐中央公園"},
                "cn": {"name": "城南市", "description": "板桥科技谷和盆唐新城所在的IT中心",
                       "feature": "板桥科技谷和盆唐中央公园"}
            }, "favorite_count": 15, "latitude": 37.4201, "longitude": 127.1262},

            {"region_id": 9, "tour_api_subcode": "13", "translations": {
                "ko": {"name": "수원시", "description": "화성과 삼성전자가 있는 경기남부 중심", "feature": "수원화성과 삼성전자"},
                "en": {"name": "Suwon-si",
                       "description": "Southern Gyeonggi center with Hwaseong Fortress and Samsung Electronics",
                       "feature": "Suwon Hwaseong Fortress and Samsung Electronics"},
                "jp": {"name": "水原市", "description": "華城とサムスン電子がある京畿南部の中心",
                       "feature": "水原華城とサムスン電子"},
                "cn": {"name": "水原市", "description": "华城和三星电子所在的京畿南部中心",
                       "feature": "水原华城和三星电子"}
            }, "favorite_count": 15, "latitude": 37.2636, "longitude": 127.0286},

            {"region_id": 9, "tour_api_subcode": "14", "translations": {
                "ko": {"name": "시흥시", "description": "오이도와 연꽃테마파크가 있는 서해안도시", "feature": "오이도와 연꽃테마파크"},
                "en": {"name": "Siheung-si", "description": "West coast city with Oido and Lotus Theme Park",
                       "feature": "Oido Island and Lotus Theme Park"},
                "jp": {"name": "始興市", "description": "烏耳島と蓮花テーマパークがある西海岸都市",
                       "feature": "烏耳島と蓮花テーマパーク"},
                "cn": {"name": "始兴市", "description": "乌耳岛和莲花主题公园所在的西海岸城市",
                       "feature": "乌耳岛和莲花主题公园"}
            }, "favorite_count": 6, "latitude": 37.3802, "longitude": 126.8031},

            {"region_id": 9, "tour_api_subcode": "15", "translations": {
                "ko": {"name": "안산시", "description": "다문화특구와 대부도가 있는 산업도시", "feature": "다문화특구와 대부도"},
                "en": {"name": "Ansan-si", "description": "Industrial city with multicultural district and Daebudo",
                       "feature": "Multicultural district and Daebudo Island"},
                "jp": {"name": "安山市", "description": "多文化特区と大阜島がある産業都市",
                       "feature": "多文化特区と大阜島"},
                "cn": {"name": "安山市", "description": "多元文化特区和大阜岛所在的产业城市",
                       "feature": "多元文化特区和大阜岛"}
            }, "favorite_count": 5, "latitude": 37.3236, "longitude": 126.8219},

            {"region_id": 9, "tour_api_subcode": "16", "translations": {
                "ko": {"name": "안성시", "description": "안성맞춤과 팜랜드가 있는 농업도시", "feature": "안성팜랜드와 안성맞춤랜드"},
                "en": {"name": "Anseong-si", "description": "Agricultural city with Anseong Machum and Farmland",
                       "feature": "Anseong Farmland and Anseong Machum Land"},
                "jp": {"name": "安城市", "description": "安城マッチュムとファームランドがある農業都市",
                       "feature": "安城ファームランドと安城マッチュムランド"},
                "cn": {"name": "安城市", "description": "安城量身定制和农场所在的农业城市",
                       "feature": "安城农场和安城量身定制乐园"}
            }, "favorite_count": 5, "latitude": 37.0079, "longitude": 127.2698},

            {"region_id": 9, "tour_api_subcode": "17", "translations": {
                "ko": {"name": "안양시", "description": "안양예술공원과 삼성디지털시티가 있는 도시", "feature": "안양예술공원과 삼성디지털시티"},
                "en": {"name": "Anyang-si", "description": "City with Anyang Art Park and Samsung Digital City",
                       "feature": "Anyang Art Park and Samsung Digital City"},
                "jp": {"name": "安養市", "description": "安養芸術公園とサムスンデジタルシティがある都市",
                       "feature": "安養芸術公園とサムスンデジタルシティ"},
                "cn": {"name": "安养市", "description": "安养艺术公园和三星数字城所在的城市",
                       "feature": "安养艺术公园和三星数字城"}
            }, "favorite_count": 8, "latitude": 37.3943, "longitude": 126.9568},

            {"region_id": 9, "tour_api_subcode": "18", "translations": {
                "ko": {"name": "양주시", "description": "장흥관광지와 송암스페이스센터가 있는 도시", "feature": "장흥관광지와 송암스페이스센터"},
                "en": {"name": "Yangju-si", "description": "City with Jangheung Tourist Site and Songam Space Center",
                       "feature": "Jangheung Tourist Site and Songam Space Center"},
                "jp": {"name": "楊州市", "description": "長興観光地と松岩スペースセンターがある都市",
                       "feature": "長興観光地と松岩スペースセンター"},
                "cn": {"name": "杨州市", "description": "长兴旅游地和松岩太空中心所在的城市",
                       "feature": "长兴旅游地和松岩太空中心"}
            }, "favorite_count": 4, "latitude": 37.7853, "longitude": 127.0458},

            {"region_id": 9, "tour_api_subcode": "19", "translations": {
                "ko": {"name": "양평군", "description": "용문산과 세미원이 있는 자연휴양지", "feature": "용문산과 세미원"},
                "en": {"name": "Yangpyeong-gun", "description": "Natural resort with Yongmunsan and Semiwon",
                       "feature": "Yongmunsan Mountain and Semiwon Garden"},
                "jp": {"name": "楊平郡", "description": "龍門山とセミウォンがある自然休養地",
                       "feature": "龍門山とセミウォン"},
                "cn": {"name": "杨平郡", "description": "龙门山和细美苑所在的自然休养地", "feature": "龙门山和细美苑"}
            }, "favorite_count": 8, "latitude": 37.4891, "longitude": 127.4947},

            {"region_id": 9, "tour_api_subcode": "20", "translations": {
                "ko": {"name": "여주시", "description": "세종대왕릉과 여주프리미엄아울렛이 있는 도시", "feature": "세종대왕릉과 여주프리미엄아울렛"},
                "en": {"name": "Yeoju-si", "description": "City with King Sejong's Tomb and Yeoju Premium Outlets",
                       "feature": "King Sejong's Tomb and Yeoju Premium Outlets"},
                "jp": {"name": "驪州市", "description": "世宗大王陵と驪州プレミアムアウトレットがある都市",
                       "feature": "世宗大王陵と驪州プレミアムアウトレット"},
                "cn": {"name": "骊州市", "description": "世宗大王陵和骊州奥特莱斯所在的城市",
                       "feature": "世宗大王陵和骊州奥特莱斯"}
            }, "favorite_count": 7, "latitude": 37.2982, "longitude": 127.6372},

            {"region_id": 9, "tour_api_subcode": "21", "translations": {
                "ko": {"name": "연천군", "description": "DMZ와 전곡리유적이 있는 최북단", "feature": "전곡리선사박물관과 허준테마파크"},
                "en": {"name": "Yeoncheon-gun", "description": "Northernmost area with DMZ and Jeongok-ri site",
                       "feature": "Jeongok Prehistory Museum and Heo Jun Theme Park"},
                "jp": {"name": "漣川郡", "description": "DMZと全谷里遺跡がある最北端",
                       "feature": "全谷里先史博物館と許浚テーマパーク"},
                "cn": {"name": "涟川郡", "description": "DMZ和全谷里遗址所在的最北端",
                       "feature": "全谷里史前博物馆和许浚主题公园"}
            }, "favorite_count": 5, "latitude": 38.0967, "longitude": 127.0746},

            {"region_id": 9, "tour_api_subcode": "22", "translations": {
                "ko": {"name": "오산시", "description": "물향기수목원과 오산시립미술관이 있는 도시", "feature": "물향기수목원과 오산시립미술관"},
                "en": {"name": "Osan-si", "description": "City with Mulhyanggi Arboretum and Osan City Museum",
                       "feature": "Mulhyanggi Arboretum and Osan City Museum"},
                "jp": {"name": "烏山市", "description": "物香気樹木園と烏山市立美術館がある都市",
                       "feature": "物香気樹木園と烏山市立美術館"},
                "cn": {"name": "乌山市", "description": "物香气树木园和乌山市立美术馆所在的城市",
                       "feature": "物香气树木园和乌山市立美术馆"}
            }, "favorite_count": 4, "latitude": 37.1497, "longitude": 127.0773},

            {"region_id": 9, "tour_api_subcode": "23", "translations": {
                "ko": {"name": "용인시", "description": "에버랜드와 한국민속촌이 있는 관광도시", "feature": "에버랜드와 한국민속촌"},
                "en": {"name": "Yongin-si", "description": "Tourism city with Everland and Korean Folk Village",
                       "feature": "Everland and Korean Folk Village"},
                "jp": {"name": "龍仁市", "description": "エバーランドと韓国民俗村がある観光都市",
                       "feature": "エバーランドと韓国民俗村"},
                "cn": {"name": "龙仁市", "description": "爱宝乐园和韩国民俗村所在的旅游城市",
                       "feature": "爱宝乐园和韩国民俗村"}
            }, "favorite_count": 18, "latitude": 37.2410, "longitude": 127.1776},

            {"region_id": 9, "tour_api_subcode": "24", "translations": {
                "ko": {"name": "의왕시", "description": "왕송호수와 철도박물관이 있는 도시", "feature": "왕송호수와 철도박물관"},
                "en": {"name": "Uiwang-si", "description": "City with Wangsong Lake and Railroad Museum",
                       "feature": "Wangsong Lake and Railroad Museum"},
                "jp": {"name": "義王市", "description": "往十湖と鉄道博物館がある都市",
                       "feature": "往十湖と鉄道博物館"},
                "cn": {"name": "义王市", "description": "往松湖和铁道博物馆所在的城市", "feature": "往松湖和铁道博物馆"}
            }, "favorite_count": 5, "latitude": 37.3449, "longitude": 126.9689},

            {"region_id": 9, "tour_api_subcode": "25", "translations": {
                "ko": {"name": "의정부시", "description": "부대찌개거리와 회룡문화역사공원이 있는 도시", "feature": "부대찌개거리와 회룡문화역사공원"},
                "en": {"name": "Uijeongbu-si",
                       "description": "City with Budae-jjigae Street and Hoeryong Cultural History Park",
                       "feature": "Budae-jjigae Street and Hoeryong Cultural History Park"},
                "jp": {"name": "議政府市", "description": "部隊チゲ街と回龍文化歴史公園がある都市",
                       "feature": "部隊チゲ街と回龙文化歴史公園"},
                "cn": {"name": "议政府市", "description": "部队汤街和回龙文化历史公园所在的城市",
                       "feature": "部队汤街和回龙文化历史公园"}
            }, "favorite_count": 6, "latitude": 37.7384, "longitude": 127.0338},

            {"region_id": 9, "tour_api_subcode": "26", "translations": {
                "ko": {"name": "이천시", "description": "도자기와 쌀로 유명한 전통문화도시", "feature": "이천도자기와 설봉공원"},
                "en": {"name": "Icheon-si", "description": "Traditional cultural city famous for ceramics and rice",
                       "feature": "Icheon ceramics and Seolbong Park"},
                "jp": {"name": "利川市", "description": "陶磁器と米で有名な伝統文化都市",
                       "feature": "利川陶磁器と雪峰公園"},
                "cn": {"name": "利川市", "description": "以陶瓷和大米闻名的传统文化城市",
                       "feature": "利川陶瓷和雪峰公园"}
            }, "favorite_count": 8, "latitude": 37.2792, "longitude": 127.4419},

            {"region_id": 9, "tour_api_subcode": "27", "translations": {
                "ko": {"name": "파주시", "description": "DMZ와 출판도시가 있는 북부 접경", "feature": "임진각과 헤이리예술마을"},
                "en": {"name": "Paju-si", "description": "Northern border area with DMZ and Publishing City",
                       "feature": "Imjingak and Heyri Art Village"},
                "jp": {"name": "坡州市", "description": "DMZと出版都市がある北部国境",
                       "feature": "臨津閣とヘイリ芸術村"},
                "cn": {"name": "坡州市", "description": "DMZ和出版城所在的北部边境", "feature": "临津阁和坡州艺术村"}
            }, "favorite_count": 10, "latitude": 37.7598, "longitude": 126.7800},

            {"region_id": 9, "tour_api_subcode": "28", "translations": {
                "ko": {"name": "평택시", "description": "평택항과 소사벌한우가 있는 교통요지", "feature": "평택항과 소사벌한우"},
                "en": {"name": "Pyeongtaek-si",
                       "description": "Transportation hub with Pyeongtaek Port and Sosabelhanwoo",
                       "feature": "Pyeongtaek Port and Sosabelhanwoo"},
                "jp": {"name": "平沢市", "description": "平沢港と小砂伐韓牛がある交通要地",
                       "feature": "平沢港と小砂伐韓牛"},
                "cn": {"name": "平泽市", "description": "平泽港和小沙伐韩牛所在的交通要地",
                       "feature": "平泽港和小沙伐韩牛"}
            }, "favorite_count": 6, "latitude": 36.9921, "longitude": 127.1128},

            {"region_id": 9, "tour_api_subcode": "29", "translations": {
                "ko": {"name": "포천시", "description": "허브아일랜드와 산정호수가 있는 북부산간", "feature": "허브아일랜드와 산정호수"},
                "en": {"name": "Pocheon-si", "description": "Northern mountain area with Herb Island and Sanjeong Lake",
                       "feature": "Herb Island and Sanjeong Lake"},
                "jp": {"name": "抱川市", "description": "ハーブアイランドと山井湖がある北部山間",
                       "feature": "ハーブアイランドと山井湖"},
                "cn": {"name": "抱川市", "description": "草本岛和山井湖所在的北部山区", "feature": "草本岛和山井湖"}
            }, "favorite_count": 8, "latitude": 37.8951, "longitude": 127.2004},

            {"region_id": 9, "tour_api_subcode": "30", "translations": {
                "ko": {"name": "하남시", "description": "미사신도시와 스타필드가 있는 동부신도시", "feature": "미사신도시와 스타필드하남"},
                "en": {"name": "Hanam-si", "description": "Eastern new city with Misa New Town and Starfield",
                       "feature": "Misa New Town and Starfield Hanam"},
                "jp": {"name": "河南市", "description": "美沙新都市とスターフィールドがある東部新都市",
                       "feature": "美沙新都市とスターフィールド河南"},
                "cn": {"name": "河南市", "description": "美沙新城和星空购物中心所在的东部新城",
                       "feature": "美沙新城和星空购物中心河南"}
            }, "favorite_count": 7, "latitude": 37.5394, "longitude": 127.2147},

            {"region_id": 9, "tour_api_subcode": "31", "translations": {
                "ko": {"name": "화성시", "description": "동탄신도시와 제부도가 있는 서남부도시", "feature": "동탄신도시와 제부도"},
                "en": {"name": "Hwaseong-si", "description": "Southwest city with Dongtan New Town and Jebudo",
                       "feature": "Dongtan New Town and Jebudo Island"},
                "jp": {"name": "華城市", "description": "東灘新都市と済扶島がある西南部都市",
                       "feature": "東灘新都市と済扶島"},
                "cn": {"name": "华城市", "description": "东滩新城和济扶岛所在的西南部城市",
                       "feature": "东滩新城和济扶岛"}
            }, "favorite_count": 9, "latitude": 37.1996, "longitude": 126.8311},

            # ===== 강원특별자치도 (18개 시/군) =====
            {"region_id": 10, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "강릉시", "description": "동해안 최대의 관광도시", "feature": "경포대와 정동진"},
                "en": {"name": "Gangneung-si", "description": "Largest tourism city on the east coast",
                       "feature": "Gyeongpodae and Jeongdongjin"},
                "jp": {"name": "江陵市", "description": "東海岸最大の観光都市", "feature": "鏡浦台と正東津"},
                "cn": {"name": "江陵市", "description": "东海岸最大的旅游城市", "feature": "镜浦台和正东津"}
            }, "favorite_count": 20, "latitude": 37.7519, "longitude": 128.8761},

            {"region_id": 10, "tour_api_subcode": "2", "translations": {
                "ko": {"name": "고성군", "description": "DMZ박물관과 화진포가 있는 최북단", "feature": "DMZ박물관과 화진포"},
                "en": {"name": "Goseong-gun", "description": "Northernmost area with DMZ Museum and Hwajinpo",
                       "feature": "DMZ Museum and Hwajinpo Lake"},
                "jp": {"name": "高城郡", "description": "DMZ博物館と花津浦がある最北端",
                       "feature": "DMZ博物館と花津浦"},
                "cn": {"name": "高城郡", "description": "DMZ博物馆和花津浦所在的最北端", "feature": "DMZ博物馆和花津浦"}
            }, "favorite_count": 8, "latitude": 38.3802, "longitude": 128.4677},

            {"region_id": 10, "tour_api_subcode": "3", "translations": {
                "ko": {"name": "동해시", "description": "무릉계곡과 망상해수욕장이 있는 동해안도시", "feature": "무릉계곡과 망상해수욕장"},
                "en": {"name": "Donghae-si", "description": "East coast city with Mureung Valley and Mangsang Beach",
                       "feature": "Mureung Valley and Mangsang Beach"},
                "jp": {"name": "東海市", "description": "武陵渓谷と望祥海水浴場がある東海岸都市",
                       "feature": "武陵渓谷と望祥海水浴場"},
                "cn": {"name": "东海市", "description": "武陵溪谷和望祥海水浴场所在的东海岸城市",
                       "feature": "武陵溪谷和望祥海水浴场"}
            }, "favorite_count": 10, "latitude": 37.5245, "longitude": 129.1144},

            {"region_id": 10, "tour_api_subcode": "4", "translations": {
                "ko": {"name": "삼척시", "description": "환선굴과 죽서루가 있는 석회암지대", "feature": "환선굴과 죽서루"},
                "en": {"name": "Samcheok-si", "description": "Limestone area with Hwanseon Cave and Jukseo-ru",
                       "feature": "Hwanseon Cave and Jukseo-ru Pavilion"},
                "jp": {"name": "三陟市", "description": "幻仙窟と竹西楼がある石灰岩地帯", "feature": "幻仙窟と竹西楼"},
                "cn": {"name": "三陟市", "description": "幻仙窟和竹西楼所在的石灰岩地区", "feature": "幻仙窟和竹西楼"}
            }, "favorite_count": 12, "latitude": 37.4497, "longitude": 129.1653},

            {"region_id": 10, "tour_api_subcode": "5", "translations": {
                "ko": {"name": "속초시", "description": "설악산 관문도시", "feature": "설악산과 속초해수욕장"},
                "en": {"name": "Sokcho-si", "description": "Gateway city to Seoraksan",
                       "feature": "Seoraksan Mountain and Sokcho Beach"},
                "jp": {"name": "束草市", "description": "雪嶽山の玄関都市", "feature": "雪嶽山と束草海水浴場"},
                "cn": {"name": "束草市", "description": "雪岳山门户城市", "feature": "雪岳山和束草海水浴场"}
            }, "favorite_count": 18, "latitude": 38.2070, "longitude": 128.5918},

            {"region_id": 10, "tour_api_subcode": "6", "translations": {
                "ko": {"name": "양구군", "description": "두타연과 을지전망대가 있는 DMZ인근", "feature": "두타연과 을지전망대"},
                "en": {"name": "Yanggu-gun", "description": "Near DMZ with Dutayeon and Eulji Observatory",
                       "feature": "Dutayeon Falls and Eulji Observatory"},
                "jp": {"name": "楊口郡", "description": "豆陀淵と乙支展望台があるDMZ近隣",
                       "feature": "豆陀淵と乙支展望台"},
                "cn": {"name": "杨口郡", "description": "豆陀渊和乙支展望台所在的DMZ附近",
                       "feature": "豆陀渊和乙支展望台"}
            }, "favorite_count": 6, "latitude": 38.1068, "longitude": 127.9926},

            {"region_id": 10, "tour_api_subcode": "7", "translations": {
                "ko": {"name": "양양군", "description": "낙산사와 서피비치가 있는 해안군", "feature": "낙산사와 양양서피비치"},
                "en": {"name": "Yangyang-gun", "description": "Coastal county with Naksansa Temple and Surf Beach",
                       "feature": "Naksansa Temple and Yangyang Surf Beach"},
                "jp": {"name": "襄陽郡", "description": "洛山寺とサーフビーチがある海岸郡",
                       "feature": "洛山寺と襄陽サーフビーチ"},
                "cn": {"name": "襄阳郡", "description": "洛山寺和冲浪海滩所在的海岸郡",
                       "feature": "洛山寺和襄阳冲浪海滩"}
            }, "favorite_count": 12, "latitude": 38.0756, "longitude": 128.6190},

            {"region_id": 10, "tour_api_subcode": "8", "translations": {
                "ko": {"name": "영월군", "description": "선돌과 청령포가 있는 역사군", "feature": "청령포와 선돌"},
                "en": {"name": "Yeongwol-gun", "description": "Historic county with Standing Stone and Cheongryeongpo",
                       "feature": "Cheongryeongpo and Standing Stone"},
                "jp": {"name": "寧越郡", "description": "立石と清泠浦がある歴史郡", "feature": "清泠浦と立石"},
                "cn": {"name": "宁越郡", "description": "立石和清泠浦所在的历史郡", "feature": "清泠浦和立石"}
            }, "favorite_count": 9, "latitude": 37.1836, "longitude": 128.4611},

            {"region_id": 10, "tour_api_subcode": "9", "translations": {
                "ko": {"name": "원주시", "description": "치악산과 소금산출렁다리가 있는 중부도시", "feature": "치악산과 소금산출렁다리"},
                "en": {"name": "Wonju-si", "description": "Central city with Chiaksan and Sogeumsan Suspension Bridge",
                       "feature": "Chiaksan Mountain and Sogeumsan Suspension Bridge"},
                "jp": {"name": "原州市", "description": "雉岳山と塩山吊り橋がある中部都市",
                       "feature": "雉岳山と塩山吊り橋"},
                "cn": {"name": "原州市", "description": "雉岳山和盐山悬索桥所在的中部城市",
                       "feature": "雉岳山和盐山悬索桥"}
            }, "favorite_count": 8, "latitude": 37.3422, "longitude": 127.9202},

            {"region_id": 10, "tour_api_subcode": "10", "translations": {
                "ko": {"name": "인제군", "description": "내린천과 원대리자작나무숲이 있는 내륙산간", "feature": "내린천과 원대리자작나무숲"},
                "en": {"name": "Inje-gun",
                       "description": "Inland mountain area with Naerin Stream and Wondaeri Birch Forest",
                       "feature": "Naerin Stream and Wondaeri Birch Forest"},
                "jp": {"name": "麟蹄郡", "description": "内麟川と院垈里白樺の森がある内陸山間",
                       "feature": "内麟川と院垈里白樺の森"},
                "cn": {"name": "麟蹄郡", "description": "内麟川和院垈里白桦林所在的内陆山区",
                       "feature": "内麟川和院垈里白桦林"}
            }, "favorite_count": 11, "latitude": 38.0693, "longitude": 128.1708},

            {"region_id": 10, "tour_api_subcode": "11", "translations": {
                "ko": {"name": "정선군", "description": "정선아리랑과 화암동굴이 있는 탄광지역", "feature": "정선아리랑과 화암동굴"},
                "en": {"name": "Jeongseon-gun", "description": "Coal mining area with Jeongseon Arirang and Hwaam Cave",
                       "feature": "Jeongseon Arirang and Hwaam Cave"},
                "jp": {"name": "旌善郡", "description": "旌善アリランと花岩洞窟がある炭鉱地域",
                       "feature": "旌善アリランと花岩洞窟"},
                "cn": {"name": "旌善郡", "description": "旌善阿里郎和花岩洞窟所在的煤矿地区",
                       "feature": "旌善阿里郎和花岩洞窟"}
            }, "favorite_count": 10, "latitude": 37.3806, "longitude": 128.6606},

            {"region_id": 10, "tour_api_subcode": "12", "translations": {
                "ko": {"name": "철원군", "description": "철원평야와 한탄강이 있는 DMZ인근", "feature": "한탄강과 고석정"},
                "en": {"name": "Cheorwon-gun", "description": "Near DMZ with Cheorwon Plain and Hantan River",
                       "feature": "Hantan River and Goseokjeong Pavilion"},
                "jp": {"name": "鉄原郡", "description": "鉄原平野と漢灘江があるDMZ近隣", "feature": "漢灘江と孤石亭"},
                "cn": {"name": "铁原郡", "description": "铁原平野和汉滩江所在的DMZ附近", "feature": "汉滩江和孤石亭"}
            }, "favorite_count": 7, "latitude": 38.1467, "longitude": 127.3138},

            {"region_id": 10, "tour_api_subcode": "13", "translations": {
                "ko": {"name": "춘천시", "description": "강원도의 도청소재지", "feature": "남이섬과 소양강"},
                "en": {"name": "Chuncheon-si", "description": "Provincial capital of Gangwon-do",
                       "feature": "Nami Island and Soyang River"},
                "jp": {"name": "春川市", "description": "江原道の道庁所在地", "feature": "南怡島と昭陽江"},
                "cn": {"name": "春川市", "description": "江原道道政府所在地", "feature": "南怡岛和昭阳江"}
            }, "favorite_count": 15, "latitude": 37.8813, "longitude": 127.7298},

            {"region_id": 10, "tour_api_subcode": "14", "translations": {
                "ko": {"name": "태백시", "description": "태백산과 석탄박물관이 있는 고원도시", "feature": "태백산과 석탄박물관"},
                "en": {"name": "Taebaek-si", "description": "Highland city with Taebaeksan and Coal Museum",
                       "feature": "Taebaeksan Mountain and Coal Museum"},
                "jp": {"name": "太白市", "description": "太白山と石炭博物館がある高原都市",
                       "feature": "太白山と石炭博物館"},
                "cn": {"name": "太白市", "description": "太白山和煤炭博物馆所在的高原城市",
                       "feature": "太白山和煤炭博物馆"}
            }, "favorite_count": 8, "latitude": 37.1640, "longitude": 128.9856},

            {"region_id": 10, "tour_api_subcode": "15", "translations": {
                "ko": {"name": "평창군", "description": "2018 동계올림픽 개최지", "feature": "알펜시아와 용평리조트"},
                "en": {"name": "Pyeongchang-gun", "description": "Host of 2018 Winter Olympics",
                       "feature": "Alpensia and Yongpyong Resort"},
                "jp": {"name": "平昌郡", "description": "2018冬季オリンピック開催地",
                       "feature": "アルペンシアと龍平リゾート"},
                "cn": {"name": "平昌郡", "description": "2018年冬奥会举办地", "feature": "阿尔卑西亚和龙平度假村"}
            }, "favorite_count": 12, "latitude": 37.3704, "longitude": 128.3900},

            {"region_id": 10, "tour_api_subcode": "16", "translations": {
                "ko": {"name": "홍천군", "description": "홍천강과 비발디파크가 있는 내륙군", "feature": "비발디파크와 홍천강"},
                "en": {"name": "Hongcheon-gun", "description": "Inland county with Hongcheon River and Vivaldi Park",
                       "feature": "Vivaldi Park and Hongcheon River"},
                "jp": {"name": "洪川郡", "description": "洪川江とビバルディパークがある内陸郡",
                       "feature": "ビバルディパークと洪川江"},
                "cn": {"name": "洪川郡", "description": "洪川江和维瓦尔第公园所在的内陆郡",
                       "feature": "维瓦尔第公园和洪川江"}
            }, "favorite_count": 9, "latitude": 37.6969, "longitude": 127.8889},

            {"region_id": 10, "tour_api_subcode": "17", "translations": {
                "ko": {"name": "화천군", "description": "산천어축제와 파로호가 있는 북부군", "feature": "산천어축제와 파로호"},
                "en": {"name": "Hwacheon-gun",
                       "description": "Northern county with Mountain Trout Festival and Paro Lake",
                       "feature": "Mountain Trout Festival and Paro Lake"},
                "jp": {"name": "華川郡", "description": "山川魚祭りと破虜湖がある北部郡",
                       "feature": "山川魚祭りと破虜湖"},
                "cn": {"name": "华川郡", "description": "山鳟鱼节和破虏湖所在的北部郡", "feature": "山鳟鱼节和破虏湖"}
            }, "favorite_count": 8, "latitude": 38.1063, "longitude": 127.7083},

            {"region_id": 10, "tour_api_subcode": "18", "translations": {
                "ko": {"name": "횡성군", "description": "횡성한우와 웰리힐리파크가 있는 내륙군", "feature": "횡성한우와 웰리힐리파크"},
                "en": {"name": "Hoengseong-gun",
                       "description": "Inland county with Hoengseong Hanwoo and Welli Hilli Park",
                       "feature": "Hoengseong Hanwoo and Welli Hilli Park"},
                "jp": {"name": "横城郡", "description": "横城韓牛とウェリヒリパークがある内陸郡",
                       "feature": "横城韓牛とウェリヒリパーク"},
                "cn": {"name": "横城郡", "description": "横城韩牛和威利希利公园所在的内陆郡",
                       "feature": "横城韩牛和威利希利公园"}
            }, "favorite_count": 6, "latitude": 37.4910, "longitude": 127.9855},

            # ===== 충청북도 (11개 시/군) =====
            {"region_id": 11, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "괴산군", "description": "속리산과 산막이옛마을이 있는 산간군", "feature": "속리산과 산막이옛마을"},
                "en": {"name": "Goesan-gun", "description": "Mountain county with Songnisan and Sanmakyi Old Village",
                       "feature": "Songnisan Mountain and Sanmakyi Old Village"},
                "jp": {"name": "槐山郡", "description": "俗離山と山幕里古村がある山間郡",
                       "feature": "俗離山と山幕里古村"},
                "cn": {"name": "槐山郡", "description": "俗离山和山幕里古村所在的山区郡",
                       "feature": "俗离山和山幕里古村"}
            }, "favorite_count": 7, "latitude": 36.8148, "longitude": 127.7884},

            {"region_id": 11, "tour_api_subcode": "2", "translations": {
                "ko": {"name": "단양군", "description": "단양팔경과 도담삼봉이 있는 관광군", "feature": "단양팔경과 도담삼봉"},
                "en": {"name": "Danyang-gun",
                       "description": "Tourism county with Danyang Eight Scenes and Dodamsambong",
                       "feature": "Danyang Eight Scenes and Dodamsambong Peaks"},
                "jp": {"name": "丹陽郡", "description": "丹陽八景と島潭三峰がある観光郡",
                       "feature": "丹陽八景と島潭三峰"},
                "cn": {"name": "丹阳郡", "description": "丹阳八景和岛潭三峰所在的旅游郡",
                       "feature": "丹阳八景和岛潭三峰"}
            }, "favorite_count": 12, "latitude": 36.9845, "longitude": 128.3655},

            {"region_id": 11, "tour_api_subcode": "3", "translations": {
                "ko": {"name": "보은군", "description": "법주사와 속리산이 있는 불교성지", "feature": "법주사와 속리산"},
                "en": {"name": "Boeun-gun", "description": "Buddhist sanctuary with Beopjusa Temple and Songnisan",
                       "feature": "Beopjusa Temple and Songnisan Mountain"},
                "jp": {"name": "報恩郡", "description": "法住寺と俗離山がある仏教聖地", "feature": "法住寺と俗離山"},
                "cn": {"name": "报恩郡", "description": "法住寺和俗离山所在的佛教圣地", "feature": "法住寺和俗离山"}
            }, "favorite_count": 10, "latitude": 36.4895, "longitude": 127.7294},

            {"region_id": 11, "tour_api_subcode": "4", "translations": {
                "ko": {"name": "영동군", "description": "영동포도와 난계국악박물관이 있는 음악의고장", "feature": "영동포도와 난계국악박물관"},
                "en": {"name": "Yeongdong-gun",
                       "description": "Music hometown with Yeongdong grapes and Nangye Gugak Museum",
                       "feature": "Yeongdong grapes and Nangye Gugak Museum"},
                "jp": {"name": "永同郡", "description": "永同葡萄と蘭渓国楽博物館がある音楽の故郷",
                       "feature": "永同葡萄と蘭渓国楽博物館"},
                "cn": {"name": "永同郡", "description": "永同葡萄和兰溪国乐博物馆所在的音乐故乡",
                       "feature": "永同葡萄和兰溪国乐博物馆"}
            }, "favorite_count": 6, "latitude": 36.1750, "longitude": 127.7764},

            {"region_id": 11, "tour_api_subcode": "5", "translations": {
                "ko": {"name": "옥천군", "description": "정지용문학관과 장계관광지가 있는 문학의고장", "feature": "정지용문학관과 장계관광지"},
                "en": {"name": "Okcheon-gun",
                       "description": "Literary hometown with Jeong Ji-yong Literature Hall and Janggye Tourist Site",
                       "feature": "Jeong Ji-yong Literature Hall and Janggye Tourist Site"},
                "jp": {"name": "沃川郡", "description": "鄭芝溶文学館と長溪観光地がある文学の故郷",
                       "feature": "鄭芝溶文学館と長溪観光地"},
                "cn": {"name": "沃川郡", "description": "郑芝溶文学馆和长溪旅游地所在的文学故乡",
                       "feature": "郑芝溶文学馆和长溪旅游地"}
            }, "favorite_count": 5, "latitude": 36.3065, "longitude": 127.5707},

            {"region_id": 11, "tour_api_subcode": "6", "translations": {
                "ko": {"name": "음성군", "description": "설성공원과 금왕읍이 있는 교통요지", "feature": "설성공원과 금왕읍"},
                "en": {"name": "Eumseong-gun", "description": "Transportation hub with Seolseong Park and Geumwang-eup",
                       "feature": "Seolseong Park and Geumwang-eup"},
                "jp": {"name": "陰城郡", "description": "雪城公園と金旺邑がある交通要地",
                       "feature": "雪城公園と金旺邑"},
                "cn": {"name": "阴城郡", "description": "雪城公园和金旺邑所在的交通要地", "feature": "雪城公园和金旺邑"}
            }, "favorite_count": 4, "latitude": 36.9441, "longitude": 127.6884},

            {"region_id": 11, "tour_api_subcode": "7", "translations": {
                "ko": {"name": "제천시", "description": "청풍호와 월악산이 있는 관광도시", "feature": "청풍호와 월악산"},
                "en": {"name": "Jecheon-si", "description": "Tourism city with Cheongpung Lake and Woraksan",
                       "feature": "Cheongpung Lake and Woraksan Mountain"},
                "jp": {"name": "堤川市", "description": "清風湖と月岳山がある観光都市", "feature": "清風湖と月岳山"},
                "cn": {"name": "堤川市", "description": "清风湖和月岳山所在的旅游城市", "feature": "清风湖和月岳山"}
            }, "favorite_count": 11, "latitude": 37.1327, "longitude": 128.1910},

            {"region_id": 11, "tour_api_subcode": "8", "translations": {
                "ko": {"name": "진천군", "description": "농다리와 종박물관이 있는 역사군", "feature": "농다리와 종박물관"},
                "en": {"name": "Jincheon-gun", "description": "Historic county with Nongdari Bridge and Bell Museum",
                       "feature": "Nongdari Bridge and Bell Museum"},
                "jp": {"name": "鎮川郡", "description": "籠橋と鐘博物館がある歴史郡", "feature": "籠橋と鐘博物館"},
                "cn": {"name": "镇川郡", "description": "笼桥和钟博物馆所在的历史郡", "feature": "笼桥和钟博物馆"}
            }, "favorite_count": 5, "latitude": 36.8575, "longitude": 127.4332},

            {"region_id": 11, "tour_api_subcode": "9", "translations": {
              "ko": {"name": "청원군", "description": "오송·오창을 중심으로 한 바이오·산업단지가 있는 도농복합군", "feature": "오송바이오폴리스와 오창과학산업단지"},
              "en": {"name": "Cheongwon-gun", "description": "Rural–urban county centered on Osong and Ochang with biotech and industrial complexes",
                     "feature": "Osong Bio-Polis and Ochang Science Industrial Complex"},
              "jp": {"name": "清原郡", "description": "オソン・オチャンを中心にバイオ・産業団地がある都市農村複合郡", "feature": "オソン・バイオポリスとオチャン科学産業団地"},
              "cn": {"name": "清原郡", "description": "以五松与梧仓为中心、拥有生物与工业园区的城乡复合郡", "feature": "五松生物聚落与梧仓科学产业园区"}
            }, "favorite_count": 6, "latitude": 36.7160, "longitude": 127.4860},

            {"region_id": 11, "tour_api_subcode": "10", "translations": {
                "ko": {"name": "청주시", "description": "충청북도의 도청소재지", "feature": "청주고인쇄박물관과 상당산성"},
                "en": {"name": "Cheongju-si", "description": "Provincial capital of Chungcheongbuk-do",
                       "feature": "Cheongju Early Printing Museum and Sangdangsanseong Fortress"},
                "jp": {"name": "清州市", "description": "忠清北道の道庁所在地",
                       "feature": "清州古印刷博物館と上党山城"},
                "cn": {"name": "清州市", "description": "忠清北道道政府所在地", "feature": "清州古印刷博物馆和上党山城"}
            }, "favorite_count": 8, "latitude": 36.6424, "longitude": 127.4890},

            {"region_id": 11, "tour_api_subcode": "11", "translations": {
                "ko": {"name": "충주시", "description": "충주호와 중원문화가 있는 중부내륙", "feature": "충주호와 중원고구려비"},
                "en": {"name": "Chungju-si", "description": "Central inland with Chungju Lake and Jungwon culture",
                       "feature": "Chungju Lake and Jungwon Goguryeo Stele"},
                "jp": {"name": "忠州市", "description": "忠州湖と中原文化がある中部内陸",
                       "feature": "忠州湖と中原高句麗碑"},
                "cn": {"name": "忠州市", "description": "忠州湖和中原文化所在的中部内陆",
                       "feature": "忠州湖和中原高句丽碑"}
            }, "favorite_count": 6, "latitude": 37.0138, "longitude": 127.9259},

            {"region_id": 11, "tour_api_subcode": "12", "translations": {
                "ko": {"name": "증평군", "description": "좌구산휴양림과 미니어처빌리지가 있는 작은군", "feature": "좌구산휴양림과 미니어처빌리지"},
                "en": {"name": "Jeungpyeong-gun",
                       "description": "Small county with Jwagusan Recreation Forest and Miniature Village",
                       "feature": "Jwagusan Recreation Forest and Miniature Village"},
                "jp": {"name": "曾坪郡", "description": "左九山休養林とミニチュアビレッジがある小さな郡",
                       "feature": "左九山休養林とミニチュアビレッジ"},
                "cn": {"name": "曾坪郡", "description": "左九山休养林和微缩村庄所在的小郡",
                       "feature": "左九山休养林和微缩村庄"}
            }, "favorite_count": 3, "latitude": 36.7819, "longitude": 127.5825},

            # ===== 충청남도 (15개 시/군) =====
            {"region_id": 12, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "공주시", "description": "백제의 고도와 공산성이 있는 역사도시", "feature": "공산성과 무령왕릉"},
                "en": {"name": "Gongju-si", "description": "Historic city with ancient Baekje capital and Gongsanseong",
                       "feature": "Gongsanseong Fortress and Tomb of King Muryeong"},
                "jp": {"name": "公州市", "description": "百済の古都と公山城がある歴史都市",
                       "feature": "公山城と武寧王陵"},
                "cn": {"name": "公州市", "description": "百济古都和公山城所在的历史城市", "feature": "公山城和武宁王陵"}
            }, "favorite_count": 12, "latitude": 36.4465, "longitude": 127.1189},

            {"region_id": 12, "tour_api_subcode": "2", "translations": {
                "ko": {"name": "금산군", "description": "금산인삼과 적벽강이 있는 산간군", "feature": "금산인삼과 적벽강"},
                "en": {"name": "Geumsan-gun", "description": "Mountain county with Geumsan ginseng and Jeokbyeokgang",
                       "feature": "Geumsan ginseng and Jeokbyeokgang River"},
                "jp": {"name": "錦山郡", "description": "錦山人参と赤壁江がある山間郡", "feature": "錦山人参と赤壁江"},
                "cn": {"name": "锦山郡", "description": "锦山人参和赤壁江所在的山区郡", "feature": "锦山人参和赤壁江"}
            }, "favorite_count": 7, "latitude": 36.1086, "longitude": 127.4880},

            {"region_id": 12, "tour_api_subcode": "3", "translations": {
                "ko": {"name": "논산시", "description": "관촉사와 연무대가 있는 역사도시", "feature": "관촉사와 연무대"},
                "en": {"name": "Nonsan-si", "description": "Historic city with Gwanchoksa Temple and Yeonmudae",
                       "feature": "Gwanchoksa Temple and Yeonmudae Training Ground"},
                "jp": {"name": "論山市", "description": "灌燭寺と練武台がある歴史都市", "feature": "灌燭寺と練武台"},
                "cn": {"name": "论山市", "description": "灌烛寺和练武台所在的历史城市", "feature": "灌烛寺和练武台"}
            }, "favorite_count": 6, "latitude": 36.1871, "longitude": 127.0987},

            {"region_id": 12, "tour_api_subcode": "4", "translations": {
                "ko": {"name": "당진시", "description": "석문면과 합덕제가 있는 서해안도시", "feature": "석문면간척지와 합덕제"},
                "en": {"name": "Dangjin-si", "description": "West coast city with Seokmun-myeon and Hapdeokje",
                       "feature": "Seokmun-myeon reclaimed land and Hapdeokje reservoir"},
                "jp": {"name": "唐津市", "description": "石門面と合徳堤がある西海岸都市",
                       "feature": "石門面干拓地と合徳堤"},
                "cn": {"name": "唐津市", "description": "石门面和合德堤所在的西海岸城市",
                       "feature": "石门面围垦地和合德堤"}
            }, "favorite_count": 5, "latitude": 36.8934, "longitude": 126.6297},

            {"region_id": 12, "tour_api_subcode": "5", "translations": {
                "ko": {"name": "보령시", "description": "머드축제로 유명한 서해안 관광도시", "feature": "대천해수욕장과 머드축제"},
                "en": {"name": "Boryeong-si", "description": "West coast tourism city famous for Mud Festival",
                       "feature": "Daecheon Beach and Mud Festival"},
                "jp": {"name": "保寧市", "description": "マッドフェスティバルで有名な西海岸観光都市",
                       "feature": "大川海水浴場とマッドフェスティバル"},
                "cn": {"name": "保宁市", "description": "以泥浆节闻名的西海岸旅游城市",
                       "feature": "大川海水浴场和泥浆节"}
            }, "favorite_count": 10, "latitude": 36.3333, "longitude": 126.6128},

            {"region_id": 12, "tour_api_subcode": "6", "translations": {
                "ko": {"name": "부여군", "description": "백제문화단지와 정림사지가 있는 백제고도", "feature": "백제문화단지와 정림사지"},
                "en": {"name": "Buyeo-gun",
                       "description": "Ancient Baekje capital with Baekje Cultural Land and Jeongnimsaji",
                       "feature": "Baekje Cultural Land and Jeongnimsaji Temple Site"},
                "jp": {"name": "扶余郡", "description": "百済文化団地と定林寺址がある百済古都",
                       "feature": "百済文化団地と定林寺址"},
                "cn": {"name": "扶余郡", "description": "百济文化园区和定林寺址所在的百济古都",
                       "feature": "百济文化园区和定林寺址"}
            }, "favorite_count": 11, "latitude": 36.2756, "longitude": 126.9100},

            {"region_id": 12, "tour_api_subcode": "7", "translations": {
                "ko": {"name": "서산시", "description": "해미읍성과 간월암이 있는 서해안도시", "feature": "해미읍성과 간월암"},
                "en": {"name": "Seosan-si", "description": "West coast city with Haemi Fortress and Ganwolam",
                       "feature": "Haemi Fortress and Ganwolam Hermitage"},
                "jp": {"name": "瑞山市", "description": "海美邑城と看月庵がある西海岸都市",
                       "feature": "海美邑城と看月庵"},
                "cn": {"name": "瑞山市", "description": "海美邑城和看月庵所在的西海岸城市",
                       "feature": "海美邑城和看月庵"}
            }, "favorite_count": 9, "latitude": 36.7848, "longitude": 126.4503},

            {"region_id": 12, "tour_api_subcode": "8", "translations": {
                "ko": {"name": "서천군", "description": "국립생태원과 춘장대해수욕장이 있는 생태군", "feature": "국립생태원과 춘장대해수욕장"},
                "en": {"name": "Seocheon-gun",
                       "description": "Ecological county with National Institute of Ecology and Chungjangdae Beach",
                       "feature": "National Institute of Ecology and Chungjangdae Beach"},
                "jp": {"name": "舒川郡", "description": "国立生態院と春長台海水浴場がある生態郡",
                       "feature": "国立生態院と春長台海水浴場"},
                "cn": {"name": "舒川郡", "description": "国立生态院和春长台海水浴场所在的生态郡",
                       "feature": "国立生态院和春长台海水浴场"}
            }, "favorite_count": 8, "latitude": 36.0780, "longitude": 126.6919},

            {"region_id": 12, "tour_api_subcode": "9", "translations": {
                "ko": {"name": "아산시", "description": "온양온천과 현충사가 있는 온천도시", "feature": "온양온천과 현충사"},
                "en": {"name": "Asan-si",
                       "description": "Hot spring city with Onyang Hot Springs and Hyeonchungsa Shrine",
                       "feature": "Onyang Hot Springs and Hyeonchungsa Shrine"},
                "jp": {"name": "牙山市", "description": "温陽温泉と顕忠祠がある温泉都市",
                       "feature": "温陽温泉と顕忠祠"},
                "cn": {"name": "牙山市", "description": "温阳温泉和显忠祠所在的温泉城市", "feature": "温阳温泉和显忠祠"}
            }, "favorite_count": 10, "latitude": 36.7898, "longitude": 127.0018},

            {"region_id": 12, "tour_api_subcode": "11", "translations": {
                "ko": {"name": "예산군", "description": "수덕사와 윤봉길의사 생가가 있는 역사군", "feature": "수덕사와 윤봉길의사 생가"},
                "en": {"name": "Yesan-gun",
                       "description": "Historic county with Sudeoksa Temple and Yun Bong-gil's birthplace",
                       "feature": "Sudeoksa Temple and Yun Bong-gil's birthplace"},
                "jp": {"name": "礼山郡", "description": "修徳寺と尹奉吉義士生家がある歴史郡",
                       "feature": "修徳寺と尹奉吉義士生家"},
                "cn": {"name": "礼山郡", "description": "修德寺和尹奉吉义士故居所在的历史郡",
                       "feature": "修德寺和尹奉吉义士故居"}
            }, "favorite_count": 7, "latitude": 36.6791, "longitude": 126.8428},

            {"region_id": 12, "tour_api_subcode": "12", "translations": {
                "ko": {"name": "청양군", "description": "청양고추와 칠갑산이 있는 산간군", "feature": "청양고추와 칠갑산"},
                "en": {"name": "Cheongyang-gun",
                       "description": "Mountain county with Cheongyang peppers and Chilgapsan",
                       "feature": "Cheongyang peppers and Chilgapsan Mountain"},
                "jp": {"name": "青陽郡", "description": "青陽唐辛子と七甲山がある山間郡",
                       "feature": "청양唐辛子と七甲山"},
                "cn": {"name": "青阳郡", "description": "청양辣椒和七甲山所在的山区郡", "feature": "청양辣椒和七甲山"}
            }, "favorite_count": 6, "latitude": 36.4593, "longitude": 126.8022},

            {"region_id": 12, "tour_api_subcode": "13", "translations": {
                "ko": {"name": "천안시", "description": "교통의 요지이자 독립기념관이 있는 도시", "feature": "독립기념관과 아라리오"},
                "en": {"name": "Cheonan-si", "description": "Transportation hub and city with Independence Hall",
                       "feature": "Independence Hall and Arario"},
                "jp": {"name": "天安市", "description": "交通の要地かつ独立記念館がある都市",
                       "feature": "独立記念館とアラリオ"},
                "cn": {"name": "天安市", "description": "交통要地和독립纪念馆所在的城市", "feature": "독립纪念馆和阿拉里奥"}
            }, "favorite_count": 7, "latitude": 36.8151, "longitude": 127.1139},

            {"region_id": 12, "tour_api_subcode": "14", "translations": {
                "ko": {"name": "태안군", "description": "안면도와 꽃지해수욕장이 있는 해안군", "feature": "안면도와 꽃지해수욕장"},
                "en": {"name": "Taean-gun", "description": "Coastal county with Anmyeondo and Kkotji Beach",
                       "feature": "Anmyeondo Island and Kkotji Beach"},
                "jp": {"name": "泰安郡", "description": "安眠島と花芝海水浴場がある海岸郡",
                       "feature": "安眠島と花芝海水浴場"},
                "cn": {"name": "泰安郡", "description": "安眠岛和花芝海水浴场所在的海岸郡",
                       "feature": "安眠岛和花芝해수욕장"}
            }, "favorite_count": 9, "latitude": 36.7455, "longitude": 126.2983},

            {"region_id": 12, "tour_api_subcode": "15", "translations": {
                "ko": {"name": "홍성군", "description": "홍성읍과 결성면이 있는 충남의 중심", "feature": "홍성읍과 결성면"},
                "en": {"name": "Hongseong-gun",
                       "description": "Center of Chungnam with Hongseong-eup and Gyeolseong-myeon",
                       "feature": "Hongseong-eup and Gyeolseong-myeon"},
                "jp": {"name": "洪城郡", "description": "洪城邑と結城面がある忠南の中心", "feature": "洪城邑と結城面"},
                "cn": {"name": "洪城郡", "description": "洪城邑和结城面所在的忠南中심", "feature": "洪城邑和결城面"}
            }, "favorite_count": 5, "latitude": 36.6012, "longitude": 126.6609},

            {"region_id": 12, "tour_api_subcode": "16", "translations": {
                "ko": {"name": "계룡시", "description": "계룡산과 국방대학교가 있는 군사도시", "feature": "계룡산과 국방대학교"},
                "en": {"name": "Gyeryong-si",
                       "description": "Military city with Gyeryongsan and Korea National Defense University",
                       "feature": "Gyeryongsan Mountain and Korea National Defense University"},
                "jp": {"name": "鶏龍市", "description": "鶏龍山と国防大学校がある軍事都市",
                       "feature": "鶏龍山と国防大学校"},
                "cn": {"name": "鸡龙市", "description": "鸡龙山和国防大学所在的军事城市", "feature": "鸡龙山和国防大学"}
            }, "favorite_count": 6, "latitude": 36.2743, "longitude": 127.2149},

            # ===== 경상북도 (23개 시/군) =====
            {"region_id": 13, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "경산시", "description": "영남대학교와 와촌면이 있는 교육도시", "feature": "영남대학교와 와촌면"},
                "en": {"name": "Gyeongsan-si",
                       "description": "Education city with Yeungnam University and Wachon-myeon",
                       "feature": "Yeungnam University and Wachon-myeon"},
                "jp": {"name": "慶山市", "description": "嶺南大学校と瓦村面がある教育都市",
                       "feature": "嶺南大学校と瓦村面"},
                "cn": {"name": "庆山市", "description": "岭南大学和瓦村面所在的教育城市", "feature": "岭南大学和瓦村面"}
            }, "favorite_count": 6, "latitude": 35.8250, "longitude": 128.7411},

            {"region_id": 13, "tour_api_subcode": "2", "translations": {
                "ko": {"name": "경주시", "description": "신라 천년의 고도", "feature": "불국사와 석굴암"},
                "en": {"name": "Gyeongju-si", "description": "Ancient capital of millennium Silla",
                       "feature": "Bulguksa Temple and Seokguram Grotto"},
                "jp": {"name": "慶州市", "description": "新羅千年の古都", "feature": "仏国寺と石窟庵"},
                "cn": {"name": "庆州市", "description": "新罗千年古都", "feature": "佛国寺和石窟庵"}
            }, "favorite_count": 25, "latitude": 35.8562, "longitude": 129.2250},

            {"region_id": 13, "tour_api_subcode": "3", "translations": {
                "ko": {"name": "고령군", "description": "대가야박물관과 지산동고분군이 있는 가야군", "feature": "대가야박물관과 지산동고분군"},
                "en": {"name": "Goryeong-gun",
                       "description": "Gaya county with Daegaya Museum and Jisan-dong Tomb Complex",
                       "feature": "Daegaya Museum and Jisan-dong Tomb Complex"},
                "jp": {"name": "高霊郡", "description": "大伽耶博物館と池山洞古墳群がある伽耶郡",
                       "feature": "大伽耶博物館と池山洞古墳群"},
                "cn": {"name": "高灵郡", "description": "大伽耶博物馆和池山洞古坟群所在的伽耶郡",
                       "feature": "大伽耶博物馆和池山洞古坟群"}
            }, "favorite_count": 8, "latitude": 35.7274, "longitude": 128.2635},

            {"region_id": 13, "tour_api_subcode": "4", "translations": {
                "ko": {"name": "구미시", "description": "삼성전자와 구미전자공업단지가 있는 전자도시", "feature": "삼성전자와 구미전자공업단지"},
                "en": {"name": "Gumi-si",
                       "description": "Electronics city with Samsung Electronics and Gumi Electronics Industrial Complex",
                       "feature": "Samsung Electronics and Gumi Electronics Industrial Complex"},
                "jp": {"name": "亀尾市", "description": "サムスン電子と亀尾電子工業団地がある電子都市",
                       "feature": "サムスン電子と亀尾電子工業団地"},
                "cn": {"name": "龟尾市", "description": "三星电子和龟尾电子工业园区所在的电子城市",
                       "feature": "三星电子和龟尾电子工业园区"}
            }, "favorite_count": 8, "latitude": 36.1195, "longitude": 128.3441},

            {"region_id": 13, "tour_api_subcode": "6", "translations": {
                "ko": {"name": "김천시", "description": "직지사와 황악산이 있는 불교도시", "feature": "직지사와 황악산"},
                "en": {"name": "Gimcheon-si", "description": "Buddhist city with Jikjisa Temple and Hwangaksan",
                       "feature": "Jikjisa Temple and Hwangaksan Mountain"},
                "jp": {"name": "金泉市", "description": "直指寺と黄岳山がある仏教都市", "feature": "直指寺と黄岳山"},
                "cn": {"name": "金泉市", "description": "直指寺和黄岳山所在的佛教城市", "feature": "直指寺和黄岳山"}
            }, "favorite_count": 7, "latitude": 36.1399, "longitude": 128.1137},

            {"region_id": 13, "tour_api_subcode": "7", "translations": {
                "ko": {"name": "문경시", "description": "문경새재와 문경온천이 있는 관문도시", "feature": "문경새재와 문경온천"},
                "en": {"name": "Mungyeong-si",
                       "description": "Gateway city with Mungyeong Saejae and Mungyeong Hot Springs",
                       "feature": "Mungyeong Saejae Pass and Mungyeong Hot Springs"},
                "jp": {"name": "聞慶市", "description": "聞慶セジェと聞慶温泉がある関門都市",
                       "feature": "聞慶セジェと聞慶温泉"},
                "cn": {"name": "闻庆市", "description": "闻庆鸟岭和闻庆温泉所在的关门城市",
                       "feature": "闻庆鸟岭和闻庆温泉"}
            }, "favorite_count": 9, "latitude": 36.5867, "longitude": 128.1866},

            {"region_id": 13, "tour_api_subcode": "8", "translations": {
                "ko": {"name": "봉화군", "description": "청량산과 춘양목이 있는 산림군", "feature": "청량산과 춘양목"},
                "en": {"name": "Bonghwa-gun", "description": "Forest county with Cheongnyangsan and Chunyang pine",
                       "feature": "Cheongnyangsan Mountain and Chunyang pine"},
                "jp": {"name": "奉化郡", "description": "清涼山と春陽木がある山林郡", "feature": "清涼山と春陽木"},
                "cn": {"name": "奉化郡", "description": "清凉山和春阳木所在的山林郡", "feature": "清凉山和春阳木"}
            }, "favorite_count": 7, "latitude": 36.8931, "longitude": 128.7320},

            {"region_id": 13, "tour_api_subcode": "9", "translations": {
                "ko": {"name": "상주시", "description": "상주곶감과 경천대가 있는 농업도시", "feature": "상주곶감과 경천대"},
                "en": {"name": "Sangju-si",
                       "description": "Agricultural city with Sangju dried persimmons and Gyeongcheon-dae",
                       "feature": "Sangju dried persimmons and Gyeongcheon-dae"},
                "jp": {"name": "尚州市", "description": "尚州干し柿と景天台がある農業都市",
                       "feature": "尚州干し柿と景天台"},
                "cn": {"name": "尚州市", "description": "尚州柿饼和景天台所在的农业城市", "feature": "尚州柿饼和景天台"}
            }, "favorite_count": 7, "latitude": 36.4109, "longitude": 128.1591},

            {"region_id": 13, "tour_api_subcode": "10", "translations": {
                "ko": {"name": "성주군", "description": "성주참외와 성주산성이 있는 농업군", "feature": "성주참외와 성주산성"},
                "en": {"name": "Seongju-gun",
                       "description": "Agricultural county with Seongju melons and Seongju Fortress",
                       "feature": "Seongju melons and Seongju Fortress"},
                "jp": {"name": "星州郡", "description": "星州マスクメロンと星州山城がある農業郡",
                       "feature": "星州マスクメロンと星州山城"},
                "cn": {"name": "星州郡", "description": "星州甜瓜和星州山城所在的农业郡",
                       "feature": "星州甜瓜和星州山城"}
            }, "favorite_count": 6, "latitude": 35.9189, "longitude": 128.2823},

            {"region_id": 13, "tour_api_subcode": "11", "translations": {
                "ko": {"name": "안동시", "description": "하회마을과 한국정신문화의 수도", "feature": "안동 하회마을과 도산서원"},
                "en": {"name": "Andong-si", "description": "Capital of Korean spiritual culture with Hahoe Village",
                       "feature": "Andong Hahoe Village and Dosan Seowon"},
                "jp": {"name": "安東市", "description": "河回村と韓国精神文化の首都",
                       "feature": "安東河回村と陶山書院"},
                "cn": {"name": "安东市", "description": "河回村和韩国精神文化之都", "feature": "安东河回村和陶山书院"}
            }, "favorite_count": 18, "latitude": 36.5684, "longitude": 128.7294},

            {"region_id": 13, "tour_api_subcode": "12", "translations": {
                "ko": {"name": "영덕군", "description": "영덕대게와 강구항이 있는 동해안군", "feature": "영덕대게와 강구항"},
                "en": {"name": "Yeongdeok-gun",
                       "description": "East coast county with Yeongdeok snow crab and Ganggu Port",
                       "feature": "Yeongdeok snow crab and Ganggu Port"},
                "jp": {"name": "盈德郡", "description": "盈德ズワイガニと江口港がある東海岸郡",
                       "feature": "盈德ズワイガニと江口港"},
                "cn": {"name": "盈德郡", "description": "盈德雪蟹和江口港所在的东海岸郡", "feature": "盈德雪蟹和江口港"}
            }, "favorite_count": 10, "latitude": 36.4151, "longitude": 129.3665},

            {"region_id": 13, "tour_api_subcode": "13", "translations": {
                "ko": {"name": "영양군", "description": "영양고추와 일월산이 있는 산간군", "feature": "영양고추와 일월산"},
                "en": {"name": "Yeongyang-gun", "description": "Mountain county with Yeongyang peppers and Ilwolsan",
                       "feature": "Yeongyang peppers and Ilwolsan Mountain"},
                "jp": {"name": "英陽郡", "description": "英陽唐辛子と日月山がある山間郡",
                       "feature": "英陽唐辛子と日月山"},
                "cn": {"name": "英阳郡", "description": "英阳辣椒和日月山所在的山区郡", "feature": "英阳辣椒和日月山"}
            }, "favorite_count": 5, "latitude": 36.6695, "longitude": 129.1126},

            {"region_id": 13, "tour_api_subcode": "14", "translations": {
                "ko": {"name": "영주시", "description": "부석사와 소수서원이 있는 유교문화도시", "feature": "부석사와 소수서원"},
                "en": {"name": "Yeongju-si",
                       "description": "Confucian cultural city with Buseoksa Temple and Sosu Seowon",
                       "feature": "Buseoksa Temple and Sosu Seowon"},
                "jp": {"name": "栄州市", "description": "浮石寺と紹修書院がある儒教文化都市",
                       "feature": "浮石寺と紹修書院"},
                "cn": {"name": "荣州市", "description": "浮石寺和绍修书院所在的儒教文化城市",
                       "feature": "浮石寺和绍修书院"}
            }, "favorite_count": 12, "latitude": 36.8056, "longitude": 128.6240},

            {"region_id": 13, "tour_api_subcode": "15", "translations": {
                "ko": {"name": "영천시", "description": "보현산천문대와 영천시장이 있는 과학도시", "feature": "보현산천문대와 영천시장"},
                "en": {"name": "Yeongcheon-si",
                       "description": "Science city with Bohyeonsan Observatory and Yeongcheon Market",
                       "feature": "Bohyeonsan Observatory and Yeongcheon Market"},
                "jp": {"name": "永川市", "description": "普賢山天文台と永川市場がある科学都市",
                       "feature": "普賢山天文台と永川市場"},
                "cn": {"name": "永川市", "description": "普贤山天文台和永川市场所在的科学城市",
                       "feature": "普贤山天文台和永川市场"}
            }, "favorite_count": 6, "latitude": 35.9733, "longitude": 128.9386},

            {"region_id": 13, "tour_api_subcode": "16", "translations": {
                "ko": {"name": "예천군", "description": "회룡포와 삼강주막이 있는 강변군", "feature": "회룡포와 삼강주막"},
                "en": {"name": "Yecheon-gun", "description": "Riverside county with Hoeryongpo and Samgang Jumak",
                       "feature": "Hoeryongpo and Samgang Jumak"},
                "jp": {"name": "醴泉郡", "description": "回龍浦と三江酒幕がある川辺郡", "feature": "回龍浦と三江酒幕"},
                "cn": {"name": "醴泉郡", "description": "回龙浦和三江酒幕所在的江边郡", "feature": "回龙浦和三江酒幕"}
            }, "favorite_count": 8, "latitude": 36.6553, "longitude": 128.4516},

            {"region_id": 13, "tour_api_subcode": "17", "translations": {
                "ko": {"name": "울릉군", "description": "독도와 울릉도가 있는 동해의 섬", "feature": "독도와 울릉도"},
                "en": {"name": "Ulleung-gun", "description": "East Sea island with Dokdo and Ulleungdo",
                       "feature": "Dokdo and Ulleungdo Islands"},
                "jp": {"name": "鬱陵郡", "description": "独島と鬱陵島がある東海の島", "feature": "独島と鬱陵島"},
                "cn": {"name": "郁陵郡", "description": "独岛和郁陵岛所在的东海岛屿", "feature": "独岛和郁陵岛"}
            }, "favorite_count": 15, "latitude": 37.4844, "longitude": 130.9058},

            {"region_id": 13, "tour_api_subcode": "18", "translations": {
                "ko": {"name": "울진군", "description": "울진금강송과 불영사가 있는 동해안군", "feature": "울진금강송과 불영사"},
                "en": {"name": "Uljin-gun",
                       "description": "East coast county with Uljin Geumgangsong pine and Bulyeongsa Temple",
                       "feature": "Uljin Geumgangsong pine and Bulyeongsa Temple"},
                "jp": {"name": "蔚珍郡", "description": "蔚珍金剛松と仏影寺がある東海岸郡",
                       "feature": "蔚珍金剛松と仏影寺"},
                "cn": {"name": "蔚珍郡", "description": "蔚珍金刚松和佛影寺所在的东海岸郡",
                       "feature": "蔚珍金刚松和佛影寺"}
            }, "favorite_count": 8, "latitude": 36.9931, "longitude": 129.4003},

            {"region_id": 13, "tour_api_subcode": "19", "translations": {
                "ko": {"name": "의성군", "description": "의성마늘과 조문국박물관이 있는 농업군", "feature": "의성마늘과 조문국박물관"},
                "en": {"name": "Uiseong-gun",
                       "description": "Agricultural county with Uiseong garlic and Jomungguk Museum",
                       "feature": "Uiseong garlic and Jomungguk Museum"},
                "jp": {"name": "義城郡", "description": "義城ニンニクと召文国博物館がある農業郡",
                       "feature": "義城ニンニクと召文国博物館"},
                "cn": {"name": "义城郡", "description": "义城大蒜和召文国博物馆所在的农业郡",
                       "feature": "义城大蒜和召文国博物馆"}
            }, "favorite_count": 5, "latitude": 36.3522, "longitude": 128.6975},

            {"region_id": 13, "tour_api_subcode": "20", "translations": {
                "ko": {"name": "청도군", "description": "청도소싸움과 프로방스마을이 있는 체험군", "feature": "청도소싸움과 프로방스마을"},
                "en": {"name": "Cheongdo-gun",
                       "description": "Experience county with Cheongdo bull fighting and Provence Village",
                       "feature": "Cheongdo bull fighting and Provence Village"},
                "jp": {"name": "清道郡", "description": "清道闘牛とプロバンス村がある体験郡",
                       "feature": "清道闘牛とプロバンス村"},
                "cn": {"name": "清道郡", "description": "清道斗牛和普罗旺斯村所在的体验郡",
                       "feature": "清道斗牛和普罗旺斯村"}
            }, "favorite_count": 8, "latitude": 35.6484, "longitude": 128.7357},

            {"region_id": 13, "tour_api_subcode": "21", "translations": {
                "ko": {"name": "청송군", "description": "주왕산과 청송사과가 있는 산간군", "feature": "주왕산과 청송사과"},
                "en": {"name": "Cheongsong-gun", "description": "Mountain county with Juwangsan and Cheongsong apples",
                       "feature": "Juwangsan Mountain and Cheongsong apples"},
                "jp": {"name": "青松郡", "description": "周王山と青松リンゴがある山間郡",
                       "feature": "周王山と青松リンゴ"},
                "cn": {"name": "青松郡", "description": "周王山和青松苹果所在的山区郡", "feature": "周王山和青松苹果"}
            }, "favorite_count": 9, "latitude": 36.4335, "longitude": 129.0572},

            {"region_id": 13, "tour_api_subcode": "22", "translations": {
                "ko": {"name": "칠곡군", "description": "가산산성과 인동장시장이 있는 역사군", "feature": "가산산성과 인동장시장"},
                "en": {"name": "Chilgok-gun", "description": "Historic county with Gasan Fortress and Indong Market",
                       "feature": "Gasan Fortress and Indong Market"},
                "jp": {"name": "漆谷郡", "description": "嘉山山城と仁同場市場がある歴史郡",
                       "feature": "嘉山山城と仁同場市場"},
                "cn": {"name": "漆谷郡", "description": "嘉山山城和仁同场市场所在的历史郡",
                       "feature": "嘉山山城和仁同场市场"}
            }, "favorite_count": 5, "latitude": 35.9955, "longitude": 128.4014},

            {"region_id": 13, "tour_api_subcode": "23", "translations": {
                "ko": {"name": "포항시", "description": "철강산업과 호미곶이 있는 동해안 도시", "feature": "호미곶과 포스코"},
                "en": {"name": "Pohang-si", "description": "East coast city with steel industry and Homigot Cape",
                       "feature": "Homigot Cape and POSCO"},
                "jp": {"name": "浦項市", "description": "鉄鋼産業と虎尾岬がある東海岸都市",
                       "feature": "虎尾岬とポスコ"},
                "cn": {"name": "浦项市", "description": "钢铁产业和虎尾岬所在的东海岸城市",
                       "feature": "虎尾岬和浦项制铁"}
            }, "favorite_count": 12, "latitude": 36.0190, "longitude": 129.3435},

            # ===== 경상남도 (18개 시/군) =====
            {"region_id": 14, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "거제시", "description": "거제도와 조선소가 있는 섬도시", "feature": "거제도와 대우조선해양"},
                "en": {"name": "Geoje-si", "description": "Island city with Geojedo and shipyard",
                       "feature": "Geojedo Island and Daewoo Shipbuilding & Marine Engineering"},
                "jp": {"name": "巨済市", "description": "巨済島と造船所がある島都市",
                       "feature": "巨済島と大宇造船海洋"},
                "cn": {"name": "巨济市", "description": "巨济岛和造船厂所在的岛屿城市",
                       "feature": "巨济岛和大宇造船海洋"}
            }, "favorite_count": 12, "latitude": 34.8807, "longitude": 128.6211},

            {"region_id": 14, "tour_api_subcode": "2", "translations": {
                "ko": {"name": "거창군", "description": "가조온천과 수승대가 있는 산간군", "feature": "가조온천과 수승대"},
                "en": {"name": "Geochang-gun", "description": "Mountain county with Gajo Hot Springs and Suseungdae",
                       "feature": "Gajo Hot Springs and Suseungdae"},
                "jp": {"name": "居昌郡", "description": "加祚温泉と水昇台がある山間郡", "feature": "加祚温泉と水昇台"},
                "cn": {"name": "居昌郡", "description": "加祚温泉和水升台所在的山区郡", "feature": "加祚温泉和水升台"}
            }, "favorite_count": 7, "latitude": 35.6871, "longitude": 127.9095},

            {"region_id": 14, "tour_api_subcode": "3", "translations": {
                "ko": {"name": "고성군", "description": "공룡발자국과 당항포가 있는 남해안군", "feature": "공룡발자국과 당항포"},
                "en": {"name": "Goseong-gun",
                       "description": "South coast county with dinosaur footprints and Danghangpo",
                       "feature": "Dinosaur footprints and Danghangpo Port"},
                "jp": {"name": "固城郡", "description": "恐竜足跡と唐項浦がある南海岸郡",
                       "feature": "恐竜足跡と唐項浦"},
                "cn": {"name": "固城郡", "description": "恐龙足迹和唐项浦所在的南海岸郡", "feature": "恐龙足迹和唐项浦"}
            }, "favorite_count": 9, "latitude": 34.9732, "longitude": 128.3227},

            {"region_id": 14, "tour_api_subcode": "4", "translations": {
                "ko": {"name": "김해시", "description": "가야의 고도이자 김해공항이 있는 도시", "feature": "수로왕릉과 가야의 숨결"},
                "en": {"name": "Gimhae-si", "description": "Ancient capital of Gaya with Gimhae Airport",
                       "feature": "Tomb of King Suro and Breath of Gaya"},
                "jp": {"name": "金海市", "description": "伽耶の古都かつ金海空港がある都市",
                       "feature": "首露王陵と伽耶の息吹"},
                "cn": {"name": "金海市", "description": "伽倻古都和金海机场所在的城市", "feature": "首露王陵和伽倻气息"}
            }, "favorite_count": 8, "latitude": 35.2281, "longitude": 128.8889},

            {"region_id": 14, "tour_api_subcode": "5", "translations": {
                "ko": {"name": "남해군", "description": "남해대교와 독일마을이 있는 섬군", "feature": "남해대교와 독일마을"},
                "en": {"name": "Namhae-gun", "description": "Island county with Namhae Bridge and German Village",
                       "feature": "Namhae Bridge and German Village"},
                "jp": {"name": "南海郡", "description": "南海大橋とドイツ村がある島郡",
                       "feature": "南海大橋とドイツ村"},
                "cn": {"name": "南海郡", "description": "南海大桥和德国村所在的岛郡", "feature": "南海大桥和德国村"}
            }, "favorite_count": 11, "latitude": 34.8374, "longitude": 127.8926},

            {"region_id": 14, "tour_api_subcode": "6", "translations": {
                "ko": {"name": "마산시", "description": "마산어시장과 가고파국화축제로 알려진 항만도시", "feature": "마산어시장과 가고파국화축제"},
                "en": {"name": "Masan-si", "description": "Port city known for Masan Fish Market and Chrysanthemum Festival", 
                       "feature": "Masan Fish Market and Chrysanthemum Festival"},
                "jp": {"name": "馬山市", "description": "馬山魚市場と菊花祭りで知られる港町", "feature": "馬山魚市場と菊花祭り"},
                "cn": {"name": "马山市", "description": "以马山鱼市场和菊花庆典闻名的港口城市", "feature": "马山鱼市场与菊花庆典"}
            }, "favorite_count": 7, "latitude": 35.2045, "longitude": 128.5725},            

            {"region_id": 14, "tour_api_subcode": "7", "translations": {
                "ko": {"name": "밀양시", "description": "밀양아리랑과 표충사가 있는 전통도시", "feature": "밀양아리랑과 표충사"},
                "en": {"name": "Miryang-si",
                       "description": "Traditional city with Miryang Arirang and Pyochungsa Temple",
                       "feature": "Miryang Arirang and Pyochungsa Temple"},
                "jp": {"name": "密陽市", "description": "密陽アリランと表忠寺がある伝統都市",
                       "feature": "密陽アリランと表忠寺"},
                "cn": {"name": "密阳市", "description": "密阳阿里郎和表忠寺所在的传统城市",
                       "feature": "密阳阿里郎和表忠寺"}
            }, "favorite_count": 8, "latitude": 35.5041, "longitude": 128.7463},

            {"region_id": 14, "tour_api_subcode": "8", "translations": {
                "ko": {"name": "사천시", "description": "한국항공우주산업과 실안해수욕장이 있는 항공도시", "feature": "한국항공우주산업과 실안해수욕장"},
                "en": {"name": "Sacheon-si",
                       "description": "Aviation city with Korea Aerospace Industries and Silan Beach",
                       "feature": "Korea Aerospace Industries and Silan Beach"},
                "jp": {"name": "泗川市", "description": "韓国航空宇宙産業と実安海水浴場がある航空都市",
                       "feature": "韓国航空宇宙産業と実安海水浴場"},
                "cn": {"name": "泗川市", "description": "韩国航空宇宙产业和实安海水浴场所在的航空城市",
                       "feature": "韩国航空宇宙产业和实安海水浴场"}
            }, "favorite_count": 7, "latitude": 35.0036, "longitude": 128.0645},

            {"region_id": 14, "tour_api_subcode": "9", "translations": {
                "ko": {"name": "산청군", "description": "지리산과 한의학박물관이 있는 산간군", "feature": "지리산과 한의학박물관"},
                "en": {"name": "Sancheong-gun",
                       "description": "Mountain county with Jirisan and Traditional Korean Medicine Museum",
                       "feature": "Jirisan Mountain and Traditional Korean Medicine Museum"},
                "jp": {"name": "山清郡", "description": "智異山と韓医学博物館がある山間郡",
                       "feature": "智異山と韓医学博物館"},
                "cn": {"name": "山清郡", "description": "智异山和韩医学博物馆所在的山区郡",
                       "feature": "智异山和韩医学博物馆"}
            }, "favorite_count": 9, "latitude": 35.4151, "longitude": 127.8733},

            {"region_id": 14, "tour_api_subcode": "10", "translations": {
                "ko": {"name": "양산시", "description": "통도사와 신불산이 있는 불교도시", "feature": "통도사와 신불산"},
                "en": {"name": "Yangsan-si", "description": "Buddhist city with Tongdosa Temple and Sinbulsan",
                       "feature": "Tongdosa Temple and Sinbulsan Mountain"},
                "jp": {"name": "梁山市", "description": "通度寺と神仏山がある仏教都市", "feature": "通度寺と神仏山"},
                "cn": {"name": "梁山市", "description": "通度寺和神佛山所在的佛教城市", "feature": "通度寺和神佛山"}
            }, "favorite_count": 9, "latitude": 35.3351, "longitude": 129.0378},

            {"region_id": 14, "tour_api_subcode": "12", "translations": {
                "ko": {"name": "의령군", "description": "의병박물관과 정암루가 있는 의병의고장", "feature": "의병박물관과 정암루"},
                "en": {"name": "Uiryeong-gun",
                       "description": "Hometown of righteous army with Uibyeong Museum and Jeongamnu",
                       "feature": "Uibyeong Museum and Jeongamnu Pavilion"},
                "jp": {"name": "宜寧郡", "description": "義兵博物館と鄭菴楼がある義兵の故郷",
                       "feature": "義兵博物館と鄭菴楼"},
                "cn": {"name": "宜宁郡", "description": "义兵博物馆和郑庵楼所在的义兵故乡",
                       "feature": "义兵博物馆和郑庵楼"}
            }, "favorite_count": 6, "latitude": 35.3220, "longitude": 128.2618},

            {"region_id": 14, "tour_api_subcode": "13", "translations": {
                "ko": {"name": "진주시", "description": "진주성과 유등축제로 유명한 역사도시", "feature": "진주성과 촉석루"},
                "en": {"name": "Jinju-si", "description": "Historic city famous for Jinju Castle and Lantern Festival",
                       "feature": "Jinju Castle and Chokseongnu Pavilion"},
                "jp": {"name": "晋州市", "description": "晋州城と流燈祭で有名な歴史都市", "feature": "晋州城と矗石楼"},
                "cn": {"name": "晋州市", "description": "晋州城和流灯节闻名的历史城市", "feature": "晋州城和矗石楼"}
            }, "favorite_count": 10, "latitude": 35.1800, "longitude": 128.1076},

            {"region_id": 14, "tour_api_subcode": "14", "translations": {
                "ko": {"name": "진해시", "description": "벚꽃으로 유명한 해군 도시", "feature": "진해군항제와 여좌천·경화역 벚꽃길"},
                "en": {"name": "Jinhae-si", "description": "Navy city famous for cherry blossoms",
                       "feature": "Jinhae Gunhangje Festival and Yeojwacheon/Gyeonghwa Station cherry blossom road"},
                "jp": {"name": "鎮海市", "description": "桜で有名な海軍の街", "feature": "鎮海軍港祭と余佐川・慶和駅の桜並木"},
                "cn": {"name": "镇海市", "description": "以樱花闻名的海军城市", "feature": "镇海军港节与余佐川·庆和站樱花路"}
            }, "favorite_count": 14, "latitude": 35.1490, "longitude": 128.6597},

            {"region_id": 14, "tour_api_subcode": "15", "translations": {
                "ko": {"name": "창녕군", "description": "우포늪과 부곡온천이 있는 생태군", "feature": "우포늪과 부곡온천"},
                "en": {"name": "Changnyeong-gun",
                       "description": "Ecological county with Upo Wetland and Bugok Hot Springs",
                       "feature": "Upo Wetland and Bugok Hot Springs"},
                "jp": {"name": "昌寧郡", "description": "牛浦沼と釜谷温泉がある生態郡", "feature": "牛浦沼と釜谷温泉"},
                "cn": {"name": "昌宁郡", "description": "牛浦沼和釜谷温泉所在的生态郡", "feature": "牛浦沼和釜谷温泉"}
            }, "favorite_count": 8, "latitude": 35.5445, "longitude": 128.4924},

            {"region_id": 14, "tour_api_subcode": "16", "translations": {
                "ko": {"name": "창원시", "description": "경상남도청이 있는 도청소재지", "feature": "창원시청과 용지호수공원"},
                "en": {"name": "Changwon-si", "description": "Provincial capital of Gyeongsangnam-do",
                       "feature": "Changwon City Hall and Yongji Lake Park"},
                "jp": {"name": "昌原市", "description": "慶尚南道庁がある道庁所在地",
                       "feature": "昌原市庁と龍池湖水公園"},
                "cn": {"name": "昌原市", "description": "庆尚南道道政府所在地", "feature": "昌原市政府和龙池湖水公园"}
            }, "favorite_count": 10, "latitude": 35.2281, "longitude": 128.6811},

            {"region_id": 14, "tour_api_subcode": "17", "translations": {
                "ko": {"name": "통영시", "description": "한려수도의 아름다운 바다도시", "feature": "통영케이블카와 동피랑"},
                "en": {"name": "Tongyeong-si", "description": "Beautiful sea city of Hallyeohaesang",
                       "feature": "Tongyeong Cable Car and Dongpirang"},
                "jp": {"name": "統営市", "description": "閑麗水道の美しい海都市",
                       "feature": "統営ケーブルカーと東皮郎"},
                "cn": {"name": "统营市", "description": "闲丽水道美丽的海洋城市", "feature": "统营缆车和东皮郎"}
            }, "favorite_count": 15, "latitude": 34.8543, "longitude": 128.4330},

            {"region_id": 14, "tour_api_subcode": "18", "translations": {
                "ko": {"name": "하동군", "description": "하동녹차와 화개장터가 있는 차의고장", "feature": "하동녹차와 화개장터"},
                "en": {"name": "Hadong-gun", "description": "Tea hometown with Hadong green tea and Hwagae Market",
                       "feature": "Hadong green tea and Hwagae Market"},
                "jp": {"name": "河東郡", "description": "河東緑茶と花開場터がある茶の故郷",
                       "feature": "河東緑茶と花開場터"},
                "cn": {"name": "河东郡", "description": "河东绿茶和花开集市所在的茶叶故乡",
                       "feature": "河东绿茶和花开集市"}
            }, "favorite_count": 9, "latitude": 35.0675, "longitude": 127.7514},

            {"region_id": 14, "tour_api_subcode": "19", "translations": {
                "ko": {"name": "함안군", "description": "아라가야와 함안연꽃축제가 있는 고대군", "feature": "아라가야와 함안연꽃축제"},
                "en": {"name": "Haman-gun", "description": "Ancient county with Ara-Gaya and Haman Lotus Festival",
                       "feature": "Ara-Gaya and Haman Lotus Festival"},
                "jp": {"name": "咸安郡", "description": "阿羅伽耶と咸安蓮花祭がある古代郡",
                       "feature": "阿羅伽耶と咸安蓮花祭"},
                "cn": {"name": "咸安郡", "description": "阿罗伽倻和咸安莲花节所在的古代郡",
                       "feature": "阿罗伽倻和咸安莲花节"}
            }, "favorite_count": 7, "latitude": 35.2722, "longitude": 128.4065},

            {"region_id": 14, "tour_api_subcode": "20", "translations": {
                "ko": {"name": "함양군", "description": "지리산과 상림공원이 있는 산간군", "feature": "지리산과 상림공원"},
                "en": {"name": "Hamyang-gun", "description": "Mountain county with Jirisan and Sangnim Park",
                       "feature": "Jirisan Mountain and Sangnim Park"},
                "jp": {"name": "咸陽郡", "description": "智異山と上林公園がある山間郡", "feature": "智異山と上林公園"},
                "cn": {"name": "咸阳郡", "description": "智异山和上林公园所在的山区郡", "feature": "智异山和上林公园"}
            }, "favorite_count": 8, "latitude": 35.5204, "longitude": 127.7250},

            {"region_id": 14, "tour_api_subcode": "21", "translations": {
                "ko": {"name": "합천군", "description": "해인사와 팔만대장경이 있는 불교성지", "feature": "해인사와 팔만대장경"},
                "en": {"name": "Hapcheon-gun",
                       "description": "Buddhist sanctuary with Haeinsa Temple and Tripitaka Koreana",
                       "feature": "Haeinsa Temple and Tripitaka Koreana"},
                "jp": {"name": "陜川郡", "description": "海印寺と八万大蔵経がある仏教聖地",
                       "feature": "海印寺と八万大蔵経"},
                "cn": {"name": "陕川郡", "description": "海印寺和八万大藏经所在的佛教圣地",
                       "feature": "海印寺和八万大藏经"}
            }, "favorite_count": 12, "latitude": 35.5664, "longitude": 128.1695},

            # ===== 전북특별자치도 (14개 시/군) =====
            {"region_id": 15, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "고창군", "description": "고창갯벌과 운곡습지가 있는 생태군", "feature": "고창갯벌과 운곡습지"},
                "en": {"name": "Gochang-gun",
                       "description": "Ecological county with Gochang Tidal Flat and Ungok Wetland",
                       "feature": "Gochang Tidal Flat and Ungok Wetland"},
                "jp": {"name": "高敞郡", "description": "高敞干潟と雲谷湿地がある生態郡",
                       "feature": "高敞干潟と雲谷湿地"},
                "cn": {"name": "高敞郡", "description": "高敞滩涂和云谷湿地所在的生态郡",
                       "feature": "高敞滩涂和云谷湿地"}
            }, "favorite_count": 8, "latitude": 35.4355, "longitude": 126.7011},

            {"region_id": 15, "tour_api_subcode": "2", "translations": {
                "ko": {"name": "군산시", "description": "근대문화유산과 새만금이 있는 항구도시", "feature": "군산근대역사박물관과 이성당"},
                "en": {"name": "Gunsan-si", "description": "Port city with modern cultural heritage and Saemangeum",
                       "feature": "Gunsan Modern History Museum and Iseongdang"},
                "jp": {"name": "群山市", "description": "近代文化遺産とセマングムがある港都市",
                       "feature": "群山近代歴史博物館と李成堂"},
                "cn": {"name": "群山市", "description": "近代文化遗产和新万金所在的港口城市",
                       "feature": "群山近代历史博物馆和李成堂"}
            }, "favorite_count": 8, "latitude": 35.9676, "longitude": 126.7369},

            {"region_id": 15, "tour_api_subcode": "3", "translations": {
                "ko": {"name": "김제시", "description": "김제평야와 금산사가 있는 농업도시", "feature": "김제평야와 금산사"},
                "en": {"name": "Gimje-si", "description": "Agricultural city with Gimje Plain and Geumsansa Temple",
                       "feature": "Gimje Plain and Geumsansa Temple"},
                "jp": {"name": "金堤市", "description": "金堤平野と金山寺がある農業都市",
                       "feature": "金堤平野と金山寺"},
                "cn": {"name": "金堤市", "description": "金堤平原和金山寺所在的农业城市", "feature": "金堤平原和金山寺"}
            }, "favorite_count": 6, "latitude": 35.8039, "longitude": 126.8819},

            {"region_id": 15, "tour_api_subcode": "4", "translations": {
                "ko": {"name": "남원시", "description": "춘향전과 지리산이 있는 문학도시", "feature": "춘향테마파크와 지리산"},
                "en": {"name": "Namwon-si", "description": "Literary city with Chunhyang story and Jirisan",
                       "feature": "Chunhyang Theme Park and Jirisan Mountain"},
                "jp": {"name": "南原市", "description": "春香伝と智異山がある文学都市",
                       "feature": "春香テーマパークと智異山"},
                "cn": {"name": "南原市", "description": "春香传和智异山所在的文学城市",
                       "feature": "春香主题公园和智异山"}
            }, "favorite_count": 10, "latitude": 35.4164, "longitude": 127.3904},

            {"region_id": 15, "tour_api_subcode": "5", "translations": {
                "ko": {"name": "무주군", "description": "무주리조트와 덕유산이 있는 산간군", "feature": "무주리조트와 덕유산"},
                "en": {"name": "Muju-gun", "description": "Mountain county with Muju Resort and Deogyusan",
                       "feature": "Muju Resort and Deogyusan Mountain"},
                "jp": {"name": "茂朱郡", "description": "茂朱リゾートと徳裕山がある山間郡",
                       "feature": "茂朱リゾートと徳裕山"},
                "cn": {"name": "茂朱郡", "description": "茂朱度假村和德裕山所在的山区郡",
                       "feature": "茂朱度假村和德裕山"}
            }, "favorite_count": 9, "latitude": 35.9078, "longitude": 127.6615},

            {"region_id": 15, "tour_api_subcode": "6", "translations": {
                "ko": {"name": "부안군", "description": "변산반도와 채석강이 있는 해안군", "feature": "변산반도와 채석강"},
                "en": {"name": "Buan-gun", "description": "Coastal county with Byeonsan Peninsula and Chaeseokgang",
                       "feature": "Byeonsan Peninsula and Chaeseokgang Cliff"},
                "jp": {"name": "扶安郡", "description": "扁山半島と彩石江がある海岸郡", "feature": "扁山半島と彩石江"},
                "cn": {"name": "扶安郡", "description": "边山半岛和彩石江所在的海岸郡", "feature": "边山半岛和彩石江"}
            }, "favorite_count": 10, "latitude": 35.7318, "longitude": 126.7338},

            {"region_id": 15, "tour_api_subcode": "7", "translations": {
                "ko": {"name": "순창군", "description": "순창고추장과 강천산이 있는 전통군", "feature": "순창고추장과 강천산"},
                "en": {"name": "Sunchang-gun",
                       "description": "Traditional county with Sunchang gochujang and Gangcheonsan",
                       "feature": "Sunchang gochujang and Gangcheonsan Mountain"},
                "jp": {"name": "淳昌郡", "description": "淳昌コチュジャンと江川山がある伝統郡",
                       "feature": "淳昌コチュジャンと江川山"},
                "cn": {"name": "淳昌郡", "description": "淳昌韩式辣椒酱和江川山所在的传统郡",
                       "feature": "淳昌韩式辣椒酱和江川山"}
            }, "favorite_count": 7, "latitude": 35.3745, "longitude": 127.1373},

            {"region_id": 15, "tour_api_subcode": "8", "translations": {
                "ko": {"name": "완주군", "description": "전주와 인접한 위성도시", "feature": "완주삼례문화예술촌과 대둔산"},
                "en": {"name": "Wanju-gun", "description": "Satellite city adjacent to Jeonju",
                       "feature": "Wanju Samrye Culture Art Village and Daedunsan Mountain"},
                "jp": {"name": "完州郡", "description": "全州と隣接する衛星都市",
                       "feature": "完州三礼文化芸術村と大屯山"},
                "cn": {"name": "完州郡", "description": "与全州相邻的卫星城市", "feature": "完州三礼文化艺术村和大屯山"}
            }, "favorite_count": 6, "latitude": 35.9054, "longitude": 127.1669},

            {"region_id": 15, "tour_api_subcode": "9", "translations": {
                "ko": {"name": "익산시", "description": "백제왕궁리유적과 미륵사지가 있는 백제도시", "feature": "백제왕궁리유적과 미륵사지"},
                "en": {"name": "Iksan-si", "description": "Baekje city with Baekje Royal Palace site and Mireuksaji",
                       "feature": "Baekje Royal Palace site and Mireuksaji Temple Site"},
                "jp": {"name": "益山市", "description": "百済王宮里遺跡と弥勒寺址がある百済都市",
                       "feature": "百済王宮里遺跡と弥勒寺址"},
                "cn": {"name": "益山市", "description": "百济王宫里遗址和弥勒寺址所在的百济城市",
                       "feature": "百济王宫里遗址和弥勒寺址"}
            }, "favorite_count": 9, "latitude": 35.9483, "longitude": 126.9575},

            {"region_id": 15, "tour_api_subcode": "10", "translations": {
                "ko": {"name": "임실군", "description": "임실치즈와 국사봉이 있는 치즈의고장", "feature": "임실치즈와 국사봉"},
                "en": {"name": "Imsil-gun", "description": "Cheese hometown with Imsil cheese and Guksabong",
                       "feature": "Imsil cheese and Guksabong Peak"},
                "jp": {"name": "任実郡", "description": "任実チーズと国師峰があるチーズの故郷",
                       "feature": "任実チーズと国師峰"},
                "cn": {"name": "任实郡", "description": "任实奶酪和国师峰所在的奶酪故乡", "feature": "任实奶酪和国师峰"}
            }, "favorite_count": 6, "latitude": 35.6176, "longitude": 127.2886},

            {"region_id": 15, "tour_api_subcode": "11", "translations": {
                "ko": {"name": "장수군", "description": "장수한우와 논개생가가 있는 산간군", "feature": "장수한우와 논개생가"},
                "en": {"name": "Jangsu-gun",
                       "description": "Mountain county with Jangsu Hanwoo and Nongae's birthplace",
                       "feature": "Jangsu Hanwoo and Nongae's birthplace"},
                "jp": {"name": "長水郡", "description": "長水韓牛と論介生家がある山間郡",
                       "feature": "長水韓牛と論介生家"},
                "cn": {"name": "长水郡", "description": "长水韩牛和论介故居所在的山区郡",
                       "feature": "长水韩牛和论介故居"}
            }, "favorite_count": 5, "latitude": 35.6475, "longitude": 127.5194},

            {"region_id": 15, "tour_api_subcode": "12", "translations": {
                "ko": {"name": "전주시", "description": "한옥마을과 비빔밥의 고장", "feature": "전주한옥마을과 전통음식"},
                "en": {"name": "Jeonju-si", "description": "Hometown of Hanok Village and bibimbap",
                       "feature": "Jeonju Hanok Village and traditional food"},
                "jp": {"name": "全州市", "description": "韓屋村とビビンバの故郷", "feature": "全州韓屋村と伝統料理"},
                "cn": {"name": "全州市", "description": "韩屋村和拌饭的故乡", "feature": "全州韩屋村和传统料理"}
            }, "favorite_count": 22, "latitude": 35.8242, "longitude": 127.1480},

            {"region_id": 15, "tour_api_subcode": "13", "translations": {
                "ko": {"name": "정읍시", "description": "내장산과 정읍사가 있는 단풍도시", "feature": "내장산과 정읍사"},
                "en": {"name": "Jeongeup-si", "description": "Autumn foliage city with Naejangsan and Jeongeupsagok",
                       "feature": "Naejangsan Mountain and Jeongeupsagok"},
                "jp": {"name": "井邑市", "description": "内蔵山と井邑詞がある紅葉都市", "feature": "内蔵山と井邑詞"},
                "cn": {"name": "井邑市", "description": "内藏山和井邑歌所在的枫叶城市", "feature": "内藏山和井邑歌"}
            }, "favorite_count": 9, "latitude": 35.5697, "longitude": 126.8561},

            {"region_id": 15, "tour_api_subcode": "14", "translations": {
                "ko": {"name": "진안군", "description": "진안홍삼과 마이산이 있는 산간군", "feature": "진안홍삼과 마이산"},
                "en": {"name": "Jinan-gun", "description": "Mountain county with Jinan red ginseng and Maisan",
                       "feature": "Jinan red ginseng and Maisan Mountain"},
                "jp": {"name": "鎮安郡", "description": "鎮安紅参と馬耳山がある山間郡", "feature": "鎮安紅参と馬耳山"},
                "cn": {"name": "镇安郡", "description": "镇安红参和马耳山所在的山区郡", "feature": "镇安红参和马耳山"}
            }, "favorite_count": 7, "latitude": 35.7919, "longitude": 127.4249},

            # ===== 전라남도 (22개 시/군) =====
            {"region_id": 16, "tour_api_subcode": "1", "translations": {
                "ko": {"name": "강진군", "description": "다산초당과 고려청자가 있는 문화군", "feature": "다산초당과 고려청자"},
                "en": {"name": "Gangjin-gun", "description": "Cultural county with Dasan Chodang and Goryeo celadon",
                       "feature": "Dasan Chodang and Goryeo celadon"},
                "jp": {"name": "康津郡", "description": "茶山草堂と高麗青磁がある文化郡",
                       "feature": "茶山草堂と高麗青磁"},
                "cn": {"name": "康津郡", "description": "茶山草堂和高丽青瓷所在的文化郡",
                       "feature": "茶山草堂和高丽青瓷"}
            }, "favorite_count": 8, "latitude": 34.6420, "longitude": 126.7675},

            {"region_id": 16, "tour_api_subcode": "2", "translations": {
                "ko": {"name": "고흥군", "description": "나로우주센터와 소록도가 있는 우주군", "feature": "나로우주센터와 소록도"},
                "en": {"name": "Goheung-gun", "description": "Space county with Naro Space Center and Sorokdo",
                       "feature": "Naro Space Center and Sorokdo Island"},
                "jp": {"name": "高興郡", "description": "羅老宇宙センターと小鹿島がある宇宙郡",
                       "feature": "羅老宇宙センターと小鹿島"},
                "cn": {"name": "高兴郡", "description": "罗老宇宙中心和小鹿岛所在的宇宙郡",
                       "feature": "罗老宇宙中心和小鹿岛"}
            }, "favorite_count": 10, "latitude": 34.6112, "longitude": 127.2846},

            {"region_id": 16, "tour_api_subcode": "3", "translations": {
                "ko": {"name": "곡성군", "description": "섬진강기차마을과 심청이야기가 있는 기차군", "feature": "섬진강기차마을과 심청이야기"},
                "en": {"name": "Gokseong-gun",
                       "description": "Train county with Seomjingang Train Village and Simcheong story",
                       "feature": "Seomjingang Train Village and Simcheong story"},
                "jp": {"name": "谷城郡", "description": "蟾津江汽車村と沈清物語がある汽車郡",
                       "feature": "蟾津江汽車村と沈清物語"},
                "cn": {"name": "谷城郡", "description": "蟾津江火车村和沈清故事所在的火车郡",
                       "feature": "蟾津江火车村和沈清故事"}
            }, "favorite_count": 8, "latitude": 35.2820, "longitude": 127.2914},

            {"region_id": 16, "tour_api_subcode": "4", "translations": {
                "ko": {"name": "광양시", "description": "광양제철소와 매화축제가 있는 철강도시", "feature": "광양제철소와 매화축제"},
                "en": {"name": "Gwangyang-si",
                       "description": "Steel city with Gwangyang Steel Works and Plum Blossom Festival",
                       "feature": "Gwangyang Steel Works and Plum Blossom Festival"},
                "jp": {"name": "光陽市", "description": "光陽製鉄所と梅花祭がある鉄鋼都市",
                       "feature": "光陽製鉄所と梅花祭"},
                "cn": {"name": "光阳市", "description": "光阳钢铁厂和梅花节所在的钢铁城市",
                       "feature": "光阳钢铁厂和梅花节"}
            }, "favorite_count": 7, "latitude": 34.9404, "longitude": 127.5956},

            {"region_id": 16, "tour_api_subcode": "5", "translations": {
                "ko": {"name": "구례군", "description": "지리산과 산수유마을이 있는 산간군", "feature": "지리산과 산수유마을"},
                "en": {"name": "Gurye-gun", "description": "Mountain county with Jirisan and Sansuyu Village",
                       "feature": "Jirisan Mountain and Sansuyu Village"},
                "jp": {"name": "求礼郡", "description": "智異山と山茱萸村がある山間郡", "feature": "智異山と山茱萸村"},
                "cn": {"name": "求礼郡", "description": "智异山和山茱萸村所在的山区郡", "feature": "智异山和山茱萸村"}
            }, "favorite_count": 9, "latitude": 35.2022, "longitude": 127.4636},

            {"region_id": 16, "tour_api_subcode": "6", "translations": {
                "ko": {"name": "나주시", "description": "나주배와 금성관이 있는 전통도시", "feature": "나주배와 금성관"},
                "en": {"name": "Naju-si", "description": "Traditional city with Naju pears and Geumseongwan",
                       "feature": "Naju pears and Geumseongwan"},
                "jp": {"name": "羅州市", "description": "羅州梨と錦城館がある伝統都市", "feature": "羅州梨と錦城館"},
                "cn": {"name": "罗州市", "description": "罗州梨和锦城馆所在的传统城市", "feature": "罗州梨和锦城馆"}
            }, "favorite_count": 6, "latitude": 35.0160, "longitude": 126.7107},

            {"region_id": 16, "tour_api_subcode": "7", "translations": {
                "ko": {"name": "담양군", "description": "죽녹원과 메타세쿼이아길이 있는 대나무군", "feature": "죽녹원과 메타세쿼이아길"},
                "en": {"name": "Damyang-gun", "description": "Bamboo county with Juknokwon and Metasequoia Road",
                       "feature": "Juknokwon and Metasequoia Road"},
                "jp": {"name": "潭陽郡", "description": "竹緑苑とメタセコイア道がある竹郡",
                       "feature": "竹緑苑とメタセコイア道"},
                "cn": {"name": "潭阳郡", "description": "竹绿苑和水杉路所在的竹子郡", "feature": "竹绿苑和水杉路"}
            }, "favorite_count": 10, "latitude": 35.3214, "longitude": 126.9881},

            {"region_id": 16, "tour_api_subcode": "8", "translations": {
                "ko": {"name": "목포시", "description": "목포항과 유달산이 있는 항구도시", "feature": "목포항과 유달산"},
                "en": {"name": "Mokpo-si", "description": "Port city with Mokpo Port and Yudalsan",
                       "feature": "Mokpo Port and Yudalsan Mountain"},
                "jp": {"name": "木浦市", "description": "木浦港と儒達山がある港都市", "feature": "木浦港と儒達山"},
                "cn": {"name": "木浦市", "description": "木浦港和儒达山所在的港口城市", "feature": "木浦港和儒达山"}
            }, "favorite_count": 9, "latitude": 34.8118, "longitude": 126.3922},

            {"region_id": 16, "tour_api_subcode": "9", "translations": {
                "ko": {"name": "무안군", "description": "무안공항과 회산백련지가 있는 공항군", "feature": "무안공항과 회산백련지"},
                "en": {"name": "Muan-gun", "description": "Airport county with Muan Airport and Hoesan Baengnyeonji",
                       "feature": "Muan Airport and Hoesan Baengnyeonji Lotus Pond"},
                "jp": {"name": "務安郡", "description": "務安空港と回山白蓮池がある空港郡",
                       "feature": "務安空港と回山白蓮池"},
                "cn": {"name": "务安郡", "description": "务安机场和回山白莲池所在的机场郡",
                       "feature": "务安机场和回山白莲池"}
            }, "favorite_count": 7, "latitude": 34.9900, "longitude": 126.4828},

            {"region_id": 16, "tour_api_subcode": "10", "translations": {
                "ko": {"name": "보성군", "description": "보성녹차와 벌교꼬막이 있는 차의군", "feature": "보성녹차와 벌교꼬막"},
                "en": {"name": "Boseong-gun", "description": "Tea county with Boseong green tea and Beolgyo cockles",
                       "feature": "Boseong green tea and Beolgyo cockles"},
                "jp": {"name": "宝城郡", "description": "宝城緑茶と筏橋血蛤がある茶の郡",
                       "feature": "宝城緑茶と筏橋血蛤"},
                "cn": {"name": "宝城郡", "description": "宝城绿茶和筏桥血蛤所在的茶叶郡",
                       "feature": "宝城绿茶和筏桥血蛤"}
            }, "favorite_count": 11, "latitude": 34.7712, "longitude": 127.0801},

            {"region_id": 16, "tour_api_subcode": "11", "translations": {
                "ko": {"name": "순천시", "description": "순천만 국가정원이 있는 생태도시", "feature": "순천만 국가정원과 선암사"},
                "en": {"name": "Suncheon-si", "description": "Ecological city with Suncheon Bay National Garden",
                       "feature": "Suncheon Bay National Garden and Seonamsa Temple"},
                "jp": {"name": "順天市", "description": "順天湾国家庭園がある生態都市",
                       "feature": "順天湾国家庭園と仙岩寺"},
                "cn": {"name": "顺天市", "description": "顺天湾国家庭园所在的生态城市",
                       "feature": "顺天湾国家庭园和仙岩寺"}
            }, "favorite_count": 15, "latitude": 34.9506, "longitude": 127.4872},

            {"region_id": 16, "tour_api_subcode": "12", "translations": {
                "ko": {"name": "신안군", "description": "천사대교와 천일염전이 있는 섬군", "feature": "천사대교와 천일염전"},
                "en": {"name": "Sinan-gun", "description": "Island county with Angel Bridge and Cheonil Salt Fields",
                       "feature": "Angel Bridge and Cheonil Salt Fields"},
                "jp": {"name": "新安郡", "description": "天使大橋と天日塩田がある島郡",
                       "feature": "天使大橋と天日塩田"},
                "cn": {"name": "新安郡", "description": "天使大桥和天日盐田所在的岛屿郡",
                       "feature": "天使大桥和天日盐田"}
            }, "favorite_count": 9, "latitude": 34.8267, "longitude": 126.1063},

            {"region_id": 16, "tour_api_subcode": "13", "translations": {
                "ko": {"name": "여수시", "description": "2012 여수엑스포 개최지", "feature": "여수밤바다와 오동도"},
                "en": {"name": "Yeosu-si", "description": "Host city of 2012 Yeosu Expo",
                       "feature": "Yeosu night sea and Odongdo Island"},
                "jp": {"name": "麗水市", "description": "2012麗水エキスポ開催地", "feature": "麗水夜海とオドンド"},
                "cn": {"name": "丽水市", "description": "2012年丽水世博会举办地", "feature": "丽水夜海和梧桐岛"}
            }, "favorite_count": 20, "latitude": 34.7604, "longitude": 127.6622},

            {"region_id": 16, "tour_api_subcode": "16", "translations": {
                "ko": {"name": "영광군", "description": "영광원전과 백수해안도로가 있는 해안군", "feature": "영광원전과 백수해안도로"},
                "en": {"name": "Yeonggwang-gun",
                       "description": "Coastal county with Yeonggwang Nuclear Power Plant and Baeksu Coastal Road",
                       "feature": "Yeonggwang Nuclear Power Plant and Baeksu Coastal Road"},
                "jp": {"name": "霊光郡", "description": "霊光原発と白水海岸道路がある海岸郡",
                       "feature": "霊光原発と白水海岸道路"},
                "cn": {"name": "灵光郡", "description": "灵光核电站和白水海岸公路所在的海岸郡",
                       "feature": "灵光核电站和白水海岸公路"}
            }, "favorite_count": 6, "latitude": 35.2772, "longitude": 126.5116},

            {"region_id": 16, "tour_api_subcode": "17", "translations": {
                "ko": {"name": "영암군", "description": "월출산과 왕인박사유적지가 있는 역사군", "feature": "월출산과 왕인박사유적지"},
                "en": {"name": "Yeongam-gun",
                       "description": "Historic county with Wolchulsan and Dr. Wangin Historic Site",
                       "feature": "Wolchulsan Mountain and Dr. Wangin Historic Site"},
                "jp": {"name": "霊岩郡", "description": "月出山と王仁博士遺跡地がある歴史郡",
                       "feature": "月出山と王仁博士遺跡地"},
                "cn": {"name": "灵岩郡", "description": "月出山和王仁博士遗址所在的历史郡",
                       "feature": "月出山和王仁博士遗址"}
            }, "favorite_count": 7, "latitude": 34.8005, "longitude": 126.6968},

            {"region_id": 16, "tour_api_subcode": "18", "translations": {
                "ko": {"name": "완도군", "description": "완도수목원과 청산도가 있는 섬군", "feature": "완도수목원과 청산도"},
                "en": {"name": "Wando-gun", "description": "Island county with Wando Arboretum and Cheongsando",
                       "feature": "Wando Arboretum and Cheongsando Island"},
                "jp": {"name": "莞島郡", "description": "莞島樹木園と青山島がある島郡",
                       "feature": "莞島樹木園と青山島"},
                "cn": {"name": "莞岛郡", "description": "莞岛树木园和青山岛所在的岛屿郡",
                       "feature": "莞岛树木园和青山岛"}
            }, "favorite_count": 10, "latitude": 34.3117, "longitude": 126.7555},

            {"region_id": 16, "tour_api_subcode": "19", "translations": {
                "ko": {"name": "장성군", "description": "백양사와 홍길동테마파크가 있는 문화군", "feature": "백양사와 홍길동테마파크"},
                "en": {"name": "Jangseong-gun",
                       "description": "Cultural county with Baegyangsa Temple and Hong Gildong Theme Park",
                       "feature": "Baegyangsa Temple and Hong Gildong Theme Park"},
                "jp": {"name": "長城郡", "description": "白羊寺と洪吉童テーマパークがある文化郡",
                       "feature": "白羊寺と洪吉童テーマパーク"},
                "cn": {"name": "长城郡", "description": "白羊寺和洪吉童主题公园所在的文化郡",
                       "feature": "白羊寺和洪吉童主题公园"}
            }, "favorite_count": 7, "latitude": 35.3018, "longitude": 126.7855},

            {"region_id": 16, "tour_api_subcode": "20", "translations": {
                "ko": {"name": "장흥군", "description": "정남진과 천관산이 있는 남쪽군", "feature": "정남진과 천관산"},
                "en": {"name": "Jangheung-gun", "description": "Southern county with Jeongnamjin and Cheongwansan",
                       "feature": "Jeongnamjin and Cheongwansan Mountain"},
                "jp": {"name": "長興郡", "description": "正南津と天冠山がある南側郡", "feature": "正南津と天冠山"},
                "cn": {"name": "长兴郡", "description": "正南津和天冠山所在的南方郡", "feature": "正南津和天冠山"}
            }, "favorite_count": 6, "latitude": 34.6888, "longitude": 126.9067},

            {"region_id": 16, "tour_api_subcode": "21", "translations": {
                "ko": {"name": "진도군", "description": "진도개와 진도아리랑이 있는 전통섬", "feature": "진도개와 진도아리랑"},
                "en": {"name": "Jindo-gun", "description": "Traditional island with Jindo dogs and Jindo Arirang",
                       "feature": "Jindo dogs and Jindo Arirang"},
                "jp": {"name": "珍島郡", "description": "珍島犬と珍島アリランがある伝統島",
                       "feature": "珍島犬と珍島アリラン"},
                "cn": {"name": "珍岛郡", "description": "珍岛犬和珍岛阿里郎所在的传统岛屿",
                       "feature": "珍岛犬和珍岛阿里郎"}
            }, "favorite_count": 8, "latitude": 34.4867, "longitude": 126.2633},

            {"region_id": 16, "tour_api_subcode": "22", "translations": {
                "ko": {"name": "함평군", "description": "함평나비축제와 자연생태공원이 있는 나비군", "feature": "함평나비축제와 자연생태공원"},
                "en": {"name": "Hampyeong-gun",
                       "description": "Butterfly county with Hampyeong Butterfly Festival and Natural Ecology Park",
                       "feature": "Hampyeong Butterfly Festival and Natural Ecology Park"},
                "jp": {"name": "咸平郡", "description": "咸平蝶祭りと自然生態公園がある蝶郡",
                       "feature": "咸平蝶祭りと自然生態公園"},
                "cn": {"name": "咸平郡", "description": "咸平蝴蝶节和自然生态公园所在的蝴蝶郡",
                       "feature": "咸平蝴蝶节和自然生态公园"}
            }, "favorite_count": 7, "latitude": 35.0658, "longitude": 126.5165},

            {"region_id": 16, "tour_api_subcode": "23", "translations": {
                "ko": {"name": "해남군", "description": "땅끝마을과 대흥사가 있는 최남단", "feature": "땅끝마을과 대흥사"},
                "en": {"name": "Haenam-gun",
                       "description": "Southernmost county with Land's End Village and Daeheungsa Temple",
                       "feature": "Land's End Village and Daeheungsa Temple"},
                "jp": {"name": "海南郡", "description": "土地の果て村と大興寺がある最南端",
                       "feature": "土地の果て村と大興寺"},
                "cn": {"name": "海南郡", "description": "陆地尽头村和大兴寺所在的最南端",
                       "feature": "陆地尽头村和大兴寺"}
            }, "favorite_count": 8, "latitude": 34.5733, "longitude": 126.5990},

            {"region_id": 16, "tour_api_subcode": "24", "translations": {
                "ko": {"name": "화순군", "description": "화순고인돌과 적벽이 있는 고인돌군", "feature": "화순고인돌과 적벽"},
                "en": {"name": "Hwasun-gun", "description": "Dolmen county with Hwasun Dolmens and Red Cliffs",
                       "feature": "Hwasun Dolmens and Red Cliffs"},
                "jp": {"name": "和順郡", "description": "和順支石墓と赤壁がある支石墓郡",
                       "feature": "和順支石墓と赤壁"},
                "cn": {"name": "和顺郡", "description": "和顺支石墓和赤壁所在的支石墓郡", "feature": "和顺支石墓和赤壁"}
            }, "favorite_count": 6, "latitude": 35.0641, "longitude": 126.9895},

            # ======= 제주특별자치도 (2개 시) =======
            {
                "region_id": 17,
                "tour_api_subcode": "1",
                "translations": {
                    "ko": {"name": "제주시", "description": "제주도의 중심도시", "feature": "한라산과 성산일출봉"},
                    "en": {"name": "Jeju-si", "description": "Main city of Jeju Island", "feature": "Hallasan and Seongsan Ilchulbong"},
                    "jp": {"name": "済州市", "description": "済州島の中心都市", "feature": "漢拏山と城山日出峰"},
                    "cn": {"name": "济州市", "description": "济州岛中心城市", "feature": "汉拿山和城山日出峰"}
                },
                "favorite_count": 20, "latitude": 33.4996, "longitude": 126.5312
            },
            {
                "region_id": 17,
                "tour_api_subcode": "2",
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
                location=Point(
                    subregion_data["longitude"],
                    subregion_data["latitude"]
                )
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
