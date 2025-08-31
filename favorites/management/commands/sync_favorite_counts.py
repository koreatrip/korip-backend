from django.core.management.base import BaseCommand
from django.db.models import Count, F
from django.db import transaction
from places.models import Place
from favorites.models import FavoritePlace


class Command(BaseCommand):
    help = 'Place 모델의 favorite_count를 실제 즐겨찾기 수와 동기화합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제로 업데이트하지 않고 결과만 확인',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='배치 크기 (기본: 100)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        self.stdout.write('즐겨찾기 카운트 동기화를 시작합니다...')
        
        # 동기화가 필요한 장소들 찾기
        places_to_sync = Place.objects.annotate(
            actual_count=Count('favorited_by')
        ).exclude(favorite_count=F('actual_count'))
        
        total_count = places_to_sync.count()
        
        if total_count == 0:
            self.stdout.write(
                self.style.SUCCESS('모든 장소의 favorite_count가 이미 동기화되어 있습니다.')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] {total_count}개 장소가 동기화가 필요합니다.')
            )
            
            # 샘플 출력
            for place in places_to_sync[:10]:
                self.stdout.write(
                    f'  - {place.get_name("ko")} (ID: {place.id}): '
                    f'{place.favorite_count} -> {place.actual_count}'
                )
            
            if total_count > 10:
                self.stdout.write(f'  ... 외 {total_count - 10}개 더')
            return
        
        # 실제 업데이트
        updated_count = 0
        
        try:
            with transaction.atomic():
                for place in places_to_sync:
                    old_count = place.favorite_count
                    place.favorite_count = place.actual_count
                    place.save(update_fields=['favorite_count'])
                    
                    updated_count += 1
                    
                    if updated_count % batch_size == 0:
                        self.stdout.write(f'진행상황: {updated_count}/{total_count}')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ 총 {updated_count}개 장소의 favorite_count가 동기화되었습니다.'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 동기화 중 오류 발생: {str(e)}')
            )
            raise