from django.urls import path
from favorites.views import (
    FavoritePlaceAPIView,
)

urlpatterns = [
    path("places", FavoritePlaceAPIView.as_view(), name="favorite-places"),
]
