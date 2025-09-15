from django.urls import path
from plans import views

app_name = "plans"

urlpatterns = [
    path("", views.PlanListCreateAPIView.as_view(), name="plan_list_create"),
    path("<int:plan_id>/", views.PlanDetailAPIView.as_view(), name="plan_detail"),
    path("<int:plan_id>/places/<int:place_id>/", views.RemovePlaceFromPlanAPIView.as_view(), name="remove_place_from_plan"),
]
