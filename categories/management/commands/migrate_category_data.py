from django.core.management.base import BaseCommand
from categories.models import Category, CategoryTranslation, SubCategory, SubCategoryTranslation


class Command(BaseCommand):
    """기존 카테고리 데이터를 새로운 번역 구조로 이전하는 Django Management Command"""

    help = "기존 카테고리 데이터를 CategoryTranslation으로 이전"

    def handle(self, *args, **options):
        self.stdout.write("=== 카테고리 데이터 이전 시작 ===")

        # 1. 현재 상황 확인
        category_count = Category.objects.count()
        translation_count = CategoryTranslation.objects.count()

        self.stdout.write(f"기존 카테고리 개수: {category_count}")
        self.stdout.write(f"현재 번역 개수: {translation_count}")

        if category_count == 0:
            self.stdout.write(
                self.style.WARNING("카테고리가 없습니다. 먼저 카테고리를 생성해주세요.")
            )
            return

        # 2. 기존 카테고리 데이터 출력
        self.stdout.write("\n=== 기존 카테고리 데이터 ===")
        for category in Category.objects.all():
            self.stdout.write(f"ID: {category.id}")
            self.stdout.write(f"  한국어: {category.name_ko}")
            self.stdout.write(f"  영어: {category.name_en}")
            self.stdout.write(f"  일본어: {category.name_jp}")
            self.stdout.write(f"  중국어: {category.name_cn}")
            self.stdout.write("---")

        # 3. 카테고리 데이터 이전
        self.migrate_categories()

        # 4. 서브카테고리 데이터 이전
        self.migrate_subcategories()

        # 5. 최종 결과
        final_translation_count = CategoryTranslation.objects.count()
        final_sub_translation_count = SubCategoryTranslation.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 데이터 이전 완료!\n"
                f"카테고리 번역: {final_translation_count}개\n"
                f"서브카테고리 번역: {final_sub_translation_count}개"
            )
        )

    def migrate_categories(self):
        """카테고리 데이터 이전"""
        self.stdout.write("\n=== 카테고리 데이터 이전 실행 ===")

        for category in Category.objects.all():
            self.stdout.write(f"카테고리 {category.id} 이전 중...")

            # 언어별 데이터 매핑
            languages = [
                ("ko", category.name_ko),
                ("en", category.name_en),
                ("jp", category.name_jp),
                ("cn", category.name_cn)
            ]

            for lang, name in languages:
                if name:  # 이름이 있는 경우만 번역 생성
                    translation, created = CategoryTranslation.objects.get_or_create(
                        category=category,
                        lang=lang,
                        defaults={"name": name}
                    )

                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"  {lang} 번역 생성: {name}")
                        )
                    else:
                        self.stdout.write(f"  {lang} 번역 이미 존재: {name}")

    def migrate_subcategories(self):
        """서브카테고리 데이터 이전"""
        subcategory_count = SubCategory.objects.count()

        if subcategory_count == 0:
            self.stdout.write(
                self.style.WARNING("서브카테고리가 없습니다.")
            )
            return

        self.stdout.write("\n=== 서브카테고리 데이터 이전 실행 ===")
        self.stdout.write(f"기존 서브카테고리 개수: {subcategory_count}")

        for subcategory in SubCategory.objects.all():
            self.stdout.write(f"서브카테고리 {subcategory.id} 이전 중...")

            # 언어별 데이터 매핑
            languages = [
                ("ko", subcategory.name_ko),
                ("en", subcategory.name_en),
                ("jp", subcategory.name_jp),
                ("cn", subcategory.name_cn)
            ]

            for lang, name in languages:
                if name:  # 이름이 있는 경우만 번역 생성
                    translation, created = SubCategoryTranslation.objects.get_or_create(
                        sub_category=subcategory,
                        lang=lang,
                        defaults={"name": name}
                    )

                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"  {lang} 번역 생성: {name}")
                        )
                    else:
                        self.stdout.write(f"  {lang} 번역 이미 존재: {name}")
