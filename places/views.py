from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from places.models import PlaceKR, PlaceEN, PlaceJP, PlaceCN
from places.serializers import PlaceKRSerializer, PlaceENSerializer, PlaceJPSerializer, PlaceCNSerializer


# 한국어 관광지 목록 조회/생성 API
class PlaceKRListAPIView(APIView):

    def get(self, request):
        places = PlaceKR.objects.all()

        # 카테고리 필터링
        category_name = request.GET.get("category")
        if category_name:
            places = places.filter(category__name_ko=category_name)

        # 지역 필터링
        region_code = request.GET.get("region")
        if region_code:
            places = places.filter(region_code=region_code)

        # 이름 검색
        search = request.GET.get("search")
        if search:
            places = places.filter(name__icontains=search)

        # 아이돌 성지 필터링
        is_idol_spot = request.GET.get("is_idol_spot")
        if is_idol_spot:
            is_idol = is_idol_spot.lower() == "true"
            places = places.filter(is_idol_spot=is_idol)

        serializer = PlaceKRSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 한국어 관광지 생성
    def post(self, request):
        serializer = PlaceKRSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 한국어 관광지 상세 조회/수정/삭제 API
class PlaceKRDetailAPIView(APIView):

    def get_object(self, pk):
        try:
            return PlaceKR.objects.get(pk=pk)
        except PlaceKR.DoesNotExist:
            return None

# 관광지 상세 조회
    def get(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response(
                {"error": "관광지를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PlaceKRSerializer(place)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 관광지 전체 수정
    def put(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response(
                {"error": "관광지를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PlaceKRSerializer(place, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 관광지 부분 수정
    def patch(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response(
                {"error": "관광지를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PlaceKRSerializer(place, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 관광지 삭제
    def delete(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response(
                {"error": "관광지를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlaceENListAPIView(APIView):

    def get(self, request):
        places = PlaceEN.objects.all()

        category_name = request.GET.get("category")
        if category_name:
            places = places.filter(category__name_en=category_name)

        region_code = request.GET.get("region")
        if region_code:
            places = places.filter(region_code=region_code)

        search = request.GET.get("search")
        if search:
            places = places.filter(name__icontains=search)

        is_idol_spot = request.GET.get("is_idol_spot")
        if is_idol_spot:
            is_idol = is_idol_spot.lower() == "true"
            places = places.filter(is_idol_spot=is_idol)

        serializer = PlaceENSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PlaceENSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaceENDetailAPIView(APIView):

    def get_object(self, pk):
        try:
            return PlaceEN.objects.get(pk=pk)
        except PlaceEN.DoesNotExist:
            return None

    def get(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response(
                {"error": "관광지를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PlaceENSerializer(place)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response(
                {"error": "관광지를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PlaceENSerializer(place, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response(
                {"error": "관광지를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PlaceENSerializer(place, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response(
                {"error": "관광지를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlaceJPListAPIView(APIView):

    def get(self, request):
        places = PlaceJP.objects.all()

        category_name = request.GET.get("category")
        if category_name:
            places = places.filter(category__name_jp=category_name)  # 일본어 이름

        region_code = request.GET.get("region")
        if region_code:
            places = places.filter(region_code=region_code)

        search = request.GET.get("search")
        if search:
            places = places.filter(name__icontains=search)

        is_idol_spot = request.GET.get("is_idol_spot")
        if is_idol_spot:
            is_idol = is_idol_spot.lower() == "true"
            places = places.filter(is_idol_spot=is_idol)

        serializer = PlaceJPSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PlaceJPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaceJPDetailAPIView(APIView):

    def get_object(self, pk):
        try:
            return PlaceJP.objects.get(pk=pk)
        except PlaceJP.DoesNotExist:
            return None

    def get(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response({"error": "관광지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlaceJPSerializer(place)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response({"error": "관광지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlaceJPSerializer(place, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response({"error": "관광지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlaceJPSerializer(place, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response({"error": "관광지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlaceCNListAPIView(APIView):

    def get(self, request):
        places = PlaceCN.objects.all()

        category_name = request.GET.get("category")
        if category_name:
            places = places.filter(category__name_cn=category_name)  # 중국어 이름

        region_code = request.GET.get("region")
        if region_code:
            places = places.filter(region_code=region_code)

        search = request.GET.get("search")
        if search:
            places = places.filter(name__icontains=search)

        is_idol_spot = request.GET.get("is_idol_spot")
        if is_idol_spot:
            is_idol = is_idol_spot.lower() == "true"
            places = places.filter(is_idol_spot=is_idol)

        serializer = PlaceCNSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PlaceCNSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaceCNDetailAPIView(APIView):

    def get_object(self, pk):
        try:
            return PlaceCN.objects.get(pk=pk)
        except PlaceCN.DoesNotExist:
            return None

    def get(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response({"error": "관광지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlaceCNSerializer(place)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response({"error": "관광지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlaceCNSerializer(place, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response({"error": "관광지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlaceCNSerializer(place, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        place = self.get_object(pk)
        if place is None:
            return Response({"error": "관광지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)