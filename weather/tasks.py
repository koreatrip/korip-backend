from celery import shared_task
from weather.management.commands.sync_weather import Command

@shared_task
def sync_weather_task(region_id=None):  # 기본값을 None으로
    command = Command()
    if region_id:
        command.handle(region_id=region_id)
        return f"Weather sync completed for region {region_id}"
    else:
        command.handle()  # region_id 없으면 전체 지역
        return "Weather sync completed for all regions"