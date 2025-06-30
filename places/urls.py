from django.urls import path
from places.views import (
    PlaceKRListAPIView, PlaceKRDetailAPIView,
    PlaceENListAPIView, PlaceENDetailAPIView,
    PlaceJPListAPIView, PlaceJPDetailAPIView,
    PlaceCNListAPIView, PlaceCNDetailAPIView
)

urlpatterns = [
    path("kr/", PlaceKRListAPIView.as_view(), name="place-kr-list"),
    path("kr/<int:pk>/", PlaceKRDetailAPIView.as_view(), name="place-kr-detail"),

    path("en/", PlaceENListAPIView.as_view(), name="place-en-list"),
    path("en/<int:pk>/", PlaceENDetailAPIView.as_view(), name="place-en-detail"),

    path("jp/", PlaceJPListAPIView.as_view(), name="place-jp-list"),
    path("jp/<int:pk>/", PlaceJPDetailAPIView.as_view(), name="place-jp-detail"),

    path("cn/", PlaceCNListAPIView.as_view(), name="place-cn-list"),
    path("cn/<int:pk>/", PlaceCNDetailAPIView.as_view(), name="place-cn-detail"),
]