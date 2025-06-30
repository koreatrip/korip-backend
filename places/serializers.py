from rest_framework import serializers
from places.models import PlaceKR, PlaceEN, PlaceJP, PlaceCN


class PlaceKRSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceKR
        fields = "__all__"


class PlaceENSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceEN
        fields = "__all__"


class PlaceJPSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceJP
        fields = "__all__"


class PlaceCNSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceCN
        fields = "__all__"