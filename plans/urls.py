from django.urls import path
from plans import views

app_name = "plans"

urlpatterns = [
    path("", views.plan_list_create, name="plan_list_create"),
    path("<int:plan_id>/", views.plan_detail, name="plan_detail"),
]
