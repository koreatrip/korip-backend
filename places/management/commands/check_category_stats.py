# 카테고리별 관광지 통계를 확인하는 명령어

from django.core.management.base import BaseCommand
from django.utils import timezone
from places.models import Place
from categories.models import Category


class Command(BaseCommand):
    help = "카테고리별 관광지 통계를 확인합니다"

    def add_arguments(self, parser):
        parser.add_argument(
            "--show-recent",
            type=int,
            default=5,
            help="각 카테고리별로 보여줄 최근 관광지 개수 (기본: 5개)"
        )

        parser.add_argument(
            "--category",
            type=str,
            help="특정 카테고리만 확인 (예: 자연, 문화, 음식)"
        )

    def handle(self, *args, **options):
        show_recent = options["show_recent"]
        target_category = options.get("category")

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("KORIP 관광지 카테고리 통계"))
        self.stdout.write("=" * 60)

        total_places = Place.objects.count()
        self.stdout.write(f" 전체 관광지: {total_places:,}개")

        categories = Category.objects.all().order_by("id")

        total_categorized = 0

        for category in categories:
            korean_translation = category.translations.filter(lang="ko").first()
            if not korean_translation:
                continue

            category_name = korean_translation.name

            # 특정 카테고리만 보기 옵션
            if target_category and category_name != target_category:
                continue

            # 해당 카테고리 관광지 개수
            tour_categories = self.get_tour_categories_for_our_category(category.id)
            places_in_category = Place.objects.filter(category_id__in=tour_categories)
            count = places_in_category.count()
            total_categorized += count

            if count == 0:
                continue

            # 카테고리 정보 출력
            percentage = (count / total_places * 100) if total_places > 0 else 0

            self.stdout.write(f"\n️ {category_name} (ID: {category.id})")
            self.stdout.write(f"    관광지 수: {count:,}개 ({percentage:.1f}%)")

            # 최근 업데이트된 관광지들 보여주기
            if show_recent > 0:
                recent_places = places_in_category.order_by('-updated_at')[:show_recent]

                if recent_places.exists():
                    self.stdout.write(f"    최근 업데이트된 {show_recent}개:")

                    for i, place in enumerate(recent_places, 1):
                        # 한국어 이름 가져오기
                        korean_name = "이름 없음"
                        korean_translation = place.translations.filter(lang="ko").first()
                        if korean_translation:
                            korean_name = korean_translation.name

                        # 업데이트 시간
                        update_time = place.updated_at.strftime("%m/%d %H:%M")

                        self.stdout.write(f"      {i}. {korean_name} (ID: {place.content_id}) - {update_time}")

        uncategorized = Place.objects.filter(category_id__isnull=True).count()
        if uncategorized > 0:
            uncategorized_percentage = (uncategorized / total_places * 100) if total_places > 0 else 0
            self.stdout.write(f"\n 미분류 관광지: {uncategorized:,}개 ({uncategorized_percentage:.1f}%)")

        categorized_percentage = (total_categorized / total_places * 100) if total_places > 0 else 0

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f" 요약:")
        self.stdout.write(f"   • 전체 관광지: {total_places:,}개")
        self.stdout.write(f"   • 분류된 관광지: {total_categorized:,}개 ({categorized_percentage:.1f}%)")
        self.stdout.write(f"   • 미분류 관광지: {uncategorized:,}개")

        if not target_category:
            nature_category = categories.filter(translations__name="자연", translations__lang="ko").first()
            if nature_category:
                nature_count = Place.objects.filter(category_id=nature_category.id).count()
                self.stdout.write(f"\n 자연 카테고리 특별 현황:")
                self.stdout.write(f"   • 자연 관광지: {nature_count:,}개")

                if nature_count > 0:
                    # 최근 1시간 내 업데이트된 자연 관광지
                    one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
                    recent_nature = Place.objects.filter(
                        category_id=nature_category.id,
                        updated_at__gte=one_hour_ago
                    ).count()

                    if recent_nature > 0:
                        self.stdout.write(f"   • 최근 1시간 내 업데이트: {recent_nature}개")

        self.stdout.write("=" * 60)

        # 성공 메시지
        if target_category:
            self.stdout.write(self.style.SUCCESS(f" '{target_category}' 카테고리 통계 조회 완료!"))
        else:
            self.stdout.write(self.style.SUCCESS(" 전체 카테고리 통계 조회 완료!"))


def get_tour_categories_for_our_category(self, our_category_id):

    try:
        from places.services.category_mapper import CategoryMapper
        mapper = CategoryMapper()

        from categories.models import Category
        our_category = Category.objects.filter(id=our_category_id).first()
        if not our_category:
            return []

        korean_translation = our_category.translations.filter(lang="ko").first()
        if not korean_translation:
            return []

        our_category_name = korean_translation.name

        tour_categories = []
        for tour_cat, mapped_name in mapper.category_mapping.items():
            if mapped_name == our_category_name:
                tour_categories.append(tour_cat)

        return tour_categories

    except Exception as e:
        print(f"CategoryMapper 조회 실패: {e}")
        return []