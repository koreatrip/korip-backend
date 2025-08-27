from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@shared_task
def sync_tour_api_daily():
    """매일 전국 투어 API 증분 수집"""
    try:
        logger.info("투어 API 전국 일일 수집 시작")
        call_command('sync_tour_api',
                     incremental_all=True,    # 전국 증분 모드
                     daily_limit=2000,        # 하루 2000개 제한
                     detail_delay=0.8)
        logger.info("투어 API 전국 일일 수집 완료")
    except Exception as e:
        logger.error(f"투어 API 전국 일일 수집 실패: {e}")

@shared_task
def sync_tour_api_weekly():
    """주간 전국 대량 수집 (상세정보 포함)"""
    try:
        logger.info("투어 API 전국 주간 수집 시작")
        call_command('sync_tour_api',
                     incremental_all=True,    # 전국 증분 모드
                     daily_limit=10000,       # 주간 10000개
                     collect_all=True,        # 상세정보까지
                     detail_delay=0.5)
        logger.info("투어 API 전국 주간 수집 완료")
    except Exception as e:
        logger.error(f"투어 API 전국 주간 수집 실패: {e}")
