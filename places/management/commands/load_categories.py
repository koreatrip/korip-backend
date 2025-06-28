# 다국어 카테고리 및 서브카테고리 기본 데이터를 DB에 삽입하는 management command
# 번역된 카테고리 데이터를 일괄 생성

from django.core.management.base import BaseCommand
from places.models import Category, SubCategory


class Command(BaseCommand):
    help = '다국어 카테고리 및 서브카테고리 기본 데이터를 생성합니다'

    def handle(self, *args, **options):
        # 기존 데이터 삭제 (재실행 시)
        SubCategory.objects.all().delete()
        Category.objects.all().delete()

        # 대분류 카테고리 데이터
        categories_data = {
            '문화': {'ko': '문화', 'en': 'Culture', 'jp': '文化', 'cn': '文化'},
            '자연': {'ko': '자연', 'en': 'Nature', 'jp': '自然', 'cn': '自然'},
            '액티비티': {'ko': '액티비티', 'en': 'Activities', 'jp': 'アクティビティ', 'cn': '活动'},
            '쇼핑': {'ko': '쇼핑', 'en': 'Shopping', 'jp': 'ショッピング', 'cn': '购物'},
            '음식': {'ko': '음식', 'en': 'Food', 'jp': '食べ物', 'cn': '美食'},
            'kpop': {'ko': 'K-POP', 'en': 'K-POP', 'jp': 'K-POP', 'cn': 'K-POP'}
        }

        # 중분류 서브카테고리 데이터
        subcategories_data = {
            '문화': [
                {'ko': '역사', 'en': 'History', 'jp': '歴史', 'cn': '历史'},
                {'ko': '박물관', 'en': 'Museum', 'jp': '博物館', 'cn': '博物馆'},
                {'ko': '미술관', 'en': 'Art Gallery', 'jp': '美術館', 'cn': '美术馆'},
                {'ko': '전통문화', 'en': 'Traditional Culture', 'jp': '伝統文化', 'cn': '传统文化'},
                {'ko': '종교', 'en': 'Religion', 'jp': '宗教', 'cn': '宗教'},
                {'ko': '궁궐', 'en': 'Palace', 'jp': '宮殿', 'cn': '宫殿'},
            ],
            '자연': [
                {'ko': '산', 'en': 'Mountain', 'jp': '山', 'cn': '山'},
                {'ko': '바다', 'en': 'Beach', 'jp': '海', 'cn': '海'},
                {'ko': '강', 'en': 'River', 'jp': '川', 'cn': '河'},
                {'ko': '호수', 'en': 'Lake', 'jp': '湖', 'cn': '湖'},
                {'ko': '계곡', 'en': 'Valley', 'jp': '渓谷', 'cn': '峡谷'},
                {'ko': '공원', 'en': 'Park', 'jp': '公園', 'cn': '公园'},
                {'ko': '숲', 'en': 'Forest', 'jp': '森', 'cn': '森林'},
            ],
            '액티비티': [
                {'ko': '등산', 'en': 'Hiking', 'jp': '登山', 'cn': '登山'},
                {'ko': '테마파크', 'en': 'Theme Park', 'jp': 'テーマパーク', 'cn': '主题公园'},
                {'ko': '놀이공원', 'en': 'Amusement Park', 'jp': '遊園地', 'cn': '游乐园'},
                {'ko': '동물원', 'en': 'Zoo', 'jp': '動物園', 'cn': '动物园'},
                {'ko': '수족관', 'en': 'Aquarium', 'jp': '水族館', 'cn': '水族馆'},
            ],
            '쇼핑': [
                {'ko': '전통시장', 'en': 'Local Market', 'jp': '伝統市場', 'cn': '传统市场'},
                {'ko': '백화점', 'en': 'Department Store', 'jp': 'デパート', 'cn': '百货商店'},
                {'ko': '아울렛', 'en': 'Outlet Mall', 'jp': 'アウトレット', 'cn': '奥特莱斯'},
                {'ko': '면세점', 'en': 'Duty Free', 'jp': '免税店', 'cn': '免税店'},
                {'ko': '기념품', 'en': 'Souvenir', 'jp': 'お土産', 'cn': '纪念品'},
                {'ko': '패션', 'en': 'Fashion', 'jp': 'ファッション', 'cn': '时尚'},
                {'ko': '화장품', 'en': 'Cosmetics', 'jp': '化粧品', 'cn': '化妆品'},
            ],
            '음식': [
                {'ko': '한식', 'en': 'Korean Food', 'jp': '韓国料理', 'cn': '韩式料理'},
                {'ko': '일식', 'en': 'Japanese Food', 'jp': '日本料理', 'cn': '日式料理'},
                {'ko': '중식', 'en': 'Chinese Food', 'jp': '中華料理', 'cn': '中式料理'},
                {'ko': '양식', 'en': 'Western Food', 'jp': '洋食', 'cn': '西式料理'},
            ],
            'kpop': [
                {'ko': 'BTS', 'en': 'BTS', 'jp': 'BTS', 'cn': 'BTS'},
                {'ko': 'BLACKPINK', 'en': 'BLACKPINK', 'jp': 'BLACKPINK', 'cn': 'BLACKPINK'},
                {'ko': 'SEVENTEEN', 'en': 'SEVENTEEN', 'jp': 'SEVENTEEN', 'cn': 'SEVENTEEN'},
                {'ko': 'AESPA', 'en': 'AESPA', 'jp': 'AESPA', 'cn': 'AESPA'},
                {'ko': 'NEWJEANS', 'en': 'NEWJEANS', 'jp': 'NEWJEANS', 'cn': 'NEWJEANS'},
            ]
        }

        # 카테고리 생성
        created_categories = {}
        for category_key, translations in categories_data.items():
            category = Category.objects.create(
                name_ko=translations['ko'],
                name_en=translations['en'],
                name_jp=translations['jp'],
                name_cn=translations['cn']
            )
            created_categories[category_key] = category
            self.stdout.write(
                self.style.SUCCESS(f'카테고리 생성: {translations["ko"]} ({category.id})')
            )

        # 서브카테고리 생성
        for category_key, subcategory_list in subcategories_data.items():
            category = created_categories[category_key]
            for subcategory_data in subcategory_list:
                SubCategory.objects.create(
                    name_ko=subcategory_data['ko'],
                    name_en=subcategory_data['en'],
                    name_jp=subcategory_data['jp'],
                    name_cn=subcategory_data['cn'],
                    category=category
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  서브카테고리 생성: {subcategory_data["ko"]}')
                )

        self.stdout.write(
            self.style.SUCCESS('모든 다국어 카테고리 데이터 생성 완료!')
        )