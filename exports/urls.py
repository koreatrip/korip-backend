from django.urls import path
from exports import views

app_name = "exports"

urlpatterns = [
    # PDF 내보내기 관련 URL
    path("plans/<int:plan_id>/pdf/data/", views.plan_pdf_data, name="plan_pdf_data"),
    # 구글 캘린더 관련 URL
    path("auth/google/", views.google_calendar_auth, name="google_calendar_auth"),
    path("auth/google/callback/", views.google_calendar_callback, name="google_calendar_callback"),
    path("plans/<int:plan_id>/calendar/", views.google_calendar_sync, name="google_calendar_sync"),
]