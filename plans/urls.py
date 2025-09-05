from django.urls import path
from plans import views

app_name = "plans"

urlpatterns = [
    path("", views.plan_list_create, name="plan_list_create"),
    path("<int:plan_id>/pdf/data/", views.plan_pdf_data, name="plan_pdf_data"),  # 새로 추가
    path("<int:plan_id>/", views.plan_detail, name="plan_detail"),
]
