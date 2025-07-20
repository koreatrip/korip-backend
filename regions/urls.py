from django.urls import path
from regions.views import (
    RegionsAPI,
    RegionDetailAPI,
    RegionSubRegionsAPI,
    SubRegionDetailAPI,
    AllSubRegionsAPI,
    DefaultRegionAPI
)

app_name = "regions"

urlpatterns = [
    path("default/", DefaultRegionAPI.as_view(), name="default_region"),
    path("", RegionsAPI.as_view(), name="regions_list"),
    path("<int:region_id>/", RegionDetailAPI.as_view(), name="region_detail"),
    path("<int:region_id>/subregions/", RegionSubRegionsAPI.as_view(), name="region_subregions"),
    path("subregions/<int:subregion_id>/", SubRegionDetailAPI.as_view(), name="subregion_detail"),
    path("subregions/", AllSubRegionsAPI.as_view(), name="all_subregions"),
]
