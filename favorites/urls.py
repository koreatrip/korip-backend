from django.urls import path
from favorites.views import (
    FavoritePlaceAPIView,
    FavoriteSubRegionAPIView
)

urlpatterns = [
    path("places", FavoritePlaceAPIView.as_view(), name="favorite-places"),
    path("regions", FavoriteSubRegionAPIView.as_view(), name="favorite-subregions"),
]
