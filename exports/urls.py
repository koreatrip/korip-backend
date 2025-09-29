from django.urls import path
from exports import views

app_name = "exports"

urlpatterns = [
    # PDF 내보내기 관련 URL
    path("plans/<int:plan_id>/pdf/data/", views.PlanPdfDataView.as_view(), name="plan_pdf_data"),
    # 구글 캘린더 관련 URL
    path("auth/google/", views.GoogleCalendarAuthView.as_view(), name="google_calendar_auth"),
    path("auth/google/callback/", views.GoogleCalendarCallbackView.as_view(), name="google_calendar_callback"),
    path("plans/<int:plan_id>/calendar/sync/", views.GoogleCalendarSyncView.as_view(), name="google_calendar_sync"),
]