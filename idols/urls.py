from django.urls import path
from idols.views import IdolRequestCreateAPIView

app_name = "idols"

urlpatterns = [
    path("requests/", IdolRequestCreateAPIView.as_view(), name="idol_request_create"),
]
