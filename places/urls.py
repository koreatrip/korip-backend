from django.urls import path
from places.views import (
    PlacesListAPIView, PlaceDetailAPIView, PlacesBySubRegionAPIView,
    PlaceTourListAPIView, PlacesByCategoryIdAPIView
)

urlpatterns = [
    path("test/", PlacesListAPIView.as_view(), name="places_list"),
    path("<int:place_id>/", PlaceDetailAPIView.as_view(), name="place_detail"),
    path("regions/<int:subregion_id>/", PlacesBySubRegionAPIView.as_view(), name="places_by_subregion"),
    path('category/<int:category_id>/', PlacesByCategoryIdAPIView.as_view(), name='places-by-category'),
    path("", PlaceTourListAPIView.as_view(), name="places_tour_list"),
]
