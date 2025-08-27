import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# 2시간마다 날씨 데이터 수집
app.conf.beat_schedule = {
    "sync-weather-every-2hours": {
        "task": "weather.tasks.sync_weather_task",
        "schedule": crontab(minute=0, hour="*/2"),  # 0시, 2시, 4시, 6시...
    },
}

app.conf.timezone = "Asia/Seoul"
