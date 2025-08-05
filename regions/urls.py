from django.urls import path
from regions.views import RegionsListAPI, RegionDetailAPI

urlpatterns = [
    path("", RegionsListAPI.as_view(), name="regions_list"), # 전체 지역 목록
    path("<int:region_id>/", RegionDetailAPI.as_view(), name="region_detail"), # 지역 상세
]
