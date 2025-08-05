from django.urls import path
from places.views import PlacesListAPI, PlaceDetailAPI, PlacesBySubRegionAPI, UserFavoritePlacesAPI

urlpatterns = [
    path("", PlacesListAPI.as_view(), name="places_list"),
    path("<int:place_id>/", PlaceDetailAPI.as_view(), name="place_detail"),
    path("regions/<int:subregion_id>/", PlacesBySubRegionAPI.as_view(), name="places_by_subregion"),
    path("users/<int:user_id>/", UserFavoritePlacesAPI.as_view(), name="user_favorite_places"),
]
